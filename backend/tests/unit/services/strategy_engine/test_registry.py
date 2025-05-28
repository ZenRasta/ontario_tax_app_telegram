import unittest

from app.data_models.scenario import StrategyCodeEnum
from app.services.strategy_engine.engine import _STRATEGY_REGISTRY


class StrategyRegistryTests(unittest.TestCase):
    def test_all_expected_strategies_registered(self) -> None:
        expected = {c.value for c in StrategyCodeEnum if c != StrategyCodeEnum.MIN}
        self.assertTrue(expected.issubset(set(_STRATEGY_REGISTRY.keys())))


if __name__ == "__main__":
    unittest.main()
