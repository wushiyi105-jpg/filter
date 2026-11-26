"""每日扫描：同一耗材同一天只推一次。"""

from __future__ import annotations

from datetime import date

from ..adapters.notify import WebhookNotifier
from ..adapters.store import SqliteStore
from ..config import Settings
from .run import digest, scan


def enqueue_daily(store: SqliteStore, today: date) -> int:
    items, _ = scan(store, today)
    n = 0
    for item in items:
        if item.days_left > 7:
            continue
        key = f"filter:{today}:{item.appliance}:{item.consumable}"
        n += int(store.enqueue(key, "due_reminder", item.consumable, today))
    return n


def run_due(store: SqliteStore, settings: Settings, today: date) -> int:
    notifier = WebhookNotifier(settings.webhook_url)
    sent = 0
    for job in store.due_jobs(today):
        ok = notifier.send(digest(store, today))
        store.finish_job(job.id, ok, "" if ok else "推送失败")
        sent += int(ok)
    return sent
