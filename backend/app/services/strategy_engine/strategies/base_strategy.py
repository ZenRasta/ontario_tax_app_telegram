# app/services/strategy_engine/strategies/base_strategy.py
"""
Abstract class shared by all deterministic withdrawal strategies.

A concrete subclass **must**:
    • declare  `code : StrategyCodeEnum`
    • declare  `display_name : str`
    • declare  `complexity : int  # 1 (simple) → 5 (complex))`
    • implement `run_year(idx: int, state: EngineState)`

The StrategyEngine will:
    1. create an EngineState (initial balances, etc.)
    2. loop over projection years, calling strategy.run_year()
    3. afterwards convert `state.rows` → YearlyResult list and SummaryMetrics
"""

from __future__ import annotations

import datetime as _dt
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List

from ....data_models.scenario import (
    ScenarioInput,
    StrategyParamsInput,
    StrategyCodeEnum,
)
from ....data_models.results import (
    IncomeSources,
    SummaryMetrics,
    TaxBreakdown,
    YearlyResult,
)
from ..tax_rules import TaxYearData
from ..state import EngineState, YearScratch  # ensure this file exists

# real discount rate used for PV calcs (2 % after inflation)
REAL_DISCOUNT_RATE = Decimal("0.02")


# ------------------------------------------------------------------ #
class BaseStrategy(ABC):
    # --- to be overridden in subclasses --------------------------------
    code: StrategyCodeEnum
    display_name: str = "Unnamed Strategy"
    complexity: int = 1  # 1 = simple, 5 = complex
    # -------------------------------------------------------------------

    def __init__(
        self,
        scenario: ScenarioInput,
        params: StrategyParamsInput,
        tax_loader,  # callable(year:int, prov:str) → TaxYearData
    ):
        self.scenario = scenario
        self.params = params
        self._tax_loader = tax_loader
        self.start_year = _dt.datetime.now().year  # e.g., 2025
        self.validate_params()

    # -------------------------------------------------------------- #
    def validate_params(self) -> None:
        """Hook for subclasses to enforce required parameters."""
        return

    # ================================================================== #
    # abstract hook every concrete strategy must implement
    # ================================================================== #
    @abstractmethod
    def run_year(self, idx: int, state: EngineState) -> None: ...

    # ================================================================== #
    # -------------- helpers available to all subclasses ----------------
    # ================================================================== #
    def tax_data(self, year: int) -> TaxYearData:
        return self._tax_loader(year, self.scenario.province)

    # ================================================================== #
    # -------- functions the ENGINE calls after year loop ---------------
    # ================================================================== #
    def build_yearly_results(self, state: EngineState) -> List[YearlyResult]:
        """
        Convert internal YearScratch rows into API‑facing YearlyResult
        objects.  Decimals → float for JSON serialisation.
        """
        results: list[YearlyResult] = []
        for y in state.rows:
            results.append(
                YearlyResult(
                    year=y.year,
                    age=y.age,
                    spouse_age=y.spouse_age,
                    begin_rrif_balance=float(y.begin_rrif),
                    begin_tfsa_balance=float(y.begin_tfsa),
                    begin_non_reg_balance=float(y.begin_non_reg),
                    income_sources=IncomeSources(
                        rrif_withdrawal=float(y.gross_rrif),
                        cpp_received=float(y.cpp),
                        oas_received_gross=float(y.oas_gross),
                        defined_benefit_pension=float(y.db_pension),
                        other_taxable_income=float(y.other_taxable_income),
                    ),
                    total_taxable_income=float(y.taxable_income),
                    tax_breakdown=TaxBreakdown(
                        federal_tax=float(y.fed_tax),
                        provincial_tax=float(y.prov_tax),
                        oas_clawback_amount=float(y.oas_claw),
                    ),
                    total_tax_paid=float(y.total_tax),
                    after_tax_income=float(y.after_tax_income),
                    oas_net_received=float(y.oas_net),
                    actual_spending=float(y.spending),
                    end_rrif_balance=float(y.end_rrif),
                    end_tfsa_balance=float(y.end_tfsa),
                    end_non_reg_balance=float(y.end_non_reg),
                    marginal_tax_rate=None,  # optional – fill in strategy if desired
                )
            )
        return results

    # ------------------------------------------------------------------ #
    def build_summary(self, yearly: List[YearlyResult]) -> SummaryMetrics:
        """Very basic aggregation; refine as needed."""
        lifetime_tax_nom = sum(y.total_tax_paid for y in yearly)
        pv_tax = float(
            sum(
                y.total_tax_paid / ((1 + float(REAL_DISCOUNT_RATE)) ** i)
                for i, y in enumerate(yearly)
            )
        )
        avg_spend = sum(y.actual_spending for y in yearly) / len(yearly)

        end_bal = (
            yearly[-1].end_rrif_balance
            + yearly[-1].end_tfsa_balance
            + yearly[-1].end_non_reg_balance
        )

        return SummaryMetrics(
            lifetime_tax_paid_nominal=lifetime_tax_nom,
            lifetime_tax_paid_pv=pv_tax,
            average_effective_tax_rate=0.0,             # compute later
            average_marginal_tax_rate_on_rrif=None,
            years_in_oas_clawback=sum(
                1 for y in yearly if y.tax_breakdown.oas_clawback_amount > 0
            ),
            total_oas_clawback_paid_nominal=sum(
                y.tax_breakdown.oas_clawback_amount for y in yearly
            ),
            tax_volatility_score=None,
            max_sustainable_spending_pv=None,
            average_annual_real_spending=avg_spend,
            cashflow_coverage_ratio=None,
            ruin_probability_pct=None,
            years_to_ruin_percentile_10=None,
            final_total_portfolio_value_nominal=end_bal,
            final_total_portfolio_value_pv=end_bal,
            net_value_to_heirs_after_final_taxes_pv=end_bal,
            sequence_risk_score=None,
            strategy_complexity_score=self.complexity,
        )

    # ------------------------------------------------------------------ #
    def run(self) -> SummaryMetrics:
        """Execute the strategy for the full projection horizon."""
        # 1. Create initial state with starting balances
        state = EngineState.initial(self.scenario, self.start_year)

        # 2. Iterate through each projection year and run strategy logic
        for idx in range(self.scenario.life_expectancy_years):
            self.run_year(idx, state)

        # 3. Convert scratch rows to YearlyResult objects
        yearly_results = self.build_yearly_results(state)

        # 4. Build aggregated summary metrics
        summary = self.build_summary(yearly_results)

        # 5. Store yearly results for external access
        self.yearly_results = yearly_results

        # 6. Return summary metrics
        return summary
