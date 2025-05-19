import pytest
from decimal import Decimal
from app.services.strategy_engine import tax_rules

TD_2025 = {
    'federal_personal_amount': 15978,
    'federal_personal_amount_min': 14156,
    'federal_personal_amount_phaseout_start': 173205,
    'federal_personal_amount_phaseout_end': 246752,
    'federal_age_amount': 8396,
    'federal_age_amount_threshold': 43179,
    'federal_pension_income_credit_max': 2000,
    'federal_tax_brackets': [
        {'upto': 55868, 'rate': 0.15},
        {'upto': 111733, 'rate': 0.205},
        {'upto': 173205, 'rate': 0.26},
        {'upto': 246752, 'rate': 0.29},
        {'upto': None, 'rate': 0.33},
    ],
    'oas_clawback_threshold': 93454,
    'oas_clawback_rate': 0.15,
    'oas_max_benefit_at_65': 8250,
    'oas_deferral_factor_per_month': 0.006,
    'cpp_max_benefit_at_65': 17060,
    'cpp_deferral_factor_per_year': 0.084,
    'cpp_early_factor_per_year': 0.072,
    'rrif_table': {},
    'ontario_personal_amount': 12122,
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
    'ontario_surtax_threshold_1': 5315,
    'ontario_surtax_rate_1': 0.20,
    'ontario_surtax_threshold_2': 6802,
    'ontario_surtax_rate_2': 0.36,
}

CASES = {
    40000: {
        'federal_tax': Decimal('3603.30'),
        'provincial_tax': Decimal('1407.84'),
        'provincial_surtax': Decimal('0.00'),
        'total_income_tax': Decimal('5011.14'),
        'oas_clawback': Decimal('0.00'),
    },
    95000: {
        'federal_tax': Decimal('14005.56'),
        'provincial_tax': Decimal('6102.26'),
        'provincial_surtax': Decimal('131.21'),
        'total_income_tax': Decimal('20107.82'),
        'oas_clawback': Decimal('231.90'),
    },
    120000: {
        'federal_tax': Decimal('19585.24'),
        'provincial_tax': Decimal('9547.92'),
        'provincial_surtax': Decimal('945.54'),
        'total_income_tax': Decimal('29133.17'),
        'oas_clawback': Decimal('3981.90'),
    },
    280000: {
        'federal_tax': Decimal('65992.32'),
        'provincial_tax': Decimal('36416.08'),
        'provincial_surtax': Decimal('8057.70'),
        'total_income_tax': Decimal('102408.40'),
        'oas_clawback': Decimal('8250.00'),
    },
}

@pytest.mark.parametrize('income', [40000, 95000, 120000, 280000])
def test_tax_calculations(income):
    res = tax_rules.calculate_all_taxes(income, age=30, pension_inc=0, td=TD_2025)
    expected = CASES[income]
    for key, val in expected.items():
        assert Decimal(str(res[key])).quantize(Decimal('0.01')) == val
