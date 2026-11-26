"""周期推算：上次更换 + 周期 / 使用强度。"""

from __future__ import annotations

import calendar
from datetime import date, timedelta

PENALTY_DUE = 2
PENALTY_IRREGULAR = 5


def add_days(base: date, days: int) -> date:
    return base + timedelta(days=days)


def next_due(last_replaced: date, cycle_days: int, intensity: float = 1.0) -> date:
    if cycle_days <= 0:
        raise ValueError("cycle_days 必须为正")
    intensity = max(0.2, intensity)
    return add_days(last_replaced, int(cycle_days / intensity))


def add_months(base: date, months: int) -> date:
    month = base.month - 1 + months
    year = base.year + month // 12
    month = month % 12 + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def irregular(last_replaced: date, previous: date | None, cycle_days: int) -> bool:
    if previous is None:
        return False
    actual = (last_replaced - previous).days
    if cycle_days <= 0:
        return False
    return abs(actual - cycle_days) / cycle_days > 0.5
