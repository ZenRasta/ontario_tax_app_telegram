import React from 'react';
import { Container } from '@mui/material';
import App from '../App';

export default function CalculatorPage() {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <App />
    </Container>
  );
}
