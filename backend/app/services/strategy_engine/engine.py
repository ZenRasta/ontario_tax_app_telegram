# app/services/strategy_engine/engine.py
"""
Deterministic simulation orchestrator.

Each concrete withdrawal method lives in
`app/services/strategy_engine/strategies/`.
"""

from __future__ import annotations

import datetime as _dt
from typing import Callable, Dict, List, Tuple

from app.data_models.scenario import (
    ScenarioInput,
    StrategyCodeEnum,
    StrategyParamsInput,
)
from app.data_models.results import YearlyResult, SummaryMetrics
from app.services.strategy_engine.tax_rules import TaxYearData
from app.services.strategy_engine.state import EngineState
from app.services.strategy_engine.strategies.base_strategy import BaseStrategy

# ---------- concrete strategy classes ------------------------------ #
from app.services.strategy_engine.strategies.bracket_filling import (
    BracketFillingStrategy,
)
from app.services.strategy_engine.strategies.gradual_meltdown import (
    GradualMeltdownStrategy,
    EmptyByXStrategy,
)
from app.services.strategy_engine.strategies.early_rrif_conversion import (
    EarlyRRIFConversionStrategy,
)
from app.services.strategy_engine.strategies.delay_cpp_oas import (
    DelayCppOasStrategy,
)
from app.services.strategy_engine.strategies.spousal_equalization import (
    SpousalEqualizationStrategy,
)
from app.services.strategy_engine.strategies.lump_sum_withdrawal import (
    LumpSumWithdrawalStrategy,
)
from app.services.strategy_engine.strategies.interest_offset_loan import (
    InterestOffsetStrategy,
)

# ---------- registry ------------------------------------------------ #
_STRATEGY_REGISTRY: Dict[StrategyCodeEnum, type[BaseStrategy]] = {
    StrategyCodeEnum.BF: BracketFillingStrategy,
    StrategyCodeEnum.GM: GradualMeltdownStrategy,
    StrategyCodeEnum.MIN: GradualMeltdownStrategy,       # handled via flag
    StrategyCodeEnum.E65: EarlyRRIFConversionStrategy,
    StrategyCodeEnum.CD: DelayCppOasStrategy,
    StrategyCodeEnum.SEQ: SpousalEqualizationStrategy,
    StrategyCodeEnum.LS: LumpSumWithdrawalStrategy,
    StrategyCodeEnum.IO: InterestOffsetStrategy,
    StrategyCodeEnum.EBX: EmptyByXStrategy,
}


# ==================================================================== #
class StrategyEngine:
    """
    Runs one deterministic simulation for a chosen strategy.

    Parameters
    ----------
    tax_year_data_loader
        Callable (year:int, province:str) → TaxYearData.
    """

    def __init__(self, tax_year_data_loader: Callable[[int, str], TaxYearData]):
        self.tax_year_data_loader = tax_year_data_loader

    # -------------------------------------------------------------- #
    def run(
        self,
        scenario: ScenarioInput,
        strategy_code: StrategyCodeEnum,
        params: StrategyParamsInput,
    ) -> Tuple[List[YearlyResult], SummaryMetrics]:
        """
        Return (yearly_results, summary_metrics).
        """
        strat_cls = _STRATEGY_REGISTRY.get(strategy_code)
        if strat_cls is None:
            raise ValueError(f"Strategy {strategy_code} not implemented.")

        # MIN = GradualMeltdown with `min_only=True`
        extra_kwargs = {"min_only": True} if strategy_code == StrategyCodeEnum.MIN else {}

        strategy: BaseStrategy = strat_cls(
            scenario=scenario,
            params=params,
            tax_loader=self.tax_year_data_loader,
            **extra_kwargs,
        )

        n_years = scenario.life_expectancy_years
        state = EngineState.initial(scenario, _dt.datetime.now().year)

        for idx in range(n_years):
            strategy.run_year(idx, state)

        yearly_results: List[YearlyResult] = strategy.build_yearly_results(state)
        summary: SummaryMetrics = strategy.build_summary(yearly_results)

        return yearly_results, summary
