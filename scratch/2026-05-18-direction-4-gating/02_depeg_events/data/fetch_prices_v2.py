"""Fetch daily USDC/USDT/DAI vs USD from CryptoCompare with explicit Kraken exchange.

Kraken-direct pairs avoid the inversion noise CryptoCompare introduces for
exchanges that quote only against BTC/ETH.

CryptoCompare free tier: 100k requests/month, no auth required. histoday returns
up to 2000 daily bars per call; we paginate backwards via toTs.
"""
import json
import os
import time
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))

# (CryptoCompare symbol, Kraken-listed?, output short name)
COINS = [
    ("USDC", "usdc"),
    ("USDT", "usdt"),
    ("DAI", "dai"),
]
EXCHANGE = "Kraken"

# USDC Kraken listing began 2020-08; pre-2020 we'll have to flag as no-data.
# USDT/USD on Kraken since 2017. DAI/USD on Kraken since 2019-12.
END_TS = int(datetime(2026, 5, 18, tzinfo=timezone.utc).timestamp())
START_TS = int(datetime(2018, 9, 26, tzinfo=timezone.utc).timestamp())


def fetch_page(sym: str, to_ts: int, limit: int = 2000) -> list[dict]:
    url = (
        f"https://min-api.cryptocompare.com/data/v2/histoday"
        f"?fsym={sym}&tsym=USD&limit={limit}&toTs={to_ts}&e={EXCHANGE}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "abrigo-d4-research/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode())
    if d.get("Response") != "Success":
        raise RuntimeError(f"{sym}: {d.get('Message')}")
    return d["Data"]["Data"]


def fetch_all(sym: str) -> list[dict]:
    out = []
    to_ts = END_TS
    while to_ts > START_TS:
        page = fetch_page(sym, to_ts, 2000)
        if not page:
            break
        # CryptoCompare prepends zero-volume rows when history doesn't extend
        # that far. Filter them.
        nonzero = [b for b in page if b.get("volumefrom", 0) > 0]
        if not nonzero:
            print(f"  [{sym}] all-zero page at toTs={to_ts}, stopping")
            break
        out = nonzero + out
        oldest = nonzero[0]["time"]
        print(f"  [{sym}] got {len(nonzero)} rows, oldest={datetime.fromtimestamp(oldest, tz=timezone.utc).date()}")
        if oldest <= START_TS:
            break
        to_ts = oldest - 1
        time.sleep(1.5)
    return [b for b in out if b["time"] >= START_TS and b["time"] <= END_TS]


def main():
    for sym, short in COINS:
        path = os.path.join(HERE, f"{short}_daily.json")
        if os.path.exists(path):
            print(f"[skip] {path}")
            continue
        print(f"[fetch] {sym} -> {EXCHANGE}/USD")
        try:
            rows = fetch_all(sym)
        except Exception as e:
            print(f"[err] {sym}: {e!r}")
            continue
        if not rows:
            print(f"[skip-empty] {sym}")
            continue
        # Re-encode in CoinGecko-compatible shape (ts_ms, close) so analyze.py works unchanged
        # but keep richer OHLCV in a separate file.
        prices = [[r["time"] * 1000, r["close"]] for r in rows]
        ohlcv = [
            {
                "ts": r["time"],
                "open": r["open"], "high": r["high"], "low": r["low"], "close": r["close"],
                "vol_from": r["volumefrom"], "vol_to": r["volumeto"],
            }
            for r in rows
        ]
        with open(path, "w") as fh:
            json.dump({"prices": prices, "source": f"cryptocompare:{EXCHANGE}"}, fh)
        with open(os.path.join(HERE, f"{short}_ohlcv.json"), "w") as fh:
            json.dump(ohlcv, fh)
        print(f"[write] {path} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
