# backend/app/api/v1/simulate.py
from fastapi import APIRouter, HTTPException
from app.data_models.scenario import CompareRequest          # or SimulateRequest
from app.services.strategy_engine.engine import run_strategy_batch

router = APIRouter(prefix="/api/v1", tags=["simulation"])


@router.post("/simulate")
def simulate(req: CompareRequest):
    """
    Run every strategy listed in ``req.strategies`` and return their
    summary metrics for the front-end wizard.
    """
    try:
        summaries = run_strategy_batch(req.scenario, req.strategies)
        # run_strategy_batch returns a list of Pydantic models; convert to dicts
        return {"comparisons": [s.dict() for s in summaries]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

