from copy import deepcopy

from app.data_models.scenario import (
    ScenarioInput,
    StrategyCodeEnum,
    StrategyParamsInput,
)
from app.services.strategy_engine.engine import StrategyEngine
from backend.tests.conftest import YEAR_2025


def test_bracket_filling_produces_positive_withdrawal_and_tax():
    scenario = ScenarioInput(**deepcopy(ScenarioInput.Config.json_schema_extra["example"]))
    engine = StrategyEngine(tax_year_data_loader=lambda y, p="ON": YEAR_2025)
    params = scenario.strategy_params_override or StrategyParamsInput()
    yearly, summary = engine.run(StrategyCodeEnum.BF, scenario, params)

    assert yearly[0].income_sources.rrif_withdrawal > 0
    assert summary.lifetime_tax_paid_nominal > 0
