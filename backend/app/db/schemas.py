# app/db/schemas.py
"""
SQLAlchemy ORM models.

* Scenario – the raw user scenario (deduped by hash so identical inputs
  aren’t stored twice).
* SimulationRun – one deterministic strategy run (summary JSON only).
* MonteCarloRun – one MC run (links back to its deterministic run).
* SessionCache – generic key‑value with expiry (useful for short‑lived UI
  state, presigned URLs, etc.).
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data_models.scenario import StrategyCodeEnum
from app.db.session_manager import DbBase


# --------------------------------------------------------------------------- #
# helper – stable hash of a ScenarioInput dict so identical requests
#           share the same Scenario row (saves space)
# --------------------------------------------------------------------------- #
def _scenario_hash(scenario_dict: Dict[str, Any]) -> str:
    # NOTE – sort_keys=True so logically‑identical JSON hashes the same
    blob = json.dumps(scenario_dict, sort_keys=True).encode("utf‑8")
    return hashlib.sha256(blob).hexdigest()


# --------------------------------------------------------------------------- #
# ORM models
# --------------------------------------------------------------------------- #
class Scenario(DbBase):
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    scenario_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # relationships
    runs: Mapped[list["SimulationRun"]] = relationship(
        back_populates="scenario", cascade="all, delete-orphan"
    )

    # ------------------------ factory -------------------------------- #
    @classmethod
    def get_or_create(cls, session, scenario_dict: Dict[str, Any]) -> "Scenario":
        """
        Idempotent helper – returns existing Scenario row if identical input
        was already stored; otherwise inserts a new one.
        """
        digest = _scenario_hash(scenario_dict)
        obj: Scenario | None = (
            session.query(cls).filter(cls.sha256 == digest).one_or_none()
        )
        if obj:
            return obj
        obj = cls(sha256=digest, scenario_json=scenario_dict)
        session.add(obj)
        return obj


class SimulationRun(DbBase):
    """
    One deterministic run for a given strategy & scenario.
    The heavy year‑by‑year list is kept in `full_results_json`; keep only the
    high‑level SummaryMetrics you need to query in `summary_json`.
    """

    __tablename__ = "simulation_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenarios.id", ondelete="CASCADE"), index=True, nullable=False
    )
    strategy_code: Mapped[StrategyCodeEnum] = mapped_column(
        Enum(StrategyCodeEnum), nullable=False
    )

    summary_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    full_results_json: Mapped[Dict[str, Any] | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, index=True
    )

    # relationships
    scenario: Mapped["Scenario"] = relationship(back_populates="runs")
    mc_runs: Mapped[list["MonteCarloRun"]] = relationship(
        back_populates="parent_run", cascade="all, delete-orphan"
    )


class MonteCarloRun(DbBase):
    """
    Stores only the *summary* and (optionally) a few selected paths.
    Very large path dumps should live in object storage (S3, GCS, …) and
    be referenced here by URL.
    """

    __tablename__ = "mc_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    parent_run_id: Mapped[str] = mapped_column(
        ForeignKey("simulation_runs.id", ondelete="CASCADE"), index=True
    )
    n_trials: Mapped[int] = mapped_column(Integer, nullable=False)
    summary_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    sample_paths_json: Mapped[Dict[str, Any] | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, index=True
    )

    # relationships
    parent_run: Mapped["SimulationRun"] = relationship(back_populates="mc_runs")


class SessionCache(DbBase):
    """
    Generic TTL key‑value cache (e.g. presigned download links, temporary
    auth tokens, etc.).  You decide how you want to use it.
    """

    __tablename__ = "session_cache"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    json_value: Mapped[Dict[str, Any]] = mapped_column(JSON)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    # ------------------------ helpers -------------------------------- #
    @classmethod
    def put(
        cls, session, key: str, payload: Dict[str, Any], ttl_hours: int = 24
    ) -> None:
        expiry = datetime.utcnow() + timedelta(hours=ttl_hours)
        row = cls(key=key, json_value=payload, expires_at=expiry)
        session.merge(row)  # upsert

    @classmethod
    def get(cls, session, key: str) -> Dict[str, Any] | None:
        row: SessionCache | None = session.get(cls, key)
        if not row or row.expires_at < datetime.utcnow():
            return None
        return row.json_value

