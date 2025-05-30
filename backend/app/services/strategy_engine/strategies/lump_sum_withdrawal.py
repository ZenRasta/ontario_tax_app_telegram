# app/services/strategy_engine/strategies/lump_sum_withdrawal.py
"""
Lump‑Sum Withdrawal (code = LS)

• Same mechanics as Gradual Meltdown, plus a one‑time extra RRIF
  withdrawal (`params.lump_sum_amount`) in projection year
  `params.lump_sum_year_offset` (0 = first year).

• Lump sum is fully taxable that year; any surplus after‑tax cash goes
  to the non‑registered account.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from app.data_models.scenario import StrategyCodeEnum
from app.services.strategy_engine import tax_rules
from app.services.strategy_engine.engine import register

from .base_strategy import BaseStrategy, EngineState, YearScratch

ASSUMED_INFLATION = Decimal("0.02")
TAXABLE_PORTION_NONREG_GROWTH = Decimal("0.40")
MAX_ITER = 20
TOL = Decimal("1")  # $1 tolerance on cash shortfall


@register(StrategyCodeEnum.LS.value)
class LumpSumWithdrawalStrategy(BaseStrategy):
    code = StrategyCodeEnum.LS
    display_name = "Lump‑Sum Withdrawal"
    complexity = 2

    # alias for backward compatibility / tests
    def validate_params(self) -> None:  # noqa: D401
        """Ensure lump-sum parameters provided."""
        if (
            self.params.lump_sum_amount is None
            or self.params.lump_sum_year_offset is None
        ):
            raise ValueError(
                "lump_sum_amount and lump_sum_year_offset required for Lump-Sum strategy"
            )


# Keep the implementation outside the class body, then mix in
def _run_year(self: LumpSumWithdrawalStrategy, idx: int, state: EngineState) -> None:
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

    # ---------------- regular income ------------------------------ #
    cpp = Decimal(str(self.scenario.cpp_at_65)) if age >= 65 else Decimal("0")
    oas_gross = Decimal(str(self.scenario.oas_at_65)) if age >= 65 else Decimal("0")
    db_pension = Decimal(str(self.scenario.defined_benefit_pension))

    non_reg_growth = begin_non * Decimal(str(self.scenario.expect_return_pct / 100))
    taxable_nonreg_income = non_reg_growth * TAXABLE_PORTION_NONREG_GROWTH

    # -------------- CRA minimum withdrawal ------------------------ #
    rrif_age = min(age, spouse_age_this_year) if spouse_age_this_year else age
    min_rrif = Decimal(
        str(
            tax_rules.get_rrif_min_withdrawal_amount(
                float(begin_rrif), rrif_age, td
            )
        )
    )

    # -------------- Binary‑search withdrawal to hit spend target --- #
    spend_target = Decimal(str(self.scenario.desired_spending)) * (
        (Decimal("1") + ASSUMED_INFLATION) ** idx
    )
    low, high = min_rrif, begin_rrif

    def after_tax(w: Decimal) -> Decimal:
        taxable = w + cpp + oas_gross + db_pension + taxable_nonreg_income
        elig = tax_rules.get_eligible_pension_income_for_credit(
            rrif_withdrawal=float(w),
            db_pension_income=float(db_pension),
            age=age,
        )
        tr = tax_rules.calculate_all_taxes(
            float(taxable),
            age,
            float(elig),
            td,
            self.scenario.province,
        )
        tot_tax = Decimal(str(tr["total_income_tax"] + tr["oas_clawback"]))
        return taxable - tot_tax

    gross_rrif = low
    for _ in range(MAX_ITER):
        mid = (low + high) / 2
        diff = after_tax(mid) - spend_target
        if abs(diff) <= TOL:
            gross_rrif = mid
            break
        if diff > 0:
            high = mid
        else:
            low = mid
    else:
        gross_rrif = high

    # -------------- add lump‑sum if this is the year --------------- #
    if (
        self.params.lump_sum_year_offset is not None
        and self.params.lump_sum_amount is not None
        and idx == self.params.lump_sum_year_offset
    ):
        gross_rrif += Decimal(str(self.params.lump_sum_amount))
        gross_rrif = min(begin_rrif, max(gross_rrif, min_rrif))

    # -------------- final tax calculation ------------------------- #
    taxable_income = gross_rrif + cpp + oas_gross + db_pension + taxable_nonreg_income
    elig_pension = tax_rules.get_eligible_pension_income_for_credit(
        rrif_withdrawal=float(gross_rrif),
        db_pension_income=float(db_pension),
        age=age,
    )
    tax = tax_rules.calculate_all_taxes(
        float(taxable_income),
        age,
        float(elig_pension),
        td,
        self.scenario.province,
    )

    total_tax = Decimal(str(tax["total_income_tax"] + tax["oas_clawback"]))
    after_tax_income = taxable_income - total_tax
    oas_net = oas_gross - Decimal(str(tax["oas_clawback"]))

    spending = min(after_tax_income, spend_target)
    surplus = after_tax_income - spending

    # -------------- grow balances --------------------------------- #
    growth = Decimal("1") + Decimal(str(self.scenario.expect_return_pct / 100))
    end_rrif = (begin_rrif - gross_rrif) * growth
    end_tfsa = begin_tfsa * growth
    end_non = (begin_non + surplus + non_reg_growth) * growth

    # -------------- record ---------------------------------------- #
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


# bind method to class (so we didn’t indent a 300‑line class body)
LumpSumWithdrawalStrategy.run_year = _run_year  # type: ignore[attr-defined}

# backward‑compat alias
LumpSumStrategy = LumpSumWithdrawalStrategy

