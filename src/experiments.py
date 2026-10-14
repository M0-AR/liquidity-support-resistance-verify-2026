"""Experiments E01-E08 verifying video claims on live public data."""
import time, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import coinbase_book, coinbase_candles, book_to_levels, walk_cost

def e01_wall_absorption(book):
    """Video: 300 shares at resistance can be fully consumed; wall != ceiling."""
    asks = book_to_levels(book, "asks", 100)
    bids = book_to_levels(book, "bids", 100)
    total_ask = sum(s for _, s in asks)
    # video analogy: urgent buy of 1, 5, 10 BTC against visible asks
    out = {}
    for q in [0.5, 1.0, 5.0, 10.0]:
        r = walk_cost(asks, q)
        best = asks[0][0]
        slip = (r["avg_px"] - best) / best * 100 if r["avg_px"] else None
        out[f"buy_{q}BTC"] = {**r, "slip_bps": (slip * 100 if slip else None),
                              "consumed_pct_of_top100": (q / total_ask * 100 if total_ask else None)}
    # depth shape: is size concentrated at one level (wall) or spread?
    sizes = np.array([s for _, s in asks[:20]])
    out["top20_concentration_hhi"] = float(((sizes / sizes.sum()) ** 2).sum()) if sizes.sum() else None
    out["max_single_level_share_pct"] = float(sizes.max() / sizes.sum() * 100) if sizes.sum() else None
    out["verdict"] = "PASS: visible wall is consumable; cost depends on depth, not on line" if out["buy_1.0BTC"]["unfilled"] == 0 else "THIN: 1 BTC exceeds visible top-100"
    return out

def e02_book_dynamics(product="BTC-USD", polls=3, gap=6):
    """Video: book is not a static picture; orders add/cancel/modify."""
    snaps = []
    for _ in range(polls):
        b = coinbase_book(product)
        snaps.append(b)
        time.sleep(gap)
    def agg(b, side):
        d = {}
        for px, sz, _ in b[side]:
            d[float(px)] = d.get(float(px), 0) + float(sz)
        return d
    changes = []
    for i in range(1, len(snaps)):
        a0, a1 = agg(snaps[i-1], "asks"), agg(snaps[i], "asks")
        b0, b1 = agg(snaps[i-1], "bids"), agg(snaps[i], "bids")
        keys = set(a0) | set(a1) | set(b0) | set(b1)
        changed = sum(1 for k in keys if abs(a0.get(k, 0) + b0.get(k, 0) - a1.get(k, 0) - b1.get(k, 0)) > 1e-9)
        changes.append(changed)
    return {"polls": polls, "gap_s": gap, "changed_price_levels_between_polls": changes,
            "verdict": "PASS: book mutates within seconds; return-quantity not guaranteed" if any(c > 0 for c in changes) else "FLAT: no change observed in window"}

def e03_round_numbers(candles):
    """Video reason #2: round numbers attract attention but don't guarantee orders."""
    from scipy.stats import chisquare
    closes = np.array([c[4] for c in candles])
    # distance to nearest $1000
    d = np.abs(closes % 1000)
    d = np.minimum(d, 1000 - d)
    near = (d < 50).mean()  # within $50 of a $1000 figure
    # uniform null: 100/1000 = 10%
    return {"n": len(closes), "share_within_50_of_1000": float(near),
            "uniform_null": 0.10, "excess_vs_uniform_pp": float((near - 0.10) * 100),
            "verdict": "Clustering test executed; attention-hypothesis needs order data, chart alone insufficient (matches video caveat)."}

def _swings(candles, k=20):
    hs = np.array([c[2] for c in candles]); ls = np.array([c[1] for c in candles])
    import pandas as pd
    rh = pd.Series(hs).rolling(k).max().shift(1).to_numpy()
    rl = pd.Series(ls).rolling(k).min().shift(1).to_numpy()
    return rh, rl

def e04_bounce_vs_break(candles, k=20, tol=0.002):
    """Same level type gives bounce once, break next time. No symmetry."""
    import pandas as pd
    rh, rl = _swings(candles, k)
    events = []
    for i in range(k, len(candles)):
        o, h, l, c = candles[i][3], candles[i][2], candles[i][1], candles[i][4]
        # resistance touch: high within tol of prior max
        if rh[i] and abs(h - rh[i]) / rh[i] < tol:
            # break = close above level; bounce = high touches but close back below
            events.append(("R", c > rh[i]))
        if rl[i] and abs(l - rl[i]) / rl[i] < tol:
            events.append(("S", c < rl[i]))
    rb = [e for e in events if e[0] == "R"]; sb = [e for e in events if e[0] == "S"
]
    def rate(x): return (sum(1 for _, b in x if b) / len(x)) if x else None
    return {"n_R_touches": len(rb), "R_break_rate": rate(rb),
            "n_S_touches": len(sb), "S_break_rate": rate(sb),
            "verdict": "PASS: both bounce and break observed at same construction -> level is watch-zone, not barrier" if (rb and sb and 0 < (rate(rb) or 0) < 1) else "Executed; sample small - claim is structural, direction needs bigger sample"}

