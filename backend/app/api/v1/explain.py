from fastapi import APIRouter
from pydantic import BaseModel

from app.data_models.scenario import ScenarioInput, StrategyCodeEnum, GoalEnum
from app.data_models.results import SummaryMetrics
from app.services.llm_service import explain_strategy_with_context

router = APIRouter(prefix="/api/v1", tags=["explain"])


class ExplainRequest(BaseModel):
    scenario: ScenarioInput
    strategy_code: StrategyCodeEnum
    summary: SummaryMetrics
    goal: GoalEnum


class ExplainResponse(BaseModel):
    explanation: str


@router.post("/explain", response_model=ExplainResponse)
async def explain(req: ExplainRequest) -> ExplainResponse:
    text = await explain_strategy_with_context(
        req.scenario, req.strategy_code, req.summary, req.goal
    )
    return ExplainResponse(explanation=text)
