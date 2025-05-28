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
  // Determine recommended best strategy based on goal
  const recommended = useMemo(() => {
    if (!results || results.length === 0) return null;
    let bestStrategy = results[0];
    if (goal === 'Minimize Tax') {
      results.forEach(res => {
        if (res.totalTaxes < bestStrategy.totalTaxes) bestStrategy = res;
      });
    } else if (goal === 'Maximize Spending') {
      results.forEach(res => {
        if (res.totalSpending > bestStrategy.totalSpending) bestStrategy = res;
      });
    } else if (goal === 'Preserve Estate') {
      results.forEach(res => {
        if (res.finalEstate > bestStrategy.finalEstate) bestStrategy = res;
      });
    } else if (goal === 'Simplify') {
      // For "Simplify", choose the strategy with the fewest interventions (we assume that's the one with minimal strategies or baseline)
      // Here, as a proxy, pick the one with the lowest totalTaxes (or we could choose a specific baseline strategy if present).
      results.forEach(res => {
        if (res.strategyName === 'RRIF Minimums Only') {
          bestStrategy = res;
        }
      });
    }
    return bestStrategy;
  }, [goal, results]);

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        4. Results & Recommendation
      </Typography>
      {recommended && (
        <Typography variant="h5" color="primary" gutterBottom>
          Recommended Strategy: <strong>{recommended.strategyName}</strong>
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
          {results.map((res: any) => (
            <TableRow key={res.strategyCode} 
              selected={recommended && res.strategyName === recommended.strategyName}
              sx={{ bgcolor: recommended && res.strategyName === recommended.strategyName ? 'action.hover' : 'inherit' }}
            >
              <TableCell>{res.strategyName}</TableCell>
              <TableCell align="right">${res.totalTaxes.toLocaleString()}</TableCell>
              <TableCell align="right">${res.totalSpending.toLocaleString()}</TableCell>
              <TableCell align="right">${res.finalEstate.toLocaleString()}</TableCell>
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
        {/* results.map(res => <StrategyChart key={res.strategyCode} data={res.yearlyBalances} title={res.strategyName} />) */}
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

