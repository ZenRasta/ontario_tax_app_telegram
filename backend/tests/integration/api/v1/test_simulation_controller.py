import pytest
from httpx import AsyncClient

from app.main import app

VALID_SCENARIO = {
    "age": 65,
    "rrsp_balance": 500000,
    "defined_benefit_pension": 20000,
    "cpp_at_65": 12000,
    "oas_at_65": 8000,
    "tfsa_balance": 100000,
    "desired_spending": 60000,
    "expect_return_pct": 5,
    "stddev_return_pct": 8,
    "life_expectancy_years": 25,
    "province": "ON",
    "goal": "maximize_spending",
}


@pytest.mark.asyncio
async def test_simulate_missing_scenario():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/simulate", json={"strategy_code": "GM"})
    assert response.status_code == 422
    assert response.json()["detail"] == "scenario is required"


@pytest.mark.asyncio
async def test_compare_missing_scenario():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/compare", json={"strategies": ["GM"]})
    assert response.status_code == 422
    assert response.json()["detail"] == "scenario is required"


@pytest.mark.asyncio
async def test_compare_empty_strategies():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/compare", json={"scenario": VALID_SCENARIO, "strategies": []}
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "strategies list cannot be empty"


@pytest.mark.asyncio
async def test_simulate_mc_missing_scenario():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/simulate_mc", json={"strategy_code": "GM"}
        )
    assert response.status_code == 422
    assert response.json()["detail"] == "scenario is required"
=======
from app.data_models.scenario import ScenarioInput, StrategyCodeEnum

EXAMPLE_SCENARIO = ScenarioInput.Config.json_schema_extra["example"]

@pytest.mark.parametrize("code", [c for c in StrategyCodeEnum])
async def test_simulate_success(client, code):
    payload = {"scenario": EXAMPLE_SCENARIO, "strategy_code": code.value}
    resp = await client.post("/api/v1/simulate", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["strategy_code"] == code.value
    assert body["yearly_results"]

@pytest.mark.parametrize("code", [c for c in StrategyCodeEnum])
async def test_simulate_missing_param_422(client, code):
    bad = EXAMPLE_SCENARIO.copy()
    bad.pop("age")
    payload = {"scenario": bad, "strategy_code": code.value}
    resp = await client.post("/api/v1/simulate", json=payload)
    assert resp.status_code == 422

