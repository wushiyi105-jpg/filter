"""到期推算：按剩余天数排序，余量为 0 时改口径。"""

from __future__ import annotations

from datetime import date

from .catalog import find as find_catalog
from .models import Appliance, Consumable, DueItem, Finding, Service
from .rules.interval import irregular, next_due
from .rules.stock import check as stock_check
from .rules.warranty import check as warranty_check

REPLACE = "更换"
BUY_ONLY = "购买"


def due_items(
    appliances: list[Appliance], consumables: list[Consumable], today: date
) -> list[DueItem]:
    names = {a.id: a for a in appliances}
    out: list[DueItem] = []
    for c in consumables:
        app = names.get(c.appliance_id)
        if app is None:
            continue
        due = next_due(c.last_replaced, c.cycle_days, app.intensity)
        days_left = (due - today).days
        action = BUY_ONLY if c.stock <= 0 else REPLACE
        item = DueItem(
            appliance=app.name, consumable=c.name, due_on=due, days_left=days_left,
            stock=c.stock, action=action, price_low=c.price_low, price_high=c.price_high,
            brand=app.brand, model=app.model,
        )
        row = find_catalog(app.model, c.name)
        if row:
            item.spec = str(row["spec"])
            item.channel = str(row["channel"])
            # 种子价格优先；目录给出的价格带只在种子没填时才接管。
            if item.price_low <= 0 and item.price_high <= 0:
                item.price_low = float(row["price_low"])
                item.price_high = float(row["price_high"])
        item.findings.extend(stock_check(c))
        if irregular(c.last_replaced, None, c.cycle_days):
            item.findings.append(
                Finding("interval.irregular", f"{c.name} 更换间隔与周期差超过 50%", 5, c.name)
            )
        out.append(item)
    out.sort(key=lambda i: (i.days_left, i.appliance, i.consumable))
    return out


def due_soon(items: list[DueItem]) -> list[DueItem]:
    return [i for i in items if i.days_left <= 7]


def build(
    appliances: list[Appliance], consumables: list[Consumable], services: list[Service], today: date
) -> tuple[list[DueItem], list[Finding]]:
    items = due_items(appliances, consumables, today)
    return items, warranty_check(services, today)
