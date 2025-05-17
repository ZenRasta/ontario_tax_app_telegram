# app/services/strategy_engine/tax_rules.py
"""
Core Canadian tax helpers: RRIF minimums, OAS clawback, CPP/OAS deferral
adjustments, federal + Ontario tax (including surtax) and related credits.

The module expects a dict loaded from `data/tax_years.yml`
to be passed in (or imported via a loader) as `TaxYearData`.
"""

from __future__ import annotations

from typing import List, Tuple, TypedDict

# --------------------------------------------------------------------------- #
# Typed‑dicts describing the YAML structure
# --------------------------------------------------------------------------- #


class TaxBracket(TypedDict):
    upto: float | None  # None ⇒ top bracket
    rate: float         # e.g. 0.150 for 15 %


class TaxYearData(TypedDict, total=False):
    # --- federal ---
    federal_personal_amount: float
    federal_age_amount: float
    federal_age_amount_threshold: float
    federal_pension_income_credit_max: float
    federal_tax_brackets: List[TaxBracket]

    # --- OAS ---
    oas_clawback_threshold: float
    oas_clawback_rate: float            # usually 0.15
    oas_max_benefit_at_65: float
    oas_deferral_factor_per_month: float  # 0.006

    # --- CPP ---
    cpp_max_benefit_at_65: float
    cpp_deferral_factor_per_year: float   # +7 % per year (0.07)
    cpp_early_factor_per_year: float      # –7.2 % per year (0.072)

    # --- RRIF ---
    rrif_table: dict[int, float]          # { age: factor }

    # --- Ontario ---
    ontario_personal_amount: float
    ontario_age_amount: float
    ontario_age_amount_threshold: float
    ontario_pension_income_credit_max: float
    ontario_tax_brackets: List[TaxBracket]
    ontario_surtax_threshold_1: float
    ontario_surtax_rate_1: float
    ontario_surtax_threshold_2: float
    ontario_surtax_rate_2: float


# --------------------------------------------------------------------------- #
# RRIF minimum factors
# --------------------------------------------------------------------------- #


def calculate_rrif_minimum_withdrawal_factor(
    age: int, rrif_table: dict[int, float] | None = None
) -> float:
    """
    Returns CRA‑prescribed RRIF factor.
    • If a table is supplied in TaxYearData, use it for age ≥ 71.
    • Otherwise fallback to 1/(90‑age) (planning‑grade simplification).
    """
    if age <= 0:
        return 0.0

    # Use supplied table first
    if rrif_table and age in rrif_table:
        return rrif_table[age]

    # Planning‑grade approximation
    if age < 55:
        return 0.0
    if age >= 95:
        return 0.20  # CRA caps at 20 % age 95+
    return 1.0 / (90.0 - age)


def get_rrif_min_withdrawal_amount(fmv: float, age: int, tax_data: TaxYearData) -> float:
    """FMV × factor."""
    factor = calculate_rrif_minimum_withdrawal_factor(age, tax_data.get("rrif_table"))
    return max(0.0, fmv * factor)


# --------------------------------------------------------------------------- #
# OAS clawback
# --------------------------------------------------------------------------- #


def calculate_oas_clawback(income: float, td: TaxYearData) -> float:
    thresh = td["oas_clawback_threshold"]
    if income <= thresh:
        return 0.0
    claw = (income - thresh) * td["oas_clawback_rate"]
    return min(claw, td["oas_max_benefit_at_65"])


# --------------------------------------------------------------------------- #
# CPP / OAS benefit adjustments
# --------------------------------------------------------------------------- #


def get_adjusted_cpp_benefit(cpp65: float, start_age: int, td: TaxYearData) -> float:
    if start_age == 65:
        return cpp65
    diff = start_age - 65
    if diff > 0:
        factor = 1 + diff * td.get("cpp_deferral_factor_per_year", 0.07)
    else:
        factor = 1 + diff * -td.get("cpp_early_factor_per_year", 0.072)  # diff negative
    return cpp65 * factor


def get_adjusted_oas_benefit(oas65: float, start_age: int, td: TaxYearData) -> float:
    if start_age <= 65:
        return oas65
    months = min((start_age - 65) * 12, 60)  # cap 5 yrs
    factor = 1 + months * td.get("oas_deferral_factor_per_month", 0.006)
    return oas65 * factor


