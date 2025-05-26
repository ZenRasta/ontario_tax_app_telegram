"""
Central dispatcher for running withdrawal strategies.

Original functions/classes are preserved.  Only two small additions:

    • run_strategy_batch()  ← new helper the /simulate route calls
    • _STRATEGY_REGISTRY    ← already existed but we expose it here

Everything else (individual strategy classes) lives unchanged in
backend/app/services/strategy_engine/strategies/*.py
"""

from __future__ import annotations

from typing import List, Dict, Type

from app.data_models.scenario import ScenarioInput
from app.data_models.results import ResultSummary, SummaryMetrics, YearlyResult
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
# Existing helper for single-strategy execution (unchanged)
# ------------------------------------------------------------------

def run_single_strategy(code: str, scenario: ScenarioInput) -> SummaryMetrics:
    try:
        strategy_cls = _STRATEGY_REGISTRY[code]
    except KeyError:
        raise ValueError(f"Unknown strategy code '{code}'")
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

    # ---------- legacy instance methods ---------------------------
    def run(self, code: str, scenario: ScenarioInput | None = None) -> SummaryMetrics:
        """Run a single strategy."""
        sc = scenario or self.scenario
        if sc is None:
            raise ValueError("Scenario must be supplied.")
        return run_single_strategy(code, sc)

    def run_batch(self, scenario: ScenarioInput | None = None) -> List[ResultSummary]:
        """Run all codes in the scenario for the wizard UI."""
        sc = scenario or self.scenario
        if sc is None:
            raise ValueError("Scenario must be supplied.")
        return run_strategy_batch(sc)

