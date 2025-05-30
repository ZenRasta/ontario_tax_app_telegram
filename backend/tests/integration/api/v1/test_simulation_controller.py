import pytest
import app.main as main_app
from app.data_models.scenario import ScenarioInput, StrategyCodeEnum

EXAMPLE_SCENARIO = ScenarioInput.Config.json_schema_extra["example"]

@pytest.mark.asyncio
async def test_simulate_missing_scenario(client):
    resp = await client.post("/api/v1/simulate", json={"strategy_code": "GM"})
    assert resp.status_code == 422
    assert resp.json()["detail"] == "scenario is required"


@pytest.mark.asyncio
async def test_compare_missing_scenario(client):
    resp = await client.post("/api/v1/compare", json={"strategies": ["GM"]})
    assert resp.status_code == 422
    assert resp.json()["detail"] == "scenario is required"


@pytest.mark.asyncio
async def test_compare_empty_strategies(client):
    resp = await client.post(
        "/api/v1/compare",
        json={"scenario": EXAMPLE_SCENARIO, "strategies": []},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "strategies list cannot be empty"


@pytest.mark.asyncio
async def test_simulate_mc_missing_scenario(client):
    resp = await client.post(
        "/api/v1/simulate_mc", json={"strategy_code": "GM"}
    )
    assert resp.status_code == 422
    assert resp.json()["detail"] == "scenario is required"


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


@pytest.mark.asyncio
async def test_simulate_engine_error_returns_defaults(client, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(main_app.engine, "run", boom)

    payload = {"scenario": EXAMPLE_SCENARIO, "strategy_code": "GM"}
    resp = await client.post("/api/v1/simulate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["yearly_results"] == []
    assert data["error_detail"] == "boom"
    assert data["summary"]["lifetime_tax_paid_nominal"] == 0.0
