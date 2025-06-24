import React from 'react';
import { Container, Typography, Box, Button, Paper, Grid, Card, CardContent } from '@mui/material';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Hero Section */}
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography variant="h2" component="h1" gutterBottom sx={{ fontWeight: 'bold', color: '#1a202c' }}>
          Ontario RRIF Strategy Calculator
        </Typography>
        <Typography variant="h5" sx={{ color: '#4a5568', mb: 4, maxWidth: '800px', mx: 'auto' }}>
          Optimize your retirement income with professional-grade RRIF withdrawal strategies designed specifically for Ontario residents
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Button
            component={Link}
            to="/calculator"
            variant="contained"
            size="large"
            sx={{
              bgcolor: '#2c5aa0',
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              fontWeight: 600,
              '&:hover': {
                bgcolor: '#1a365d',
                transform: 'translateY(-2px)',
              },
            }}
          >
            Start Your Analysis
          </Button>
          <Button
            component={Link}
            to="/free-rrif-guide"
            variant="outlined"
            size="large"
            sx={{
              borderColor: '#2c5aa0',
              color: '#2c5aa0',
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              fontWeight: 600,
              '&:hover': {
                bgcolor: '#2c5aa0',
                color: 'white',
                transform: 'translateY(-2px)',
              },
            }}
          >
            Free RRIF Guide
          </Button>
        </Box>
      </Box>

      {/* Features Section */}
      <Grid container spacing={4} sx={{ mb: 6 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ color: '#2c5aa0', fontWeight: 'bold' }}>
                🎯 Ontario-Specific
              </Typography>
              <Typography variant="body1" sx={{ color: '#4a5568' }}>
                Calculations use current Ontario tax rates, OAS clawback thresholds, and provincial tax credits for accurate results.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ color: '#2c5aa0', fontWeight: 'bold' }}>
                📊 8+ Strategies
              </Typography>
              <Typography variant="body1" sx={{ color: '#4a5568' }}>
                Compare income leveling, spousal splitting, CPP deferral, and other advanced withdrawal strategies side-by-side.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ color: '#2c5aa0', fontWeight: 'bold' }}>
                💰 Tax Optimization
              </Typography>
              <Typography variant="body1" sx={{ color: '#4a5568' }}>
                Minimize lifetime taxes, avoid OAS clawback, and maximize your retirement income with data-driven strategies.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Value Proposition */}
      <Paper elevation={2} sx={{ p: 4, bgcolor: '#f8fafc', textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom sx={{ color: '#1a202c', fontWeight: 'bold' }}>
          Why RRIF Strategy Matters
        </Typography>
        <Typography variant="body1" sx={{ color: '#4a5568', mb: 3, fontSize: '1.1rem', maxWidth: '800px', mx: 'auto' }}>
          The difference between an optimal and suboptimal RRIF withdrawal strategy can cost Ontario retirees 
          over <strong>$50,000 in unnecessary taxes</strong> over their retirement. Our calculator helps you 
          find the strategy that works best for your specific situation.
        </Typography>
        <Button
          component={Link}
          to="/calculator"
          variant="contained"
          size="large"
          sx={{
            bgcolor: '#e53e3e',
            color: 'white',
            px: 4,
            py: 1.5,
            fontSize: '1.1rem',
            fontWeight: 600,
            '&:hover': {
              bgcolor: '#c53030',
              transform: 'translateY(-2px)',
            },
          }}
        >
          Calculate Your Optimal Strategy
        </Button>
      </Paper>
    </Container>
  );
};

export default Home;
