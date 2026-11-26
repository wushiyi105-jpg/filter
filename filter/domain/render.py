"""离线建议文字。"""

from __future__ import annotations

from .models import DueItem


def render(items: list[DueItem]) -> str:
    if not items:
        return "没有到期的耗材。"
    lines = ["到期清单："]
    for i in items:
        lines.append(
            f"- {i.appliance} {i.consumable}：{i.due_on}（{i.days_left} 天）"
            f"{i.action}，参考 {i.price_low:g}-{i.price_high:g} 元"
        )
    return "\n".join(lines)
