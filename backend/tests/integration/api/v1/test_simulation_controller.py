import pytest
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
