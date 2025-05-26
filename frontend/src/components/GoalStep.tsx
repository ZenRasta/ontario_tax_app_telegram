import React from 'react';
import { Box, ToggleButton, ToggleButtonGroup, Typography, Button } from '@mui/material';

interface GoalStepProps {
  goal: string;
  onSelectGoal: (goal: string) => void;
}

const GoalStep: React.FC<GoalStepProps> = ({ goal, onSelectGoal }) => {
  const handleChange = (_event: React.MouseEvent<HTMLElement>, newGoal: string) => {
    if (newGoal) {
      onSelectGoal(newGoal);
    }
  };

  return (
    <Box textAlign="center">
      <Typography variant="h6" gutterBottom>
        1. Choose Your Retirement Goal
      </Typography>
      <ToggleButtonGroup
        color="primary"
        value={goal}
        exclusive
        onChange={handleChange}
        aria-label="Retirement Goal"
      >
        <ToggleButton value="Minimize Tax">Minimize Tax</ToggleButton>
        <ToggleButton value="Maximize Spending">Maximize Spending</ToggleButton>
        <ToggleButton value="Preserve Estate">Preserve Estate</ToggleButton>
        <ToggleButton value="Simplify">Simplify</ToggleButton>
      </ToggleButtonGroup>
      <Box mt={3}>
        {/** Only enable Next when a goal is selected */}
        <Button 
          variant="contained" 
          color="primary" 
          onClick={() => onSelectGoal(goal)} 
          disabled={!goal}
        >
          Next
        </Button>
      </Box>
    </Box>
  );
};

export default GoalStep;
