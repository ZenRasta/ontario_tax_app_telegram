import unittest

from app.services.strategy_engine import tax_rules

TD = {
    "cpp_deferral_factor_per_year": 0.084,
    "cpp_early_factor_per_year": 0.072,
}

class CppBenefitAdjustmentTests(unittest.TestCase):
    def test_no_change_at_65(self):
        self.assertAlmostEqual(
            tax_rules.get_adjusted_cpp_benefit(17060, 65, TD),
            17060,
            delta=17060 * 0.05,
        )

    def test_deferral(self):
        start = 70
        expected = 17060 * (1 + (start - 65) * TD["cpp_deferral_factor_per_year"])
        res = tax_rules.get_adjusted_cpp_benefit(17060, start, TD)
        self.assertAlmostEqual(res, expected, delta=expected * 0.05)

    def test_early_start(self):
        start = 60
        expected = 17060 * (1 + (start - 65) * -TD["cpp_early_factor_per_year"])
        res = tax_rules.get_adjusted_cpp_benefit(17060, start, TD)
        self.assertAlmostEqual(res, expected, delta=expected * 0.05)


if __name__ == "__main__":
    unittest.main()
