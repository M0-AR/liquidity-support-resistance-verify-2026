"""Fetch-once live public data, run E01-E08, write results + figures. Verifies by execution."""
import os, json, time, datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from common import coinbase_book, coinbase_candles, book_to_levels
import experiments as X

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
RES = os.path.join(ROOT, "results")
FIG = os.path.join(RES, "figures")
os.makedirs(RAW, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

def main():
    stamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print("fetch: coinbase book + candles (public, no key)...")
    book = coinbase_book("BTC-USD")
    candles = coinbase_candles("BTC-USD", 3600, 300)
    json.dump(book, open(os.path.join(RAW, "coinbase_BTC-USD_book_L2.json"), "w"))
    json.dump(candles, open(os.path.join(RAW, "coinbase_BTC-USD_1h_300.json"), "w"))
    print(f"book levels: bids={len(book['bids'])} asks={len(book['asks'])}; candles={len(candles)}")

    out = {"stamp_utc": stamp, "symbol": "BTC-USD", "venue": "coinbase",
           "note": "Single-venue visible book; not consolidated market. Stops latent by design."}
    out["E01_wall"] = X.e01_wall_absorption(book)
    out["E02_dynamics"] = X.e02_book_dynamics("BTC-USD", polls=3, gap=6)
    out["E03_round"] = X.e03_round_numbers(candles)
    out["E04_bounce_break"] = X.e04_bounce_vs_break(candles)
    out["E05_follow"] = X.e05_halt_insufficient(candles)
    out["E06_latent"] = X.e06_latent_vs_visible(book, candles)
    out["E07_definition"] = X.e07_definition_fragility(candles)
    out["E08_price_alone"] = X.e08_price_alone_insufficient(candles)

    # hidden-pattern probe: imbalance vs next-candle direction (toy, honest N)
    bids = book_to_levels(book, "bids", 50); asks = book_to_levels(book, "asks", 50)
    bq = sum(s for _, s in bids); aq = sum(s for _, s in asks)
    out["HIDDEN_imbalance_snapshot"] = {"bid_qty": bq, "ask_qty": aq,
        "imbalance": (bq - aq) / (bq + aq) if (bq + aq) else None,
        "caveat": "Single snapshot cannot predict; included to PREVENT overclaim. Time-series imbalance->return test needs L2 replay (Binance Vision / Tardis) listed as next step."}

    json.dump(out, open(os.path.join(RES, "summary.json"), "w"), indent=2, default=float)
    print(json.dumps(out, indent=2, default=float)[:4000])

    # figures (verify by rendering, not by hand)
    asks50 = book_to_levels(book, "asks", 50); bids50 = book_to_levels(book, "bids", 50)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.barh([p for p, _ in bids50[::-1]], [s for _, s in bids50[::-1]], label="bids")
    ax.barh([p for p, _ in asks50], [s for _, s in asks50], label="asks")
    ax.set_title("BTC-USD live L2 depth snapshot (Coinbase, top-50 each side)")
    ax.legend(); fig.tight_layout(); fig.savefig(os.path.join(FIG, "depth_snapshot.png"), dpi=120)

    cl = np.array([c[4] for c in candles])
    fig2, ax2 = plt.subplots(figsize=(9, 3))
    ax2.plot(cl); ax2.set_title("BTC-USD 1h closes (Coinbase, 300 candles, live)")
    fig2.tight_layout(); fig2.savefig(os.path.join(FIG, "closes_1h.png"), dpi=120)
    print("wrote results/summary.json + figures.")

if __name__ == "__main__":
    main()
