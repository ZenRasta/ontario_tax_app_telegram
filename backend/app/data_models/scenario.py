# app/data_models/scenario.py
"""
Pydantic data‑models used throughout the engine layer.

• ScenarioInput           – user facts for a single projection
• StrategyParamsInput     – optional overrides per strategy
• SpouseInput             – extra data for spousal logic
• SimulateRequest / CompareRequest – thin request wrappers for the API
"""

from __future__ import annotations

import datetime as _dt
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4
import warnings

from pydantic import (
    BaseModel,
    Field,
    conint,
    condecimal,
    confloat,
    root_validator,
)

from app.utils.year_data_loader import load_tax_year_data

# --------------------------------------------------------------------------- #
# Enumerations
# --------------------------------------------------------------------------- #


class GoalEnum(str, Enum):
    MINIMIZE_TAX = "minimize_tax"
    MAXIMIZE_SPENDING = "maximize_spending"
    PRESERVE_ESTATE = "preserve_estate"
    SIMPLIFY = "simplify"


class ProvinceEnum(str, Enum):
    ON = "ON"  # Ontario
    # TODO: add QC, BC, AB … once tax tables are in place


class StrategyCodeEnum(str, Enum):
    BF = "BF"    # Bracket‑Filling
    E65 = "E65"  # Early RRIF Conversion @65
    CD = "CD"    # CPP / OAS Delay (RRSP bridge)
    GM = "GM"    # Gradual Meltdown (default)
    SEQ = "SEQ"  # Spousal Equalisation
    IO = "IO"    # Interest‑Offset Loan
    LS = "LS"    # Lump‑Sum Withdrawal
    EBX = "EBX"  # Empty‑by‑X
    MIN = "MIN"  # RRIF Minimums only (baseline)

# --------------------------------------------------------------------------- #
# Strategy‑specific knobs
# --------------------------------------------------------------------------- #


class SpouseInput(BaseModel):
    age: conint(gt=0, lt=120)
    rrsp_balance: confloat(ge=0)
    other_income: confloat(ge=0) = 0.0
    cpp_at_65: confloat(ge=0) = 0.0
    oas_at_65: confloat(ge=0) = 0.0
    tfsa_balance: confloat(ge=0) = 0.0
    defined_benefit_pension: confloat(ge=0) = 0.0

    # ----------------------- validators ------------------------------- #

    @root_validator(skip_on_failure=True)
    def _check_pension_max(cls, v):
        td = load_tax_year_data(_dt.datetime.now().year)
        max_cpp = td.get("cpp_max_benefit_at_65")
        max_oas = td.get("oas_max_benefit_at_65")
        if max_cpp is not None and v.get("cpp_at_65", 0) > max_cpp:
            raise ValueError(
                f"cpp_at_65 exceeds maximum allowed benefit of {max_cpp}"
            )
        if max_oas is not None and v.get("oas_at_65", 0) > max_oas:
            raise ValueError(
                f"oas_at_65 exceeds maximum allowed benefit of {max_oas}"
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "age": 63,
                "rrsp_balance": 250_000,
                "other_income": 10_000,
                "cpp_at_65": 9_000,
                "oas_at_65": 7_000,
                "tfsa_balance": 50_000,
                "defined_benefit_pension": 0,
            }
        }


class StrategyParamsInput(BaseModel):
    # --- Bracket‑Filling
    bracket_fill_ceiling: Optional[condecimal(ge=30000, le=250000)] = Field(
        None, description="Taxable‑income ceiling for BF strategy."
    )

    # --- Early RRIF Conversion
    rrif_conversion_age: Optional[conint(ge=55, le=71)] = Field(
        65, description="Age to convert RRSP→RRIF (E65 strategy)."
    )

    # --- CPP/OAS Delay
    cpp_start_age: Optional[conint(ge=60, le=70)] = Field(
        65, description="Age CPP starts (CD strategy)."
    )
    oas_start_age: Optional[conint(ge=65, le=70)] = Field(
        65, description="Age OAS starts (CD strategy)."
    )

    # --- Empty‑by‑X
    target_depletion_age: Optional[conint(ge=70, le=120)] = Field(
        None,
        description="Age by which RRIF should be ~depleted (EBX strategy).",
    )

    # --- Lump‑Sum
    lump_sum_year_offset: Optional[conint(ge=0)] = Field(
        None,
        description="Year offset (0 = first projection year) for LS strategy.",
    )
    lump_sum_amount: Optional[condecimal(gt=0)] = Field(
        None, description="One‑time withdrawal amount for LS strategy."
    )

    # --- Interest‑Offset
    loan_interest_rate_pct: Optional[confloat(gt=0, lt=100)] = Field(
        5.0, description="Annual deductible interest rate (%)."
    )
    loan_amount_as_pct_of_rrif: Optional[confloat(gt=0, le=100)] = Field(
        20.0, description="Notional loan principal as % of RRIF balance."
    )

    # --- Spousal override ---
    spouse: Optional["SpouseInput"] = Field(
        None,
        description="Override spouse info for strategy calculations.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "bracket_fill_ceiling": 92_000,
                "cpp_start_age": 70,
                "oas_start_age": 70,
                "target_depletion_age": 85,
                "lump_sum_year_offset": 0,
                "lump_sum_amount": 50_000,
                "spouse": SpouseInput.Config.json_schema_extra["example"],
            }
        }

# --------------------------------------------------------------------------- #
# Core scenario input
# --------------------------------------------------------------------------- #


