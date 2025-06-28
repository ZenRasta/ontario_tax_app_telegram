from fastapi import APIRouter
from typing import List

from ...data_models.scenario import CompareRequest
from ...data_models.results import ResultSummary
from ...services.strategy_engine.engine import run_strategy_batch


router = APIRouter(prefix="/api/v1", tags=["simulate"])


@router.post("/simulate", response_model=List[ResultSummary])
async def simulate(req: CompareRequest) -> List[ResultSummary]:
    """
    Run the scenario against all strategies provided in ``req.strategies`` and
    return an array of ``ResultSummary`` objects.
    """
    return run_strategy_batch(req.scenario, req.strategies)
