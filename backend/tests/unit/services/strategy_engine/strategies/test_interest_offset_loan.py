from copy import deepcopy

from app.data_models.scenario import (
    ScenarioInput,
    StrategyCodeEnum,
    StrategyParamsInput,
)
from app.services.strategy_engine.engine import StrategyEngine
from backend.tests.conftest import YEAR_2025


def test_interest_offset_loan_positive_withdrawal_and_tax():
    scenario = ScenarioInput(**deepcopy(ScenarioInput.Config.json_schema_extra["example"]))
    engine = StrategyEngine(tax_year_data_loader=lambda y, p="ON": YEAR_2025)
    params = StrategyParamsInput(
        loan_interest_rate_pct=5.0,
        loan_amount_as_pct_of_rrif=20.0,
    )
    yearly, summary = engine.run(StrategyCodeEnum.IO, scenario, params)

    assert yearly[0].income_sources.rrif_withdrawal > 0
    assert summary.lifetime_tax_paid_nominal > 0
