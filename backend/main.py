# app/main.py
"""
FastAPI entry-point.

Dev server:
    poetry run uvicorn app.main:app --reload
"""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from pydantic import BaseModel

from app.core.config import settings
from app.data_models.results import (
    CompareResponse as CompareApiResponse,
    ComparisonResponseItem,
    MonteCarloPath,
    SummaryMetrics,
    SimulationResponse as SimulationApiResponse,
)
from app.data_models.scenario import (
    CompareRequest,
    GoalEnum,
    ScenarioInput,
    SimulateRequest,
    StrategyCodeEnum,
    StrategyParamsInput,
)
from app.data_models.strategy import ALL_STRATEGIES, StrategyMeta
from app.db.session_manager import create_db_and_tables
from app.services.monte_carlo_service import MonteCarloService
from app.services.strategy_engine.engine import _STRATEGY_REGISTRY, StrategyEngine
from app.utils.year_data_loader import load_tax_year_data

# ------------------------------------------------------------------ #
# logging
# ------------------------------------------------------------------ #
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger("rrif_api")

# ------------------------------------------------------------------ #
# top-level FastAPI app
# ------------------------------------------------------------------ #
app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Simulate tax-efficient RRIF/RRSP withdrawal strategies",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False if "*" in settings.ALLOWED_CORS_ORIGINS else True,
)

# ------------------------------------------------------------------ #
# include v1 simulation router (defined in app/api/v1/simulate.py)
# ------------------------------------------------------------------ #
from app.api.v1.simulate import router as simulate_router  # noqa: E402  (import after FastAPI instantiated)

app.include_router(simulate_router)

# ------------------------------------------------------------------ #
# database init (runs once at start-up)
# ------------------------------------------------------------------ #
@app.on_event("startup")
async def _init_db() -> None:
    logger.info("Creating DB tables if missing …")
    await create_db_and_tables()
    logger.info("DB ready.")

# ------------------------------------------------------------------ #
# singletons
# ------------------------------------------------------------------ #
engine = StrategyEngine(tax_year_data_loader=load_tax_year_data)

mc_service = MonteCarloService(
    engine_factory=lambda: StrategyEngine(tax_year_data_loader=load_tax_year_data),
    n_trials=1_000,
)

# ------------------------------------------------------------------ #
# helpers
# ------------------------------------------------------------------ #
def _strategy_display(code: StrategyCodeEnum) -> str:
    cls = _STRATEGY_REGISTRY.get(code)
    return getattr(cls, "display_name", code.value)


def _auto_strategies(goal: GoalEnum) -> List[StrategyCodeEnum]:
    if goal == GoalEnum.MINIMIZE_TAX:
        return [StrategyCodeEnum.BF, StrategyCodeEnum.SEQ, StrategyCodeEnum.GM]
    if goal == GoalEnum.MAXIMIZE_SPENDING:
        return [StrategyCodeEnum.CD, StrategyCodeEnum.GM, StrategyCodeEnum.LS]
    if goal == GoalEnum.PRESERVE_ESTATE:
        return [StrategyCodeEnum.EBX, StrategyCodeEnum.LS, StrategyCodeEnum.SEQ]
    if goal == GoalEnum.SIMPLIFY:
        return [StrategyCodeEnum.MIN, StrategyCodeEnum.GM]
    return [StrategyCodeEnum.GM]


def _create_default_summary_metrics(strategy_code: StrategyCodeEnum) -> SummaryMetrics:
    """Create a default SummaryMetrics object when calculation fails"""
    return SummaryMetrics(
        strategy_code=strategy_code,
        strategy_name=_strategy_display(strategy_code),
        # Original fields (if they exist)
        lifetime_tax_paid=0.0,
        max_sustainable_spending=0.0,
        estate_value=0.0,
        total_withdrawals=0.0,
        average_tax_rate=0.0,
        # Required fields from the error message
        lifetime_tax_paid_nominal=0.0,
        lifetime_tax_paid_pv=0.0,
        average_effective_tax_rate=0.0,
        years_in_oas_clawback=0,
        total_oas_clawback_paid_nominal=0.0,
        average_annual_real_spending=0.0,
        final_total_portfolio_value_nominal=0.0,
        final_total_portfolio_value_pv=0.0,
        net_value_to_heirs_after_final_taxes_pv=0.0,
        strategy_complexity_score=0,
        # Add any other fields that might be required
    )

# ------------------------------------------------------------------ #
# legacy router (deterministic + MC endpoints) – mounted at /api
# ------------------------------------------------------------------ #
router = APIRouter()


class StrategiesResponse(BaseModel):
    strategies: List[StrategyMeta]
    recommended: List[StrategyCodeEnum] = []


