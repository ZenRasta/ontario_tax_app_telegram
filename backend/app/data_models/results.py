# app/data_models/results.py
"""
Pydantic models for representing simulation results, both yearly and summary.

– YearlyResult: Detailed financial breakdown for each year of a simulation.
– SummaryMetrics: Aggregated key performance indicators for an entire strategy.
– MonteCarloPath: (Primarily internal) Represents a single path in a Monte Carlo simulation.
– SimulationResponse: Wrapper for /simulate endpoint response.
– ComparisonResponseItem & CompareResponse: Wrappers for /compare endpoint response.
"""
from __future__ import (
    annotations,  # Ensures type hints are treated as strings at definition time
)

from typing import (  # Dict, Any removed as not strictly needed in this version
    List,
    Optional,
)
from uuid import UUID

from pydantic import BaseModel, Field, confloat, conint

# Import StrategyCodeEnum from scenario.py
from app.data_models.scenario import StrategyCodeEnum

# --------------------------------------------------------------------------- #
# Yearly Simulation Result
# --------------------------------------------------------------------------- #

class TaxBreakdown(BaseModel):
    """Detailed breakdown of taxes paid in a given year."""
    federal_tax: confloat(ge=0) = Field(..., description="Federal income tax paid (CAD).")
    provincial_tax: confloat(ge=0) = Field(..., description="Provincial income tax paid (e.g., Ontario) (CAD).")
    oas_clawback_amount: confloat(ge=0) = Field(
        default=0.0, description="Amount of OAS benefit clawed back due to high income (CAD)."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "federal_tax": 15000.00,
                "provincial_tax": 7000.00,
                "oas_clawback_amount": 1200.00
            }
        }



class IncomeSources(BaseModel):
    """Detailed breakdown of income sources in a given year."""
    rrif_withdrawal: confloat(ge=0) = Field(..., description="Gross withdrawal from RRSP/RRIF (CAD).")
    cpp_received: confloat(ge=0) = Field(..., description="CPP benefits received (CAD).")
    oas_received_gross: confloat(ge=0) = Field(..., description="Gross OAS benefits received (before clawback) (CAD).")
    defined_benefit_pension: confloat(ge=0) = Field(..., description="Defined benefit pension income received (CAD).")
    other_taxable_income: confloat(ge=0) = Field(
        default=0.0, description="Other taxable income (e.g., from non-registered investments, part-time work) (CAD)."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "rrif_withdrawal": 30000.00,
                "cpp_received": 12000.00,
                "oas_received_gross": 8000.00,
                "defined_benefit_pension": 20000.00,
                "other_taxable_income": 5000.00
            }
        }


class YearlyResult(BaseModel):
    """Represents detailed financial outcomes for a single year of the projection."""
    year: conint(ge=2000, le=2150) = Field(..., description="Projection year (e.g., 2025).")
    age: conint(gt=0, lt=121) = Field(..., description="Client's age in that year.")
    spouse_age: Optional[conint(gt=0, lt=121)] = Field(default=None, description="Spouse's age in that year, if applicable.")

    begin_rrif_balance: confloat(ge=0) = Field(..., description="RRSP/RRIF portfolio balance at the start of the year (CAD).")
    begin_tfsa_balance: confloat(ge=0) = Field(..., description="TFSA balance at the start of the year (CAD).")
    begin_non_reg_balance: confloat(ge=0) = Field(
        default=0.0, description="Non-registered investment account balance at the start of the year (CAD)."
    )

    income_sources: IncomeSources = Field(..., description="Breakdown of various income sources for the year.")
    total_taxable_income: confloat(ge=0) = Field(..., description="Total taxable income for the year (CAD).")

    tax_breakdown: TaxBreakdown = Field(..., description="Detailed breakdown of taxes paid.")
    total_tax_paid: confloat(ge=0) = Field(..., description="Total income taxes paid (federal + provincial, including OAS clawback) (CAD).")

    # Changed type to float as per feedback
    after_tax_income: float = Field(
        ...,
        description="Total income after all taxes (CAD). May be negative in rare edge cases."
    )

    oas_net_received: confloat(ge=0) = Field(..., description="Net OAS benefit received (after recovery tax/clawback) (CAD).")

    actual_spending: confloat(ge=0) = Field(..., description="Actual after-tax spending achieved in the year (CAD).")

    end_rrif_balance: confloat(ge=0) = Field(..., description="RRSP/RRIF portfolio balance at the end of the year (CAD).")
    end_tfsa_balance: confloat(ge=0) = Field(..., description="TFSA balance at the end of the year (CAD).")
    end_non_reg_balance: confloat(ge=0) = Field(
        default=0.0, description="Non-registered investment account balance at the end of the year (CAD)."
    )

    marginal_tax_rate: Optional[confloat(ge=0, le=100)] = Field(
        default=None, description="Effective marginal tax rate on the last dollar of RRIF withdrawal (%)."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2025,
                "age": 65,
                "spouse_age": 63,
                "begin_rrif_balance": 500000.00,
                "begin_tfsa_balance": 100000.00,
                "begin_non_reg_balance": 50000.00,
                "income_sources": IncomeSources.Config.json_schema_extra["example"],
                "total_taxable_income": 75000.00,
                "tax_breakdown": TaxBreakdown.Config.json_schema_extra["example"],
                "total_tax_paid": 23200.00,
                "after_tax_income": 51800.00, # Example adjusted if it was negative
                "oas_net_received": 6800.00,
                "actual_spending": 60000.00,
                "end_rrif_balance": 485000.00,
                "end_tfsa_balance": 105000.00,
                "end_non_reg_balance": 52000.00,
                "marginal_tax_rate": 30.5
            }
        }

