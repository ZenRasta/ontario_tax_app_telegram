import React from 'react';
import { Box, Grid, ToggleButton, ToggleButtonGroup, Typography, Button, Tooltip, Stack } from '@mui/material';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';


interface StrategyStepProps {
  selectedStrategies: string[];
  onToggleStrategy: (strategies: string[]) => void;
  onNext: () => void;
  onBack: () => void;
}

// Define the strategy options with codes, labels, and descriptions
const strategyOptions = [
  { code: 'BF', label: 'Bracket Filling', description: 'Accelerate withdrawals to fully use lower tax brackets each year.' },
  { code: 'E65', label: 'Early RRIF @65', description: 'Convert RRSP to RRIF at 65 to withdraw earlier (before mandatory age 72).' },
  { code: 'CD', label: 'Delay CPP/OAS', description: 'Delay CPP and OAS start to age 70 for higher future payouts.' },
  { code: 'GM', label: 'Gradual Meltdown', description: 'Steadily draw down registered accounts to reduce future taxes.' },
  { code: 'SEQ', label: 'Spousal Equalization', description: 'Split withdrawals between spouses to equalize incomes and tax rates.' },
  { code: 'IO', label: 'Interest-Offset Loan', description: 'Use a loan strategy where loan interest offsets investment income tax.' },
  { code: 'LS', label: 'Lump-Sum Withdrawal', description: 'Take a one-time large withdrawal in a specific year to reduce later balances.' },
  { code: 'EBX', label: 'Empty-by-X', description: 'Plan withdrawals so accounts are emptied by a chosen age (X years old).' }
];

const StrategyStep: React.FC<StrategyStepProps> = ({ selectedStrategies, onToggleStrategy, onNext, onBack }) => {

  const handleToggle = (_event: React.MouseEvent<HTMLElement>, newSelection: string[]) => {
    // newSelection is the array of selected strategy codes
    onToggleStrategy(newSelection);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        2. Select Strategies to Compare
      </Typography>
      <Typography variant="body2" color="textSecondary" gutterBottom>
        Toggle the strategies you want to consider. (You can select multiple.)
      </Typography>
      <Grid container spacing={2}>
        {strategyOptions.map(({ code, label, description }) => (
          <Grid item xs={12} sm={6} md={6} key={code}>
            <ToggleButtonGroup 
              value={selectedStrategies} 
              onChange={handleToggle} 
              aria-label="strategies" 
              size="small"
              color="primary"
              exclusive={false}
            >
              <ToggleButton value={code}>
                {label}
              </ToggleButton>
            </ToggleButtonGroup>
            <Tooltip title={description} placement="right">
              <InfoOutlinedIcon fontSize="small" sx={{ ml: 1, verticalAlign: 'middle', color: 'action.active' }}/>
            </Tooltip>
          </Grid>
        ))}
      </Grid>
      <Box mt={3} textAlign="right">
        <Button variant="outlined" onClick={onBack} sx={{ mr: 2 }}>
          Back
        </Button>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={onNext} 
          disabled={selectedStrategies.length === 0}
        >
          Next
        </Button>
      </Box>
    </Box>
  );
};

export default StrategyStep;
