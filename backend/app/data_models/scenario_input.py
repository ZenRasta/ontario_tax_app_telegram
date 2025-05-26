# backend/app/data_models/scenario_input.py
"""
ScenarioInput — user request payload for the wizard UI.

Key features
------------
• married flag + spouse data
• advanced params for BF, CD, LS, EBX
• Pydantic-2 `model_validator` ensures spouse fields are consistent
"""

from __future__ import annotations
from typing import List, Optional

from pydantic import (
    BaseModel,
    Field,
    conint,
    confloat,
    model_validator,  # ✓ Pydantic 2
)


class ScenarioInput(BaseModel):
    # ───────── core demographics / balances ─────────
    age: conint(ge=55, le=100)
    province: str = "ON"
    rrsp_balance: confloat(ge=0)
    tfsa_balance: confloat(ge=0) = 0
    cpp_at_65: confloat(ge=0)
    oas_at_65: confloat(ge=0)
    db_pension: confloat(ge=0) = 0
    desired_spending: confloat(ge=0)
    horizon_years: conint(ge=1, le=50) = 30
    expected_return_pct: confloat(ge=-5, le=15) = 5.0
    stddev_return_pct: confloat(ge=0, le=25) = 8.0
    goal: str
    strategies: List[str]

    # ───────── spouse block ─────────
    married: bool = False
    spouse_age: Optional[conint(ge=55, le=100)] = None
    spouse_rrsp_balance: Optional[confloat(ge=0)] = None
    spouse_tfsa_balance: Optional[confloat(ge=0)] = None
    spouse_cpp_at_65: Optional[confloat(ge=0)] = None
    spouse_oas_at_65: Optional[confloat(ge=0)] = None
    spouse_other_income: Optional[confloat(ge=0)] = None

    # ───────── strategy-specific params ─────────
    bracket_fill_ceiling: Optional[confloat(ge=0)] = None          # BF
    cpp_start_age: Optional[conint(ge=60, le=70)] = None           # CD
    lump_sum_year_offset: Optional[conint(ge=0, le=40)] = None     # LS
    lump_sum_amount: Optional[confloat(ge=0)] = None               # LS
    target_depletion_age: Optional[conint(ge=75, le=100)] = None   # EBX

    # ───────── meta ─────────
    goal: str                                # “Minimize Tax”, …
    strategies: List[str]                    # e.g. ["BF","GM"]

    # ───────── validation ─────────
    @model_validator(mode="after")
    def _validate_spouse(self):
        spouse_fields = (
            self.spouse_age,
            self.spouse_rrsp_balance,
            self.spouse_tfsa_balance,
            self.spouse_cpp_at_65,
            self.spouse_oas_at_65,
        )
        if self.married and not any(spouse_fields):
            raise ValueError("married=True but no spouse data supplied")

        if not self.married:
            # zero-out spouse attrs so downstream code won’t mis-read
            self.spouse_age = None
            self.spouse_rrsp_balance = None
            self.spouse_tfsa_balance = None
            self.spouse_cpp_at_65 = None
            self.spouse_oas_at_65 = None
            self.spouse_other_income = None

        return self

