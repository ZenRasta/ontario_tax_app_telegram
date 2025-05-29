import unittest

from app.data_models.scenario import StrategyCodeEnum
from app.main import _strategy_display
from app.services.strategy_engine.engine import _STRATEGY_REGISTRY


class StrategyDisplayTests(unittest.TestCase):
    def test_display_name_lookup(self) -> None:
        for code in StrategyCodeEnum:
            if code == StrategyCodeEnum.MIN:
                continue
            cls = _STRATEGY_REGISTRY[code.value]
            self.assertEqual(_strategy_display(code), getattr(cls, "display_name", code.value))


if __name__ == "__main__":
    unittest.main()
