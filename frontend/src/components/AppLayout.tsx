import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';

const AppLayout: React.FC = () => {
  return (
    <>
      <AppBar position="static" sx={{ bgcolor: '#2c5aa0' }}>
        <Toolbar>
          <Typography variant="h6" component={Link} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}>
            Ontario Tax App
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button color="inherit" component={Link} to="/calculator">
              RRIF Calculator
            </Button>
            <Button color="inherit" component={Link} to="/free-rrif-guide">
              Free RRIF Guide
            </Button>
          </Box>
        </Toolbar>
      </AppBar>
      <Outlet />
    </>
  );
};

export default AppLayout;
