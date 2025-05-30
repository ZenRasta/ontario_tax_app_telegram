from copy import deepcopy

import pytest

from app.data_models.scenario import (
    ScenarioInput,
    StrategyCodeEnum,
    StrategyParamsInput,
)
from app.services.strategy_engine.engine import StrategyEngine
from backend.tests.conftest import YEAR_2025


def test_seq_first_year_tax_within_expected_range():
    """Run the Spousal Equalization strategy and sanity check first year tax."""
    scenario = ScenarioInput(**deepcopy(ScenarioInput.Config.json_schema_extra["example"]))
    engine = StrategyEngine(tax_year_data_loader=lambda y, p="ON": YEAR_2025)
    params = scenario.strategy_params_override or StrategyParamsInput()
    yearly, _ = engine.run(scenario, StrategyCodeEnum.SEQ, params)

    assert 12_000 <= yearly[0].total_tax_paid <= 15_000


def test_spouse_cpp_amount_validation():
    """ScenarioInput should reject spouse CPP amounts above the allowed max."""
    bad_data = deepcopy(ScenarioInput.Config.json_schema_extra["example"])
    bad_data["spouse"]["cpp_at_65"] = 999_999
    with pytest.raises(ValueError):
        ScenarioInput(**bad_data)

