"""Shared public-data clients. No API keys. Coinbase + Binance Vision only."""
import json, time, urllib.request, io, zipfile

UA = {"User-Agent": "liq-sr-research/1.0 (public-data, contact: research@localhost)"}

def _get(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def coinbase_book(product="BTC-USD", level=2):
    raw = _get(f"https://api.exchange.coinbase.com/products/{product}/book?level={level}")
    return json.loads(raw)

def coinbase_candles(product="BTC-USD", granularity=3600, limit=300):
    raw = _get(f"https://api.exchange.coinbase.com/products/{product}/candles?granularity={granularity}")
    rows = json.loads(raw)
    # [time, low, high, open, close, volume] per Coinbase docs
    rows = sorted(rows)[:limit]
    return rows

def coinbase_spot(product="BTC-USD"):
    raw = _get(f"https://api.coinbase.com/v2/prices/{product}/spot")
    return json.loads(raw)

def book_to_levels(book, side, n=50):
    out = []
    for px, sz, _n in book[side][:n]:
        out.append((float(px), float(sz)))
    return out

def walk_cost(levels, target_qty):
    """Simulate urgent market order against resting levels. Returns (avg_px, worst_px, levels_used, unfilled)."""
    remaining = target_qty
    cost = 0.0
    used = 0
    worst = None
    for px, sz in levels:
        take = min(remaining, sz)
        cost += take * px
        remaining -= take
        used += 1
        worst = px
        if remaining <= 1e-12:
            break
    filled = target_qty - max(remaining, 0)
    avg = cost / filled if filled > 0 else None
    return {"avg_px": avg, "worst_px": worst, "levels_used": used, "unfilled": max(remaining, 0)}
