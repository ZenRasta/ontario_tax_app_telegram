import { render, screen, waitFor } from '@testing-library/react';
import ResultsPage from './ResultsPage';
import DOMPurify from 'dompurify';
import type { ComparisonResponseItem, ScenarioInput } from '../types/api';

jest.mock('dompurify', () => ({
  __esModule: true,
  default: { sanitize: jest.fn(() => 'cleaned') }
}));

const summary = {
  lifetime_tax_paid_nominal: 0,
  lifetime_tax_paid_pv: 0,
  average_effective_tax_rate: 0,
  years_in_oas_clawback: 0,
  total_oas_clawback_paid_nominal: 0,
  average_annual_real_spending: 0,
  final_total_portfolio_value_nominal: 0,
  final_total_portfolio_value_pv: 0,
  net_value_to_heirs_after_final_taxes_pv: 0,
  strategy_complexity_score: 0,
};

const result: ComparisonResponseItem = {
  strategy_code: 'T',
  strategy_name: 'Test',
  summary,
  total_taxes: 0,
  total_spending: 0,
  final_estate: 0,
};

const scenario: ScenarioInput = {
  age: 65,
  rrsp_balance: 0,
  tfsa_balance: 0,
  cpp_at_65: 0,
  oas_at_65: 0,
  desired_spending: 0,
  expect_return_pct: 0,
  stddev_return_pct: 0,
  life_expectancy_years: 30,
  province: 'ON',
  goal: 'minimize_tax',
};

beforeEach(() => {
  (DOMPurify.sanitize as jest.Mock).mockClear();
});

test('sanitizes explanation HTML before rendering', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ explanation: '<script>alert(1)</script>' }),
  }) as jest.Mock;

  render(
    <ResultsPage
      goal="Minimize Tax"
      strategies={[result.strategy_code]}
      horizon={30}
      results={[result]}
      scenario={scenario}
      onBack={() => {}}
      onStartOver={() => {}}
    />,
  );

  await waitFor(() => {
    expect(DOMPurify.sanitize).toHaveBeenCalledWith('<script>alert(1)</script>');
  });

  expect(screen.getByText('cleaned')).toBeInTheDocument();
});
