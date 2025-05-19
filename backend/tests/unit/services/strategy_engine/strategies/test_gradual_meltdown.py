from app.services.strategy_engine.engine import StrategyEngine
from app.data_models.scenario import ScenarioInput, StrategyParamsInput, StrategyCodeEnum

YEAR_2025 = {
    'federal_personal_amount': 15705,
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

def test_golden_first_year_tax_within_tolerance():
    scenario = ScenarioInput(**ScenarioInput.Config.json_schema_extra["example"])
    engine = StrategyEngine(tax_year_data_loader=lambda y, p="ON": YEAR_2025)
    params = scenario.strategy_params_override or StrategyParamsInput()
    yearly, _ = engine.run(scenario, StrategyCodeEnum.GM, params)
    assert abs(yearly[0].total_tax_paid - 11790) <= 5
