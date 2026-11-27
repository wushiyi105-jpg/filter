"""命令行：seed / due / scan / jobs / doctor / serve。"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..adapters.llm import build_llm
from ..adapters.notify import WebhookNotifier
from ..adapters.store import SqliteStore
from ..app.jobs import enqueue_daily, run_due
from ..app.run import PROMPT, digest, scan
from ..config import Settings
from ..config import settings as default_settings
from ..doctor import main as doctor_main

app = typer.Typer(help="家电保养：该换什么、什么时候换", no_args_is_help=True)
console = Console()


def _settings(db: Path | None, port: int | None = None) -> Settings:
    s = default_settings.model_copy(deep=True)
    if db:
        s.db_path = db
    if port:
        s.port = port
    return s


def _store(settings: Settings) -> SqliteStore:
    return SqliteStore(settings.db_path)


@app.command()
def seed(db: Path = typer.Option(None)) -> None:
    """写入家电、耗材与维修记录。"""
    s = _settings(db)
    store = _store(s)
    data = json.loads(
        (Path(__file__).resolve().parents[2] / "data" / "seed.json").read_text(encoding="utf-8")
    )
    ids: dict[str, int] = {}
    for a in data["appliances"]:
        ids[a["name"]] = store.add_appliance(
            a["name"], a["brand"], a["model"], date.fromisoformat(a["since"]), a.get("intensity", 1.0)
        )
    for c in data["consumables"]:
        store.add_consumable(
            ids[c["appliance"]], c["name"], c["cycle_days"], date.fromisoformat(c["last_replaced"]),
            c["stock"], c["price_low"], c["price_high"],
        )
    for sv in data["services"]:
        store.add_service(
            ids[sv["appliance"]], date.fromisoformat(sv["on"]), sv["kind"], sv["cost"],
            date.fromisoformat(sv["warranty_until"]) if sv.get("warranty_until") else None,
        )
    console.print(
        f"已写入 {len(data['appliances'])} 台家电、{len(data['consumables'])} 个耗材、{len(data['services'])} 次维修"
    )


@app.command()
def due(day: str = typer.Option("", help="YYYY-MM-DD"), db: Path = typer.Option(None)) -> None:
    """到期清单。"""
    s = _settings(db)
    d = date.fromisoformat(day) if day else date.today()
    llm = build_llm(s.llm_base_url, s.llm_api_key, s.llm_model, PROMPT) if s.llm_enabled else None
    items, findings = scan(_store(s), d, llm)
    table = Table(title=f"到期清单 {d}")
    table.add_column("家电")
    table.add_column("耗材")
    table.add_column("到期")
    table.add_column("剩余")
    table.add_column("动作")
    for i in items:
        table.add_row(i.appliance, i.consumable, i.due_on.isoformat(), str(i.days_left), i.action)
    console.print(table)
    for f in findings:
        console.print(f"  [yellow]{f.rule_id}[/] -{f.penalty} {f.message}")


@app.command("scan")
def scan_cmd(day: str = typer.Option(""), db: Path = typer.Option(None)) -> None:
    """7 天内到期的推送文案。"""
    s = _settings(db)
    d = date.fromisoformat(day) if day else date.today()
    console.print(digest(_store(s), d))




@app.command()
def jobs(
    day: str = typer.Option(""), run: bool = typer.Option(False, "--run"), db: Path = typer.Option(None)
) -> None:
    """每日扫描入队 / 执行。"""
    s = _settings(db)
    d = date.fromisoformat(day) if day else date.today()
    store = _store(s)
    if run:
        console.print(f"发出 {run_due(store, s, d, WebhookNotifier(s.webhook_url))} 条")
        return
    console.print(f"入队 {enqueue_daily(store, d)} 条")


@app.command()
def doctor(db: Path = typer.Option(None)) -> None:
    """四项体检。"""
    raise typer.Exit(code=doctor_main(_settings(db)))


@app.command()
def serve(port: int = typer.Option(None), db: Path = typer.Option(None)) -> None:
    """Web 界面。"""
    import uvicorn

    from .web import create_app

    s = _settings(db, port)
    uvicorn.run(create_app(s), host="127.0.0.1", port=s.port)


if __name__ == "__main__":
    app()
