"""价格守卫：模型给的价格必须落在种子区间内，越界丢该字段。"""

from __future__ import annotations

from .models import Finding

PENALTY = 6


def price(low: float, high: float, seed_low: float, seed_high: float, item: str) -> tuple[float, float, Finding | None]:
    if low > high:
        low, high = high, low
    if low < seed_low or high > seed_high:
        finding = Finding(
            "guard.price",
            f"{item} 报价 {low:g}-{high:g} 越出参考 {seed_low:g}-{seed_high:g}，已丢弃",
            PENALTY,
            item,
        )
        return seed_low, seed_high, finding
    return low, high, None

