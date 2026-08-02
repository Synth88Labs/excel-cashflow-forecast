"""Tests for Excel Cash-Flow & Runway Forecaster. Run with:  python -m pytest"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cashflow import is_active, project  # noqa: E402


def _item(**kw):
    base = {"name": "x", "type": "inflow", "amount": 100, "start": 1, "freq": "monthly", "end": None}
    base.update(kw)
    return base


def test_active_monthly():
    it = _item(freq="monthly", start=2)
    assert not is_active(it, 1)
    assert is_active(it, 2) and is_active(it, 5)


def test_active_once():
    it = _item(freq="once", start=3)
    assert is_active(it, 3)
    assert not is_active(it, 4)


def test_active_quarterly():
    it = _item(freq="quarterly", start=1)
    assert is_active(it, 1) and is_active(it, 4) and is_active(it, 7)
    assert not is_active(it, 2) and not is_active(it, 3)


def test_active_end_month():
    it = _item(freq="monthly", start=1, end=3)
    assert is_active(it, 3)
    assert not is_active(it, 4)


def test_running_balance():
    items = [_item(type="inflow", amount=1000, freq="monthly"),
             _item(type="outflow", amount=400, freq="monthly")]
    r = project(items, start_balance=500, months=3)
    # net +600/month: 1100, 1700, 2300
    assert [row["balance"] for row in r["rows"]] == [1100, 1700, 2300]
    assert r["ending_balance"] == 2300
    assert r["runway"] is None


def test_runway_detected():
    items = [_item(type="inflow", amount=1000, freq="monthly"),
             _item(type="outflow", amount=1500, freq="monthly")]
    r = project(items, start_balance=1200, months=6)
    # -500/month from 1200: 700, 200, -300 -> runway month 3
    assert r["runway"] == 3
    assert r["lowest_month"] == 6


def test_once_and_quarterly_combine():
    items = [_item(type="inflow", amount=5000, freq="quarterly", start=1),
             _item(type="outflow", amount=8000, freq="once", start=2)]
    r = project(items, start_balance=10000, months=4)
    # m1 +5000=15000; m2 -8000=7000; m3 0=7000; m4 +5000=12000
    assert [row["balance"] for row in r["rows"]] == [15000, 7000, 7000, 12000]
