import { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import {
  Box,
  Checkbox,
  FormControlLabel,
  FormGroup,
  RadioGroup,
  Radio,
  TextField,
  Button,
  Typography,
  Select,
  MenuItem,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import type { GridColDef } from '@mui/x-data-grid';
import type { StrategyParamsInput } from '../types/api';
import { ALL_STRATEGIES, StrategyCodeEnum } from '../strategies';

interface FormValues {
  strategy_params: StrategyParamsInput;
}

const schema = yup.object({
  strategy_params: yup.object({
    bracket_fill_ceiling: yup
      .number()
      .typeError('Required')
      .when('$bf', (bf: boolean, s: any) => (bf ? s.required() : s)),
    lump_sum_amount: yup
      .number()
      .typeError('Required')
      .when('$ls', (ls: boolean, s: any) => (ls ? s.required() : s)),
    lump_sum_year_offset: yup
      .number()
      .typeError('Required')
      .when('$ls', (ls: boolean, s: any) => (ls ? s.required() : s)),
    target_depletion_age: yup
      .number()
      .typeError('Required')
      .when('$ebx', (ebx: boolean, s: any) => (ebx ? s.required() : s)),
    cpp_start_age: yup
      .number()
      .typeError('Required')
      .min(60)
      .max(70)
      .when('$delay', (delay: boolean, s: any) => (delay ? s.required() : s)),
    oas_start_age: yup
      .number()
      .typeError('Required')
      .min(60)
      .max(70)
      .when('$delay', (delay: boolean, s: any) => (delay ? s.required() : s)),
    interest_rate: yup
      .number()
      .typeError('Required')
      .when('$interest', (interest: boolean, s: any) => (interest ? s.required() : s)),
    loan_pct_rrif: yup
      .number()
      .typeError('Required')
      .when('$interest', (interest: boolean, s: any) => (interest ? s.required() : s)),
  }).required(),
});

export default function SimulationForm() {
  const [mode, setMode] = useState<'simulate' | 'compare'>('simulate');
  const [selectedStrategy, setSelectedStrategy] = useState<StrategyCodeEnum>('GM');
  const [compareSelection, setCompareSelection] = useState<StrategyCodeEnum[]>([]);
  const [toggles, setToggles] = useState<Record<StrategyCodeEnum, boolean>>(
    Object.fromEntries(ALL_STRATEGIES.map((s) => [s.code, false])) as Record<StrategyCodeEnum, boolean>
  );

  const handleToggle = (code: StrategyCodeEnum, value: boolean) => {
    setToggles((prev) => ({ ...prev, [code]: value }));
  };

  const handleCompareSelect = (code: StrategyCodeEnum, value: boolean) => {
    setCompareSelection((prev) =>
      value ? [...prev, code] : prev.filter((c) => c !== code)
    );
  };

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: {
      strategy_params: {},
    },
    context: {
      bf: toggles.BF,
      ls: toggles.LS,
      ebx: toggles.EBX,
      delay: toggles.CD,
      interest: toggles.IO,
    },
    resolver: yupResolver(schema),
  });

  const [rows, setRows] = useState([]);

  const onSubmit = async (data: FormValues) => {
    const body: any = {
      scenario: {
        params: data.strategy_params,
      },
    };
    let url = '/api/v1/simulate';
    if (mode === 'compare') {
      url = '/api/v1/compare';
      body.strategies = compareSelection;
    } else {
      body.strategy_code = selectedStrategy;
    }
    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!resp.ok) throw new Error('request failed');
      const result = await resp.json();
      setRows(result.yearly_results || []);
    } catch (err) {
      console.error(err);
    }
  };

  const columns: GridColDef[] = [
    { field: 'year', headerName: 'Year', width: 80 },
    {
      field: 'tax_payable',
      headerName: 'Tax Payable',
      width: 120,
      description: 'Includes any OAS recovery tax (clawback)',
    },
    { field: 'net_income', headerName: 'Net Income', width: 120 },
  ];

  const renderParamFields = (code: StrategyCodeEnum) => {
    switch (code) {
      case 'BF':
        return (
          <Controller
            name="strategy_params.bracket_fill_ceiling"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Income ceiling ($)"
                error={!!errors.strategy_params?.bracket_fill_ceiling}
                helperText={errors.strategy_params?.bracket_fill_ceiling?.message}
                type="number"
                fullWidth
                margin="normal"
              />
            )}
          />
        );
      case 'LS':
        return (
          <Box>
            <Controller
              name="strategy_params.lump_sum_amount"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Lump-Sum ($)"
                  error={!!errors.strategy_params?.lump_sum_amount}
                  helperText={errors.strategy_params?.lump_sum_amount?.message}
                  type="number"
                  fullWidth
                  margin="normal"
                />
              )}
            />
            <Controller
              name="strategy_params.lump_sum_year_offset"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Year Offset"
                  error={!!errors.strategy_params?.lump_sum_year_offset}
                  helperText={errors.strategy_params?.lump_sum_year_offset?.message}
                  type="number"
                  fullWidth
                  margin="normal"
                />
              )}
            />
          </Box>
        );
      case 'EBX':
        return (
          <Controller
            name="strategy_params.target_depletion_age"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Deplete RRIF by age"
                error={!!errors.strategy_params?.target_depletion_age}
                helperText={errors.strategy_params?.target_depletion_age?.message}
                type="number"
                fullWidth
                margin="normal"
              />
            )}
          />
        );
      case 'CD':
        return (
          <Box>
            <Controller
              name="strategy_params.cpp_start_age"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="CPP start age"
                  error={!!errors.strategy_params?.cpp_start_age}
                  helperText={errors.strategy_params?.cpp_start_age?.message}
                  type="number"
                  fullWidth
                  margin="normal"
                />
              )}
            />
            <Controller
              name="strategy_params.oas_start_age"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="OAS start age"
                  error={!!errors.strategy_params?.oas_start_age}
                  helperText={errors.strategy_params?.oas_start_age?.message}
                  type="number"
                  fullWidth
                  margin="normal"
                />
              )}
            />
          </Box>
        );
      case 'IO':
        return (
          <Box>
            <Controller
              name="strategy_params.interest_rate"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Loan interest rate %"
                  error={!!errors.strategy_params?.interest_rate}
                  helperText={errors.strategy_params?.interest_rate?.message}
                  type="number"
                  fullWidth
                  margin="normal"
                />
              )}
            />
            <Controller
              name="strategy_params.loan_pct_rrif"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Loan % of RRIF (0-100)"
                  error={!!errors.strategy_params?.loan_pct_rrif}
                  helperText={errors.strategy_params?.loan_pct_rrif?.message}
                  type="number"
                  fullWidth
                  margin="normal"
                />
              )}
            />
          </Box>
        );
      default:
        return null;
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ p: 2 }}>
      <FormControlLabel
        control={
          <Checkbox
            checked={mode === 'compare'}
            onChange={(_, v) => setMode(v ? 'compare' : 'simulate')}
          />
        }
        label="Compare multiple strategies"
      />

      {mode === 'simulate' ? (
        <TextField
          select
          label="Strategy"
          value={selectedStrategy}
          onChange={(e) =>
            setSelectedStrategy(e.target.value as StrategyCodeEnum)
          }
          fullWidth
          margin="normal"
        >
          {ALL_STRATEGIES.map((s) => (
            <MenuItem key={s.code} value={s.code}>
              {s.label}
            </MenuItem>
          ))}
        </TextField>
      ) : (
        <FormGroup>
          {ALL_STRATEGIES.map((s) => (
            <FormControlLabel
              key={s.code}
              control={
                <Checkbox
                  checked={compareSelection.includes(s.code)}
                  onChange={(_, v) => handleCompareSelect(s.code, v)}
                />
              }
              label={s.label}
            />
          ))}
        </FormGroup>
      )}

      {ALL_STRATEGIES.map((s) => (
        <Box key={`params-${s.code}`}>
          <FormControlLabel
            control={
              <Checkbox
                checked={toggles[s.code]}
                onChange={(_, v) => handleToggle(s.code, v)}
              />
            }
            label={s.label}
          />
          {toggles[s.code] && renderParamFields(s.code)}
        </Box>
      ))}

      <Box mt={2}>
        <Button type="submit" variant="contained">
          {mode === 'compare' ? 'Compare' : 'Simulate'}
        </Button>
      </Box>

      {rows.length > 0 && (
        <Box mt={4} height={300}>
          <Typography variant="h6" gutterBottom>
            Results
          </Typography>
          <DataGrid rows={rows} columns={columns} disableRowSelectionOnClick />
        </Box>
      )}
    </Box>
  );
}
