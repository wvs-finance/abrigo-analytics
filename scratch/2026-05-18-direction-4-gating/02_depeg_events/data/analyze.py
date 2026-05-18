"""Analyze fetched USDC/USDT/DAI daily prices for depeg events and GPD POT fit.

Outputs printed in markdown-friendly format for inclusion in findings.md.
"""
import json
import os
import math
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))


def load(short: str) -> pd.DataFrame:
    with open(os.path.join(HERE, f"{short}_daily.json")) as fh:
        d = json.load(fh)
    df = pd.DataFrame(d["prices"], columns=["ts_ms", "price"])
    df["date"] = pd.to_datetime(df["ts_ms"], unit="ms", utc=True).dt.floor("D")
    # CoinGecko daily endpoint returns one snapshot per day (00:00 UTC close).
    df = df.drop_duplicates(subset="date", keep="last").sort_values("date").reset_index(drop=True)
    df["tail_below"] = (1.0 - df["price"]).clip(lower=0)  # below-peg distance
    df["tail_above"] = (df["price"] - 1.0).clip(lower=0)
    df["abs_dev"] = (df["price"] - 1.0).abs()
    return df


def summarize(df: pd.DataFrame, name: str) -> None:
    print(f"\n### {name}")
    print(f"- N daily observations: {len(df)}")
    print(f"- First/last date: {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"- Mean price: {df['price'].mean():.6f}")
    print(f"- Min/max price: {df['price'].min():.6f} / {df['price'].max():.6f}")
    print(f"- StdDev: {df['price'].std():.6f}")
    for thr in (0.001, 0.0025, 0.005, 0.01, 0.02, 0.05, 0.10):
        n = (df["abs_dev"] >= thr).sum()
        nb = (df["tail_below"] >= thr).sum()
        na = (df["tail_above"] >= thr).sum()
        print(f"- |dev|≥{thr*100:.2f}%: {n} days (below={nb}, above={na})")


def find_episodes(df: pd.DataFrame, side: str, threshold: float, min_persist_days: int = 1) -> list[dict]:
    """An episode = contiguous run of days with tail-distance >= threshold on the given side.

    side: 'below' or 'above'.
    """
    col = "tail_below" if side == "below" else "tail_above"
    flag = (df[col] >= threshold).astype(int).values
    episodes = []
    i = 0
    n = len(flag)
    while i < n:
        if flag[i] == 1:
            j = i
            while j < n and flag[j] == 1:
                j += 1
            run = df.iloc[i:j]
            if (j - i) >= min_persist_days:
                episodes.append({
                    "side": side,
                    "start": run["date"].iloc[0].date(),
                    "end": run["date"].iloc[-1].date(),
                    "days": j - i,
                    "max_tail_pct": run[col].max() * 100,
                    "min_price": run["price"].min() if side == "below" else None,
                    "max_price": run["price"].max() if side == "above" else None,
                })
            i = j
        else:
            i += 1
    return episodes


def gpd_fit(exceedances: np.ndarray) -> tuple[float, float, int]:
    """Fit GPD by MLE on positive exceedances over threshold u (already subtracted).

    Returns (shape ξ, scale σ, N).
    """
    if len(exceedances) < 5:
        return (float("nan"), float("nan"), len(exceedances))
    # scipy.stats.genpareto: shape c == ξ, scale == σ, loc=0
    c, loc, scale = stats.genpareto.fit(exceedances, floc=0)
    return (c, scale, len(exceedances))


def recovery_stats(df: pd.DataFrame, threshold: float = 0.005) -> dict:
    """For each crossing of |dev|>=threshold, time until next return to within 0.1%."""
    inside = 0.001
    dev = (df["price"] - 1.0).values
    abs_dev = np.abs(dev)
    times = []
    i = 0
    n = len(df)
    while i < n:
        if abs_dev[i] >= threshold:
            j = i
            while j < n and abs_dev[j] >= inside:
                j += 1
            if j > i:
                times.append(j - i)  # days until back inside ±0.1%
            i = j
        else:
            i += 1
    if not times:
        return {"n": 0}
    arr = np.array(times)
    return {
        "n": int(len(arr)),
        "mean_days": float(arr.mean()),
        "median_days": float(np.median(arr)),
        "p90_days": float(np.percentile(arr, 90)),
        "max_days": int(arr.max()),
    }


def main():
    out_lines = []
    coins = []
    for short in ("usdc", "usdt", "dai"):
        path = os.path.join(HERE, f"{short}_daily.json")
        if not os.path.exists(path):
            print(f"[missing] {path}")
            continue
        df = load(short)
        coins.append((short, df))
        summarize(df, short.upper())

    print("\n## Episodes (≥1.0% tail-distance, ≥1 day)\n")
    for short, df in coins:
        print(f"\n### {short.upper()} below-peg episodes (≥1.0%)")
        eps = find_episodes(df, "below", 0.01, 1)
        for e in eps:
            print(f"- {e['start']} → {e['end']} ({e['days']} d), max tail {e['max_tail_pct']:.2f}%, min price {e['min_price']:.4f}")
        print(f"### {short.upper()} above-peg episodes (≥1.0%)")
        eps = find_episodes(df, "above", 0.01, 1)
        for e in eps:
            print(f"- {e['start']} → {e['end']} ({e['days']} d), max tail {e['max_tail_pct']:.2f}%, max price {e['max_price']:.4f}")

    print("\n## Episodes (≥0.5% tail-distance, ≥1 day) — noise + event mixture\n")
    for short, df in coins:
        print(f"\n### {short.upper()} |dev|≥0.5%")
        eps_b = find_episodes(df, "below", 0.005, 1)
        eps_a = find_episodes(df, "above", 0.005, 1)
        for e in sorted(eps_b + eps_a, key=lambda x: x["start"]):
            label = "BELOW" if e["side"] == "below" else "ABOVE"
            mp = e.get("min_price") if e["side"] == "below" else e.get("max_price")
            print(f"- {e['start']} → {e['end']} ({e['days']} d) {label} max {e['max_tail_pct']:.2f}% price {mp:.4f}")

    print("\n## GPD POT fits (below-peg, u = $0.99 ⇒ exceedance over 1%)\n")
    for short, df in coins:
        u = 0.01
        exc = df.loc[df["tail_below"] > u, "tail_below"].values - u
        xi, sigma, N = gpd_fit(exc)
        print(f"- {short.upper()}: N_exc={N}, ξ̂={xi:.4f}, σ̂={sigma:.4f}")
        # also at u = 0.005 (0.5%)
        u2 = 0.005
        exc2 = df.loc[df["tail_below"] > u2, "tail_below"].values - u2
        xi2, sigma2, N2 = gpd_fit(exc2)
        print(f"- {short.upper()} (u=0.5%): N_exc={N2}, ξ̂={xi2:.4f}, σ̂={sigma2:.4f}")

    print("\n## Recovery statistics (days from |dev|≥0.5% back to within ±0.1%)\n")
    for short, df in coins:
        r = recovery_stats(df, 0.005)
        print(f"- {short.upper()}: {r}")


if __name__ == "__main__":
    main()