class ScenarioInput(BaseModel):
    age: conint(ge=50, le=100)
    rrsp_balance: confloat(ge=100)
    defined_benefit_pension: confloat(ge=0) = 0.0
    cpp_at_65: confloat(ge=0, le=18000)
    oas_at_65: confloat(ge=0)
    tfsa_balance: confloat(ge=0, le=200000) = 0.0
    desired_spending: confloat(ge=20000, le=300000)
    expect_return_pct: confloat(ge=0.5, le=12)
    stddev_return_pct: confloat(ge=0.5, le=25)
    life_expectancy_years: conint(ge=5, le=40)
    province: ProvinceEnum = ProvinceEnum.ON
    goal: GoalEnum
    spouse: Optional[SpouseInput] = None
    # user‑supplied overrides – alias accepts "params" in JSON
    strategy_params_override: Optional[StrategyParamsInput] = Field(
        None,
        alias="params",
        description="Per‑strategy override knobs.",
    )

    # ----------------------- validators ------------------------------- #

    @root_validator(skip_on_failure=True)
    def _check_pension_max(cls, v):
        td = load_tax_year_data(_dt.datetime.now().year, v.get("province", "ON"))
        max_cpp = td.get("cpp_max_benefit_at_65")
        max_oas = td.get("oas_max_benefit_at_65")
        if max_cpp is not None and v.get("cpp_at_65", 0) > max_cpp:
            raise ValueError(
                f"cpp_at_65 exceeds maximum allowed benefit of {max_cpp}"
            )
        if max_oas is not None and v.get("oas_at_65", 0) > max_oas:
            raise ValueError(
                f"oas_at_65 exceeds maximum allowed benefit of {max_oas}"
            )
        return v

@root_validator(skip_on_failure=True)
def _check_horizon_and_lump(cls, v):
    if v["age"] + v["life_expectancy_years"] > 120:
        raise ValueError("Projection exceeds age 120.")

    sp = v.get("strategy_params_override")
    if sp and sp.lump_sum_year_offset is not None:
        if sp.lump_sum_year_offset > v["life_expectancy_years"]:
            raise ValueError("lump_sum_year_offset beyond projection horizon.")
    if sp and sp.target_depletion_age is not None:
        if sp.target_depletion_age <= v["age"]:
            raise ValueError("target_depletion_age must be after current age")
    if sp and sp.cpp_start_age is not None:
        if sp.cpp_start_age < v["age"]:
            raise ValueError("cpp_start_age cannot be before current age")
        if sp.cpp_start_age > 70:
            raise ValueError("cpp_start_age cannot exceed 70")
    if v.get("spouse") and abs(v["spouse"].age - v["age"]) > 20:
        warnings.warn(
            "Large age difference detected - review strategy suitability",
            RuntimeWarning,
        )
    if v["desired_spending"] > (v["rrsp_balance"] + v["tfsa_balance"]) / 10:
        warnings.warn(
            "High spending relative to savings - review sustainability",
            RuntimeWarning,
        )
    return v

    # ----------------------- config ----------------------------------- #

    class Config:
        use_enum_values = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "age": 65,
                "rrsp_balance": 500_000,
                "defined_benefit_pension": 20_000,
                "cpp_at_65": 12_000,
                "oas_at_65": 8_000,
                "tfsa_balance": 100_000,
                "desired_spending": 60_000,
                "expect_return_pct": 5,
                "stddev_return_pct": 8,
                "life_expectancy_years": 25,
                "province": "ON",
                "goal": "maximize_spending",
                "spouse": {
                    "age": 63,
                    "rrsp_balance": 250_000,
                    "other_income": 10_000,
                    "cpp_at_65": 9_000,
                    "oas_at_65": 7_000,
                    "tfsa_balance": 50_000,
                    "defined_benefit_pension": 0,
                },
                "params": {
                    "bracket_fill_ceiling": 92_000,
                    "cpp_start_age": 70,
                    "oas_start_age": 70,
                },
            }
        }

# --------------------------------------------------------------------------- #
# API request wrappers
# --------------------------------------------------------------------------- #


class SimulateRequest(BaseModel):
    scenario: ScenarioInput
    strategy_code: StrategyCodeEnum
    request_id: UUID = Field(default_factory=uuid4)

    # ------------------------------------------------------------------
    @root_validator(skip_on_failure=True)
    def _apply_strategy_defaults(cls, v):
        sc: ScenarioInput = v["scenario"]
        code: StrategyCodeEnum = v["strategy_code"]
        params = sc.strategy_params_override or StrategyParamsInput()
        sc.strategy_params_override = params

        td = load_tax_year_data(_dt.datetime.now().year, sc.province)

        if code == StrategyCodeEnum.BF:
            if params.bracket_fill_ceiling is None:
                if "oas_clawback_threshold" in td:
                    params.bracket_fill_ceiling = td["oas_clawback_threshold"]
                else:
                    raise ValueError(
                        "Tax data missing 'oas_clawback_threshold'; cannot "
                        "default bracket_fill_ceiling"
                    )

        if code == StrategyCodeEnum.LS:
            if params.lump_sum_amount is None:
                raise ValueError("lump_sum_amount required for LS strategy")

        if code == StrategyCodeEnum.CD:
            if params.cpp_start_age is None:
                params.cpp_start_age = 70
            if params.oas_start_age is None:
                params.oas_start_age = 70

        if code == StrategyCodeEnum.SEQ:
            if sc.spouse is None:
                raise ValueError("Spousal strategy requires spouse data")

        v["scenario"] = sc
        return v


class CompareRequest(BaseModel):
    scenario: ScenarioInput
    strategies: List[StrategyCodeEnum]  # routing layer may accept ["auto"]
    request_id: UUID = Field(default_factory=uuid4)

    # ------------------------------------------------------------------
    @root_validator(skip_on_failure=True)
    def _apply_defaults_all(cls, v):
        for code in v["strategies"]:
            SimulateRequest(scenario=v["scenario"], strategy_code=code)
        return v

