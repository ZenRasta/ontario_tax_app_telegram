import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';
import { Box, Typography, Paper } from '@mui/material';
import type { ComparisonResponseItem } from '../types/api';

export type YearlyBalance = NonNullable<ComparisonResponseItem['yearly_balances']>[number];

interface StrategyChartProps {
  title: string;
  data: YearlyBalance[];
}

const currencyFormatter = new Intl.NumberFormat('en-CA', {
  style: 'currency',
  currency: 'CAD',
  maximumFractionDigits: 0,
});

const StrategyChart: React.FC<StrategyChartProps> = ({ title, data }) => {
  // Custom tooltip formatter
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Paper 
          sx={{ 
            p: 2, 
            backgroundColor: 'rgba(255, 255, 255, 0.95)', 
            border: '1px solid #1976d2',
            borderRadius: 1,
            boxShadow: 2
          }}
        >
          <Typography variant="body2" sx={{ fontWeight: 600, color: '#1976d2' }}>
            Year {label}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Portfolio Value: {currencyFormatter.format(payload[0].value)}
          </Typography>
        </Paper>
      );
    }
    return null;
  };

  // Format Y-axis labels
  const formatYAxis = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return `$${value.toFixed(0)}`;
  };

  return (
    <Box 
      sx={{ 
        my: 3,
        '@media print': {
          pageBreakInside: 'avoid',
          breakInside: 'avoid',
          '& .recharts-wrapper': {
            backgroundColor: 'white !important',
          },
          '& .recharts-cartesian-grid line': {
            stroke: '#ccc !important',
          },
          '& .recharts-line': {
            strokeWidth: '2 !important',
          },
          '& .recharts-text': {
            fill: '#333 !important',
            fontSize: '10px !important',
          },
        }
      }}
    >
      <Typography 
        variant="h6" 
        sx={{ 
          fontWeight: 600, 
          color: '#1976d2', 
          mb: 2,
          textAlign: 'center',
          fontSize: { xs: '1rem', md: '1.25rem' }
        }}
      >
        {title} - Portfolio Projection
      </Typography>
      
      <Paper 
        elevation={2} 
        sx={{ 
          p: 2, 
          backgroundColor: '#fafafa',
          '@media print': {
            boxShadow: 'none',
            border: '1px solid #ccc',
          }
        }}
      >
        <ResponsiveContainer width="100%" height={350}>
          <LineChart 
            data={data} 
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="year" 
              stroke="#666"
              fontSize={12}
              tickLine={{ stroke: '#666' }}
              axisLine={{ stroke: '#666' }}
            />
            <YAxis 
              stroke="#666"
              fontSize={12}
              tickLine={{ stroke: '#666' }}
              axisLine={{ stroke: '#666' }}
              tickFormatter={formatYAxis}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ 
                paddingTop: '20px',
                fontSize: '14px',
                color: '#666'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="portfolio_end" 
              name="Portfolio Value" 
              stroke="#1976d2" 
              strokeWidth={3}
              dot={{ fill: '#1976d2', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#1976d2', strokeWidth: 2, fill: '#ffffff' }}
            />
          </LineChart>
        </ResponsiveContainer>
        
        <Typography 
          variant="caption" 
          color="text.secondary" 
          sx={{ 
            display: 'block', 
            textAlign: 'center', 
            mt: 1,
            fontStyle: 'italic'
          }}
        >
          * Portfolio values shown in Canadian dollars. Projections are estimates based on assumptions.
        </Typography>
      </Paper>
    </Box>
  );
};

export default StrategyChart;
