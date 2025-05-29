import importlib

import pytest

from app.data_models.scenario import ScenarioInput, SimulateRequest, StrategyCodeEnum
from app.utils import year_data_loader

EXAMPLE = ScenarioInput.Config.json_schema_extra["example"].copy()
EXAMPLE.pop("params", None)


def test_bf_defaults_to_oas_threshold(monkeypatch):
    data = {"oas_clawback_threshold": 88000}
    monkeypatch.setattr(year_data_loader, "load_tax_year_data", lambda y, p="ON": data)
    scenario = ScenarioInput(**EXAMPLE)
    SimulateRequest(scenario=scenario, strategy_code=StrategyCodeEnum.BF)
    assert scenario.strategy_params_override.bracket_fill_ceiling == data["oas_clawback_threshold"]


def test_bf_missing_oas_threshold_raises(monkeypatch):
    monkeypatch.setattr(year_data_loader, "load_tax_year_data", lambda y, p="ON": {})
    scenario = ScenarioInput(**EXAMPLE)
    with pytest.raises(ValueError, match="oas_clawback_threshold"):
        SimulateRequest(scenario=scenario, strategy_code=StrategyCodeEnum.BF)


def test_load_tax_year_data_parses_yaml(monkeypatch):
    import app.utils.year_data_loader as ydl
    ydl = importlib.reload(ydl)
    data = ydl.load_tax_year_data(2025, "ON")
    assert data["federal_personal_amount"] == 15705

