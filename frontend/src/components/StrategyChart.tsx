import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { Box, Typography } from '@mui/material';
import type { ComparisonResponseItem } from '../types/api';

export type YearlyBalance = NonNullable<ComparisonResponseItem['yearly_balances']>[number];

interface StrategyChartProps {
  title: string;
  data: YearlyBalance[];
}

const StrategyChart: React.FC<StrategyChartProps> = ({ title, data }) => {
  return (
    <Box my={2}>
      <Typography variant="subtitle2" align="center" gutterBottom>
        {title}
      </Typography>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <XAxis dataKey="year" />
          <YAxis />
          <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
          <Legend />
          <Line type="monotone" dataKey="portfolio_end" name={title} stroke="#8884d8" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default StrategyChart;
