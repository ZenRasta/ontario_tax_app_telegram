import React from "react";
import {
  Box,
  Grid,
  TextField,
  FormControlLabel,
  Checkbox,
  Tooltip,
  IconButton,
  Typography,
  Button,
} from "@mui/material";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import type { FormData } from "../types/formData";

const fieldLimits = {
  age: { min: 55, max: 95, step: 1 },
  rrspBalance: { min: 1000, max: 50000000, step: 1000 },
  tfsaBalance: { min: 0, max: 500000, step: 1000 },
  cppAmount: { min: 0, max: 25000, step: 100 },
  oasAmount: { min: 0, max: 10000, step: 100 },
  desiredSpending: { min: 10000, max: 500000, step: 1000 },
  expectedReturn: { min: 1, max: 15, step: 0.1 },
  stdDevReturn: { min: 1, max: 40, step: 0.1 },
  horizonYears: { min: 5, max: 50, step: 1 },
  bracketFillCeiling: { min: 20000, max: 200000, step: 1000 },
  cppStartAge: { min: 60, max: 70, step: 1 },
  lumpSumYearOffset: { min: 1, max: null, step: 1 }, // max = horizonYears
  emptyByAge: { min: null, max: 100, step: 1 }, // min = currentAge + 5
};

interface InputFormStepProps {
  data: FormData;
  onChange: (updates: Partial<FormData>) => void;
  onBack: () => void;
  onSubmit: () => void;
}

/**
 * Step 3 of the wizard – gathers all numeric inputs.
 * Shows spouse and advanced-strategy fields conditionally.
 */
