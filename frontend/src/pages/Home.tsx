import React from 'react';
import { Container } from '@mui/material';
import App from '../App';

const Home: React.FC = () => {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <App />
    </Container>
  );
};

export default Home;