# --------------------------------------------------------------------------- #
# Summary Metrics for a Strategy
# --------------------------------------------------------------------------- #

class SummaryMetrics(BaseModel):
    """Aggregated key performance indicators over the entire projection for a single strategy."""
    # Tax Metrics
    lifetime_tax_paid_nominal: confloat(ge=0) = Field(..., description="Sum of all income taxes paid over the projection (nominal CAD).")
    lifetime_tax_paid_pv: confloat(ge=0) = Field(..., description="Present value of all income taxes paid (e.g., discounted at 2% real rate) (CAD).")
    average_effective_tax_rate: confloat(ge=0, le=100) = Field(..., description="Average effective tax rate over the projection (total tax / total taxable income) (%).")
    average_marginal_tax_rate_on_rrif: Optional[confloat(ge=0, le=100)] = Field(
        default=None, description="Weighted average marginal tax rate on RRIF/RRSP withdrawals (%)."
    )
    # Changed years_in_oas_clawback to conint as per feedback
    years_in_oas_clawback: conint(ge=0) = Field(..., description="Number of years where OAS clawback was applied.")
    total_oas_clawback_paid_nominal: confloat(ge=0) = Field(..., description="Total nominal amount of OAS benefits clawed back over the projection (CAD).")
    tax_volatility_score: Optional[confloat(ge=0)] = Field(
        default=None, description="Standard deviation (in percentage points) of year-to-year marginal tax rates."
    )

    # Spending & Sustainability Metrics
    max_sustainable_spending_pv: Optional[confloat(ge=0)] = Field(
        default=None, description="Maximum constant real spending level sustainable with a low ruin probability (e.g., <=5%) (PV CAD)."
    )
    average_annual_real_spending: confloat(ge=0) = Field(..., description="Average annual real (inflation-adjusted) spending achieved (CAD).")
    cashflow_coverage_ratio: Optional[confloat(ge=0)] = Field(
        default=None, description="Ratio of mean actual after-tax income to desired spending. (Mean actual after-tax income / desired spending)."
    )
    ruin_probability_pct: Optional[confloat(ge=0, le=100)] = Field(
        default=None, description="Monte Carlo probability of depleting all financial assets before end of projection (%)."
    )
    years_to_ruin_percentile_10: Optional[conint(ge=0)] = Field(
        default=None, description="In Monte Carlo, the 10th percentile of years until assets are depleted."
    )

    # Estate & Legacy Metrics
    final_total_portfolio_value_nominal: confloat(ge=0) = Field(
        ..., description="Total nominal value of all financial assets (RRSP/RRIF, TFSA, Non-reg) at the end of the projection (CAD)."
    )
    final_total_portfolio_value_pv: confloat(ge=0) = Field(
        ..., description="Present value of the final total portfolio (CAD)."
    )
    net_value_to_heirs_after_final_taxes_pv: confloat(ge=0) = Field(
        ..., description="Present value of the estate after all final taxes (including deemed disposition of RRSP/RRIF) (CAD)."
    )
    sequence_risk_score: Optional[confloat(ge=0)] = Field(
        default=None, description="Measure of sensitivity to poor market returns early in retirement (e.g., difference between median and 10th percentile terminal wealth)."
    )

    # Strategy Characteristics
    strategy_complexity_score: conint(ge=1, le=5) = Field(
        ..., description="Subjective score of strategy complexity (1=simple, 5=complex)."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "lifetime_tax_paid_nominal": 350000.00,
                "lifetime_tax_paid_pv": 280000.00,
                "average_effective_tax_rate": 25.5,
                "average_marginal_tax_rate_on_rrif": 30.2,
                "years_in_oas_clawback": 5, # Example now an int
                "total_oas_clawback_paid_nominal": 15000.00,
                "tax_volatility_score": 3.5,
                "max_sustainable_spending_pv": 55000.00,
                "average_annual_real_spending": 58000.00,
                "cashflow_coverage_ratio": 1.02,
                "ruin_probability_pct": 4.0,
                "years_to_ruin_percentile_10": 22,
                "final_total_portfolio_value_nominal": 250000.00,
                "final_total_portfolio_value_pv": 150000.00,
                "net_value_to_heirs_after_final_taxes_pv": 120000.00,
                "sequence_risk_score": 75000.00,
                "strategy_complexity_score": 2
            }
        }

