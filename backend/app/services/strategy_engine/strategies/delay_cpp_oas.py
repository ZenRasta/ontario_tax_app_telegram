# app/services/strategy_engine/strategies/delay_cpp_oas.py
"""
CPP / OAS Delay (code = CD)

• User picks `params.cpp_start_age` / `params.oas_start_age`
  (often 70 / 70).  Until those ages the retiree bridges spending by
  drawing extra from the RRIF; afterwards it reverts to a gradual
  meltdown (still subject to CRA minimums).

• Goal‑seeks the RRIF withdrawal each year so **after‑tax income ≈ real
  spending target** (inflation‑adjusted).  Surplus cash is invested in
  the non‑registered account.

Assumptions (simplified)
------------------------
* 40 % of non‑registered growth is taxed annually
  (`TAXABLE_PORTION_NONREG_GROWTH`).
* No TFSA contribution logic yet.
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
TOL = Decimal("1")


@register(StrategyCodeEnum.CD.value)
class DelayCppOasStrategy(BaseStrategy):
    code = StrategyCodeEnum.CD
    display_name = "Delay CPP / OAS (RRSP Bridge)"
    complexity = 3

    def validate_params(self) -> None:  # noqa: D401
        """Ensure CPP/OAS start ages provided."""
        if self.params.cpp_start_age is None or self.params.oas_start_age is None:
            raise ValueError("cpp_start_age and oas_start_age required for Delay CPP/OAS strategy")

    # -------------------------------------------------------------- #
    def run_year(self, idx: int, state: EngineState) -> None:
        yr = state.start_year + idx
        age = self.scenario.age + idx
        spouse = self.params.spouse or self.scenario.spouse
        spouse_age_this_year: Optional[int] = (
            spouse.age + idx if spouse else None
        )

        td = self.tax_data(yr)

        # ------------------ balances at start ---------------------- #
        begin_rrif = state.balances["rrif"]
        begin_tfsa = state.balances["tfsa"]
        begin_non = state.balances["non_reg"]

        # ------------------ CPP / OAS income ----------------------- #
        cpp_start = self.params.cpp_start_age or 65
        oas_start = self.params.oas_start_age or 65

        cpp = Decimal("0")
        if age >= cpp_start:
            cpp = Decimal(
                str(
                    tax_rules.get_adjusted_cpp_benefit(
                        self.scenario.cpp_at_65, cpp_start, td
                    )
                )
            )

        oas_gross = Decimal("0")
        if age >= oas_start:
            oas_gross = Decimal(
                str(
                    tax_rules.get_adjusted_oas_benefit(
                        self.scenario.oas_at_65, oas_start, td
                    )
                )
            )

        db_pension = Decimal(str(self.scenario.defined_benefit_pension))

        # taxable slice of non‑reg growth
        non_reg_growth = begin_non * Decimal(str(self.scenario.expect_return_pct / 100))
        taxable_nonreg_income = non_reg_growth * TAXABLE_PORTION_NONREG_GROWTH

        # ------------------ real spending target ------------------- #
        spend_target = Decimal(str(self.scenario.desired_spending)) * (
            (Decimal("1") + ASSUMED_INFLATION) ** idx
        )

        # ------------------ CRA minimum ---------------------------- #
        rrif_age = min(age, spouse_age_this_year) if spouse_age_this_year else age
        min_rrif = Decimal(
            str(
                tax_rules.get_rrif_min_withdrawal_amount(
                    float(begin_rrif), rrif_age, td
                )
            )
        )
        low = min_rrif
        high = begin_rrif
        gross_rrif = low  # default

        # helper – after‑tax given withdrawal `w`
        def after_tax(w: Decimal) -> Decimal:
            taxable = cpp + oas_gross + db_pension + taxable_nonreg_income + w
            elig = tax_rules.get_eligible_pension_income_for_credit(
                rrif_withdrawal=float(w),
                db_pension_income=float(db_pension),
                age=age,
            )
            tr = tax_rules.calculate_all_taxes(
                total_taxable_income=float(taxable),
                age=age,
                eligible_pension_income=float(elig),
                oas_income_included_in_taxable=float(oas_gross),
                tax_year_data=td,
                province=self.scenario.province,
            )
            tot_tax = Decimal(str(tr["total_income_tax"] + tr["oas_clawback"]))
            return taxable - tot_tax

        # ------------- binary search for withdrawal ---------------- #
        for _ in range(MAX_ITER):
            gross_rrif = (low + high) / 2
            diff = after_tax(gross_rrif) - spend_target
            if abs(diff) <= TOL:
                break
            if diff > 0:  # too much cash, lower w
                high = gross_rrif
            else:         # not enough cash
                low = gross_rrif
        else:
            gross_rrif = high  # fallback

        # ----- final tax calc with chosen withdrawal --------------- #
        taxable_income = cpp + oas_gross + db_pension + taxable_nonreg_income + gross_rrif
        elig_pension = tax_rules.get_eligible_pension_income_for_credit(
            rrif_withdrawal=float(gross_rrif),
            db_pension_income=float(db_pension),
            age=age,
        )
        tax = tax_rules.calculate_all_taxes(
            total_taxable_income=float(taxable_income),
            age=age,
            eligible_pension_income=float(elig_pension),
            oas_income_included_in_taxable=float(oas_gross),
            tax_year_data=td,
            province=self.scenario.province,
        )

        total_tax = Decimal(str(tax["total_income_tax"] + tax["oas_clawback"]))
        after_tax_income = taxable_income - total_tax
        spending = min(after_tax_income, spend_target)
        surplus = after_tax_income - spending
        oas_net = oas_gross - Decimal(str(tax["oas_clawback"]))

        # ------------------ grow balances -------------------------- #
        growth = Decimal("1") + Decimal(str(self.scenario.expect_return_pct / 100))
        end_rrif = (begin_rrif - gross_rrif) * growth
        end_tfsa = begin_tfsa * growth
        end_non = (begin_non + surplus + non_reg_growth) * growth

        # ------------------ record scratch ------------------------- #
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

