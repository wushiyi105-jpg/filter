"""用例：取家电 → 算到期 → 模型报价建议 → 价格守卫 → 推送。"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from ..domain.engine import DueItem, build
from ..domain.guard import price
from ..domain.models import Finding
from ..domain.render import render
from ..ports import LLMPort, StorePort

PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "advice.md").read_text(encoding="utf-8")


def scan(
    store: StorePort, today: date, llm: LLMPort | None = None
) -> tuple[list[DueItem], list[Finding]]:
    items, warranty = build(
        store.list_appliances(), store.list_consumables(), store.list_services(), today
    )
    findings: list[Finding] = list(warranty)
    if llm is not None:
        for item in items[:3]:
            facts = f"家电={item.appliance} 耗材={item.consumable}"
            try:
                data = json.loads(llm.write(PROMPT, facts))
            except Exception:  # noqa: BLE001 模型失败不影响到期清单
                continue
            low = float(data.get("price_low") or item.price_low)
            high = float(data.get("price_high") or item.price_high)
            item.price_low, item.price_high, finding = price(
                low, high, item.price_low, item.price_high, item.consumable
            )
            if finding:
                findings.append(finding)
    return items, findings


def digest(store: StorePort, today: date) -> str:
    items, _ = scan(store, today)
    soon = [i for i in items if i.days_left <= 7]
    if not soon:
        return f"{today} 没有 7 天内到期的耗材。"
    return render(soon)


def seed_data(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