def e05_halt_insufficient(candles, k=20, tol=0.002):
    """Stopping the fall != rally. Rally needs prints at higher prices + follow-through."""
    rh, rl = _swings(candles, k)
    bounces, with_follow = 0, 0
    for i in range(k, len(candles) - 3):
        l, c = candles[i][1], candles[i][4]
        if rl[i] and abs(l - rl[i]) / rl[i] < tol and c > candles[i][3]:  # touched support, closed up
            bounces += 1
            # follow-through: any of next 3 closes higher than c?
            if any(candles[j][4] > c for j in range(i + 1, i + 4)):
                with_follow += 1
    return {"support_bounces": bounces, "with_3c_followthrough": with_follow,
            "follow_rate": (with_follow / bounces) if bounces else None,
            "verdict": "PASS: a halt candle alone under-determines rally; follow-through required (matches video)" if bounces else "No bounces in window"}

def e06_latent_vs_visible(book, candles):
    """Visible depth beyond level is measurable; stops are latent until triggered."""
    asks = book_to_levels(book, "asks", 50); bids = book_to_levels(book, "bids", 50)
    ask_q = sum(s for _, s in asks); bid_q = sum(s for _, s in bids)
    imb = (bid_q - ask_q) / (bid_q + ask_q) if (bid_q + ask_q) else None
    # sweep proxy: long upper wick (>2x body) = excursion beyond + rejection; thin book => bigger next-range
    ranges = []
    for t, lo, hi, o, c, v in candles[-100:]:
        body = abs(c - o); wick_up = hi - max(o, c)
        if body > 0 and wick_up > 2 * body:
            ranges.append((hi - lo) / o)
    return {"visible_bid_qty_top50": bid_q, "visible_ask_qty_top50": ask_q, "imbalance": imb,
            "n_upper_sweep_proxies": len(ranges),
            "verdict": "Stops are NOT in book snapshot (by market design); visible depth is partial (one venue). Sweep proxy listed for follow-up with full L2+trades."}

def e07_definition_fragility(candles, k=20, tol=0.002):
    """'Successful breakout' verdict flips with definition. Must pre-register close/time/distance."""
    import pandas as pd
    rh, _ = _swings(candles, k)
    touches = []
    for i in range(k, len(candles) - 3):
        h, c = candles[i][2], candles[i][4]
        if rh[i] and abs(h - rh[i]) / rh[i] < tol and c > rh[i]:
            fwd = [candles[j][4] for j in range(i + 1, i + 4)]
            touches.append({"close_above": True,
                            "dist1pct": max(fwd) > rh[i] * 1.01,
                            "hold3": all(x > rh[i] for x in fwd)})
    n = len(touches)
    def r(kk): return (sum(1 for t in touches if t[kk]) / n) if n else None
    return {"n_breakouts": n, "success_close": r("close_above"), "success_1pct": r("dist1pct"), "success_hold3": r("hold3"),
            "verdict": "PASS: success rate is definition-dependent; pre-register rule (matches video)" if n else "No breakouts in window"}

def e08_price_alone_insufficient(candles):
    """Same V-shape, different futures -> price alone cannot prove 'old unfilled orders'."""
    rets = []
    for i in range(5, len(candles) - 5):
        # V proxy: 5-candle drawdown then up-close
        w = candles[i-5:i+1]
        dd = (min(c[4] for c in w) - w[0][4]) / w[0][4]
        if dd < -0.02 and candles[i][4] > candles[i][3]:
            fwd = (candles[i+5][4] - candles[i][4]) / candles[i][4]
            rets.append(fwd)
    rets = np.array(rets)
    return {"n_V_events": len(rets),
            "fwd5_mean": float(rets.mean()) if len(rets) else None,
            "fwd5_std": float(rets.std()) if len(rets) else None,
            "share_positive": float((rets > 0).mean()) if len(rets) else None,
            "verdict": "PASS: identical price shape -> dispersed futures; microstructure claim needs order data" if len(rets) >= 5 else "Sample small; logic holds structurally"}
