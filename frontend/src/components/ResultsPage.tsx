import React, { useMemo } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableHead, TableRow, Button } from '@mui/material';

interface ResultsPageProps {
  goal: string;
  strategies: string[];
  results: any[];  // array of result objects for each strategy
  onBack: () => void;
  onStartOver: () => void;
}

const ResultsPage: React.FC<ResultsPageProps> = ({ goal, strategies, results, onBack, onStartOver }) => {
  // Normalize result metrics so the rest of the component can rely on them
  const processedResults = useMemo(() =>
    results.map((res) => {
      const totalTaxes =
        res.total_taxes ?? res.summary?.lifetime_tax_paid_nominal ?? null;
      const totalSpending =
        res.total_spending ?? res.summary?.average_annual_real_spending ?? null;
      const finalEstate =
        res.final_estate ??
        res.summary?.net_value_to_heirs_after_final_taxes_pv ??
        res.summary?.final_total_portfolio_value_nominal ??
        null;

      return { ...res, totalTaxes, totalSpending, finalEstate };
    }),
  [results]);

  // Determine recommended best strategy based on goal
  const recommended = useMemo(() => {
    if (!processedResults || processedResults.length === 0) return null;
    let bestStrategy = processedResults[0];
    if (goal === 'Minimize Tax') {
      processedResults.forEach((res) => {
        if (
          res.totalTaxes !== null &&
          (bestStrategy.totalTaxes === null || res.totalTaxes < bestStrategy.totalTaxes)
        ) {
          bestStrategy = res;
        }
      });
    } else if (goal === 'Maximize Spending') {
      processedResults.forEach((res) => {
        if (
          res.totalSpending !== null &&
          (bestStrategy.totalSpending === null ||
            res.totalSpending > bestStrategy.totalSpending)
        ) {
          bestStrategy = res;
        }
      });
    } else if (goal === 'Preserve Estate') {
      processedResults.forEach((res) => {
        if (
          res.finalEstate !== null &&
          (bestStrategy.finalEstate === null || res.finalEstate > bestStrategy.finalEstate)
        ) {
          bestStrategy = res;
        }
      });
    } else if (goal === 'Simplify') {
      // For "Simplify", choose the strategy with the fewest interventions (we assume that's the one with minimal strategies or baseline)
      // Here, as a proxy, pick the one with the strategy name "RRIF Minimums Only" if present.
      processedResults.forEach((res) => {
        if (res.strategy_name === 'RRIF Minimums Only') {
          bestStrategy = res;
        }
      });
    }
    return bestStrategy;
  }, [goal, processedResults]);

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        4. Results & Recommendation
      </Typography>
        {recommended && (
          <Typography variant="h5" color="primary" gutterBottom>
            Recommended Strategy: <strong>{recommended.strategy_name}</strong>
          </Typography>
        )}
      <Typography variant="body1" gutterBottom>
        Based on your goal (<em>{goal}</em>), the strategy above is projected to perform the best among those selected.
      </Typography>

      {/* Comparison Table for selected strategies */}
      <Table size="small" sx={{ my: 2 }}>
        <TableHead>
          <TableRow>
            <TableCell>Strategy</TableCell>
            <TableCell align="right">Total Taxes Paid</TableCell>
            <TableCell align="right">Total Spending</TableCell>
            <TableCell align="right">Final Estate Value</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {processedResults.map((res: any) => (
            <TableRow
              key={res.strategy_code}
              selected={
                recommended && res.strategy_name === recommended.strategy_name
              }
              sx={{
                bgcolor:
                  recommended && res.strategy_name === recommended.strategy_name
                    ? 'action.hover'
                    : 'inherit',
              }}
            >
              <TableCell>{res.strategy_name}</TableCell>
              <TableCell align="right">
                {res.totalTaxes !== null ? `$${res.totalTaxes.toLocaleString()}` : '—'}
              </TableCell>
              <TableCell align="right">
                {res.totalSpending !== null ? `$${res.totalSpending.toLocaleString()}` : '—'}
              </TableCell>
              <TableCell align="right">
                {res.finalEstate !== null ? `$${res.finalEstate.toLocaleString()}` : '—'}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* Placeholder for visuals (charts) */}
      <Box my={3}>
        <Typography variant="subtitle1">Strategy Outcomes Visualized:</Typography>
        {/* For each strategy, we could include a chart (e.g., portfolio value over time, spending over time, etc.) */}
        {/* For brevity, actual chart implementation is omitted. In practice, use a chart library (like recharts or Chart.js) to plot results. */}
        {/* Example placeholder: */}
        {/* results.map(res => <StrategyChart key={res.strategy_code} data={res.yearly_balances} title={res.strategy_name} />) */}
      </Box>

      {/* Navigation Buttons */}
      <Box mt={2} textAlign="right">
        <Button variant="outlined" onClick={onBack} sx={{ mr: 2 }}>
          Back
        </Button>
        <Button variant="contained" color="primary" onClick={onStartOver}>
          Start Over
        </Button>
      </Box>
    </Box>
  );
};

export default ResultsPage;

