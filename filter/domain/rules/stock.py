"""余量：≤1 进待购，0 只提醒购买。"""

from __future__ import annotations

from ..models import Consumable, Finding

LOW_PENALTY = 3
EMPTY_PENALTY = 2


def check(c: Consumable) -> list[Finding]:
    if c.stock <= 0:
        return [Finding("stock.empty", f"{c.name} 已用完，先买再换", EMPTY_PENALTY, c.name)]
    if c.stock <= 1:
        return [Finding("stock.low", f"{c.name} 只剩 {c.stock} 件，进待购清单", LOW_PENALTY, c.name)]
    return []
