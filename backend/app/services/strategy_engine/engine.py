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

import importlib
import pkgutil

from ...utils.year_data_loader import load_tax_year_data

from ...data_models.results import (
    ResultSummary,
    SummaryMetrics,
    YearlyBalance,
)
from ...data_models.scenario import (
    ScenarioInput,
    StrategyParamsInput,
    StrategyCodeEnum,
)
from ...data_models.strategy import get_strategy_meta
from .strategies.base_strategy import BaseStrategy
from . import strategies as _strategies_pkg


def _load_strategy_modules() -> None:
    """Import all modules in the strategies package to trigger registration."""
    for module_info in pkgutil.iter_modules(
        _strategies_pkg.__path__, _strategies_pkg.__name__ + "."
    ):
        name = module_info.name
        short_name = name.rsplit(".", 1)[-1]
        if short_name.startswith("_"):
            continue
        importlib.import_module(name)

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


# Load all strategy modules so decorators run and populate the registry
_load_strategy_modules()


# ------------------------------------------------------------------
# Existing helper for single-strategy execution (updated to handle params)
# ------------------------------------------------------------------

def run_single_strategy(
    code: str,
    scenario: ScenarioInput,
    params: StrategyParamsInput | None = None,
    tax_loader=load_tax_year_data,
) -> SummaryMetrics:
    # FIX: Convert enum to string if necessary
    code_str = code.value if hasattr(code, 'value') else str(code)

    try:
        strategy_cls = _STRATEGY_REGISTRY[code_str]
    except KeyError as err:
        raise ValueError(
            f"Unknown strategy code '{code_str}'. Available strategies: {list(_STRATEGY_REGISTRY.keys())}"
        ) from err

    # Determine parameters to use
    if params is not None:
        scenario = scenario.copy(deep=True)
        scenario.strategy_params_override = params
        params_obj = params
    else:
        params_obj = scenario.strategy_params_override or StrategyParamsInput()

    engine = strategy_cls(scenario, params_obj, tax_loader)
    return engine.run()  # returns SummaryMetrics


# ────────────────────────────────────────────────────────────────────────────
# ★ NEW batch helper – returns List[ResultSummary] for wizard UI
# ────────────────────────────────────────────────────────────────────────────
def run_strategy_batch(
    scenario: ScenarioInput,
    codes: List[StrategyCodeEnum],
    tax_loader=load_tax_year_data,
) -> List[ResultSummary]:
    """
    Loop over the supplied strategy codes and build a ``ResultSummary``
    for each (thin wrapper around existing logic).
    """
    summaries: List[ResultSummary] = []
    for code in codes:
        metrics: SummaryMetrics = run_single_strategy(code, scenario, tax_loader=tax_loader)

        # Determine strategy display name via metadata helper
        meta = get_strategy_meta(code)
        strategy_name = meta.label if meta else (code.value if hasattr(code, "value") else str(code))

        # convert SummaryMetrics into the lightweight ResultSummary
        yearly_results = getattr(metrics, "yearly_results", None)
        if yearly_results:
            balances = [
                YearlyBalance(
                    year=r.year,
                    portfolio_end=(
                        r.end_rrif_balance
                        + r.end_tfsa_balance
                        + r.end_non_reg_balance
                    ),
                )
                for r in yearly_results
            ]
        else:
            balances = []

        summaries.append(
            ResultSummary(
                strategy_code=code,
                strategy_name=strategy_name,
                total_taxes=metrics.lifetime_tax_paid_nominal,
                total_spending=metrics.average_annual_real_spending,
                final_estate=getattr(
                    metrics,
                    "net_value_to_heirs_after_final_taxes_pv",
                    metrics.final_total_portfolio_value_nominal,
                ),
                yearly_balances=balances,
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
        self.tax_year_data_loader = tax_year_data_loader or load_tax_year_data

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

        # Determine parameters
        if params is not None:
            sc = sc.copy(deep=True)
            sc.strategy_params_override = params
            params_obj = params
        else:
            params_obj = sc.strategy_params_override or StrategyParamsInput()

        try:
            strategy_cls = _STRATEGY_REGISTRY[code_str]
        except KeyError as err:
            raise ValueError(
                f"Unknown strategy code '{code_str}'. Available strategies: {list(_STRATEGY_REGISTRY.keys())}"
            ) from err

        # Create and run the strategy
        engine = strategy_cls(sc, params_obj, self.tax_year_data_loader)
        summary_metrics = engine.run()  # This returns SummaryMetrics

        # Extract yearly results from summary_metrics if available
        yearly_results = []
        if hasattr(summary_metrics, 'yearly_results') and summary_metrics.yearly_results:
            yearly_results = summary_metrics.yearly_results
        elif hasattr(engine, 'yearly_results') and engine.yearly_results:
            yearly_results = engine.yearly_results

        # Return tuple as expected by main.py: (yearly_results, summary)
        return yearly_results, summary_metrics

    def run_batch(
        self,
        codes: List[StrategyCodeEnum],
        scenario: ScenarioInput | None = None,
    ) -> List[ResultSummary]:
        """Run the supplied strategy codes for the wizard UI."""
        sc = scenario or self.scenario
        if sc is None:
            raise ValueError("Scenario must be supplied.")
        return run_strategy_batch(sc, codes, self.tax_year_data_loader)

    # ---------- Alternative single-result method for backward compatibility -------
    def run_single(self, code: str, scenario: ScenarioInput | None = None, params: StrategyParamsInput = None) -> SummaryMetrics:
        """Run a single strategy and return only the summary (original behavior)."""
        sc = scenario or self.scenario
        if sc is None:
            raise ValueError("Scenario must be supplied.")

        # FIX: Convert enum to string if necessary
        code_str = code.value if hasattr(code, 'value') else str(code)

        return run_single_strategy(code_str, sc, params, self.tax_year_data_loader)
