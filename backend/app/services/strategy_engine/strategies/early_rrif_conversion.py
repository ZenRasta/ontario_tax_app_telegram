"""
Early RRIF Conversion  (code = E65)

• Converts the entire RRSP balance to a RRIF in the calendar year the
  retiree reaches `params.rrif_conversion_age` (default 65).

• Withdraws **only the CRA minimum** each year thereafter.
  That $2 000+ of eligible pension income unlocks both the federal and
  Ontario pension‑income credits at age 65 +.

• All other mechanics (CPP/OAS at 65, spending inflation, surplus
  reinvestment) mirror Gradual Meltdown.

Limitations
-----------
* No partial RRSP—>RRIF split; once converted we treat the whole pot as
  a RRIF.
* If the minimum is below real‑spending needs, spending is simply
  clipped (no forced withdrawal).  Surplus cash is invested in the
  non‑registered account.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from app.data_models.scenario import StrategyCodeEnum
from app.services.strategy_engine import tax_rules
from app.services.strategy_engine.engine import register

from .base_strategy import BaseStrategy, EngineState, YearScratch

# shared constants (kept in sync with other strategies)
ASSUMED_INFLATION = Decimal("0.02")
TAXABLE_PORTION_NONREG_GROWTH = Decimal("0.40")


@register(StrategyCodeEnum.E65.value)
class EarlyRRIFConversionStrategy(BaseStrategy):
    code = StrategyCodeEnum.E65
    display_name = "Early RRIF Conversion @65"
    complexity = 2

    # -------------------------------------------------------------- #
    def run_year(self, idx: int, state: EngineState) -> None:
        yr = state.start_year + idx
        age = self.scenario.age + idx
        spouse_age_this_year: Optional[int] = (
            self.scenario.spouse.age + idx if self.scenario.spouse else None
        )

        td = self.tax_data(yr)

        begin_rrif = state.balances["rrif"]
        begin_tfsa = state.balances["tfsa"]
        begin_non = state.balances["non_reg"]

        # -------------------- guaranteed income --------------------- #
        cpp = Decimal(str(self.scenario.cpp_at_65)) if age >= 65 else Decimal("0")
        oas_gross = Decimal(str(self.scenario.oas_at_65)) if age >= 65 else Decimal("0")
        db_pension = Decimal(str(self.scenario.defined_benefit_pension))

        non_reg_growth = begin_non * Decimal(str(self.scenario.expect_return_pct / 100))
        taxable_nonreg_income = non_reg_growth * TAXABLE_PORTION_NONREG_GROWTH

        # -------------------- RRIF withdrawal ----------------------- #
        conv_age = self.params.rrif_conversion_age or 65
        if age < conv_age:
            gross_rrif = Decimal("0")  # still an RRSP; no withdrawal
        else:
            gross_rrif = Decimal(
                str(
                    tax_rules.get_rrif_min_withdrawal_amount(
                        float(begin_rrif), age
                    )
                )
            )

        # -------------------- tax calculation ----------------------- #
        taxable_income = (
            cpp + oas_gross + db_pension + taxable_nonreg_income + gross_rrif
        )

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
        oas_net = oas_gross - Decimal(str(tax["oas_clawback"]))

        # -------------------- spending target ----------------------- #
        spend_target = Decimal(str(self.scenario.desired_spending)) * (
            (Decimal("1") + ASSUMED_INFLATION) ** idx
        )
        spending = min(after_tax_income, spend_target)
        surplus = after_tax_income - spending

        # -------------------- grow balances ------------------------- #
        growth = Decimal("1") + Decimal(str(self.scenario.expect_return_pct / 100))

        end_rrif = (begin_rrif - gross_rrif) * growth
        end_tfsa = begin_tfsa * growth
        end_non = (begin_non + surplus + non_reg_growth) * growth

        # -------------------- record row ---------------------------- #
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

