export interface StrategyParamsInput {
  bracket_fill_ceiling?: number;
  rrif_conversion_age?: number;
  cpp_start_age?: number;
  oas_start_age?: number;
  target_depletion_age?: number;
  lump_sum_year_offset?: number;
  lump_sum_amount?: number;
  loan_interest_rate_pct?: number;
  loan_amount_as_pct_of_rrif?: number;
}

export type GoalEnum =
  | 'minimize_tax'
  | 'maximize_spending'
  | 'preserve_estate'
  | 'simplify';

export interface ScenarioInput {
  age: number;
  rrsp_balance: number;
  defined_benefit_pension: number;
  cpp_at_65: number;
  oas_at_65: number;
  tfsa_balance: number;
  desired_spending: number;
  expect_return_pct: number;
  stddev_return_pct: number;
  life_expectancy_years: number;
  province: string;
  goal: GoalEnum;
  spouse?: {
    age: number;
    rrsp_balance: number;
    other_income: number;
    cpp_at_65: number;
    oas_at_65: number;
    tfsa_balance: number;
    defined_benefit_pension: number;
  };
  params?: StrategyParamsInput;
}

export interface SimulateRequest {
  scenario: ScenarioInput;
  strategy_code: string;
}
