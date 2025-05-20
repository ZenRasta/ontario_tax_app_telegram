import { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import {
  Box,
  Checkbox,
  FormControlLabel,
  TextField,
  Button,
  Typography,
  MenuItem,
} from '@mui/material';
import { Tooltip } from 'react-tooltip';
import 'react-tooltip/dist/react-tooltip.css';
import { DataGrid } from '@mui/x-data-grid';
import type { GridColDef } from '@mui/x-data-grid';
import type { StrategyParamsInput } from '../types/api';
import { strategies } from '../strategies';

interface FormValues {
  strategy_params: StrategyParamsInput;
  strategy_code: string;
}

const schema = yup.object({
  strategy_code: yup.string().required(),
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
  const [bf, setBf] = useState(false);
  const [ls, setLs] = useState(false);
  const [ebx, setEbx] = useState(false);
  const [delay, setDelay] = useState(false);
  const [interest, setInterest] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: {
      strategy_params: {},
      strategy_code: 'GM',
    },
    context: { bf, ls, ebx, delay, interest },
    resolver: yupResolver(schema),
  });

  const [rows, setRows] = useState([]);

  const onSubmit = async (data: FormValues) => {
    const body = {
      scenario: {
        params: data.strategy_params,
      },
      strategy_code: data.strategy_code,
    };
    try {
      const resp = await fetch('/api/v1/simulate', {
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

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ p: 2 }}>
      <Controller
        name="strategy_code"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            select
            label="Strategy"
            fullWidth
            margin="normal"
            error={!!errors.strategy_code}
            helperText={errors.strategy_code?.message}
          >
            {strategies.map((s) => (
              <MenuItem key={s.code} value={s.code}>
                {s.label}
              </MenuItem>
            ))}
          </TextField>
        )}
      />
      <FormControlLabel
        control={<Checkbox checked={bf} onChange={(_, v) => setBf(v)} />}
        label="Bracket Filling"
      />
      {bf && (
        <Controller
          name="strategy_params.bracket_fill_ceiling"
          control={control}
          render={({ field }) => (
            <Box display="flex" alignItems="center">
              <TextField
                {...field}
                label="Income ceiling ($)"
                error={!!errors.strategy_params?.bracket_fill_ceiling}
                helperText={errors.strategy_params?.bracket_fill_ceiling?.message}
                type="number"
                fullWidth
                margin="normal"
              />
              <span
                className="ml-1 text-sm text-blue-600 cursor-pointer"
                data-tooltip-id="bf-ceiling-tip"
                data-tooltip-content="Bracket Fill Ceiling – taxable income target"
                aria-label="Bracket Fill Ceiling info"
                aria-describedby="bf-ceiling-tip"
                role="button"
                tabIndex={0}
              >
                ℹ️
              </span>
              <Tooltip id="bf-ceiling-tip" place="top" />
            </Box>
          )}
        />
      )}

      <FormControlLabel
        control={<Checkbox checked={ls} onChange={(_, v) => setLs(v)} />}
        label="Lump-Sum"
      />
      {ls && (
        <Box>
          <Controller
            name="strategy_params.lump_sum_amount"
            control={control}
          render={({ field }) => (
            <Box display="flex" alignItems="center">
              <TextField
                {...field}
                label="Lump-Sum ($)"
                error={!!errors.strategy_params?.lump_sum_amount}
                helperText={errors.strategy_params?.lump_sum_amount?.message}
                type="number"
                fullWidth
                margin="normal"
              />
              <span
                className="ml-1 text-sm text-blue-600 cursor-pointer"
                data-tooltip-id="ls-amount-tip"
                data-tooltip-content="One-time withdrawal amount"
                aria-label="Lump Sum Amount info"
                aria-describedby="ls-amount-tip"
                role="button"
                tabIndex={0}
              >
                ℹ️
              </span>
              <Tooltip id="ls-amount-tip" place="top" />
            </Box>
          )}
          />
          <Controller
            name="strategy_params.lump_sum_year_offset"
            control={control}
          render={({ field }) => (
            <Box display="flex" alignItems="center">
              <TextField
                {...field}
                label="Year Offset"
                error={!!errors.strategy_params?.lump_sum_year_offset}
                helperText={errors.strategy_params?.lump_sum_year_offset?.message}
                type="number"
                fullWidth
                margin="normal"
              />
              <span
                className="ml-1 text-sm text-blue-600 cursor-pointer"
                data-tooltip-id="ls-offset-tip"
                data-tooltip-content="Years from now to take lump sum"
                aria-label="Lump Sum Year Offset info"
                aria-describedby="ls-offset-tip"
                role="button"
                tabIndex={0}
              >
                ℹ️
              </span>
              <Tooltip id="ls-offset-tip" place="top" />
            </Box>
          )}
          />
        </Box>
      )}

      <FormControlLabel
        control={<Checkbox checked={ebx} onChange={(_, v) => setEbx(v)} />}
        label="Empty-by-X"
      />
      {ebx && (
        <Controller
          name="strategy_params.target_depletion_age"
          control={control}
          render={({ field }) => (
            <Box display="flex" alignItems="center">
              <TextField
                {...field}
                label="Deplete RRIF by age"
                error={!!errors.strategy_params?.target_depletion_age}
                helperText={errors.strategy_params?.target_depletion_age?.message}
                type="number"
                fullWidth
                margin="normal"
              />
              <span
                className="ml-1 text-sm text-blue-600 cursor-pointer"
                data-tooltip-id="deplete-age-tip"
                data-tooltip-content="Age by which RRIF should be empty"
                aria-label="Target Depletion Age info"
                aria-describedby="deplete-age-tip"
                role="button"
                tabIndex={0}
              >
                ℹ️
              </span>
              <Tooltip id="deplete-age-tip" place="top" />
            </Box>
          )}
        />
      )}

      <FormControlLabel
        control={<Checkbox checked={delay} onChange={(_, v) => setDelay(v)} />}
        label="Delay CPP/OAS"
      />
      {delay && (
        <Box>
          <Controller
            name="strategy_params.cpp_start_age"
            control={control}
          render={({ field }) => (
            <Box display="flex" alignItems="center">
              <TextField
                {...field}
                label="CPP start age"
                error={!!errors.strategy_params?.cpp_start_age}
                helperText={errors.strategy_params?.cpp_start_age?.message}
                type="number"
                fullWidth
                margin="normal"
              />
              <span
                className="ml-1 text-sm text-blue-600 cursor-pointer"
                data-tooltip-id="cpp-age-tip"
                data-tooltip-content="Age when CPP starts"
                aria-label="CPP Start Age info"
                aria-describedby="cpp-age-tip"
                role="button"
                tabIndex={0}
              >
                ℹ️
              </span>
              <Tooltip id="cpp-age-tip" place="top" />
            </Box>
          )}
          />
          <Controller
            name="strategy_params.oas_start_age"
            control={control}
          render={({ field }) => (
            <Box display="flex" alignItems="center">
              <TextField
                {...field}
                label="OAS start age"
                error={!!errors.strategy_params?.oas_start_age}
                helperText={errors.strategy_params?.oas_start_age?.message}
                type="number"
                fullWidth
                margin="normal"
              />
              <span
                className="ml-1 text-sm text-blue-600 cursor-pointer"
                data-tooltip-id="oas-age-tip"
                data-tooltip-content="Age when OAS starts"
                aria-label="OAS Start Age info"
                aria-describedby="oas-age-tip"
                role="button"
                tabIndex={0}
              >
                ℹ️
              </span>
              <Tooltip id="oas-age-tip" place="top" />
            </Box>
          )}
          />
        </Box>
      )}

      <FormControlLabel
        control={<Checkbox checked={interest} onChange={(_, v) => setInterest(v)} />}
        label="Interest Offset"
      />
      {interest && (
        <Box>
          <Controller
            name="strategy_params.interest_rate"
            control={control}
          render={({ field }) => (
            <Box display="flex" alignItems="center">
              <TextField
                {...field}
                label="Loan interest rate %"
                error={!!errors.strategy_params?.interest_rate}
                helperText={errors.strategy_params?.interest_rate?.message}
                type="number"
                fullWidth
                margin="normal"
              />
              <span
                className="ml-1 text-sm text-blue-600 cursor-pointer"
                data-tooltip-id="interest-rate-tip"
                data-tooltip-content="Interest rate for borrowing"
                aria-label="Loan Interest Rate info"
                aria-describedby="interest-rate-tip"
                role="button"
                tabIndex={0}
              >
                ℹ️
              </span>
              <Tooltip id="interest-rate-tip" place="top" />
            </Box>
          )}
          />
          <Controller
            name="strategy_params.loan_pct_rrif"
            control={control}
          render={({ field }) => (
            <Box display="flex" alignItems="center">
              <TextField
                {...field}
                label="Loan % of RRIF (0-100)"
                error={!!errors.strategy_params?.loan_pct_rrif}
                helperText={errors.strategy_params?.loan_pct_rrif?.message}
                type="number"
                fullWidth
                margin="normal"
              />
              <span
                className="ml-1 text-sm text-blue-600 cursor-pointer"
                data-tooltip-id="loan-pct-tip"
                data-tooltip-content="Loan amount as percentage of RRIF"
                aria-label="Loan % of RRIF info"
                aria-describedby="loan-pct-tip"
                role="button"
                tabIndex={0}
              >
                ℹ️
              </span>
              <Tooltip id="loan-pct-tip" place="top" />
            </Box>
          )}
          />
        </Box>
      )}

      <Box mt={2}>
        <Button type="submit" variant="contained">Simulate</Button>
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
