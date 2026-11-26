from __future__ import annotations

from datetime import date

from filter.domain.models import Consumable, Service
from filter.domain.rules.stock import check
from filter.domain.rules.warranty import check as warranty_check


def _c(stock: int) -> Consumable:
    return Consumable(1, 1, "PP 棉滤芯", 90, date(2026, 9, 5), stock, 39, 69)


def test_empty_only_says_buy():
    findings = check(_c(0))
    assert findings[0].rule_id == "stock.empty"
    assert "买" in findings[0].message


def test_low_stock_goes_shopping_list():
    findings = check(_c(1))
    assert findings[0].rule_id == "stock.low"


def test_enough_stock_silent():
    assert check(_c(3)) == []


def test_warranty_soon_flagged():
    services = [Service(1, 1, date(2026, 9, 5), "换滤芯", 0, date(2026, 12, 15))]
    findings = warranty_check(services, date(2026, 11, 27))
    assert findings[0].rule_id == "warranty.soon"
    assert "18 天" in findings[0].message


def test_warranty_far_away_silent():
    services = [Service(1, 1, date(2026, 3, 2), "清洗", 180, date(2027, 3, 2))]
    assert warranty_check(services, date(2026, 11, 27)) == []
