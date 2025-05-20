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
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import type { GridColDef } from '@mui/x-data-grid';
import type { StrategyParamsInput } from '../types/api';
import { Tooltip } from 'react-tooltip';
import 'react-tooltip/dist/react-tooltip.css';

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
      <FormControlLabel
        control={<Checkbox checked={bf} onChange={(_, v) => setBf(v)} />}
        label={
          <span>
            Bracket Filling
            <span
              className="ml-1 text-sm text-blue-600 cursor-pointer"
              data-tooltip-id="sim-bf-checkbox-info"
              data-tooltip-content="Enable bracket-filling strategy"
            >
              ℹ️
            </span>
            <Tooltip id="sim-bf-checkbox-info" place="top" />
          </span>
        }
      />
      {bf && (
        <Controller
          name="strategy_params.bracket_fill_ceiling"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label={
                <span>
                  Income ceiling ($)
                  <span
                    className="ml-1 text-sm text-blue-600 cursor-pointer"
                    data-tooltip-id="sim-bf-ceiling-info"
                    data-tooltip-content="Income ceiling used for Bracket-Filling strategy"
                  >
                    ℹ️
                  </span>
                  <Tooltip id="sim-bf-ceiling-info" place="top" />
                </span>
              }
              error={!!errors.strategy_params?.bracket_fill_ceiling}
              helperText={errors.strategy_params?.bracket_fill_ceiling?.message}
              type="number"
              fullWidth
              margin="normal"
            />
          )}
        />
      )}

      <FormControlLabel
        control={<Checkbox checked={ls} onChange={(_, v) => setLs(v)} />}
        label={
          <span>
            Lump-Sum
            <span
              className="ml-1 text-sm text-blue-600 cursor-pointer"
              data-tooltip-id="sim-ls-checkbox-info"
              data-tooltip-content="Enable lump-sum withdrawal"
            >
              ℹ️
            </span>
            <Tooltip id="sim-ls-checkbox-info" place="top" />
          </span>
        }
      />
      {ls && (
        <Box>
          <Controller
            name="strategy_params.lump_sum_amount"
            control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label={
                <span>
                  Lump-Sum ($)
                  <span
                    className="ml-1 text-sm text-blue-600 cursor-pointer"
                    data-tooltip-id="sim-ls-amount-info"
                    data-tooltip-content="One-time withdrawal amount"
                  >
                    ℹ️
                  </span>
                  <Tooltip id="sim-ls-amount-info" place="top" />
                </span>
              }
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
                label={
                  <span>
                    Year Offset
                    <span
                      className="ml-1 text-sm text-blue-600 cursor-pointer"
                      data-tooltip-id="sim-ls-offset-info"
                      data-tooltip-content="Years from start to withdraw lump sum"
                    >
                      ℹ️
                    </span>
                    <Tooltip id="sim-ls-offset-info" place="top" />
                  </span>
                }
                error={!!errors.strategy_params?.lump_sum_year_offset}
                helperText={errors.strategy_params?.lump_sum_year_offset?.message}
                type="number"
                fullWidth
                margin="normal"
              />
            )}
          />
        </Box>
      )}

      <FormControlLabel
        control={<Checkbox checked={ebx} onChange={(_, v) => setEbx(v)} />}
        label={
          <span>
            Empty-by-X
            <span
              className="ml-1 text-sm text-blue-600 cursor-pointer"
              data-tooltip-id="sim-ebx-checkbox-info"
              data-tooltip-content="Withdraw so RRIF is empty by target age"
            >
              ℹ️
            </span>
            <Tooltip id="sim-ebx-checkbox-info" place="top" />
          </span>
        }
      />
      {ebx && (
        <Controller
          name="strategy_params.target_depletion_age"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label={
                <span>
                  Deplete RRIF by age
                  <span
                    className="ml-1 text-sm text-blue-600 cursor-pointer"
                    data-tooltip-id="sim-target-age-info"
                    data-tooltip-content="Age by which RRIF should be depleted"
                  >
                    ℹ️
                  </span>
                  <Tooltip id="sim-target-age-info" place="top" />
                </span>
              }
              error={!!errors.strategy_params?.target_depletion_age}
              helperText={errors.strategy_params?.target_depletion_age?.message}
              type="number"
              fullWidth
              margin="normal"
            />
          )}
        />
      )}

      <FormControlLabel
        control={<Checkbox checked={delay} onChange={(_, v) => setDelay(v)} />}
        label={
          <span>
            Delay CPP/OAS
            <span
              className="ml-1 text-sm text-blue-600 cursor-pointer"
              data-tooltip-id="sim-delay-checkbox-info"
              data-tooltip-content="Delay start of CPP and OAS benefits"
            >
              ℹ️
            </span>
            <Tooltip id="sim-delay-checkbox-info" place="top" />
          </span>
        }
      />
      {delay && (
        <Box>
          <Controller
            name="strategy_params.cpp_start_age"
            control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label={
                <span>
                  CPP start age
                  <span
                    className="ml-1 text-sm text-blue-600 cursor-pointer"
                    data-tooltip-id="sim-cpp-age-info"
                    data-tooltip-content="Age to begin CPP payments"
                  >
                    ℹ️
                  </span>
                  <Tooltip id="sim-cpp-age-info" place="top" />
                </span>
              }
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
                label={
                  <span>
                    OAS start age
                    <span
                      className="ml-1 text-sm text-blue-600 cursor-pointer"
                      data-tooltip-id="sim-oas-age-info"
                      data-tooltip-content="Age to begin OAS payments"
                    >
                      ℹ️
                    </span>
                    <Tooltip id="sim-oas-age-info" place="top" />
                  </span>
                }
                error={!!errors.strategy_params?.oas_start_age}
                helperText={errors.strategy_params?.oas_start_age?.message}
                type="number"
                fullWidth
                margin="normal"
              />
            )}
          />
        </Box>
      )}

      <FormControlLabel
        control={<Checkbox checked={interest} onChange={(_, v) => setInterest(v)} />}
        label={
          <span>
            Interest Offset
            <span
              className="ml-1 text-sm text-blue-600 cursor-pointer"
              data-tooltip-id="sim-interest-checkbox-info"
              data-tooltip-content="Borrow to offset interest costs"
            >
              ℹ️
            </span>
            <Tooltip id="sim-interest-checkbox-info" place="top" />
          </span>
        }
      />
      {interest && (
        <Box>
          <Controller
            name="strategy_params.interest_rate"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label={
                  <span>
                    Loan interest rate %
                    <span
                      className="ml-1 text-sm text-blue-600 cursor-pointer"
                      data-tooltip-id="sim-interest-rate-info"
                      data-tooltip-content="Interest rate on borrowed amount"
                    >
                      ℹ️
                    </span>
                    <Tooltip id="sim-interest-rate-info" place="top" />
                  </span>
                }
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
                label={
                  <span>
                    Loan % of RRIF (0-100)
                    <span
                      className="ml-1 text-sm text-blue-600 cursor-pointer"
                      data-tooltip-id="sim-loan-pct-info"
                      data-tooltip-content="Loan size as percentage of RRIF"
                    >
                      ℹ️
                    </span>
                    <Tooltip id="sim-loan-pct-info" place="top" />
                  </span>
                }
                error={!!errors.strategy_params?.loan_pct_rrif}
                helperText={errors.strategy_params?.loan_pct_rrif?.message}
                type="number"
                fullWidth
                margin="normal"
              />
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
