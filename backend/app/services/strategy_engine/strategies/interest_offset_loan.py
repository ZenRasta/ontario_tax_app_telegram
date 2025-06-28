# app/services/strategy_engine/strategies/interest_offset_loan.py
"""
Interest‑Offset “RRIF Meltdown” (code = IO)

Idea: withdraw *W* from the RRIF, borrow *W* at r % and deduct the
interest; goal‑seek *W* so after‑tax cash ≥ real‑term spending target.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from ....data_models.scenario import StrategyCodeEnum
from .. import tax_rules
from ..engine import register

from .base_strategy import BaseStrategy, EngineState, YearScratch

ASSUMED_INFLATION = Decimal("0.02")
TAXABLE_PORTION_NONREG_GROWTH = Decimal("0.40")
MAX_ITER = 20
TOL = Decimal("1")            # $1 cash‑flow tolerance


@register(StrategyCodeEnum.IO.value)
class InterestOffsetStrategy(BaseStrategy):
    """Alias kept for backward compatibility."""
    code = StrategyCodeEnum.IO
    display_name = "Interest‑Offset Meltdown"
    complexity = 4

    def validate_params(self) -> None:  # noqa: D401
        """Ensure loan parameters provided."""
        if (
            self.params.loan_interest_rate_pct is None
            or self.params.loan_amount_as_pct_of_rrif is None
        ):
            raise ValueError(
                "loan_interest_rate_pct and loan_amount_as_pct_of_rrif required for Interest-Offset strategy"
            )

    def run_year(self, idx: int, state: EngineState) -> None:
        yr = state.start_year + idx
        age = self.scenario.age + idx
        spouse = self.params.spouse or self.scenario.spouse
        spouse_age_this_year: Optional[int] = (
            spouse.age + idx if spouse else None
        )

        td = self.tax_data(yr)

        # ---------- balances at start ------------------------------ #
        begin_rrif = state.balances["rrif"]
        begin_tfsa = state.balances["tfsa"]
        begin_non = state.balances["non_reg"]

        rate = Decimal(str(self.params.loan_interest_rate_pct or 5)) / Decimal("100")

        # ---------- guaranteed income ------------------------------ #
        cpp = Decimal(str(self.scenario.cpp_at_65)) if age >= 65 else Decimal("0")
        oas_gross = Decimal(str(self.scenario.oas_at_65)) if age >= 65 else Decimal("0")
        db_pension = Decimal(str(self.scenario.defined_benefit_pension))

        non_reg_growth = begin_non * Decimal(str(self.scenario.expect_return_pct / 100))
        taxable_nonreg_income = non_reg_growth * TAXABLE_PORTION_NONREG_GROWTH

        # ---------- CRA minimum withdrawal ------------------------- #
        rrif_age = min(age, spouse_age_this_year) if spouse_age_this_year else age
        min_rrif = Decimal(
            str(
                tax_rules.get_rrif_min_withdrawal_amount(
                    float(begin_rrif), rrif_age, td
                )
            )
        )

        # ---------- spending target (real) ------------------------- #
        spend_target = Decimal(str(self.scenario.desired_spending)) * (
            (Decimal("1") + ASSUMED_INFLATION) ** idx
        )

        # ---------- goal‑seek RRIF withdrawal ---------------------- #
        low, high = min_rrif, begin_rrif

        def net_cash(w: Decimal) -> Decimal:
            """After‑tax cash *after* paying interest."""
            interest = w * rate
            taxable = (
                cpp + oas_gross + db_pension + taxable_nonreg_income + w - interest
            )
            taxable = max(Decimal("0"), taxable)

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
            # cash in hand = gross incomes – tax – interest
            return (
                cpp + oas_gross + db_pension + taxable_nonreg_income + w
            ) - tot_tax - interest

        gross_rrif = low
        for _ in range(MAX_ITER):
            mid = (low + high) / 2
            diff = net_cash(mid) - spend_target
            if abs(diff) <= TOL:
                gross_rrif = mid
                break
            if diff > 0:
                high = mid
            else:
                low = mid
        else:
            gross_rrif = high

        # ---------- final tax using chosen withdrawal -------------- #
        interest_exp = gross_rrif * rate
        taxable_income = (
            cpp
            + oas_gross
            + db_pension
            + taxable_nonreg_income
            + gross_rrif
            - interest_exp
        )
        taxable_income = max(Decimal("0"), taxable_income)

        elig_pension = tax_rules.get_eligible_pension_income_for_credit(
            rrif_withdrawal=float(gross_rrif),
            db_pension_income=float(db_pension),
            age=age,
        )
        tr = tax_rules.calculate_all_taxes(
            float(taxable_income),
            age,
            float(elig_pension),
            td,
            self.scenario.province,
        )
        total_tax = Decimal(str(tr["total_income_tax"] + tr["oas_clawback"]))
        after_tax_income = taxable_income - total_tax
        net_cash_available = after_tax_income                    # after‑tax
        net_cash_available += interest_exp                       # add back deduction
        net_cash_available -= interest_exp                       # pay the interest

        spending = min(net_cash_available, spend_target)
        surplus = net_cash_available - spending
        oas_net = oas_gross - Decimal(str(tr["oas_clawback"]))

        # ---------- grow balances --------------------------------- #
        growth = Decimal("1") + Decimal(str(self.scenario.expect_return_pct / 100))
        end_rrif = (begin_rrif - gross_rrif) * growth
        end_tfsa = begin_tfsa * growth
        end_non = (begin_non + surplus + non_reg_growth) * growth

        # ---------- record scratch row ----------------------------- #
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
                other_taxable_income=max(
                    Decimal("0"), taxable_nonreg_income - interest_exp
                ),
                taxable_income=taxable_income,
                fed_tax=tr["federal_tax"],
                prov_tax=tr["provincial_tax"],
                oas_claw=tr["oas_clawback"],
                total_tax=float(total_tax),
                after_tax_income=after_tax_income,
                oas_net=oas_net,
                spending=spending,
                end_rrif=end_rrif,
                end_tfsa=end_tfsa,
                end_non_reg=end_non,
            )
        )


# alias for engine imports that still expect this name
InterestOffsetLoanStrategy = InterestOffsetStrategy