const InputFormStep: React.FC<InputFormStepProps> = ({
  data,
  onChange,
  onBack,
  onSubmit,
}) => {
  /** generic handler for <TextField> */
  const handleInputChange =
    (field: keyof FormData) => (e: React.ChangeEvent<HTMLInputElement>) => {
      const value =
        e.target.type === "number" ? Number(e.target.value) : e.target.value;
      onChange({ [field]: value } as Partial<FormData>);
    };

  /** marital-status toggle */
  const handleMarriedChange = (
    _: React.ChangeEvent<HTMLInputElement>,
    checked: boolean
  ) => onChange({ married: checked });

  // Boolean flags to decide which advanced fields show
  const { strategies } = data;
  const hasBF = strategies.includes("BF");
  const hasDelay = strategies.includes("CD");
  const hasLS = strategies.includes("LS");
  const hasEBX = strategies.includes("EBX");

  const CPP_MAX = 17060;
  const OAS_MAX = 8250;
  const cppAmountError = data.cppAmount > CPP_MAX;
  const oasAmountError = data.oasAmount > OAS_MAX;
  const spouseCppAmountError =
    data.spouseCppAmount !== undefined && data.spouseCppAmount > CPP_MAX;
  const spouseOasAmountError =
    data.spouseOasAmount !== undefined && data.spouseOasAmount > OAS_MAX;

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        3. Enter Your Details
      </Typography>

      {/* -------------- BASIC FIELDS ---------------------------------- */}
      <Grid container spacing={2}>
        {/* Left column */}
        <Grid item xs={12} sm={6}>
          {/* Age */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                Age
                <Tooltip title="Your current age. RRIF withdrawals typically begin at age 65, but planning can start earlier.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.age}
            onChange={handleInputChange("age")}
            margin="normal"
            inputProps={fieldLimits.age}
          />

          {/* CPP at 65 */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                CPP @ 65
                <Tooltip title="Expected annual Canada Pension Plan benefit at age 65. Maximum CPP in 2025 is approximately $18,000. You can start as early as age 60 (reduced) or delay to age 70 (increased).">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.cppAmount}
            onChange={handleInputChange("cppAmount")}
            margin="normal"
            inputProps={fieldLimits.cppAmount}
            error={cppAmountError}
            helperText={cppAmountError ? `Maximum CPP amount is $${CPP_MAX}` : undefined}
          />

          {/* TFSA */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                TFSA Balance
                <Tooltip title="Tax-Free Savings Account balance. TFSA withdrawals are tax-free and have no mandatory minimums, making them valuable for tax optimization.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.tfsaBalance}
            onChange={handleInputChange("tfsaBalance")}
            margin="normal"
            inputProps={fieldLimits.tfsaBalance}
          />

          {/* Expected return */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                Expected Return %
                <Tooltip title="Expected annual investment return before inflation. Conservative: 3-5%, Moderate: 5-7%, Aggressive: 7-10%. Higher returns increase portfolio longevity but add volatility risk.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.expectedReturn}
            onChange={handleInputChange("expectedReturn")}
            margin="normal"
            inputProps={fieldLimits.expectedReturn}
          />

          {/* Horizon */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                Horizon (years)
                <Tooltip title="Planning time horizon. Typical retirement planning uses 25-30 years. Longer horizons show the impact of sustained withdrawals and investment growth.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.horizon}
            onChange={handleInputChange("horizon")}
            margin="normal"
            inputProps={fieldLimits.horizonYears}
          />
        </Grid>

        {/* Right column */}
        <Grid item xs={12} sm={6}>
          {/* RRSP */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                RRSP Balance
                <Tooltip title="Current balance in your Registered Retirement Savings Plan or Registered Retirement Income Fund. This is your primary retirement savings that will be subject to mandatory minimum withdrawals.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.rrspBalance}
            onChange={handleInputChange("rrspBalance")}
            margin="normal"
            inputProps={fieldLimits.rrspBalance}
          />

          {/* OAS @65 */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                OAS @ 65
                <Tooltip title="Expected annual Old Age Security benefit at age 65. Maximum OAS in 2025 is approximately $8,500. Available to Canadian residents with 40+ years in Canada. Subject to clawback on high incomes.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.oasAmount}
            onChange={handleInputChange("oasAmount")}
            margin="normal"
            inputProps={fieldLimits.oasAmount}
            error={oasAmountError}
            helperText={oasAmountError ? `Maximum OAS amount is $${OAS_MAX}` : undefined}
          />

          {/* Desired spending */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                Desired Spending
                <Tooltip title="Annual after-tax spending goal in today's dollars. Consider housing, food, healthcare, travel, and other lifestyle expenses. The app will determine how to fund this from your retirement accounts.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.desiredSpending}
            onChange={handleInputChange("desiredSpending")}
            margin="normal"
            inputProps={fieldLimits.desiredSpending}
          />

          {/* Volatility */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                Std Dev Return %
                <Tooltip title="Investment volatility measure. Conservative portfolios: 5-10%, Balanced: 8-15%, Aggressive: 15-25%. Higher volatility can improve long-term returns but increases year-to-year variation.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.stdDevReturn}
            onChange={handleInputChange("stdDevReturn")}
            margin="normal"
            inputProps={fieldLimits.stdDevReturn}
          />

          {/* Married toggle */}
          <Box mt={2}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={data.married}
                  onChange={handleMarriedChange}
                  color="primary"
                />
              }
              label="Married (include spouse)"
            />
            <Tooltip title="Tick if you want to include your spouse’s info.">
              <InfoOutlinedIcon
                fontSize="small"
                sx={{ verticalAlign: "middle", ml: 0.5 }}
              />
            </Tooltip>
          </Box>
        </Grid>
      </Grid>

      {/* -------------- SPOUSE FIELDS ---------------------------------- */}
      {data.married && (
        <Box mt={2}>
          <Typography variant="subtitle1">Spouse Information</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              {/* Spouse Age */}
              <TextField
                fullWidth
                type="number"
                label={
                  <Box display="flex" alignItems="center">
                    Spouse Age
                    <Tooltip title="Spouse's current age. Age differences affect optimal withdrawal sequencing and government benefit timing.">
                      <IconButton size="small" sx={{ ml: 0.5 }}>
                        <InfoOutlinedIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                }
                value={data.spouseAge ?? ""}
                onChange={handleInputChange("spouseAge")}
                margin="normal"
                inputProps={fieldLimits.age}
              />
              {/* Spouse CPP */}
              <TextField
                fullWidth
                type="number"
                label={
                  <Box display="flex" alignItems="center">
                    Spouse CPP @ 65
                    <Tooltip title="Spouse's expected government benefits. Timing these benefits relative to the primary person can optimize household taxes.">
                      <IconButton size="small" sx={{ ml: 0.5 }}>
                        <InfoOutlinedIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                }
                value={data.spouseCppAmount ?? ""}
                onChange={handleInputChange("spouseCppAmount")}
                margin="normal"
                inputProps={fieldLimits.cppAmount}
                error={spouseCppAmountError}
                helperText={
                  spouseCppAmountError ? `Maximum CPP amount is $${CPP_MAX}` : undefined
                }
              />
              {/* Spouse TFSA */}
              <TextField
                fullWidth
                type="number"
                label={
                  <Box display="flex" alignItems="center">
                    Spouse TFSA Balance
                    <Tooltip title="Spouse's Tax-Free Savings Account balance. Can be used strategically to supplement income without affecting tax brackets.">
                      <IconButton size="small" sx={{ ml: 0.5 }}>
                        <InfoOutlinedIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                }
                value={data.spouseTfsaBalance ?? ""}
                onChange={handleInputChange("spouseTfsaBalance")}
                margin="normal"
                inputProps={fieldLimits.tfsaBalance}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              {/* Spouse RRSP */}
              <TextField
                fullWidth
                type="number"
                label={
                  <Box display="flex" alignItems="center">
                    Spouse RRSP Balance
                    <Tooltip title="Spouse's registered retirement savings. Lower-income spouse should typically withdraw first to minimize household taxes.">
                      <IconButton size="small" sx={{ ml: 0.5 }}>
                        <InfoOutlinedIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                }
                value={data.spouseRrspBalance ?? ""}
                onChange={handleInputChange("spouseRrspBalance")}
                margin="normal"
                inputProps={fieldLimits.rrspBalance}
              />
              {/* Spouse OAS */}
              <TextField
                fullWidth
                type="number"
                label={
                  <Box display="flex" alignItems="center">
                    Spouse OAS @ 65
                    <Tooltip title="Spouse's expected government benefits. Timing these benefits relative to the primary person can optimize household taxes.">
                      <IconButton size="small" sx={{ ml: 0.5 }}>
                        <InfoOutlinedIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                }
                value={data.spouseOasAmount ?? ""}
                onChange={handleInputChange("spouseOasAmount")}
                margin="normal"
                inputProps={fieldLimits.oasAmount}
                error={spouseOasAmountError}
                helperText={
                  spouseOasAmountError ? `Maximum OAS amount is $${OAS_MAX}` : undefined
                }
              />
            </Grid>
          </Grid>
        </Box>
      )}

      {/* -------------- ADVANCED STRATEGY FIELDS ----------------------- */}
      {(hasBF || hasDelay || hasLS || hasEBX) && (
        <Box mt={3}>
          <Typography variant="subtitle1">Advanced Strategy Settings</Typography>
          <Grid container spacing={2}>
            {hasBF && (
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label={
                    <Box display="flex" alignItems="center">
                      Bracket-Fill Ceiling ($)
                      <Tooltip title="Maximum income target for bracket-filling strategy. Common targets: $55,867 (top of 15% federal bracket), $90,997 (OAS clawback threshold). Higher ceilings mean more current taxes but potentially lower lifetime taxes.">
                        <IconButton size="small" sx={{ ml: 0.5 }}>
                          <InfoOutlinedIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  }
                  value={data.bracketFillCeiling ?? ""}
                  onChange={handleInputChange("bracketFillCeiling")}
                  margin="normal"
                  inputProps={fieldLimits.bracketFillCeiling}
                />
              </Grid>
            )}

            {hasDelay && (
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label={
                    <Box display="flex" alignItems="center">
                      CPP Start Age
                      <Tooltip title="Age to start Canada Pension Plan. Early (60-64): reduced benefits, Normal (65): full benefits, Delayed (66-70): enhanced benefits (+0.7% per month). Delaying can be beneficial if you don't need the income immediately.">
                        <IconButton size="small" sx={{ ml: 0.5 }}>
                          <InfoOutlinedIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  }
                  value={data.cppStartAge ?? ""}
                  onChange={handleInputChange("cppStartAge")}
                  margin="normal"
                  inputProps={fieldLimits.cppStartAge}
                />
              </Grid>
            )}

            {hasLS && (
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label={
                    <Box display="flex" alignItems="center">
                      Lump-Sum Year Offset
                      <Tooltip title="Year to take a large withdrawal (relative to start of plan). Useful for major expenses like home renovations, travel, or gifts to children. Strategy will optimize when this withdrawal has the least tax impact.">
                        <IconButton size="small" sx={{ ml: 0.5 }}>
                          <InfoOutlinedIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  }
                  value={data.lumpSumYear ?? ""}
                  onChange={handleInputChange("lumpSumYear")}
                  margin="normal"
                  inputProps={{ ...fieldLimits.lumpSumYearOffset, max: data.horizon }}
                />
              </Grid>
            )}

            {hasEBX && (
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label={
                    <Box display="flex" alignItems="center">
                      Empty-by Age
                      <Tooltip title="Target age to fully deplete registered accounts. Earlier depletion reduces future mandatory withdrawals and taxes but requires higher current withdrawals. Useful for estate planning.">
                        <IconButton size="small" sx={{ ml: 0.5 }}>
                          <InfoOutlinedIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  }
                  value={data.emptyByAge ?? ""}
                  onChange={handleInputChange("emptyByAge")}
                  margin="normal"
                  inputProps={{ ...fieldLimits.emptyByAge, min: data.age + 5 }}
                />
              </Grid>
            )}
          </Grid>
        </Box>
      )}

      {/* -------------- NAV BUTTONS ------------------------------------ */}
      <Box mt={4} textAlign="right">
        <Button variant="outlined" onClick={onBack} sx={{ mr: 2 }}>
          Back
        </Button>
        <Button variant="contained" onClick={onSubmit}>
          Run Simulation
        </Button>
      </Box>
    </Box>
  );
};

export default InputFormStep;

