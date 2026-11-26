from __future__ import annotations

from datetime import date

from filter.domain.engine import build, due_items, due_soon
from filter.domain.models import Appliance, Consumable


def _data():
    a = Appliance(1, "净水器", "美的", "MRO1890", date(2024, 3, 10), 1.0)
    rows = [
        Consumable(1, 1, "PP 棉", 90, date(2026, 9, 5), 2, 39, 69),
        Consumable(2, 1, "RO 膜", 720, date(2025, 6, 1), 0, 260, 420),
        Consumable(3, 1, "后置炭", 365, date(2026, 1, 20), 3, 80, 120),
    ]
    return [a], rows


def test_sorted_by_days_left():
    items = due_items(*_data(), date(2026, 11, 27))
    assert items[0].days_left <= items[-1].days_left


def test_empty_stock_switches_to_buy():
    items = due_items(*_data(), date(2026, 11, 27))
    ro = next(i for i in items if i.consumable == "RO 膜")
    assert ro.action == "购买"


def test_due_soon_only_seven_days():
    items = due_items(*_data(), date(2026, 11, 27))
    soon = due_soon(items)
    assert all(i.days_left <= 7 for i in soon)
    assert any(i.consumable == "PP 棉" for i in soon)


def test_build_returns_warranty_findings():
    services = []
    items, findings = build(*_data(), services, date(2026, 11, 27))
    assert len(items) == 3
    assert findings == []
