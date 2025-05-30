from decimal import Decimal

from app.data_models.scenario import (
    ScenarioInput,
    StrategyCodeEnum,
    StrategyParamsInput,
)
from app.services.strategy_engine.engine import StrategyEngine


YEAR_2025 = {
    'federal_personal_amount': 15705,
    'federal_personal_amount_min': 14156,
    'federal_personal_amount_phaseout_start': 173205,
    'federal_personal_amount_phaseout_end': 246752,
    'federal_age_amount': 8396,
    'federal_age_amount_threshold': 43179,
    'federal_pension_income_credit_max': 2000,
    'federal_tax_brackets': [
        {'upto': 58579, 'rate': 0.1500},
        {'upto': 117158, 'rate': 0.2050},
        {'upto': 172620, 'rate': 0.2600},
        {'upto': 246752, 'rate': 0.2900},
        {'upto': None, 'rate': 0.3300},
    ],
    'oas_clawback_threshold': 93454,
    'oas_clawback_rate': 0.15,
    'oas_max_benefit_at_65': 8250,
    'oas_deferral_factor_per_month': 0.006,
    'cpp_max_benefit_at_65': 17060,
    'cpp_deferral_factor_per_year': 0.084,
    'cpp_early_factor_per_year': 0.072,
    'rrif_table': {65: 0.0400},
    'ontario_personal_amount': 11865,
    'ontario_age_amount': 5750,
    'ontario_age_amount_threshold': 43179,
    'ontario_pension_income_credit_max': 1500,
    'ontario_tax_brackets': [
        {'upto': 51446, 'rate': 0.0505},
        {'upto': 102894, 'rate': 0.0915},
        {'upto': 150000, 'rate': 0.1116},
        {'upto': 220000, 'rate': 0.1216},
        {'upto': None, 'rate': 0.1316},
    ],
    'ontario_surtax_threshold_1': 5554,
    'ontario_surtax_rate_1': 0.20,
    'ontario_surtax_threshold_2': 7108,
    'ontario_surtax_rate_2': 0.36,
}


def test_lump_sum_withdrawal_clamps_balance_to_zero():
    scenario = ScenarioInput(**ScenarioInput.Config.json_schema_extra["example"])
    engine = StrategyEngine(tax_year_data_loader=lambda y, p="ON": YEAR_2025)

    params = StrategyParamsInput(
        lump_sum_year_offset=0,
        lump_sum_amount=Decimal(str(scenario.rrsp_balance)) + Decimal("100000"),
    )

    yearly, _ = engine.run(scenario, StrategyCodeEnum.LS, params)
    assert yearly[0].end_rrif_balance == 0
