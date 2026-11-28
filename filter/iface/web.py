"""FastAPI + Jinja2：到期面板。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..adapters.llm import build_llm
from ..adapters.store import SqliteStore
from ..app.run import PROMPT, digest, scan
from ..config import Settings

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))


def create_app(settings: Settings, store: SqliteStore | None = None) -> FastAPI:
    app = FastAPI(title="Filter", version="1.0.0")
    app.mount(
        "/static",
        StaticFiles(directory=str(Path(__file__).resolve().parents[2] / "static")),
        name="static",
    )
    store = store or SqliteStore(settings.db_path)
    llm = build_llm(settings.llm_base_url, settings.llm_api_key, settings.llm_model, PROMPT) if settings.llm_enabled else None

    def render(request: Request) -> HTMLResponse:
        items, findings = scan(store, date.today(), llm)
        return TEMPLATES.TemplateResponse(
            request, "index.html",
            {"items": items, "findings": findings, "today": date.today().isoformat(),
             "appliances": store.list_appliances(),
             "due_count": len([i for i in items if i.days_left <= 7])},
        )

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        return render(request)

    @app.post("/replace")
    def replace(consumable_id: int = Form(...), day: str = Form("")) -> RedirectResponse:
        d = date.fromisoformat(day) if day else date.today()
        rows = {c.id: c for c in store.list_consumables()}
        c = rows.get(consumable_id)
        if c is None:
            return RedirectResponse(url="/?error=1", status_code=303)
        with store.session() as s:
            from ..adapters.store.sqlite import ConsumableRow

            row = s.get(ConsumableRow, consumable_id)
            if row is not None:
                row.last_replaced = d
                row.stock = max(0, row.stock - 1)
                s.commit()
        return RedirectResponse(url="/", status_code=303)

    @app.get("/digest.txt", response_class=PlainTextResponse)
    def digest_text() -> PlainTextResponse:
        return PlainTextResponse(digest(store, date.today()), media_type="text/plain; charset=utf-8")

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "appliances": len(store.list_appliances())}

    return app


def app_factory(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        from ..config import settings as default_settings

        settings = default_settings
    return create_app(settings)

