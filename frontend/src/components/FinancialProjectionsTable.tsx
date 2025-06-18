import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
  Box,
} from '@mui/material';
import type { ComparisonResponseItem } from '../types/api';

const currencyFormatter = new Intl.NumberFormat('en-CA', {
  style: 'currency',
  currency: 'CAD',
  maximumFractionDigits: 0,
});

interface FinancialProjectionsTableProps {
  strategy: ComparisonResponseItem;
  maxYears?: number;
}

const FinancialProjectionsTable: React.FC<FinancialProjectionsTableProps> = ({
  strategy,
  maxYears = 10,
}) => {
  const yearlyResults = strategy.yearly_results?.slice(0, maxYears) || [];

  if (!yearlyResults.length) {
    return (
      <Box my={2}>
        <Typography variant="body2" color="text.secondary">
          Detailed yearly projections are not available for this strategy.
        </Typography>
      </Box>
    );
  }

  return (
    <Box my={3}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: '#1976d2' }}>
        Financial Projections - First {Math.min(maxYears, yearlyResults.length)} Years
      </Typography>
      <Box sx={{ overflowX: 'auto' }}>
        <Table 
          size="small" 
          sx={{ 
            minWidth: 800,
            '& .MuiTableCell-head': {
              backgroundColor: '#f5f5f5',
              fontWeight: 600,
              fontSize: '0.875rem',
              borderBottom: '2px solid #e0e0e0',
            },
            '& .MuiTableCell-body': {
              fontSize: '0.8125rem',
              borderBottom: '1px solid #e0e0e0',
            },
            '& .MuiTableRow-root:nth-of-type(even)': {
              backgroundColor: '#fafafa',
            },
          }}
          className="financial-projections-table"
        >
          <TableHead>
            <TableRow>
              <TableCell>Year</TableCell>
              <TableCell>Age</TableCell>
              <TableCell align="right">Pension</TableCell>
              <TableCell align="right">CPP</TableCell>
              <TableCell align="right">OAS</TableCell>
              <TableCell align="right">RRIF WD</TableCell>
              <TableCell align="right">Total Inc</TableCell>
              <TableCell align="right">Tax Payable</TableCell>
              <TableCell align="right">Net Cash</TableCell>
              <TableCell align="right">End RRIF</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {yearlyResults.map((year: any) => (
              <TableRow key={year.year}>
                <TableCell sx={{ fontWeight: 500 }}>{year.year}</TableCell>
                <TableCell>{year.age}</TableCell>
                <TableCell align="right">
                  {year.income_sources?.defined_benefit_pension 
                    ? currencyFormatter.format(year.income_sources.defined_benefit_pension)
                    : '—'
                  }
                </TableCell>
                <TableCell align="right">
                  {year.income_sources?.cpp_received 
                    ? currencyFormatter.format(year.income_sources.cpp_received)
                    : '—'
                  }
                </TableCell>
                <TableCell align="right">
                  {year.oas_net_received 
                    ? currencyFormatter.format(year.oas_net_received)
                    : '—'
                  }
                </TableCell>
                <TableCell align="right">
                  {year.income_sources?.rrif_withdrawal 
                    ? currencyFormatter.format(year.income_sources.rrif_withdrawal)
                    : '—'
                  }
                </TableCell>
                <TableCell align="right" sx={{ fontWeight: 500 }}>
                  {currencyFormatter.format(year.total_taxable_income)}
                </TableCell>
                <TableCell align="right" sx={{ color: '#d32f2f' }}>
                  {currencyFormatter.format(year.total_tax_paid)}
                </TableCell>
                <TableCell align="right" sx={{ fontWeight: 500, color: '#2e7d32' }}>
                  {currencyFormatter.format(year.after_tax_income)}
                </TableCell>
                <TableCell align="right">
                  {currencyFormatter.format(year.end_rrif_balance)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Box>
      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
        * Amounts shown in Canadian dollars. Projections are estimates based on current assumptions.
      </Typography>
    </Box>
  );
};

export default FinancialProjectionsTable;