# --------------------------------------------------------------------------- #
# Generic bracket tax helper
# --------------------------------------------------------------------------- #


def _tax_from_brackets(income: float, brackets: List[TaxBracket]) -> float:
    tax = 0.0
    last_cap = 0.0
    for b in brackets:
        cap = b["upto"] or income
        if income <= last_cap:
            break
        span = min(income, cap) - last_cap
        tax += span * b["rate"]
        last_cap = cap
    return max(0.0, tax)


# --------------------------------------------------------------------------- #
# Non‑refundable credit helpers
# --------------------------------------------------------------------------- #


def _federal_credits(income: float, age: int, pension_inc: float, td: TaxYearData) -> float:
    lowest_rate = td["federal_tax_brackets"][0]["rate"]
    credit_base = td["federal_personal_amount"]

    if age >= 65:
        reduction = max(0.0, (income - td["federal_age_amount_threshold"]) * 0.15)
        credit_base += max(0.0, td["federal_age_amount"] - reduction)

    credit_base += min(pension_inc, td["federal_pension_income_credit_max"])
    return credit_base * lowest_rate


def _ontario_credits(income: float, age: int, pension_inc: float, td: TaxYearData) -> float:
    lowest_rate = td["ontario_tax_brackets"][0]["rate"]
    credit_base = td["ontario_personal_amount"]

    if age >= 65:
        reduction = max(0.0, (income - td["ontario_age_amount_threshold"]) * 0.05)
        credit_base += max(0.0, td["ontario_age_amount"] - reduction)

    credit_base += min(pension_inc, td["ontario_pension_income_credit_max"])
    return credit_base * lowest_rate


# --------------------------------------------------------------------------- #
# Federal & Ontario tax
# --------------------------------------------------------------------------- #


def calculate_federal_tax(
    income: float, age: int, pension_inc: float, td: TaxYearData
) -> float:
    if income <= 0:
        return 0.0
    gross = _tax_from_brackets(income, td["federal_tax_brackets"])
    return max(0.0, gross - _federal_credits(income, age, pension_inc, td))


def calculate_ontario_tax(
    income: float, age: int, pension_inc: float, td: TaxYearData
) -> Tuple[float, float]:
    if income <= 0:
        return 0.0, 0.0
    gross = _tax_from_brackets(income, td["ontario_tax_brackets"])
    net_before_surtax = max(0.0, gross - _ontario_credits(income, age, pension_inc, td))

    s1_thr, s2_thr = td["ontario_surtax_threshold_1"], td["ontario_surtax_threshold_2"]
    surtax = 0.0
    if net_before_surtax > s1_thr:
        surtax += (min(net_before_surtax, s2_thr) - s1_thr) * td["ontario_surtax_rate_1"]
    if net_before_surtax > s2_thr:
        surtax += (net_before_surtax - s2_thr) * td["ontario_surtax_rate_2"]

    return net_before_surtax + surtax, surtax


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #


class TaxCalculationResult(TypedDict):
    federal_tax: float
    provincial_tax: float
    provincial_surtax: float
    total_income_tax: float
    oas_clawback: float


def calculate_all_taxes(
    income: float,
    age: int,
    pension_inc: float,
    td: TaxYearData,
    province: str = "ON",
) -> TaxCalculationResult:
    if province != "ON":
        raise NotImplementedError("Only Ontario implemented.")

    oas_claw = calculate_oas_clawback(income, td)
    fed = calculate_federal_tax(income, age, pension_inc, td)
    prov, surtax = calculate_ontario_tax(income, age, pension_inc, td)

    return {
        "federal_tax": fed,
        "provincial_tax": prov,
        "provincial_surtax": surtax,
        "total_income_tax": fed + prov,
        "oas_clawback": oas_claw,
    }


# --------------------------------------------------------------------------- #
# Pension‑income credit eligibility helper
# --------------------------------------------------------------------------- #


def eligible_pension_income(age: int, rrif_withdrawal: float, db_pension: float) -> float:
    """RRIF income qualifies for the credit at 65+."""
    return db_pension + (rrif_withdrawal if age >= 65 else 0.0)

