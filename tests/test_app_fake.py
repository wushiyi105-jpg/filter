"""真实内存 Store 跑 digest：不建 SQLite，mypy 校验 StorePort。"""

from __future__ import annotations

from datetime import date
from typing import Any

from filter.app.run import digest
from filter.domain.models import Appliance, Consumable, Service
from filter.ports import StorePort


class InMemoryStore:
    def list_appliances(self) -> list[Appliance]:
        return []

    def list_consumables(self) -> list[Consumable]:
        return []

    def list_services(self) -> list[Service]:
        return []

    def enqueue(self, idem_key: str, kind: str, payload: str, due_on: date) -> bool:
        return True

    def due_jobs(self, today: date) -> list[Any]:
        return []

    def finish_job(self, job_id: int, ok: bool, error: str = "") -> None:
        return None


def test_digest_with_memory_store() -> None:
    store: StorePort = InMemoryStore()
    out = digest(store, date(2026, 1, 5))
    assert out
