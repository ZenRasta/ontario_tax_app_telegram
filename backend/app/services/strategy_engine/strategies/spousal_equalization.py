# app/services/strategy_engine/strategies/spousal_equalization.py
"""
Spousal Income‑Split / Equalisation   (code = SEQ)

Objective
---------
Optimise household taxes by shifting RRIF withdrawals and other eligible
pension income 50 / 50 between spouses (CRA pension‑income splitting
rules) while still meeting the combined real spending target.

Rules & simplifications
-----------------------
* If `scenario.spouse` is None we defer to Gradual Meltdown logic.
* Uses **younger spouse’s age** for CRA RRIF‑minimum factors.
* Household has ONE RRIF balance (primary).  We notionally “attribute”
  half the withdrawal to each spouse for tax purposes.
* Other taxable income:
    – Primary: non‑reg taxable growth.  
    – Spouse : `spouse.other_income`.
* CPP/OAS amounts taken at age 65 (no deferral parameters here).
* Surplus after‑tax cash is reinvested in the non‑registered account.
* 2 % spending inflation.  40 % of non‑reg growth treated as taxable.

Complexity score = 3 (requires dual tax calculations each year).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from app.data_models.scenario import StrategyCodeEnum
from .base_strategy import BaseStrategy, EngineState, YearScratch
from app.services.strategy_engine import tax_rules
from app.services.strategy_engine.strategies.gradual_meltdown import (
    TOL,
    MAX_ITER,
    ASSUMED_INFLATION,
    TAXABLE_PORTION_NONREG_GROWTH,
)

class SpousalEqualizationStrategy(BaseStrategy):
    code = StrategyCodeEnum.SEQ
    complexity = 3

    # ------------------------------------------------------------------ #
    def run_year(self, idx: int, state: EngineState) -> None:
        if not self.scenario.spouse:
            # No spouse data → fall back to Gradual Meltdown goal‑seek behaviour
            from app.services.strategy_engine.strategies.gradual_meltdown import (
                GradualMeltdownStrategy,
            )

            fallback = GradualMeltdownStrategy(
                self.scenario, self.params, self.tax_loader
            )
            return fallback.run_year(idx, state)

        # ----------------------------------------------------------------
        # Setup / aliases
        # ----------------------------------------------------------------
        Yr = state.start_year + idx
        age_p = self.scenario.age + idx
        sp = self.scenario.spouse
        age_s = sp.age + idx
        td = self.tax_data(Yr)

        begin_rrif = state.balances["rrif"]
        begin_tfsa = state.balances["tfsa"]
        begin_non = state.balances["non_reg"]

        # younger age for RRIF minimum
        min_age = min(age_p, age_s)

        # ----------------------------------------------------------------
        # Streams: CPP / OAS / pension
        # ----------------------------------------------------------------
        cpp_p = Decimal(str(self.scenario.cpp_at_65)) if age_p >= 65 else Decimal("0")
        cpp_s = Decimal(str(sp.cpp_at_65)) if age_s >= 65 else Decimal("0")

        oas_p = Decimal(str(self.scenario.oas_at_65)) if age_p >= 65 else Decimal("0")
        oas_s = Decimal(str(sp.oas_at_65)) if age_s >= 65 else Decimal("0")

        db_p_p = Decimal(str(self.scenario.defined_benefit_pension))
        db_p_s = Decimal(str(sp.defined_benefit_pension))

        other_s = Decimal(str(sp.other_income))

        nonreg_growth = begin_non * Decimal(str(self.scenario.expect_return_pct / 100))
        taxable_nonreg_income = nonreg_growth * TAXABLE_PORTION_NONREG_GROWTH  # primary

        # ----------------------------------------------------------------
        # CRA minimum & goal‑seek withdrawal (household)
        # ----------------------------------------------------------------
        min_rrif = Decimal(
            str(
                tax_rules.get_rrif_min_withdrawal_amount(float(begin_rrif), min_age, td)
            )
        )
        low, high = min_rrif, begin_rrif

        spend_target = Decimal(str(self.scenario.desired_spending)) * (
            (Decimal("1") + ASSUMED_INFLATION) ** idx
        )

        def household_cash_after_tax(w: Decimal) -> Decimal:
            # split RRIF 50/50 for tax
            w_each = w / 2
            # -------------- primary spouse ------------------
            taxable_p = (
                w_each
                + cpp_p
                + oas_p
                + db_p_p
                + taxable_nonreg_income
            )
            elig_p = tax_rules.eligible_pension_income(
                age_p, float(w_each), float(db_p_p)
            )
            tax_p = tax_rules.calculate_all_taxes(
                float(taxable_p), age_p, float(elig_p), td
            )
            net_p = taxable_p - Decimal(
                str(tax_p["total_income_tax"] + tax_p["oas_clawback"])
            )
            # -------------- secondary spouse ----------------
            taxable_s = (
                w_each + cpp_s + oas_s + db_p_s + other_s
            )
            elig_s = tax_rules.eligible_pension_income(
                age_s, float(w_each), float(db_p_s)
            )
            tax_s = tax_rules.calculate_all_taxes(
                float(taxable_s), age_s, float(elig_s), td
            )
            net_s = taxable_s - Decimal(
                str(tax_s["total_income_tax"] + tax_s["oas_clawback"])
            )
            return net_p + net_s

        # binary search
        gross_rrif = low
        for _ in range(MAX_ITER):
            mid = (low + high) / 2
            cash = household_cash_after_tax(mid)
            if abs(cash - spend_target) <= TOL:
                gross_rrif = mid
                break
            if cash > spend_target:
                high = mid
            else:
                low = mid
        else:
            gross_rrif = high

        # ----------------------------------------------------------------
        # Final tax break‑down (need actual figures for YearScratch)
        # ----------------------------------------------------------------
        w_each = gross_rrif / 2
        taxable_p_final = (
            w_each + cpp_p + oas_p + db_p_p + taxable_nonreg_income
        )
        taxable_s_final = w_each + cpp_s + oas_s + db_p_s + other_s

        tax_p_final = tax_rules.calculate_all_taxes(
            float(taxable_p_final),
            age_p,
            float(tax_rules.eligible_pension_income(age_p, float(w_each), float(db_p_p))),
            td,
        )
        tax_s_final = tax_rules.calculate_all_taxes(
            float(taxable_s_final),
            age_s,
            float(tax_rules.eligible_pension_income(age_s, float(w_each), float(db_p_s))),
            td,
        )

        total_tax = Decimal(
            str(
                tax_p_final["total_income_tax"]
                + tax_s_final["total_income_tax"]
                + tax_p_final["oas_clawback"]
                + tax_s_final["oas_clawback"]
            )
        )

        after_tax_household = (
            taxable_p_final
            + taxable_s_final
            - total_tax
        )
        spending = min(after_tax_household, spend_target)
        surplus = after_tax_household - spending

        # ----------------------------------------------------------------
        # Grow balances
        # ----------------------------------------------------------------
        growth = Decimal("1") + Decimal(str(self.scenario.expect_return_pct / 100))
        end_rrif = (begin_rrif - gross_rrif) * growth
        end_tfsa = begin_tfsa * growth
        end_non = (begin_non + surplus + nonreg_growth) * growth

        # ----------------------------------------------------------------
        # Record
        # ----------------------------------------------------------------
        state.record(
            YearScratch(
                year=Yr,
                age=age_p,
                spouse_age=age_s,
                begin_rrif=begin_rrif,
                begin_tfsa=begin_tfsa,
                begin_non_reg=begin_non,
                gross_rrif=gross_rrif,
                cpp=cpp_p + cpp_s,
                oas_gross=oas_p + oas_s,
                db_pension=db_p_p + db_p_s,
                other_taxable_income=taxable_nonreg_income + other_s,
                taxable_income=taxable_p_final + taxable_s_final,
                fed_tax=tax_p_final["federal_tax"] + tax_s_final["federal_tax"],
                prov_tax=tax_p_final["provincial_tax"] + tax_s_final["provincial_tax"],
                oas_claw=tax_p_final["oas_clawback"] + tax_s_final["oas_clawback"],
                total_tax=float(total_tax),
                after_tax_income=after_tax_household,
                oas_net=(oas_p + oas_s)
                - Decimal(str(tax_p_final["oas_clawback"] + tax_s_final["oas_clawback"])),
                spending=spending,
                end_rrif=end_rrif,
                end_tfsa=end_tfsa,
                end_non_reg=end_non,
            )
        )

