import unittest
from app.services.strategy_engine import tax_rules

class FederalCreditsPhaseoutTests(unittest.TestCase):
    def setUp(self):
        self.base_td = {
            "federal_tax_brackets": [{"upto": 50000, "rate": 0.15}],
            "federal_personal_amount": 15000,
            "federal_personal_amount_low": 12000,
            "federal_bpa_phaseout_start": 100000,
            "federal_bpa_phaseout_end": 150000,
            "federal_age_amount": 0,
            "federal_age_amount_threshold": 0,
            "federal_pension_income_credit_max": 0,
        }

    def _credits(self, income):
        return tax_rules._federal_credits(income, 30, 0, self.base_td)

    def test_below_phaseout(self):
        self.assertAlmostEqual(self._credits(90000), 15000 * 0.15)

    def test_within_phaseout(self):
        expected_base = 15000 - (15000 - 12000) * (125000 - 100000) / (150000 - 100000)
        self.assertAlmostEqual(self._credits(125000), expected_base * 0.15)

    def test_above_phaseout(self):
        self.assertAlmostEqual(self._credits(160000), 12000 * 0.15)

if __name__ == "__main__":
    unittest.main()
