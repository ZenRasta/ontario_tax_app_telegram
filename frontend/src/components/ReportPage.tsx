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
  Paper,
  Divider,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import StrategyChart from './StrategyChart';
import FinancialProjectionsTable from './FinancialProjectionsTable';
import type { ComparisonResponseItem, ExplainResponse } from '../types/api';

const currencyFormatter = new Intl.NumberFormat('en-CA', {
  style: 'currency',
  currency: 'CAD',
  maximumFractionDigits: 0,
});

const percentFormatter = new Intl.NumberFormat('en-CA', {
  style: 'percent',
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

type ProcessedResult = ComparisonResponseItem & {
  totalTaxes: number | null;
  totalSpending: number | null;
  finalEstate: number | null;
};

interface ReportPageProps {
  goal: string;
  horizon: number;
  results: ProcessedResult[];
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
  const handlePrint = async () => {
    if (!componentRef.current) return;

    try {
      // Show loading state
      const button = document.querySelector('[data-pdf-button]') as HTMLButtonElement;
      if (button) {
        button.disabled = true;
        button.textContent = 'Generating PDF...';
      }

      // Wait a bit for any animations to complete
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Configure html2canvas options for better quality
      const canvas = await html2canvas(componentRef.current, {
        scale: 2, // Higher resolution
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff',
        logging: false,
        width: componentRef.current.scrollWidth,
        height: componentRef.current.scrollHeight,
        onclone: (clonedDoc) => {
          // Ensure charts are visible in the cloned document
          const clonedElement = clonedDoc.querySelector('[data-testid="recharts-wrapper"]');
          if (clonedElement) {
            (clonedElement as HTMLElement).style.backgroundColor = 'white';
          }
        }
      });

      // Calculate PDF dimensions
      const imgWidth = 210; // A4 width in mm
      const pageHeight = 295; // A4 height in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;

      // Create PDF
      const pdf = new jsPDF('p', 'mm', 'a4');
      let position = 0;

      // Add first page
      pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      // Add additional pages if needed
      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }

      // Save the PDF
      const fileName = `RRIF_Strategy_Report_${new Date().toISOString().split('T')[0]}.pdf`;
      pdf.save(fileName);

      console.log('PDF generated successfully');
    } catch (error) {
      console.error('PDF generation failed:', error);
      alert(`PDF generation failed: ${error instanceof Error ? error.message : 'Unknown error occurred'}. Please try refreshing the page and generating the report again.`);
    } finally {
      // Reset button state
      const button = document.querySelector('[data-pdf-button]') as HTMLButtonElement;
      if (button) {
        button.disabled = false;
        button.textContent = 'Export PDF';
      }
    }
  };

  const recommended = results.reduce((best, res) => {
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
  }, results[0]);

  const currentDate = new Date().toLocaleDateString('en-CA', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <Box>
      <div ref={componentRef} className="print:p-0">
        <Paper 
          elevation={0} 
          sx={{ 
            p: 4, 
            maxWidth: '210mm', 
            margin: '0 auto',
            backgroundColor: '#ffffff',
            '@media print': {
              boxShadow: 'none',
              margin: 0,
              maxWidth: 'none',
              padding: '20mm',
            }
          }}
        >
          {/* Header Section */}
          <Box sx={{ textAlign: 'center', mb: 4, borderBottom: '3px solid #1976d2', pb: 3 }}>
            <Typography 
              variant="h3" 
              sx={{ 
                fontWeight: 700, 
                color: '#1976d2', 
                mb: 1,
                fontSize: { xs: '1.75rem', md: '2.5rem' }
              }}
            >
              Personalized Withdrawal Strategy Report
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
              Professional Retirement Income Analysis
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Report Generated: {currentDate} | Projection Horizon: {horizon} years
            </Typography>
          </Box>

          {/* Executive Summary */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2', mb: 2 }}>
              Executive Summary
            </Typography>
            
            {recommended && (
              <Card sx={{ mb: 3, backgroundColor: '#f8f9fa', border: '2px solid #1976d2' }}>
                <CardContent>
                  <Typography variant="h5" sx={{ fontWeight: 600, color: '#1976d2', mb: 2 }}>
                    Recommended Strategy: {recommended.strategy_name}
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>
                    Based on your primary goal of <strong>{goal}</strong>, this strategy is projected 
                    to deliver optimal results over your {horizon}-year planning horizon.
                  </Typography>
                  
                  {/* Key Metrics Grid */}
                  <Grid container spacing={2} sx={{ mt: 2 }}>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#ffffff', borderRadius: 1 }}>
                        <Typography variant="h6" color="primary" sx={{ fontWeight: 600 }}>
                          {recommended.totalTaxes !== null 
                            ? currencyFormatter.format(recommended.totalTaxes)
                            : '—'
                          }
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Lifetime Taxes (PV)
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#ffffff', borderRadius: 1 }}>
                        <Typography variant="h6" color="primary" sx={{ fontWeight: 600 }}>
                          {currencyFormatter.format(recommended.summary.average_annual_real_spending)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Average Annual Spending
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#ffffff', borderRadius: 1 }}>
                        <Typography variant="h6" color="primary" sx={{ fontWeight: 600 }}>
                          {recommended.finalEstate !== null 
                            ? currencyFormatter.format(recommended.finalEstate)
                            : '—'
                          }
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Estate Value (PV)
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            )}

            {explanation && (
              <Box sx={{ mb: 3 }}>
                <Typography
                  variant="body1"
                  sx={{ lineHeight: 1.7, color: '#333' }}
                  dangerouslySetInnerHTML={{
                    __html: DOMPurify.sanitize(explanation.summary),
                  }}
                />
              </Box>
            )}
          </Box>

          <Divider sx={{ my: 4 }} />

          {/* Financial Projections */}
          {recommended && (
            <Box sx={{ mb: 4 }}>
              <FinancialProjectionsTable strategy={recommended} maxYears={15} />
            </Box>
          )}

          <Divider sx={{ my: 4 }} />

          {/* Strategy Comparison */}
          {results.length > 1 && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2', mb: 3 }}>
                Strategy Comparison Analysis
              </Typography>
              <Typography variant="body1" sx={{ mb: 3, color: '#666' }}>
                The following table compares all analyzed strategies based on key financial metrics:
              </Typography>
              
              <Table 
                sx={{ 
                  '& .MuiTableCell-head': {
                    backgroundColor: '#1976d2',
                    color: 'white',
                    fontWeight: 600,
                    fontSize: '0.875rem',
                  },
                  '& .MuiTableCell-body': {
                    fontSize: '0.8125rem',
                  },
                  '& .MuiTableRow-root:nth-of-type(even)': {
                    backgroundColor: '#f8f9fa',
                  },
                }}
                className="strategy-comparison-table"
              >
                <TableHead>
                  <TableRow>
                    <TableCell>Strategy</TableCell>
                    <TableCell align="right">Lifetime Taxes (PV)</TableCell>
                    <TableCell align="right">Annual Spending</TableCell>
                    <TableCell align="right">Estate Value (PV)</TableCell>
                    <TableCell align="right">Tax Rate</TableCell>
                    <TableCell align="center">Complexity</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {results.map((res) => (
                    <TableRow 
                      key={res.strategy_code}
                      sx={{
                        backgroundColor: res.strategy_name === recommended?.strategy_name 
                          ? '#e3f2fd !important' 
                          : 'inherit',
                        fontWeight: res.strategy_name === recommended?.strategy_name ? 600 : 400,
                      }}
                    >
                      <TableCell>
                        {res.strategy_name}
                        {res.strategy_name === recommended?.strategy_name && (
                          <Typography variant="caption" color="primary" sx={{ ml: 1, fontWeight: 600 }}>
                            (Recommended)
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell align="right">
                        {res.totalTaxes !== null
                          ? currencyFormatter.format(res.totalTaxes)
                          : '—'}
                      </TableCell>
                      <TableCell align="right">
                        {currencyFormatter.format(res.summary.average_annual_real_spending)}
                      </TableCell>
                      <TableCell align="right">
                        {res.finalEstate !== null
                          ? currencyFormatter.format(res.finalEstate)
                          : '—'}
                      </TableCell>
                      <TableCell align="right">
                        {percentFormatter.format(res.summary.average_effective_tax_rate / 100)}
                      </TableCell>
                      <TableCell align="center">
                        {res.summary.strategy_complexity_score}/5
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          )}

          <Divider sx={{ my: 4 }} />

          {/* Key Outcomes & Recommendations */}
          {explanation && (
            <Box sx={{ mb: 4 }}>
              <Grid container spacing={4}>
                <Grid item xs={12} md={6}>
                  <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2', mb: 3 }}>
                    Key Outcomes
                  </Typography>
                  <Box component="ul" sx={{ pl: 2, '& li': { mb: 1.5, lineHeight: 1.6 } }}>
                    {explanation.key_outcomes.map((outcome, idx) => (
                      <Typography component="li" key={idx} variant="body1">
                        {outcome}
                      </Typography>
                    ))}
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2', mb: 3 }}>
                    Key Recommendations
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{ lineHeight: 1.7 }}
                    dangerouslySetInnerHTML={{
                      __html: DOMPurify.sanitize(explanation.recommendations),
                    }}
                  />
                </Grid>
              </Grid>
            </Box>
          )}

          <Divider sx={{ my: 4 }} />

          {/* Strategy Outcomes Visualized */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2', mb: 3 }}>
              Strategy Outcomes Visualized
            </Typography>
            <Typography variant="body1" sx={{ mb: 3, color: '#666' }}>
              The following charts illustrate the projected portfolio values over time for each analyzed strategy:
            </Typography>
            {results.map((res) => (
              <Box key={res.strategy_code} sx={{ mb: 3 }}>
                <StrategyChart
                  title={res.strategy_name}
                  data={res.yearly_balances || []}
                />
              </Box>
            ))}
          </Box>

          <Divider sx={{ my: 4 }} />

          {/* Bottom Line Summary */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2', mb: 3 }}>
              Bottom Line Summary
            </Typography>
            <Card sx={{ backgroundColor: '#f8f9fa', border: '1px solid #e0e0e0' }}>
              <CardContent>
                <Typography variant="body1" sx={{ lineHeight: 1.7, mb: 2 }}>
                  Based on your goal of <strong>{goal}</strong> and the comprehensive analysis above, 
                  the <strong>{recommended?.strategy_name}</strong> strategy offers the best balance 
                  of tax efficiency, spending sustainability, and estate preservation for your specific situation.
                </Typography>
                
                {recommended && (
                  <Box sx={{ mt: 3, p: 2, backgroundColor: '#ffffff', borderRadius: 1, border: '1px solid #1976d2' }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#1976d2', mb: 1 }}>
                      Key Takeaways:
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      • Projected lifetime tax burden: <strong>
                        {recommended.totalTaxes !== null 
                          ? currencyFormatter.format(recommended.totalTaxes)
                          : 'Not available'
                        }
                      </strong> (present value)
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      • Sustainable annual spending: <strong>
                        {currencyFormatter.format(recommended.summary.average_annual_real_spending)}
                      </strong> (inflation-adjusted)
                    </Typography>
                    <Typography variant="body2">
                      • Projected estate value: <strong>
                        {recommended.finalEstate !== null 
                          ? currencyFormatter.format(recommended.finalEstate)
                          : 'Not available'
                        }
                      </strong> (present value)
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Box>

          {/* Disclaimer */}
          <Box sx={{ mt: 4, p: 2, backgroundColor: '#fff3cd', borderRadius: 1, border: '1px solid #ffeaa7' }}>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', lineHeight: 1.5 }}>
              <strong>Important Disclaimer:</strong> This report is based on projections and assumptions that may not reflect actual future results. 
              Tax laws, investment returns, and personal circumstances can change. Please consult with a qualified financial advisor 
              before making any investment or withdrawal decisions. This analysis is for informational purposes only and does not 
              constitute financial advice.
            </Typography>
          </Box>
        </Paper>
      </div>

      {/* Action Buttons */}
      <Box mt={4} textAlign="center" className="no-print">
        <Button 
          variant="outlined" 
          onClick={onBack} 
          sx={{ mr: 2, minWidth: 120 }}
        >
          Back to Results
        </Button>
        <Button 
          variant="contained" 
          onClick={handlePrint} 
          sx={{ mr: 2, minWidth: 120, backgroundColor: '#1976d2' }}
          data-pdf-button
        >
          Export PDF
        </Button>
        <Button 
          variant="contained" 
          color="secondary" 
          onClick={onStartOver}
          sx={{ minWidth: 120 }}
        >
          Start Over
        </Button>
      </Box>
    </Box>
  );
};

export default ReportPage;
