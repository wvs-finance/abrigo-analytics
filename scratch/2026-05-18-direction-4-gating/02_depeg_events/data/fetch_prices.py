"""Fetch daily price history for USDC, USDT, DAI from CoinGecko free API.

Free-tier endpoint /coins/{id}/market_chart/range with `from`/`to` UNIX seconds
returns daily granularity automatically when range > 90 days. We chunk by year
to stay polite and cache results to JSON.
"""
import json
import time
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone

COINS = {
    "usd-coin": "usdc",        # USDC launched 2018-09-26
    "tether": "usdt",          # USDT exists since 2014; we restrict to 2018-09 for parity
    "dai": "dai",              # DAI multi-collateral live 2019-11; SAI before that
}

START = datetime(2018, 9, 26, tzinfo=timezone.utc)
END = datetime(2026, 5, 18, tzinfo=timezone.utc)


def fetch_range(coin_id: str, frm: int, to: int) -> dict:
    url = (
        f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
        f"?vs_currency=usd&from={frm}&to={to}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "abrigo-d4-research/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main():
    outdir = os.path.dirname(os.path.abspath(__file__))
    for coin_id, short in COINS.items():
        outpath = os.path.join(outdir, f"{short}_daily.json")
        if os.path.exists(outpath):
            print(f"[skip] {outpath} exists")
            continue
        prices_all: list[list[float]] = []
        # Chunk by ~360 days to stay under the 365-day daily-bucket boundary
        cur = START
        while cur < END:
            nxt = min(cur.replace(year=cur.year + 1), END)
            frm_ts = int(cur.timestamp())
            to_ts = int(nxt.timestamp())
            print(f"[{short}] {cur.date()} -> {nxt.date()} ", end="", flush=True)
            for attempt in range(5):
                try:
                    payload = fetch_range(coin_id, frm_ts, to_ts)
                    prices_all.extend(payload.get("prices", []))
                    print(f"ok ({len(payload.get('prices', []))} pts)")
                    break
                except urllib.error.HTTPError as e:
                    print(f"HTTP {e.code} retry {attempt+1}")
                    time.sleep(15 * (attempt + 1))
                except Exception as e:
                    print(f"err {e!r} retry {attempt+1}")
                    time.sleep(10 * (attempt + 1))
            else:
                print("FAILED, abort coin")
                prices_all = []
                break
            cur = nxt
            time.sleep(8)  # politeness — free tier is ~10–30 calls/min
        if prices_all:
            with open(outpath, "w") as fh:
                json.dump({"prices": prices_all}, fh)
            print(f"[write] {outpath} ({len(prices_all)} points)")


if __name__ == "__main__":
    main()
