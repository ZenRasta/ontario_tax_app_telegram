import sys
from pathlib import Path

import pytest
from httpx import AsyncClient

# Ensure app package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app
from app.utils import year_data_loader

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
    'rrif_table': {
        65: 0.0400,
        66: 0.0403,
        67: 0.0406,
        68: 0.0409,
        69: 0.0412,
        70: 0.0450,
        71: 0.0528,
        72: 0.0540,
        73: 0.0553,
        74: 0.0567,
        75: 0.0582,
    },
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

@pytest.fixture(autouse=True)
def _patch_loader(monkeypatch):
    monkeypatch.setattr(year_data_loader, 'load_tax_year_data', lambda year, prov='ON': YEAR_2025)


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
