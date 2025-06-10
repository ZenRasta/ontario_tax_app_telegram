import pytest

from app.data_models.scenario import ScenarioInput, StrategyCodeEnum, GoalEnum
from app.data_models.results import SummaryMetrics
from app.core.config import settings

EXAMPLE_SCENARIO = ScenarioInput.Config.json_schema_extra["example"]
EXAMPLE_SUMMARY = SummaryMetrics.Config.json_schema_extra["example"]


@pytest.mark.asyncio
async def test_explain_endpoint(client, monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "fake-key")

    async def fake_post(self, url, json):
        class _Resp:
            status_code = 200

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "candidates": [
                        {"content": {"parts": [{"text": "sample explanation"}]}}
                    ]
                }

        return _Resp()

    monkeypatch.setattr("httpx.AsyncClient.post", fake_post)

    payload = {
        "scenario": EXAMPLE_SCENARIO,
        "strategy_code": StrategyCodeEnum.GM.value,
        "summary": EXAMPLE_SUMMARY,
        "goal": GoalEnum.MAXIMIZE_SPENDING.value,
    }
    resp = await client.post("/api/v1/explain", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"explanation": "sample explanation"}
