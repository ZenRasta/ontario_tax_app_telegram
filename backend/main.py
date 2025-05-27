from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS - IMPORTANT!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SpouseInfo(BaseModel):
    age: int
    rrsp_balance: float
    other_income: float = 0

class ScenarioInput(BaseModel):
    age: int
    rrsp_balance: float
    defined_benefit_pension: float = 0
    cpp: float = 0
    oas: float = 0
    tfsa_balance: float = 0
    desired_spending: float
    expect_return_pct: float = 5
    stddev_return_pct: float = 8
    life_expectancy_years: int = 25
    province: str = "ON"
    goal: str = "minimize_tax"
    spouse: Optional[SpouseInfo] = None

class CompareRequest(BaseModel):
    scenario: ScenarioInput
    strategies: List[str] = ["auto"]

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok", "message": "Backend is running"}

# Main compare endpoint that your frontend is calling
@app.post("/api/v1/compare")
async def compare(request: CompareRequest):
    try:
        logger.info(f"Received compare request for age {request.scenario.age}")
        
        # Mock response for now - replace with actual logic later
        return {
            "comparisons": [
                {
                    "strategy": {
                        "code": "GM",
                        "name": "Gradual Meltdown",
                        "description": "Withdraw RRIF minimums plus small extra amounts",
                        "complexity_score": 2
                    },
                    "yearly_results": [
                        {
                            "year": i,
                            "age": request.scenario.age + i,
                            "begin_balance": request.scenario.rrsp_balance * (1.05 ** i),
                            "withdrawal_gross": 50000,
                            "taxable_income": 80000,
                            "tax_paid": 20000,
                            "oas_received": 8000,
                            "spending": 60000,
                            "end_balance": request.scenario.rrsp_balance * (1.05 ** (i+1)) - 50000
                        }
                        for i in range(min(5, request.scenario.life_expectancy_years))
                    ],
                    "summary": {
                        "lifetime_tax_paid": 250000,
                        "pv_tax_paid": 200000,
                        "avg_marginal_tax_rate": 0.25,
                        "years_oas_clawback": 2,
                        "tax_volatility": 0.05,
                        "max_sustainable_spending": 65000,
                        "cashflow_coverage": 1.08,
                        "ruin_probability": 0.05,
                        "sequence_risk_score": 0.15,
                        "estate_value": 300000,
                        "estate_value_pv": 250000,
                        "net_value_to_heirs": 200000,
                        "strategy_complexity": 2
                    }
                },
                {
                    "strategy": {
                        "code": "BF",
                        "name": "Bracket Filling",
                        "description": "Withdraw to fill lower tax brackets",
                        "complexity_score": 3
                    },
                    "yearly_results": [
                        {
                            "year": i,
                            "age": request.scenario.age + i,
                            "begin_balance": request.scenario.rrsp_balance * (1.05 ** i),
                            "withdrawal_gross": 45000,
                            "taxable_income": 75000,
                            "tax_paid": 18000,
                            "oas_received": 8000,
                            "spending": 58000,
                            "end_balance": request.scenario.rrsp_balance * (1.05 ** (i+1)) - 45000
                        }
                        for i in range(min(5, request.scenario.life_expectancy_years))
                    ],
                    "summary": {
                        "lifetime_tax_paid": 230000,
                        "pv_tax_paid": 185000,
                        "avg_marginal_tax_rate": 0.23,
                        "years_oas_clawback": 0,
                        "tax_volatility": 0.03,
                        "max_sustainable_spending": 62000,
                        "cashflow_coverage": 1.03,
                        "ruin_probability": 0.03,
                        "sequence_risk_score": 0.12,
                        "estate_value": 350000,
                        "estate_value_pv": 280000,
                        "net_value_to_heirs": 230000,
                        "strategy_complexity": 3
                    }
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error in compare endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Test endpoint
@app.get("/api/v1/test")
async def test():
    return {"message": "API is working"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)