from app.data_models.scenario import ScenarioInput, StrategyCodeEnum
from app.data_models.results import SummaryMetrics
from app.services.strategy_engine import engine as engine_mod


EXAMPLE_SCENARIO = ScenarioInput(**ScenarioInput.Config.json_schema_extra["example"]) 


def test_run_strategy_batch_uses_provided_codes(monkeypatch):
    called = []
    example_metrics = SummaryMetrics(**SummaryMetrics.Config.json_schema_extra["example"])

    def fake_single(code, scenario, tax_loader=engine_mod.load_tax_year_data):
        called.append(code)
        return example_metrics

    monkeypatch.setattr(engine_mod, "run_single_strategy", fake_single)

    codes = [StrategyCodeEnum.GM, StrategyCodeEnum.MIN]
    results = engine_mod.run_strategy_batch(EXAMPLE_SCENARIO, codes)

    assert called == codes
    assert [r.strategy_code for r in results] == codes
