import os, json, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from common import walk_cost

def test_walk_cost_consumes_wall():
    lv = [(100.0, 10.0), (101.0, 10.0), (102.0, 10.0)]
    r = walk_cost(lv, 25.0)
    assert r["unfilled"] == 0
    assert r["levels_used"] == 3
    assert abs(r["avg_px"] - (100*10+101*10+102*5)/25) < 1e-9

def test_walk_cost_thin_book_leaves_unfilled():
    assert walk_cost([(100.0, 1.0)], 5.0)["unfilled"] == 4.0

def test_summary_exists_and_passes():
    p = os.path.join(os.path.dirname(__file__), "..", "results", "summary.json")
    assert os.path.exists(p), "run src/run_all.py first"
    s = json.load(open(p))
    for k in ["E01_wall", "E02_dynamics", "E04_bounce_break", "E07_definition"]:
        assert k in s
    assert s["E02_dynamics"]["changed_price_levels_between_polls"][0] > 0
