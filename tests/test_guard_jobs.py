from __future__ import annotations

from datetime import date

from filter.app.jobs import enqueue_daily
from filter.domain.guard import price


def test_price_inside_seed_range_kept():
    low, high, finding = price(40, 60, 39, 69, "PP 棉")
    assert (low, high) == (40, 60)
    assert finding is None


def test_price_outside_range_dropped():
    low, high, finding = price(30, 200, 39, 69, "PP 棉")
    assert (low, high) == (39, 69)
    assert finding is not None and finding.rule_id == "guard.price"


def test_daily_enqueue_deduped(store):
    a = store.add_appliance("净水器", "美的", "M1890", date(2024, 3, 10))
    store.add_consumable(a, "PP 棉", 90, date(2026, 9, 5), 2, 39, 69)
    first = enqueue_daily(store, date(2026, 11, 27))
    second = enqueue_daily(store, date(2026, 11, 27))
    assert first >= 1
    assert second == 0
