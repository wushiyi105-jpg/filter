from __future__ import annotations

from datetime import date

from filter.domain.rules.interval import add_months, irregular, next_due


def test_next_due_uses_intensity():
    assert next_due(date(2026, 9, 5), 90, 1.5) == date(2026, 11, 4)


def test_intensity_floor_prevents_zero_cycle():
    assert next_due(date(2026, 9, 5), 90, 0.0) == date(2027, 11, 29)


def test_add_months_handles_month_end():
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)


def test_add_months_across_year():
    assert add_months(date(2026, 11, 30), 2) == date(2027, 1, 30)


def test_leap_year_february():
    assert add_months(date(2024, 1, 31), 1) == date(2024, 2, 29)


def test_irregular_when_gap_off_by_half():
    assert irregular(date(2026, 9, 5), date(2026, 3, 1), 90) is True


def test_regular_gap_not_flagged():
    assert irregular(date(2026, 9, 5), date(2026, 6, 7), 90) is False

