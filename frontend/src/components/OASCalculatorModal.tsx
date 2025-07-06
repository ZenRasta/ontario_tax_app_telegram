import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  IconButton,
  Alert,
  CircularProgress,
  InputAdornment,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';

const API_PREFIX = import.meta.env.VITE_API_PREFIX ?? '/v1';

interface OASCalculatorModalProps {
  open: boolean;
  onClose: () => void;
}

interface FormData {
  rrif_withdrawals: string;
  cpp_pension: string;
  work_pension: string;
  other_income: string;
  email_address: string;
  recipient_name: string;
}

interface CalculationResult {
  total_income: number;
  oas_clawback_amount: number;
  oas_clawback_percentage: number;
  net_oas_amount: number;
  risk_level: string;
  recommendations_count: number;
}

const OASCalculatorModal: React.FC<OASCalculatorModalProps> = ({ open, onClose }) => {
  const [formData, setFormData] = useState<FormData>({
    rrif_withdrawals: '',
    cpp_pension: '',
    work_pension: '',
    other_income: '',
    email_address: '',
    recipient_name: '',
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CalculationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleInputChange = (field: keyof FormData) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value,
    }));
    // Clear previous results when inputs change
    if (result) {
      setResult(null);
      setSuccess(null);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-CA', {
      style: 'currency',
      currency: 'CAD',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const validateForm = (): boolean => {
    const requiredFields = ['rrif_withdrawals', 'cpp_pension', 'work_pension', 'other_income', 'email_address'];
    
    for (const field of requiredFields) {
      if (!formData[field as keyof FormData]) {
        setError(`Please fill in all required fields`);
        return false;
      }
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email_address)) {
      setError('Please enter a valid email address');
      return false;
    }

    // Validate numeric fields
    const numericFields = ['rrif_withdrawals', 'cpp_pension', 'work_pension', 'other_income'];
    for (const field of numericFields) {
      const value = parseFloat(formData[field as keyof FormData]);
      if (isNaN(value) || value < 0) {
        setError(`Please enter valid amounts (numbers only, no commas or currency symbols)`);
        return false;
      }
    }

    return true;
  };

  const handleSubmit = async () => {
    setError(null);
    setSuccess(null);

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const payload = {
        rrif_withdrawals: parseFloat(formData.rrif_withdrawals),
        cpp_pension: parseFloat(formData.cpp_pension),
        work_pension: parseFloat(formData.work_pension),
        other_income: parseFloat(formData.other_income),
        email_address: formData.email_address,
        recipient_name: formData.recipient_name || '',
      };
      
      const res = await fetch(`${API_PREFIX}/oas-calculator/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();

      if (data.success) {
        setResult(data.calculation_result);
        setSuccess(data.message);
      } else {
        setError(data.error || 'Calculation failed');
      }
    } catch (err) {
      console.error('Error calculating OAS:', err);
      setError('Failed to calculate OAS clawback. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      rrif_withdrawals: '',
      cpp_pension: '',
      work_pension: '',
      other_income: '',
      email_address: '',
      recipient_name: '',
    });
    setResult(null);
    setError(null);
    setSuccess(null);
    onClose();
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'low': return '#4caf50';
      case 'medium': return '#ff9800';
      case 'high': return '#f44336';
      default: return '#757575';
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="sm" 
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        backgroundColor: '#1976d2',
        color: 'white',
        py: 2
      }}>
        <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
          OAS Clawback Calculator
        </Typography>
        <IconButton 
          onClick={handleClose} 
          sx={{ color: 'white' }}
          aria-label="close"
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ pt: 3 }}>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Enter your estimated annual income sources below. We'll calculate your risk and email you a free, personalized summary.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && result && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        {result && (
          <Box sx={{ 
            mb: 3, 
            p: 2, 
            backgroundColor: '#f5f5f5', 
            borderRadius: 1,
            border: `2px solid ${getRiskColor(result.risk_level)}`
          }}>
            <Typography variant="h6" sx={{ mb: 1, color: getRiskColor(result.risk_level) }}>
              Quick Results Summary
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Total Income:</strong> {formatCurrency(result.total_income)}
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>OAS Clawback:</strong> {formatCurrency(result.oas_clawback_amount)} ({result.oas_clawback_percentage.toFixed(1)}%)
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Net OAS Benefit:</strong> {formatCurrency(result.net_oas_amount)}
            </Typography>
            <Typography variant="body2" sx={{ 
              fontWeight: 600, 
              color: getRiskColor(result.risk_level) 
            }}>
              <strong>Risk Level:</strong> {result.risk_level}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
              Detailed analysis with {result.recommendations_count} personalized recommendations has been emailed to you.
            </Typography>
          </Box>
        )}

        <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            label="RRIF/RRSP Withdrawals ($)"
            placeholder="e.g., 25000"
            value={formData.rrif_withdrawals}
            onChange={handleInputChange('rrif_withdrawals')}
            fullWidth
            required
            inputProps={{
              min: 0,
              step: 1,
              inputMode: 'numeric',
              pattern: '[0-9]*'
            }}
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>,
            }}
          />

          <TextField
            label="CPP Pension ($)"
            placeholder="e.g., 15000"
            value={formData.cpp_pension}
            onChange={handleInputChange('cpp_pension')}
            fullWidth
            required
            inputProps={{
              min: 0,
              step: 1,
              inputMode: 'numeric',
              pattern: '[0-9]*'
            }}
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>,
            }}
          />

          <TextField
            label="Work/Other Pension ($)"
            placeholder="e.g., 30000"
            value={formData.work_pension}
            onChange={handleInputChange('work_pension')}
            fullWidth
            required
            inputProps={{
              min: 0,
              step: 1,
              inputMode: 'numeric',
              pattern: '[0-9]*'
            }}
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>,
            }}
          />

          <TextField
            label="Other Income ($)"
            placeholder="e.g., 5000"
            value={formData.other_income}
            onChange={handleInputChange('other_income')}
            fullWidth
            required
            inputProps={{
              min: 0,
              step: 1,
              inputMode: 'numeric',
              pattern: '[0-9]*'
            }}
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>,
            }}
          />

          <TextField
            label="Email Address"
            placeholder="your.email@example.com"
            value={formData.email_address}
            onChange={handleInputChange('email_address')}
            fullWidth
            required
            type="email"
          />

          <TextField
            label="Your Name (Optional)"
            placeholder="For personalization"
            value={formData.recipient_name}
            onChange={handleInputChange('recipient_name')}
            fullWidth
          />
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 1 }}>
        <Button 
          onClick={handleClose} 
          color="inherit"
          disabled={loading}
        >
          Cancel
        </Button>
        <Button 
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
          sx={{ 
            minWidth: 200,
            backgroundColor: '#4caf50',
            '&:hover': {
              backgroundColor: '#45a049',
            }
          }}
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
        >
          {loading ? 'Calculating...' : 'Calculate & Email My Results'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default OASCalculatorModal;
