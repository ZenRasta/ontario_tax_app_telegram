from decimal import Decimal

import pytest

from app.services.strategy_engine import tax_rules

TD_2025 = {
    'federal_personal_amount': 15705,
    'federal_personal_amount_min': 14156,
    'federal_personal_amount_phaseout_start': 173205,
    'federal_personal_amount_phaseout_end': 246752,
    'federal_age_amount': 8396,
    'federal_age_amount_threshold': 43179,
    'federal_pension_income_credit_max': 2000,
    'federal_tax_brackets': [
        {'upto': 58579, 'rate': 0.15},
        {'upto': 117158, 'rate': 0.205},
        {'upto': 172620, 'rate': 0.26},
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

CASES = {
    40000: {
        'federal_tax': Decimal('3644.25'),
        'provincial_tax': Decimal('1420.82'),
        'provincial_surtax': Decimal('0.00'),
        'total_income_tax': Decimal('5065.07'),
        'oas_clawback': Decimal('0.00'),
    },
    95000: {
        'federal_tax': Decimal('13897.40'),
        'provincial_tax': Decimal('6070.04'),
        'provincial_surtax': Decimal('86.01'),
        'total_income_tax': Decimal('19967.44'),
        'oas_clawback': Decimal('231.90'),
    },
    120000: {
        'federal_tax': Decimal('19178.71'),
        'provincial_tax': Decimal('9468.81'),
        'provincial_surtax': Decimal('853.45'),
        'total_income_tax': Decimal('28647.53'),
        'oas_clawback': Decimal('3981.90'),
    },
    280000: {
        'federal_tax': Decimal('65562.39'),
        'provincial_tax': Decimal('36336.97'),
        'provincial_surtax': Decimal('7965.61'),
        'total_income_tax': Decimal('101899.36'),
        'oas_clawback': Decimal('8250.00'),
    },
}

@pytest.mark.parametrize('income', [40000, 95000, 120000, 280000])
def test_tax_calculations(income):
    res = tax_rules.calculate_all_taxes(income, age=30, pension_inc=0, td=TD_2025)
    expected = CASES[income]
    for key, val in expected.items():
        assert Decimal(str(res[key])).quantize(Decimal('0.01')) == val
