from fastapi import APIRouter
from pydantic import BaseModel

from ...data_models.scenario import ScenarioInput, StrategyCodeEnum, GoalEnum
from ...data_models.results import SummaryMetrics
from ...services.llm_service import explain_strategy_with_context

router = APIRouter(tags=["explain"])


class ExplainRequest(BaseModel):
    scenario: ScenarioInput
    strategy_code: StrategyCodeEnum
    summary: SummaryMetrics
    goal: GoalEnum


class ExplainResponse(BaseModel):
    summary: str
    key_outcomes: list[str]
    recommendations: str


@router.post("/explain", response_model=ExplainResponse)
async def explain(req: ExplainRequest) -> ExplainResponse:
    data = await explain_strategy_with_context(
        req.scenario, req.strategy_code, req.summary, req.goal
    )
    return ExplainResponse(**data)
