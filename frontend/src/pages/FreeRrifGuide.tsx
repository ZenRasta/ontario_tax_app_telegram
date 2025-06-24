import React from 'react';
import { Container, Typography, Box, Paper, Alert, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, List, ListItem, ListItemText } from '@mui/material';
import { Link } from 'react-router-dom';

const FreeRrifGuide: React.FC = () => {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 'bold', color: '#1a202c' }}>
          Your Complete Guide to RRIF Planning in Ontario
        </Typography>
        <Typography variant="h5" sx={{ color: '#4a5568', mb: 2 }}>
          Essential Strategies to Maximize Your Retirement Income and Minimize Taxes
        </Typography>
        <Typography variant="h6" sx={{ color: '#2c5aa0', fontWeight: 600 }}>
          2025 Edition
        </Typography>
      </Box>

      {/* Introduction */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ color: '#1a202c', borderBottom: '2px solid #e2e8f0', pb: 1 }}>
          Introduction: Why RRIF Planning Matters More Than Ever
        </Typography>
        
        <Typography paragraph sx={{ color: '#4a5568' }}>
          Your retirement savings could be at risk. Not from market volatility or inflation, but from something far more controllable: poor RRIF withdrawal strategy.
        </Typography>
        
        <Typography paragraph sx={{ color: '#4a5568' }}>
          If you're approaching 71 or already managing a RRIF in Ontario, you're facing decisions that could cost you tens of thousands of dollars over your retirement. The difference between an optimal and suboptimal withdrawal strategy isn't just a few percentage points—it can mean the difference between leaving a substantial estate and running out of money.
        </Typography>

        <Typography variant="h5" gutterBottom sx={{ mt: 3, color: '#2d3748' }}>
          The Stakes Are Higher in Ontario
        </Typography>
        
        <Typography paragraph sx={{ color: '#4a5568' }}>
          As an Ontario resident, you face unique challenges:
        </Typography>
        
        <List>
          <ListItem>
            <ListItemText primary="Combined federal and provincial tax rates that can reach 46% on RRIF withdrawals" />
          </ListItem>
          <ListItem>
            <ListItemText primary="OAS clawback thresholds that are easier to trigger than you think" />
          </ListItem>
          <ListItem>
            <ListItemText primary="Complex spousal income splitting rules that most people don't fully understand" />
          </ListItem>
          <ListItem>
            <ListItemText primary="Provincial tax credits that can be optimized with proper planning" />
          </ListItem>
        </List>

        <Alert severity="warning" sx={{ my: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            The $50,000 Mistake
          </Typography>
          <Typography>
            Recent analysis shows that the average Ontario retiree following a suboptimal RRIF withdrawal strategy pays approximately $50,000 more in lifetime taxes compared to those who implement even basic optimization techniques.
          </Typography>
        </Alert>
      </Paper>

      {/* RRIF Conversion Deadline */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ color: '#1a202c', borderBottom: '2px solid #e2e8f0', pb: 1 }}>
          Chapter 1: The RRIF Conversion Deadline Explained
        </Typography>
        
        <Typography variant="h5" gutterBottom sx={{ mt: 3, color: '#2d3748' }}>
          The Rule That Changes Everything
        </Typography>
        
        <Typography paragraph sx={{ color: '#4a5568' }}>
          By December 31st of the year you turn 71, you must convert your RRSP to one of three options:
        </Typography>
        
        <List>
          <ListItem>
            <ListItemText primary="1. Convert to a Registered Retirement Income Fund (RRIF)" />
          </ListItem>
          <ListItem>
            <ListItemText primary="2. Purchase an annuity" />
          </ListItem>
          <ListItem>
            <ListItemText primary="3. Cash out entirely (and pay full tax immediately)" />
          </ListItem>
        </List>

        <Alert severity="error" sx={{ my: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            What Happens If You Miss the Deadline?
          </Typography>
          <Typography>
            The Canada Revenue Agency doesn't send reminder letters. If you don't act by December 31st, your entire RRSP becomes taxable income that year, potentially pushing you into the highest tax bracket (46.16% in Ontario).
          </Typography>
        </Alert>
      </Paper>

      {/* Minimum Withdrawal Calculation */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ color: '#1a202c', borderBottom: '2px solid #e2e8f0', pb: 1 }}>
          Chapter 2: How Your Minimum Withdrawal is Calculated
        </Typography>
        
        <Typography paragraph sx={{ color: '#4a5568' }}>
          Your minimum RRIF withdrawal is calculated using a simple formula:
        </Typography>
        
        <Box sx={{ p: 2, bgcolor: '#f7fafc', borderRadius: 1, my: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold', textAlign: 'center' }}>
            Minimum Withdrawal = RRIF Value (Dec 31) × Age Factor
          </Typography>
        </Box>

        <Typography variant="h5" gutterBottom sx={{ mt: 3, color: '#2d3748' }}>
          2025 RRIF Minimum Withdrawal Rates
        </Typography>
        
        <TableContainer component={Paper} sx={{ my: 2 }}>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: '#2d3748' }}>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Age</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Withdrawal Rate</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Age</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Withdrawal Rate</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow><TableCell>71</TableCell><TableCell>5.28%</TableCell><TableCell>81</TableCell><TableCell>7.48%</TableCell></TableRow>
              <TableRow><TableCell>72</TableCell><TableCell>5.40%</TableCell><TableCell>82</TableCell><TableCell>7.85%</TableCell></TableRow>
              <TableRow><TableCell>73</TableCell><TableCell>5.53%</TableCell><TableCell>83</TableCell><TableCell>8.24%</TableCell></TableRow>
              <TableRow><TableCell>74</TableCell><TableCell>5.67%</TableCell><TableCell>84</TableCell><TableCell>8.65%</TableCell></TableRow>
              <TableRow><TableCell>75</TableCell><TableCell>5.82%</TableCell><TableCell>85</TableCell><TableCell>8.99%</TableCell></TableRow>
              <TableRow><TableCell>76</TableCell><TableCell>5.98%</TableCell><TableCell>90</TableCell><TableCell>11.92%</TableCell></TableRow>
              <TableRow><TableCell>77</TableCell><TableCell>6.17%</TableCell><TableCell>95</TableCell><TableCell>20.00%</TableCell></TableRow>
              <TableRow><TableCell>78</TableCell><TableCell>6.36%</TableCell><TableCell>95+</TableCell><TableCell>20.00%</TableCell></TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Tax Traps */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ color: '#1a202c', borderBottom: '2px solid #e2e8f0', pb: 1 }}>
          Chapter 3: The Biggest Tax Traps (and How to Avoid Them)
        </Typography>
        
        <Typography variant="h5" gutterBottom sx={{ mt: 3, color: '#2d3748' }}>
          Trap #1: Withholding Tax Confusion
        </Typography>
        
        <Alert severity="warning" sx={{ my: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            How Withholding Tax Really Works
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Minimum withdrawals: No withholding tax" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Additional withdrawals in Ontario:" />
            </ListItem>
            <ListItem sx={{ ml: 2 }}>
              <ListItemText primary="Up to $5,000: 15.15%" />
            </ListItem>
            <ListItem sx={{ ml: 2 }}>
              <ListItemText primary="$5,001 to $15,000: 30.3%" />
            </ListItem>
            <ListItem sx={{ ml: 2 }}>
              <ListItemText primary="Over $15,000: 45.45%" />
            </ListItem>
          </List>
          <Typography sx={{ mt: 2 }}>
            <strong>The Trap:</strong> Many people think withholding tax is their final tax bill. It's not—it's just a down payment.
          </Typography>
        </Alert>

        <Typography variant="h5" gutterBottom sx={{ mt: 3, color: '#2d3748' }}>
          Trap #2: The OAS Clawback - The #1 Hidden Cost
        </Typography>
        
        <Alert severity="error" sx={{ my: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            2025 OAS Clawback Rules
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Threshold: $90,997 net income" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Clawback rate: 15% of income over threshold" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Complete clawback: $148,451 (you lose all OAS)" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Maximum OAS (2025): $8,618 annually" />
            </ListItem>
          </List>
        </Alert>
      </Paper>

      {/* Smart Strategies */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ color: '#1a202c', borderBottom: '2px solid #e2e8f0', pb: 1 }}>
          Chapter 4: Beyond the Minimum - An Overview of Smart Strategies
        </Typography>
        
        <Typography paragraph sx={{ color: '#4a5568' }}>
          Now that you understand the rules and traps, let's explore the strategies that sophisticated planners use to optimize RRIF withdrawals.
        </Typography>

        <Typography variant="h5" gutterBottom sx={{ mt: 3, color: '#2d3748' }}>
          Strategy #1: Income Leveling
        </Typography>
        <Typography paragraph sx={{ color: '#4a5568' }}>
          Instead of taking minimum withdrawals that increase each year, consider taking larger withdrawals early to "level" your taxable income.
        </Typography>

        <Typography variant="h5" gutterBottom sx={{ mt: 3, color: '#2d3748' }}>
          Strategy #2: Spousal Income Splitting
        </Typography>
        <Typography paragraph sx={{ color: '#4a5568' }}>
          If you're 65 or older, you can split up to 50% of your RRIF income with your spouse.
        </Typography>

        <Typography variant="h5" gutterBottom sx={{ mt: 3, color: '#2d3748' }}>
          Strategy #3: Strategic Timing with CPP and OAS
        </Typography>
        <Typography paragraph sx={{ color: '#4a5568' }}>
          Coordinate your RRIF withdrawals with when you start government benefits.
        </Typography>

        <Alert severity="info" sx={{ my: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            Why Generic Advice Falls Short
          </Typography>
          <Typography>
            The "right" strategy depends on running actual numbers with your specific income, assets, and goals. What works for your neighbor may cost you thousands.
          </Typography>
        </Alert>
      </Paper>

      {/* CTA Section */}
      <Paper elevation={3} sx={{ p: 4, bgcolor: 'linear-gradient(135deg, #2c5aa0 0%, #1a365d 100%)', color: 'white', textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom sx={{ color: 'white' }}>
          Ready to Optimize Your RRIF Strategy?
        </Typography>
        <Typography paragraph sx={{ fontSize: '1.1rem', mb: 3 }}>
          Get your personalized analysis today and optimize your retirement income for Ontario's tax system.
        </Typography>
        <Typography paragraph sx={{ fontWeight: 'bold', mb: 3 }}>
          30-day money-back guarantee • Instant results • Secure and confidential
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
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
            Generate My Personalized Analysis Now
          </Button>
          
          <Button
            component={Link}
            to="/"
            variant="outlined"
            size="large"
            sx={{
              borderColor: 'white',
              color: 'white',
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              fontWeight: 600,
              '&:hover': {
                bgcolor: 'white',
                color: '#2c5aa0',
                transform: 'translateY(-2px)',
              },
            }}
          >
            Learn More About Our Solution
          </Button>
        </Box>
      </Paper>

      {/* Footer */}
      <Box sx={{ mt: 4, p: 2, textAlign: 'center', color: '#a0aec0', fontSize: '0.9rem' }}>
        <Typography variant="body2">
          © 2025 Ontario Tax App. All rights reserved.
        </Typography>
        <Typography variant="body2" sx={{ mt: 0.5 }}>
          This guide is for educational purposes only and does not constitute financial advice. Tax rules are subject to change. Consult with qualified professionals for advice specific to your situation.
        </Typography>
      </Box>
    </Container>
  );
};

export default FreeRrifGuide;
