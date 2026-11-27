"""领域对象：家电、耗材、维修。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Appliance:
    id: int
    name: str
    brand: str
    model: str
    since: date
    intensity: float = 1.0


@dataclass(frozen=True)
class Consumable:
    id: int
    appliance_id: int
    name: str
    cycle_days: int
    last_replaced: date
    stock: int
    price_low: float
    price_high: float


@dataclass(frozen=True)
class Service:
    id: int
    appliance_id: int
    on: date
    kind: str
    cost: float
    warranty_until: date | None


@dataclass
class Finding:
    rule_id: str
    message: str
    penalty: int
    target: str = ""


@dataclass
class DueItem:
    appliance: str
    consumable: str
    due_on: date
    days_left: int
    stock: int
    action: str
    price_low: float
    price_high: float
    brand: str = ""
    model: str = ""
    spec: str = ""
    channel: str = ""
    price_source: str = "catalog"
    findings: list[Finding] = field(default_factory=list)
