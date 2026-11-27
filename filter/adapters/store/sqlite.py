"""SQLite：appliances / consumables / services / jobs。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Date, Float, Integer, String, Text, inspect, select
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from ...domain.models import Appliance, Consumable, Service
from .base import Base, make_engine, make_session


class ApplianceRow(Base):
    __tablename__ = "appliances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    brand: Mapped[str] = mapped_column(String(40), default="")
    model: Mapped[str] = mapped_column(String(60), default="")
    since: Mapped[date] = mapped_column(Date)
    intensity: Mapped[float] = mapped_column(Float, default=1.0)


class ConsumableRow(Base):
    __tablename__ = "consumables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    appliance_id: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(60))
    cycle_days: Mapped[int] = mapped_column(Integer)
    last_replaced: Mapped[date] = mapped_column(Date)
    stock: Mapped[int] = mapped_column(Integer, default=1)
    price_low: Mapped[float] = mapped_column(Float, default=0.0)
    price_high: Mapped[float] = mapped_column(Float, default=0.0)


class ServiceRow(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    appliance_id: Mapped[int] = mapped_column(Integer, index=True)
    on: Mapped[date] = mapped_column(Date)
    kind: Mapped[str] = mapped_column(String(40), default="")
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    warranty_until: Mapped[date | None] = mapped_column(Date, nullable=True)


class JobRow(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    idem_key: Mapped[str] = mapped_column(String(90), unique=True)
    kind: Mapped[str] = mapped_column(String(24))
    payload: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(12), default="pending")
    due_on: Mapped[date] = mapped_column(Date)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str] = mapped_column(Text, default="")


def _upgrade_schema(engine) -> None:
    root = next(p for p in Path(__file__).resolve().parents if (p / "alembic.ini").exists())
    cfg = Config(str(root / "alembic.ini"))
    cfg.set_main_option("script_location", str(root / "migrations"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{engine.url.database}")
    command.upgrade(cfg, "head")


class SqliteStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.engine = make_engine(self.path)
        self.session: sessionmaker[Session] = make_session(self.engine)
        self.init_schema()

    def init_schema(self) -> None:
        _upgrade_schema(self.engine)

    def schema_ok(self) -> bool:
        return {"appliances", "consumables", "services", "jobs"} <= set(
            inspect(self.engine).get_table_names()
        )

    def summary(self) -> str:
        return f"{len(self.list_appliances())} 台家电、{len(self.list_consumables())} 个耗材"

    def add_appliance(self, name: str, brand: str, model: str, since: date, intensity: float = 1.0) -> int:
        with self.session() as s:
            row = ApplianceRow(name=name, brand=brand, model=model, since=since, intensity=intensity)
            s.add(row)
            s.commit()
            return int(row.id)

    def list_appliances(self) -> list[Appliance]:
        with self.session() as s:
            rows = s.scalars(select(ApplianceRow)).all()
        return [Appliance(r.id, r.name, r.brand, r.model, r.since, r.intensity) for r in rows]

    def add_consumable(
        self, appliance_id: int, name: str, cycle_days: int, last_replaced: date,
        stock: int, price_low: float, price_high: float,
    ) -> int:
        if cycle_days <= 0:
            raise ValueError("周期必须为正")
        with self.session() as s:
            row = ConsumableRow(
                appliance_id=appliance_id, name=name, cycle_days=cycle_days,
                last_replaced=last_replaced, stock=stock,
                price_low=price_low, price_high=price_high,
            )
            s.add(row)
            s.commit()
            return int(row.id)

    def list_consumables(self) -> list[Consumable]:
        with self.session() as s:
            rows = s.scalars(select(ConsumableRow)).all()
        return [
            Consumable(r.id, r.appliance_id, r.name, r.cycle_days, r.last_replaced, r.stock,
                       r.price_low, r.price_high)
            for r in rows
        ]

    def add_service(
        self, appliance_id: int, on: date, kind: str, cost: float, warranty_until: date | None = None
    ) -> int:
        with self.session() as s:
            row = ServiceRow(appliance_id=appliance_id, on=on, kind=kind, cost=cost,
                             warranty_until=warranty_until)
            s.add(row)
            s.commit()
            return int(row.id)

    def list_services(self) -> list[Service]:
        with self.session() as s:
            rows = s.scalars(select(ServiceRow)).all()
        return [Service(r.id, r.appliance_id, r.on, r.kind, r.cost, r.warranty_until) for r in rows]

    def enqueue(self, idem_key: str, kind: str, payload: str, due_on: date) -> bool:
        with self.session() as s:
            if s.scalar(select(JobRow).where(JobRow.idem_key == idem_key)):
                return False
            s.add(JobRow(idem_key=idem_key, kind=kind, payload=payload, due_on=due_on))
            s.commit()
            return True

    def due_jobs(self, today: date) -> list[JobRow]:
        with self.session() as s:
            return list(
                s.scalars(select(JobRow).where(JobRow.status == "pending", JobRow.due_on <= today)).all()
            )

    def finish_job(self, job_id: int, ok: bool, error: str = "") -> None:
        with self.session() as s:
            row = s.get(JobRow, job_id)
            if row is None:
                return
            row.status = "done" if ok else "pending"
            row.attempts += 1
            row.error = error
            s.commit()