def _require_params(code: StrategyCodeEnum, params: StrategyParamsInput, scenario: ScenarioInput) -> None:
    if code == StrategyCodeEnum.BF and params.bracket_fill_ceiling is None:
        raise HTTPException(422, "bracket_fill_ceiling required for BF strategy")
    if code == StrategyCodeEnum.LS and (
        params.lump_sum_amount is None or params.lump_sum_year_offset is None
    ):
        raise HTTPException(422, "lump_sum_amount and lump_sum_year_offset required for LS strategy")
    if code == StrategyCodeEnum.EBX and params.target_depletion_age is None:
        raise HTTPException(422, "target_depletion_age required for EBX strategy")
    if code == StrategyCodeEnum.CD and (
        params.cpp_start_age is None or params.oas_start_age is None
    ):
        raise HTTPException(422, "cpp_start_age and oas_start_age required for CD strategy")
    if code == StrategyCodeEnum.IO and (
        params.loan_interest_rate_pct is None or params.loan_amount_as_pct_of_rrif is None
    ):
        raise HTTPException(422, "loan_interest_rate_pct and loan_amount_as_pct_of_rrif required for IO strategy")
    if code == StrategyCodeEnum.SEQ and not (scenario.spouse or params.spouse):
        raise HTTPException(422, "spouse info required for SEQ strategy")


@router.get("/strategies", response_model=StrategiesResponse, tags=["Simulation"])
async def list_strategies(goal: Optional[GoalEnum] = None) -> StrategiesResponse:
    recommended = _auto_strategies(goal) if goal else []
    return StrategiesResponse(strategies=ALL_STRATEGIES, recommended=recommended)


# ---------- deterministic simulation --------------------------------
@router.post("/simulate", response_model=SimulationApiResponse, tags=["Simulation"])
async def simulate(req: SimulateRequest):
    logger.info("simulate request_id=%s strategy=%s", req.request_id, req.strategy_code)
    if req.scenario is None:
        raise HTTPException(422, "scenario is required")
    if req.strategy_code is None:
        raise HTTPException(422, "strategy_code is required")

    params = req.scenario.strategy_params_override or StrategyParamsInput()
    _require_params(req.strategy_code, params, req.scenario)
    
    # Apply params to scenario before running
    scenario_with_params = req.scenario.copy(deep=True)
    scenario_with_params.strategy_params_override = params
    
    # FIX: Convert enum to string value for strategy registry lookup
    code_str = req.strategy_code.value if hasattr(req.strategy_code, 'value') else str(req.strategy_code)
    yearly, summary = engine.run(code_str, scenario_with_params)

    return SimulationApiResponse(
        request_id=req.request_id,
        strategy_code=req.strategy_code,
        strategy_name=_strategy_display(req.strategy_code),
        yearly_results=yearly,
        summary=summary,
    )

# ---------- deterministic compare -----------------------------------
@router.post("/compare", response_model=CompareApiResponse, tags=["Simulation"])
async def compare(req: CompareRequest):
    logger.info("compare request_id=%s", req.request_id)
    if req.scenario is None:
        raise HTTPException(422, "scenario is required")
    if req.strategies is None:
        raise HTTPException(422, "strategies list is required")

    # decide which strategies to run
    codes = (
        _auto_strategies(req.scenario.goal)
        if req.strategies == ["auto"]
        else req.strategies or []
    )
    if not codes:
        raise HTTPException(400, "strategies list cannot be empty")

    params = req.scenario.strategy_params_override or StrategyParamsInput()
    items: List[ComparisonResponseItem] = []

    for code in codes:
        try:
            _require_params(code, params, req.scenario)
            
            # Apply params to scenario before running
            scenario_with_params = req.scenario.copy(deep=True)
            scenario_with_params.strategy_params_override = params
            
            # FIX: Convert enum to string value for strategy registry lookup
            code_str = code.value if hasattr(code, 'value') else str(code)
            yearly, summary = engine.run(code_str, scenario_with_params)
            
            items.append(
                ComparisonResponseItem(
                    strategy_code=code,
                    strategy_name=_strategy_display(code),
                    yearly_results=yearly,
                    summary=summary,
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("compare error for %s: %s", code, exc)
            # FIX: Provide valid SummaryMetrics instead of None
            default_summary = _create_default_summary_metrics(code)
            items.append(
                ComparisonResponseItem(
                    strategy_code=code,
                    strategy_name=_strategy_display(code),
                    yearly_results=[],
                    summary=default_summary,  # Use default instead of None
                    error_detail=str(exc),
                )
            )

    return CompareApiResponse(request_id=req.request_id, comparisons=items)

# ---------- Monte-Carlo simulation  ----------------------------------
@router.post("/simulate_mc", tags=["Monte-Carlo"], response_model=dict)
async def simulate_mc(req: SimulateRequest):
    logger.info("simulate_mc request_id=%s strategy=%s", req.request_id, req.strategy_code)
    if req.scenario is None:
        raise HTTPException(422, "scenario is required")
    if req.strategy_code is None:
        raise HTTPException(422, "strategy_code is required")

    params = req.scenario.strategy_params_override or StrategyParamsInput()
    _require_params(req.strategy_code, params, req.scenario)

    # Apply params to scenario before running
    scenario_with_params = req.scenario.copy(deep=True)
    scenario_with_params.strategy_params_override = params

    paths, mc_summary = mc_service.run(
        scenario=scenario_with_params,
        strategy_code=req.strategy_code,
        params=params,
    )

    return {"request_id": req.request_id, "paths": paths, "mc_summary": mc_summary}

# ---------- health ---------------------------------------------------
@router.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}

# ------------------------------------------------------------------ #
# mount legacy router under configurable prefix (default: /api)
# ------------------------------------------------------------------ #
app.include_router(router, prefix=settings.API_PREFIX)
