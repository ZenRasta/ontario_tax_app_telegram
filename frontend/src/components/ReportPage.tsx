import React, { useRef } from 'react';
import DOMPurify from 'dompurify';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Button,
} from '@mui/material';
import { useReactToPrint } from 'react-to-print';
import StrategyChart from './StrategyChart';
import type { ComparisonResponseItem, ExplainResponse } from '../types/api';

const currencyFormatter = new Intl.NumberFormat('en-CA', {
  style: 'currency',
  currency: 'CAD',
  maximumFractionDigits: 0,
});

interface ReportPageProps {
  goal: string;
  horizon: number;
  results: ComparisonResponseItem[];
  explanation: ExplainResponse | null;
  onBack: () => void;
  onStartOver: () => void;
}

const ReportPage: React.FC<ReportPageProps> = ({
  goal,
  horizon,
  results,
  explanation,
  onBack,
  onStartOver,
}) => {
  const componentRef = useRef<HTMLDivElement>(null);
  const handlePrint = useReactToPrint({ content: () => componentRef.current });

  const processedResults = results.map((res) => ({
    ...res,
    totalTaxes: res.total_taxes ?? res.summary?.lifetime_tax_paid_nominal ?? null,
    totalSpending:
      res.total_spending ?? res.summary?.average_annual_real_spending ?? null,
    finalEstate:
      res.final_estate ??
      res.summary?.net_value_to_heirs_after_final_taxes_pv ??
      res.summary?.final_total_portfolio_value_nominal ??
      null,
  }));

  const recommended = processedResults.reduce((best, res) => {
    if (!best) return res;
    if (goal === 'Minimize Tax') {
      if (
        res.totalTaxes !== null &&
        (best.totalTaxes === null || res.totalTaxes < best.totalTaxes)
      ) {
        return res;
      }
    } else if (goal === 'Maximize Spending') {
      if (
        res.totalSpending !== null &&
        (best.totalSpending === null || res.totalSpending > best.totalSpending)
      ) {
        return res;
      }
    } else if (goal === 'Preserve Estate') {
      if (
        res.finalEstate !== null &&
        (best.finalEstate === null || res.finalEstate > best.finalEstate)
      ) {
        return res;
      }
    } else if (goal === 'Simplify') {
      if (res.strategy_name === 'RRIF Minimums Only') return res;
    }
    return best;
  }, processedResults[0]);

  return (
    <Box>
      <div ref={componentRef} className="print:p-0">
        <Typography variant="h4" gutterBottom align="center">
          Retirement Strategy Report
        </Typography>
        {recommended && (
          <Typography variant="h5" gutterBottom>
            Recommended Strategy: <strong>{recommended.strategy_name}</strong>
          </Typography>
        )}
        {explanation && (
          <>
            <section className="my-4">
              <Typography variant="h6" gutterBottom>
                Summary
              </Typography>
              <Typography
                variant="body1"
                dangerouslySetInnerHTML={{
                  __html: DOMPurify.sanitize(explanation.summary),
                }}
              />
            </section>
            <section className="my-4">
              <Typography variant="h6" gutterBottom>
                Key Outcomes
              </Typography>
              <ul className="list-disc pl-5">
                {explanation.key_outcomes.map((o, idx) => (
                  <li key={idx}>{o}</li>
                ))}
              </ul>
            </section>
            <section className="my-4">
              <Typography variant="h6" gutterBottom>
                Recommendations
              </Typography>
              <Typography
                variant="body1"
                dangerouslySetInnerHTML={{
                  __html: DOMPurify.sanitize(explanation.recommendations),
                }}
              />
            </section>
          </>
        )}
        <section className="my-4">
          <Typography variant="h6" gutterBottom>
            Projection Horizon: {horizon} years
          </Typography>
          <Table size="small" sx={{ my: 2 }} className="w-full report-table">
            <TableHead>
              <TableRow>
                <TableCell>Strategy</TableCell>
                <TableCell align="right">Total Taxes Paid</TableCell>
                <TableCell align="right">Total Spending</TableCell>
                <TableCell align="right">Final Estate Value</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {processedResults.map((res) => (
                <TableRow key={res.strategy_code}>
                  <TableCell>{res.strategy_name}</TableCell>
                  <TableCell align="right">
                    {res.totalTaxes !== null
                      ? currencyFormatter.format(res.totalTaxes)
                      : '—'}
                  </TableCell>
                  <TableCell align="right">
                    {res.totalSpending !== null
                      ? currencyFormatter.format(res.totalSpending)
                      : '—'}
                  </TableCell>
                  <TableCell align="right">
                    {res.finalEstate !== null
                      ? currencyFormatter.format(res.finalEstate)
                      : '—'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </section>
        <section className="my-4">
          {processedResults.map((res) => (
            <StrategyChart
              key={res.strategy_code}
              title={res.strategy_name}
              data={res.yearly_balances || []}
            />
          ))}
        </section>
      </div>
      <Box mt={2} textAlign="right" className="no-print">
        <Button variant="outlined" onClick={onBack} sx={{ mr: 2 }}>
          Back
        </Button>
        <Button variant="contained" onClick={handlePrint} sx={{ mr: 2 }}>
          Export PDF
        </Button>
        <Button variant="contained" color="primary" onClick={onStartOver}>
          Start Over
        </Button>
      </Box>
    </Box>
  );
};

export default ReportPage;