# --------------------------------------------------------------------------- #
# Monte Carlo Path (Internal/Detailed Analysis)
# --------------------------------------------------------------------------- #

class MonteCarloPath(BaseModel):
    """
    Represents data for a single trial in a Monte Carlo simulation.
    Primarily for internal analysis or detailed views, not typically returned in full for all trials.
    """
    trial_id: conint(ge=0) = Field(..., description="Index of the Monte Carlo simulation run.")
    yearly_portfolio_values: List[confloat(ge=0)] = Field(
        ..., description="Array of end-of-year total portfolio values for this trial."
    )
    yearly_rrif_values: List[confloat(ge=0)] = Field(
        ..., description="Array of end-of-year RRSP/RRIF values for this trial."
    )
    yearly_net_withdrawals: List[confloat(ge=0)] = Field(
        ..., description="Array of annual net (after-tax) withdrawals/spending for this trial."
    )
    ruined_in_year: Optional[conint(ge=0)] = Field(
        default=None, description="Year number (offset from start) in which assets were depleted, if applicable."
    )
    final_portfolio_value: confloat(ge=0) = Field(
        ..., description="Terminal portfolio value at the end of the projection for this trial."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "trial_id": 1,
                "yearly_portfolio_values": [600000.00, 610000.00, 580000.00], # Shortened for brevity
                "yearly_rrif_values": [480000.00, 470000.00, 450000.00], # Shortened
                "yearly_net_withdrawals": [60000.00, 60000.00, 60000.00], # Shortened
                "ruined_in_year": None,
                "final_portfolio_value": 350000.00
            }
        }

# ────────────────────────────────────────────────────────────────────────────
# LIGHT-WEIGHT SUMMARY FOR THE NEW REACT COMPARISON TABLE
# ────────────────────────────────────────────────────────────────────────────
class YearlyBalance(BaseModel):
    year: int
    portfolio_end: confloat(ge=0)

class ResultSummary(BaseModel):
    """
    Minimal payload sent back when the wizard calls /simulate.
    """
    strategy_code: StrategyCodeEnum
    strategy_name: str
    total_taxes: confloat(ge=0)
    total_spending: confloat(ge=0)
    final_estate: confloat(ge=0)
    yearly_balances: List[YearlyBalance] = []


# --------------------------------------------------------------------------- #
# API Response Wrappers for Simulation Results
# --------------------------------------------------------------------------- #

class SimulationResponse(BaseModel):
    """Response for the /simulate endpoint (single strategy)."""
    strategy_code: StrategyCodeEnum # Typed with imported enum
    strategy_name: str = Field(..., description="Full human-readable name of the strategy.")

    yearly_results: List[YearlyResult] = Field(
        ..., description="List of detailed results for each year of the projection."
    )
    summary: SummaryMetrics = Field(..., description="Aggregated summary metrics for the entire strategy.")
    request_id: UUID = Field(..., description="Unique ID for the simulation request, for tracing.")

    class Config:
        use_enum_values = True # Ensures enum values are used in serialization
        json_schema_extra = {
            "example": {
                "strategy_code": "GM", # Will be serialized as string "GM"
                "strategy_name": "Gradual Meltdown",
                "yearly_results": [YearlyResult.Config.json_schema_extra["example"]],
                "summary": SummaryMetrics.Config.json_schema_extra["example"],
                "request_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
            }
        }


class ComparisonResponseItem(BaseModel):
    """Represents the results for a single strategy within a /compare response."""
    strategy_code: StrategyCodeEnum # Typed with imported enum
    strategy_name: str = Field(..., description="Full human-readable name of the strategy.")

    yearly_results: List[YearlyResult] = Field(
        ..., description="List of detailed results for each year of the projection."
    )
    summary: SummaryMetrics = Field(..., description="Aggregated summary metrics for the entire strategy.")

    class Config:
        use_enum_values = True # Ensures enum values are used in serialization
        json_schema_extra = {
            "example": {
                "strategy_code": "GM",
                "strategy_name": "Gradual Meltdown",
                "yearly_results": [YearlyResult.Config.json_schema_extra["example"]],
                "summary": SummaryMetrics.Config.json_schema_extra["example"]
            }
        }

class CompareResponse(BaseModel):
    """Response for the /compare endpoint (multiple strategies)."""
    comparisons: List[ComparisonResponseItem] = Field(
        ..., description="List of results for each compared strategy."
    )
    request_id: UUID = Field(..., description="Unique ID for the comparison request, for tracing.")

    class Config:
        json_schema_extra = {
            "example": {
                "comparisons": [ComparisonResponseItem.Config.json_schema_extra["example"]],
                "request_id": "f1e2d3c4-b5a6-0987-4321-fedcba098765"
            }
        }
