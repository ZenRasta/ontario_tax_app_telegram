from fastapi import APIRouter
from typing import List

from app.data_models.scenario import ScenarioInput
from app.data_models.results import ResultSummary
from app.services.strategy_engine.engine import run_strategy_batch
from app.data_models.scenario import ScenarioInput   # wizard model


router = APIRouter(prefix="/api/v1", tags=["simulate"])


@router.post("/simulate", response_model=List[ResultSummary])
async def simulate(scenario: ScenarioInput) -> List[ResultSummary]:
    """
    Run the scenario against all strategies requested in
    `scenario.strategies` and return an array of ResultSummary.
    """
    return run_strategy_batch(scenario)
