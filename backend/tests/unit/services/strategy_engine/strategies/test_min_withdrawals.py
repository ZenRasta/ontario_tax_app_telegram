import pytest
from copy import deepcopy

from app.data_models.scenario import ScenarioInput, StrategyParamsInput
from app.services.strategy_engine.engine import StrategyEngine, _STRATEGY_REGISTRY
from app.services.strategy_engine import tax_rules
from backend.tests.conftest import YEAR_2025


@pytest.mark.parametrize("code", sorted(_STRATEGY_REGISTRY.keys()))
def test_first_year_withdrawal_meets_minimum(code):
    scenario = ScenarioInput(**deepcopy(ScenarioInput.Config.json_schema_extra["example"]))
    engine = StrategyEngine(tax_year_data_loader=lambda y, p="ON": YEAR_2025)
    params = scenario.strategy_params_override or StrategyParamsInput()
    yearly, _ = engine.run(code, scenario, params)

    expected_min = tax_rules.get_rrif_min_withdrawal_amount(
        float(scenario.rrsp_balance), scenario.age, YEAR_2025
    )
    assert yearly[0].income_sources.rrif_withdrawal >= expected_min
