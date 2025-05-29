# app/services/strategy_engine/strategies/bracket_filling.py
"""
Bracket‑Filling strategy  (code = BF)

Pull just enough RRIF income each year so that taxable income stays
≤ `params.bracket_fill_ceiling` (often top‑of‑bracket or OAS threshold).

Enhancements:
• honours CPP/OAS start‑age deferral
• simple taxable share of non‑reg growth (40 %)
• real spending target inflated 2 % p.a.
• surplus after‑tax cash reinvested in non‑registered account
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from app.data_models.scenario import StrategyCodeEnum
from app.services.strategy_engine import tax_rules
from app.services.strategy_engine.engine import register

from .base_strategy import BaseStrategy, EngineState, YearScratch

# behavioural constants
ASSUMED_INFLATION = Decimal("0.02")
TAXABLE_PORTION_NONREG_GROWTH = Decimal("0.40")


@register(StrategyCodeEnum.BF.value)
class BracketFillingStrategy(BaseStrategy):
    code = StrategyCodeEnum.BF
    display_name = "Bracket Filling"
    complexity = 2

    def validate_params(self) -> None:  # noqa: D401
        """Ensure bracket_fill_ceiling is provided."""
        if self.params.bracket_fill_ceiling is None:
            raise ValueError("bracket_fill_ceiling required for Bracket-Filling strategy")

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
        # 1. CPP / OAS / DB pension
        # ----------------------------------------------------------------
        cpp_start_age = self.params.cpp_start_age or 65
        oas_start_age = self.params.oas_start_age or 65

        cpp = Decimal("0")
        if age >= cpp_start_age:
            cpp = Decimal(
                str(
                    tax_rules.get_adjusted_cpp_benefit(
                        self.scenario.cpp_at_65, cpp_start_age, td
                    )
                )
            )

        oas_gross = Decimal("0")
        if age >= oas_start_age:
            oas_gross = Decimal(
                str(
                    tax_rules.get_adjusted_oas_benefit(
                        self.scenario.oas_at_65, oas_start_age, td
                    )
                )
            )

        db_pension = Decimal(str(self.scenario.defined_benefit_pension))

        # taxable share of non‑reg growth
        non_reg_growth = begin_non * Decimal(
            str(self.scenario.expect_return_pct / 100)
        )
        taxable_non_reg_income = non_reg_growth * TAXABLE_PORTION_NONREG_GROWTH

        base_income = cpp + oas_gross + db_pension + taxable_non_reg_income

        # ----------------------------------------------------------------
        # 2. RRIF withdrawal needed to reach ceiling
        # ----------------------------------------------------------------
        ceiling = Decimal(str(self.params.bracket_fill_ceiling or 0))
        if ceiling <= 0:
            ceiling = Decimal("9e99")  # effectively “no ceiling”

        gross_rrif = max(Decimal("0"), ceiling - base_income)

        # ensure ≥ CRA minimum
        rrif_age = min(age, spouse_age_this_year) if spouse_age_this_year else age
        min_rrif = Decimal(
            str(
                tax_rules.get_rrif_min_withdrawal_amount(
                    float(begin_rrif), rrif_age, td
                )
            )
        )
        gross_rrif = max(gross_rrif, min_rrif)

        # SAFETY: never withdraw more than the account balance
        gross_rrif = min(gross_rrif, begin_rrif)

        # ----------------------------------------------------------------
        # 3. Taxes
        # ----------------------------------------------------------------
        taxable_income = base_income + gross_rrif
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
        # 4. Real spending target (inflated)
        # ----------------------------------------------------------------
        spend_target = Decimal(str(self.scenario.desired_spending)) * (
            (Decimal("1") + ASSUMED_INFLATION) ** idx
        )
        spending = min(after_tax_income, spend_target)
        surplus = after_tax_income - spending

        # ----------------------------------------------------------------
        # 5. Grow balances
        # ----------------------------------------------------------------
        growth_factor = Decimal("1") + Decimal(
            str(self.scenario.expect_return_pct / 100)
        )

        end_rrif = (begin_rrif - gross_rrif) * growth_factor
        end_tfsa = begin_tfsa * growth_factor
        end_non = (begin_non + surplus + non_reg_growth) * growth_factor

        # ----------------------------------------------------------------
        # 6. Record
        # ----------------------------------------------------------------
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
                other_taxable_income=taxable_non_reg_income,
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

