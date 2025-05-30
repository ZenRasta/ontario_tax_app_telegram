export interface SpouseInfo {
  age: number;
  rrsp_balance: number;
  other_income?: number;
  cpp_at_65?: number;
  oas_at_65?: number;
  tfsa_balance?: number;
  defined_benefit_pension?: number;
}

export interface StrategyParamsInput {
  bracket_fill_ceiling?: number;
  lump_sum_amount?: number;
  lump_sum_year_offset?: number;
  target_depletion_age?: number;
  cpp_start_age?: number;
  oas_start_age?: number;
  loan_interest_rate_pct?: number;
  loan_amount_as_pct_of_rrif?: number;
  spouse?: SpouseInfo;
}


export type GoalEnum =
  | 'minimize_tax'
  | 'maximize_spending'
  | 'preserve_estate'
  | 'simplify';

export interface StrategyMeta {
  code: string;
  label: string;
  blurb: string;
  default_complexity: number;
  typical_goals: string[];
}

export interface StrategiesResponse {
  strategies: StrategyMeta[];
  recommended: string[];
}

export interface SummaryMetrics {
  lifetime_tax_paid_nominal: number;
  lifetime_tax_paid_pv: number;
  average_effective_tax_rate: number;
  average_marginal_tax_rate_on_rrif?: number | null;
  years_in_oas_clawback: number;
  total_oas_clawback_paid_nominal: number;
  tax_volatility_score?: number | null;
  max_sustainable_spending_pv?: number | null;
  average_annual_real_spending: number;
  cashflow_coverage_ratio?: number | null;
  ruin_probability_pct?: number | null;
  years_to_ruin_percentile_10?: number | null;
  final_total_portfolio_value_nominal: number;
  final_total_portfolio_value_pv: number;
  net_value_to_heirs_after_final_taxes_pv: number;
  sequence_risk_score?: number | null;
  strategy_complexity_score: number;
}

export interface ComparisonResponseItem {
  strategy_code: string;
  strategy_name: string;
  yearly_results?: unknown[]; // YearlyResult not yet typed
  yearly_balances?: { year: number; portfolio_end: number }[];
  summary: SummaryMetrics;
  total_taxes?: number;
  total_spending?: number;
  final_estate?: number;
}

