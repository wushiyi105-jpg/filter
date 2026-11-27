"""30 个常见型号的耗材周期、价格带与购买渠道。"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def models() -> list[dict[str, Any]]:
    return json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))["models"]


def find(appliance_model: str, consumable: str) -> dict[str, Any] | None:
    exact = [
        row
        for row in models()
        if row["model"].lower() == appliance_model.lower() and row["consumable"] == consumable
    ]
    if exact:
        return exact[0]
    by_name = [row for row in models() if row["consumable"] == consumable]
    return by_name[0] if by_name else None
