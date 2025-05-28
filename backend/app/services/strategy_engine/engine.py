"""
Central dispatcher for running withdrawal strategies.

Original functions/classes are preserved.  Only two small additions:

    • run_strategy_batch()  ← new helper the /simulate route calls
    • _STRATEGY_REGISTRY    ← already existed but we expose it here

Everything else (individual strategy classes) lives unchanged in
backend/app/services/strategy_engine/strategies/*.py
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple, Type

from app.data_models.results import ResultSummary, SummaryMetrics, YearlyResult
from app.data_models.scenario import ScenarioInput, StrategyParamsInput
from app.services.strategy_engine.strategies.base_strategy import BaseStrategy

# ------------------------------------------------------------------
# Existing registry mapping code -> concrete Strategy class
# (the individual strategy modules register themselves on import)
# ------------------------------------------------------------------

_STRATEGY_REGISTRY: Dict[str, Type[BaseStrategy]] = {}


def register(code: str):
    """Decorator used by each strategy class to self-register"""
    def inner(cls: Type[BaseStrategy]):
        _STRATEGY_REGISTRY[code] = cls
        cls.code = code
        return cls
    return inner


# ------------------------------------------------------------------
# Existing helper for single-strategy execution (updated to handle params)
# ------------------------------------------------------------------

def run_single_strategy(code: str, scenario: ScenarioInput, params: StrategyParamsInput = None) -> SummaryMetrics:
    # FIX: Convert enum to string if necessary
    code_str = code.value if hasattr(code, 'value') else str(code)

    try:
        strategy_cls = _STRATEGY_REGISTRY[code_str]
    except KeyError as err:
        raise ValueError(
            f"Unknown strategy code '{code_str}'. Available strategies: {list(_STRATEGY_REGISTRY.keys())}"
        ) from err

    # Apply parameters to scenario if provided
    if params:
        scenario = scenario.copy(deep=True)
        scenario.strategy_params_override = params

    engine = strategy_cls(scenario)
    return engine.run()                 # returns SummaryMetrics


# ────────────────────────────────────────────────────────────────────────────
# ★ NEW batch helper – returns List[ResultSummary] for wizard UI
# ────────────────────────────────────────────────────────────────────────────
def run_strategy_batch(scenario: ScenarioInput) -> List[ResultSummary]:
    """
    Loop over the user-selected strategy codes and build a
    ResultSummary for each (thin wrapper around existing logic).
    """
    summaries: List[ResultSummary] = []
    for code in scenario.strategies:
        metrics: SummaryMetrics = run_single_strategy(code, scenario)

        # convert SummaryMetrics into the lightweight ResultSummary
        summaries.append(
            ResultSummary(
                strategy_code=code,
                strategy_name=metrics.strategy_code.replace('_', ' ').title(),
                total_taxes=metrics.lifetime_tax_paid,
                total_spending=metrics.max_sustainable_spending,
                final_estate=metrics.estate_value,
                yearly_balances=[
                    # Only send (year, portfolio_end) – small & chart-friendly
                    YearlyResult(year=r.year, portfolio_end=r.end_rrif_balance
                                 + r.end_tfsa_balance + r.end_non_reg_balance)
                    for r in metrics.yearly_results  # if you store them
                ] if hasattr(metrics, "yearly_results") else []
            )
        )
    return summaries

# ──────────────────────────────────────────────────────────────────
# ⚙️  Compatibility wrapper — keeps old imports working
# ──────────────────────────────────────────────────────────────────
class StrategyEngine:
    """
    Thin wrapper around the new functional helpers so legacy code that
    does things like:
        StrategyEngine(tax_year_data_loader=loader)
        StrategyEngine(scenario).run("GM")
    still works.
    """

    def __init__(
        self,
        scenario: ScenarioInput | None = None,
        tax_year_data_loader=None,   # legacy kwarg – ignored here
        **_ignored,                  # swallow any other old kwargs
    ):
        self.scenario = scenario
        self.tax_year_data_loader = tax_year_data_loader

    # ---------- legacy instance methods ---------------------------
    def run(self, code: str, scenario: ScenarioInput | None = None, params: StrategyParamsInput = None) -> Tuple[List[Any], SummaryMetrics]:
        """
        Run a single strategy and return both yearly results and summary.

        FIX: Updated to return tuple (yearly_results, summary) as expected by main.py
        FIX: Added params parameter to handle strategy parameters
        FIX: Ensure code is string value for registry lookup
        """
        sc = scenario or self.scenario
        if sc is None:
            raise ValueError("Scenario must be supplied.")

        # FIX: Convert enum to string if necessary
        code_str = code.value if hasattr(code, 'value') else str(code)

        # Apply parameters to scenario if provided
        if params:
            sc = sc.copy(deep=True)
            sc.strategy_params_override = params

        try:
            strategy_cls = _STRATEGY_REGISTRY[code_str]
        except KeyError as err:
            raise ValueError(
                f"Unknown strategy code '{code_str}'. Available strategies: {list(_STRATEGY_REGISTRY.keys())}"
            ) from err

        # Create and run the strategy
        engine = strategy_cls(sc)
        summary_metrics = engine.run()  # This returns SummaryMetrics

        # Extract yearly results from summary_metrics if available
        yearly_results = []
        if hasattr(summary_metrics, 'yearly_results') and summary_metrics.yearly_results:
            yearly_results = summary_metrics.yearly_results
        elif hasattr(engine, 'yearly_results') and engine.yearly_results:
            yearly_results = engine.yearly_results

        # Return tuple as expected by main.py: (yearly_results, summary)
        return yearly_results, summary_metrics

    def run_batch(self, scenario: ScenarioInput | None = None) -> List[ResultSummary]:
        """Run all codes in the scenario for the wizard UI."""
        sc = scenario or self.scenario
        if sc is None:
            raise ValueError("Scenario must be supplied.")
        return run_strategy_batch(sc)

    # ---------- Alternative single-result method for backward compatibility -------
    def run_single(self, code: str, scenario: ScenarioInput | None = None, params: StrategyParamsInput = None) -> SummaryMetrics:
        """Run a single strategy and return only the summary (original behavior)."""
        sc = scenario or self.scenario
        if sc is None:
            raise ValueError("Scenario must be supplied.")

        # FIX: Convert enum to string if necessary
        code_str = code.value if hasattr(code, 'value') else str(code)

        return run_single_strategy(code_str, sc, params)


# ------------------------------------------------------------------
# Load strategy modules (registration happens at import time)
# ------------------------------------------------------------------
from .strategies import (  # noqa: F401,E402
    bracket_filling,
    delay_cpp_oas,
    early_rrif_conversion,
    gradual_meltdown,
    interest_offset_loan,
    lump_sum_withdrawal,
    spousal_equalization,
)
