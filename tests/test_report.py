"""新功能：本月该买清单，一条命令出可复制文本。"""

from __future__ import annotations

from typer.testing import CliRunner

from filter.domain.catalog import models
from filter.iface.cli import app


def test_catalog_has_thirty_models() -> None:
    assert len(models()) == 30


def test_report_cli_writes_markdown(tmp_path) -> None:
    runner = CliRunner()
    db = str(tmp_path / "filter.db")
    assert runner.invoke(app, ["seed", "--db", db]).exit_code == 0
    out = tmp_path / "本月该买.md"
    result = runner.invoke(
        app, ["report", "--db", db, "--month", "2026-12", "--no-llm", "--out", str(out)]
    )
    assert result.exit_code == 0
    body = out.read_text(encoding="utf-8")
    assert "# 本月该买清单" in body
    assert "一键复制到微信" in body
    assert "PP 棉滤芯" in body
    assert "本次未调用模型" in body


def test_report_month_validation(tmp_path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["report", "--db", str(tmp_path / "x.db"), "--month", "2026-13"])
    assert result.exit_code == 2
