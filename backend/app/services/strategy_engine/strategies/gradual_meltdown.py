"""
Gradual RRSP/RRIF “Meltdown”   (code = GM)

Default retiree draw‑down rule:
• Each year withdraw just enough from the RRIF so that *after‑tax cash*
  meets the (inflation‑indexed) spending target, **but no more**.
• Always satisfy the CRA minimum.
• Reinvest any surplus after‑tax cash in the non‑registered account.

Two variants triggered by flags/params
--------------------------------------
* **MIN** benchmark (engine passes `min_only=True`) – withdraw exactly
  the CRA minimum, even if that undershoots spending.
* **Empty‑by‑X** (code EBX) – if `params.target_depletion_age` is set,
  the strategy accelerates withdrawals so the RRIF balance trends to ≈ 0
  by that age (linear glide‑path on beginning‑of‑year balance).

Other conventions match BF / CD:
* 2 % inflation on spending target (`ASSUMED_INFLATION`)
* 40 % of nominal non‑registered growth treated as immediate taxable income
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from app.data_models.scenario import StrategyCodeEnum, StrategyParamsInput
from .base_strategy import BaseStrategy, EngineState, YearScratch
from app.services.strategy_engine import tax_rules

ASSUMED_INFLATION = Decimal("0.02")
TAXABLE_PORTION_NONREG_GROWTH = Decimal("0.40")
MAX_ITER = 20
TOL = Decimal("1")  # $1 tolerance for cash shortfall


class GradualMeltdownStrategy(BaseStrategy):
    code = StrategyCodeEnum.GM
    complexity = 1

    # ------------------------------------------------------------------ #
    def __init__(self, *args, min_only=False, **kw):
        super().__init__(*args, **kw)
        self.min_only = min_only
        self.empty_by_x = self.params.target_depletion_age

    # ------------------------------------------------------------------ #
    def run_year(self, idx: int, state: EngineState) -> None:
        yr = state.start_year + idx
        age = self.scenario.age + idx
        spouse = self.params.spouse or self.scenario.spouse
        spouse_age_this_year: Optional[int] = (
            spouse.age + idx if spouse else None
        )
        td = self.tax_data(yr)

        begin_rrif = state.balances["rrif"]
        begin_tfsa = state.balances["tfsa"]
        begin_non = state.balances["non_reg"]

        # ----------------------------------------------------------------
        # 1. Base income streams
        # ----------------------------------------------------------------
        cpp = Decimal("0")
        if age >= 65:
            cpp = Decimal(str(self.scenario.cpp_at_65))

        oas_gross = Decimal("0")
        if age >= 65:
            oas_gross = Decimal(str(self.scenario.oas_at_65))

        db_pension = Decimal(str(self.scenario.defined_benefit_pension))

        non_reg_growth = begin_non * Decimal(str(self.scenario.expect_return_pct / 100))
        taxable_nonreg_income = non_reg_growth * TAXABLE_PORTION_NONREG_GROWTH

        # ----------------------------------------------------------------
        # 2. Determine RRIF withdrawal
        # ----------------------------------------------------------------
        rrif_age = min(age, spouse_age_this_year) if spouse_age_this_year else age
        min_rrif = Decimal(
            str(
                tax_rules.get_rrif_min_withdrawal_amount(
                    float(begin_rrif), rrif_age, td
                )
            )
        )

        if self.min_only:
            gross_rrif = min_rrif
        else:
            gross_rrif = self._compute_withdrawal(
                age,
                begin_rrif,
                min_rrif,
                cpp,
                oas_gross,
                db_pension,
                taxable_nonreg_income,
                idx,
                td,
            )

        # ----------------------------------------------------------------
        # 3. Taxes
        # ----------------------------------------------------------------
        taxable_income = (
            gross_rrif + cpp + oas_gross + db_pension + taxable_nonreg_income
        )
        elig_pension = tax_rules.eligible_pension_income(
            age, float(gross_rrif), float(db_pension)
        )
        tax = tax_rules.calculate_all_taxes(
            float(taxable_income), age, float(elig_pension), td
        )
        total_tax = Decimal(str(tax["total_income_tax"] + tax["oas_clawback"]))
        after_tax_income = taxable_income - total_tax
        oas_net = oas_gross - Decimal(str(tax["oas_clawback"]))

        # ----------------------------------------------------------------
        # 4. Spending / surplus
        # ----------------------------------------------------------------
        spend_target = Decimal(str(self.scenario.desired_spending)) * (
            (Decimal("1") + ASSUMED_INFLATION) ** idx
        )
        spending = min(after_tax_income, spend_target)
        surplus = after_tax_income - spending

        # ----------------------------------------------------------------
        # 5. Grow balances
        # ----------------------------------------------------------------
        growth = Decimal("1") + Decimal(str(self.scenario.expect_return_pct / 100))
        end_rrif = (begin_rrif - gross_rrif) * growth
        end_tfsa = begin_tfsa * growth
        end_non = (begin_non + surplus + non_reg_growth) * growth

        state.record(
            YearScratch(
                year=yr,
                age=age,
                spouse_age=spouse_age_this_year,
                begin_rrif=begin_rrif,
                begin_tfsa=begin_tfsa,
                begin_non_reg=begin_non,
                gross_rrif=gross_rrif,
                cpp=cpp,
                oas_gross=oas_gross,
                db_pension=db_pension,
                other_taxable_income=taxable_nonreg_income,
                taxable_income=taxable_income,
                fed_tax=tax["federal_tax"],
                prov_tax=tax["provincial_tax"],
                oas_claw=tax["oas_clawback"],
                total_tax=float(total_tax),
                after_tax_income=after_tax_income,
                oas_net=oas_net,
                spending=spending,
                end_rrif=end_rrif,
                end_tfsa=end_tfsa,
                end_non_reg=end_non,
            )
        )

    # ------------------------------------------------------------------ #
    # helper: choose withdrawal for normal GM or Empty‑by‑X
    # ------------------------------------------------------------------ #
    def _compute_withdrawal(
        self,
        age: int,
        begin_rrif: Decimal,
        min_rrif: Decimal,
        cpp: Decimal,
        oas_gross: Decimal,
        db_pension: Decimal,
        taxable_nonreg_income: Decimal,
        idx: int,
        td,
    ) -> Decimal:
        """
        For normal GM -> binary‑search to meet spending.
        For Empty‑by‑X   -> withdraw glide‑path fraction of balance.
        """
        if self.empty_by_x and age <= self.empty_by_x:
            remaining_years = self.empty_by_x - age + 1
            glide = begin_rrif / Decimal(remaining_years)
            return max(glide, min_rrif)

        # otherwise binary search to hit spending target
        low = min_rrif
        high = begin_rrif
        spend_target = Decimal(str(self.scenario.desired_spending)) * (
            (Decimal("1") + ASSUMED_INFLATION) ** idx
        )

        def after_tax(w: Decimal) -> Decimal:
            taxable = (
                w + cpp + oas_gross + db_pension + taxable_nonreg_income
            )
            elig = tax_rules.eligible_pension_income(age, float(w), float(db_pension))
            tr = tax_rules.calculate_all_taxes(float(taxable), age, float(elig), td)
            tot_tax = Decimal(str(tr["total_income_tax"] + tr["oas_clawback"]))
            return taxable - tot_tax

        for _ in range(MAX_ITER):
            mid = (low + high) / 2
            cash = after_tax(mid)
            diff = cash - spend_target
            if abs(diff) <= TOL:
                return mid
            if diff > 0:
                high = mid
            else:
                low = mid
        return high  # fallback


class EmptyByXStrategy(GradualMeltdownStrategy):
    """Variant requiring target_depletion_age parameter."""

    code = StrategyCodeEnum.EBX
    complexity = 2

    def validate_params(self) -> None:  # noqa: D401
        """Ensure target_depletion_age is provided."""
        if self.params.target_depletion_age is None:
            raise ValueError("target_depletion_age required for Empty-by-X strategy")

