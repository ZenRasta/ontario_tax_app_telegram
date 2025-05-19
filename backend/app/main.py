# app/main.py
"""
FastAPI entry‑point.

Run dev server:
    poetry run uvicorn app.main:app --reload
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter

from app.core.config import settings
from app.data_models.results import (
    CompareResponse as CompareApiResponse,
)
from app.data_models.results import (
    ComparisonResponseItem,
    MonteCarloPath,
    SummaryMetrics,
)
from app.data_models.results import (
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
# top‑level FastAPI app
# ------------------------------------------------------------------ #
app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Simulate tax‑efficient RRIF/RRSP withdrawal strategies",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False if "*" in settings.ALLOWED_CORS_ORIGINS else True,
)

# ------------------------------------------------------------------ #
# database init (runs once at start‑up)
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

mc_service = MonteCarloService(                       # NEW
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
    """Very simple goal ➜ strategies mapping."""
    if goal == GoalEnum.MINIMIZE_TAX:
        return [StrategyCodeEnum.BF, StrategyCodeEnum.SEQ, StrategyCodeEnum.GM]
    elif goal == GoalEnum.MAXIMIZE_SPENDING:
        return [StrategyCodeEnum.CD, StrategyCodeEnum.GM, StrategyCodeEnum.LS]
    elif goal == GoalEnum.PRESERVE_ESTATE:
        return [StrategyCodeEnum.EBX, StrategyCodeEnum.LS, StrategyCodeEnum.SEQ]
    elif goal == GoalEnum.SIMPLIFY:
        return [StrategyCodeEnum.MIN, StrategyCodeEnum.GM]
    return [StrategyCodeEnum.GM]

# ------------------------------------------------------------------ #
# API router (mounted under /api/v1 by default)
# ------------------------------------------------------------------ #
router = APIRouter()


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

# ---------- deterministic simulation --------------------------------
@router.post("/simulate", response_model=SimulationApiResponse, tags=["Simulation"])
async def simulate(req: SimulateRequest):
    logger.info("simulate request_id=%s strategy=%s", req.request_id, req.strategy_code)

    if req.scenario is None:
        raise HTTPException(status_code=422, detail="scenario is required")
    if req.strategy_code is None:
        raise HTTPException(status_code=422, detail="strategy_code is required")

    params = req.scenario.strategy_params_override or StrategyParamsInput()
    _require_params(req.strategy_code, params, req.scenario)
    yearly, summary = engine.run(req.scenario, req.strategy_code, params)

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
        raise HTTPException(status_code=422, detail="scenario is required")
    if req.strategies is None:
        raise HTTPException(status_code=422, detail="strategies list is required")

    # decide which strategies to run
    if req.strategies == ["auto"]:
        codes = _auto_strategies(req.scenario.goal)
    elif not req.strategies:
        raise HTTPException(400, "strategies list cannot be empty")
    else:
        codes = req.strategies

    params = req.scenario.strategy_params_override or StrategyParamsInput()
    items: List[ComparisonResponseItem] = []

    for code in codes:
        try:
            _require_params(code, params, req.scenario)
            yearly, summary = engine.run(req.scenario, code, params)
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
            items.append(
                ComparisonResponseItem(
                    strategy_code=code,
                    strategy_name=_strategy_display(code),
                    yearly_results=[],
                    summary=None,
                    error_detail=str(exc),
                )
            )

    return CompareApiResponse(request_id=req.request_id, comparisons=items)

# ---------- Monte‑Carlo simulation  ----------------------------------
@router.post(
    "/simulate_mc",
    response_model=dict,
    tags=["Monte‑Carlo"],
    summary="Run Monte‑Carlo simulation for a single strategy",
)
async def simulate_mc(req: SimulateRequest):
    """
    Returns
    --------
    {
        "request_id": …,
        "paths": [ MonteCarloPath, … ],
        "mc_summary": SummaryMetrics   # risk‑focused fields populated
    }
    """
    logger.info("simulate_mc request_id=%s strategy=%s", req.request_id, req.strategy_code)

    if req.scenario is None:
        raise HTTPException(status_code=422, detail="scenario is required")
    if req.strategy_code is None:
        raise HTTPException(status_code=422, detail="strategy_code is required")

    params = req.scenario.strategy_params_override or StrategyParamsInput()
    _require_params(req.strategy_code, params, req.scenario)

    paths: List[MonteCarloPath]
    mc_summary: SummaryMetrics
    paths, mc_summary = mc_service.run(
        scenario=req.scenario,
        strategy_code=req.strategy_code,
        params=params,
    )

    return {
        "request_id": req.request_id,
        "paths": paths,
        "mc_summary": mc_summary,
    }

# ---------- health ---------------------------------------------------
@router.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}

# ------------------------------------------------------------------ #
# mount router on app
# ------------------------------------------------------------------ #
app.include_router(router, prefix=settings.API_PREFIX)

