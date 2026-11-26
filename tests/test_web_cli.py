from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from filter.doctor import run_doctor
from filter.iface.cli import app
from filter.iface.web import create_app


def test_web_index_shows_due(store, settings):
    a = store.add_appliance("净水器", "美的", "M1890", date(2024, 3, 10))
    store.add_consumable(a, "PP 棉", 90, date(2026, 9, 5), 2, 39, 69)
    client = TestClient(create_app(settings, store))
    resp = client.get("/")
    assert resp.status_code == 200
    assert "PP 棉" in resp.text


def test_web_replace_moves_date(store, settings):
    a = store.add_appliance("净水器", "美的", "M1890", date(2024, 3, 10))
    cid = store.add_consumable(a, "PP 棉", 90, date(2026, 9, 5), 2, 39, 69)
    client = TestClient(create_app(settings, store))
    resp = client.post("/replace", data={"consumable_id": str(cid), "day": "2026-11-27"},
                       follow_redirects=False)
    assert resp.status_code == 303
    c = store.list_consumables()[0]
    assert c.last_replaced == date(2026, 11, 27)
    assert c.stock == 1


def test_cli_due_and_bad_date(tmp_path):
    runner = CliRunner()
    db = str(tmp_path / "c.db")
    assert runner.invoke(app, ["due", "--db", db, "--day", "2026-11-27"]).exit_code == 0
    assert runner.invoke(app, ["due", "--db", db, "--day", "2026-13-01"]).exit_code != 0


def test_doctor_green(settings):
    checks, ok = run_doctor(settings)
    assert ok is True
