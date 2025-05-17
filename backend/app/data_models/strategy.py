# app/data_models/strategy.py
"""
UI‑oriented metadata for each withdrawal strategy.
Nothing here affects the maths – it’s for front‑end dropdowns,
docs, and the /strategies helper endpoint (if you expose one).
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.data_models.scenario import GoalEnum, StrategyCodeEnum


class StrategyMeta(BaseModel):
    code: StrategyCodeEnum
    label: str                                    # Human‑readable name
    blurb: str                                    # One‑liner / tooltip
    default_complexity: int = Field(..., ge=1, le=5)
    typical_goals: List[GoalEnum] = Field(default_factory=list)
    # icon_id: Optional[str] = None              # Place‑holder for UI icon map


# ──────────────────────────────────────────────────────────────
# The master list – update here when you add new strategies
# ──────────────────────────────────────────────────────────────
ALL_STRATEGIES: List[StrategyMeta] = [
    StrategyMeta(
        code=StrategyCodeEnum.BF,
        label="Bracket‑Filling",
        blurb="Cap taxable income at a chosen ceiling.",
        default_complexity=2,
        typical_goals=[GoalEnum.MINIMIZE_TAX, GoalEnum.SIMPLIFY],
    ),
    StrategyMeta(
        code=StrategyCodeEnum.GM,
        label="Gradual Meltdown",
        blurb="Withdraw just enough each year to meet spending.",
        default_complexity=1,
        typical_goals=[GoalEnum.MAXIMIZE_SPENDING, GoalEnum.SIMPLIFY],
    ),
    StrategyMeta(
        code=StrategyCodeEnum.E65,
        label="Early RRIF @65",
        blurb="Convert RRSP early for pension credits & income splitting.",
        default_complexity=2,
        typical_goals=[GoalEnum.MINIMIZE_TAX],
    ),
    StrategyMeta(
        code=StrategyCodeEnum.CD,
        label="CPP/OAS Delay",
        blurb="Delay government pensions; bridge spending with RRIF.",
        default_complexity=3,
        typical_goals=[GoalEnum.MAXIMIZE_SPENDING],
    ),
    StrategyMeta(
        code=StrategyCodeEnum.SEQ,
        label="Spousal Equalisation",
        blurb="Even out taxable income between spouses.",
        default_complexity=3,
        typical_goals=[GoalEnum.MINIMIZE_TAX],
    ),
    StrategyMeta(
        code=StrategyCodeEnum.IO,
        label="Interest‑Offset Loan",
        blurb="Use deductible interest to offset RRIF tax.",
        default_complexity=5,
        typical_goals=[GoalEnum.MINIMIZE_TAX],
    ),
    StrategyMeta(
        code=StrategyCodeEnum.LS,
        label="Lump‑Sum Withdrawal",
        blurb="One‑time large withdrawal in a specified year.",
        default_complexity=2,
        typical_goals=[GoalEnum.SIMPLIFY],
    ),
    StrategyMeta(
        code=StrategyCodeEnum.EBX,
        label="Empty‑by‑X",
        blurb="Systematically deplete RRIF by a target age.",
        default_complexity=2,
        typical_goals=[GoalEnum.PRESERVE_ESTATE, GoalEnum.MINIMIZE_TAX],
    ),
    StrategyMeta(
        code=StrategyCodeEnum.MIN,
        label="RRIF Minimum Only",
        blurb="Withdraw only the CRA‑mandated minimum each year.",
        default_complexity=1,
        typical_goals=[GoalEnum.SIMPLIFY, GoalEnum.PRESERVE_ESTATE],
    ),
]


# Helper – fetch metadata quickly without a comprehension everywhere
def get_strategy_meta(code: StrategyCodeEnum) -> Optional[StrategyMeta]:
    return next((m for m in ALL_STRATEGIES if m.code == code), None)

