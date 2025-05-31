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
  age: { min: 50, max: 100, step: 1 },
  rrspBalance: { min: 100, max: 50000000, step: 1000 },
  tfsaBalance: { min: 0, max: 200000, step: 1000 },
  cppAmount: { min: 0, max: 18000, step: 100 },
  oasAmount: { min: 0, max: 10000, step: 100 },
  desiredSpending: { min: 20000, max: 300000, step: 1000 },
  expectedReturn: { min: 0.5, max: 12, step: 0.1 },
  stdDevReturn: { min: 0.5, max: 25, step: 0.1 },
  horizonYears: { min: 5, max: 40, step: 1 },
  bracketFillCeiling: { min: 30000, max: 250000, step: 1000 },
  cppStartAge: { min: 60, max: 70, step: 1 },
  lumpSumYearOffset: { min: 1, max: null, step: 1 }, // max = horizonYears
  lumpSumAmount: { min: 1000, max: 500000, step: 1000 },
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
  const OAS_MAX = 8500;
  const cppGovError = data.cppAmount > CPP_MAX;
  const oasGovError = data.oasAmount > OAS_MAX;
  const spouseCppGovError =
    data.spouseCppAmount !== undefined && data.spouseCppAmount > CPP_MAX;
  const spouseOasGovError =
    data.spouseOasAmount !== undefined && data.spouseOasAmount > OAS_MAX;

  const isAgeError = data.age < fieldLimits.age.min || data.age > fieldLimits.age.max;
  const isRrspBalanceError =
    data.rrspBalance < fieldLimits.rrspBalance.min ||
    data.rrspBalance > fieldLimits.rrspBalance.max;
  const isTfsaBalanceError =
    data.tfsaBalance < fieldLimits.tfsaBalance.min ||
    data.tfsaBalance > fieldLimits.tfsaBalance.max;
  const isCppAmountError =
    data.cppAmount < fieldLimits.cppAmount.min ||
    data.cppAmount > fieldLimits.cppAmount.max;
  const isOasAmountError =
    data.oasAmount < fieldLimits.oasAmount.min ||
    data.oasAmount > fieldLimits.oasAmount.max;
  const isDesiredSpendingError =
    data.desiredSpending < fieldLimits.desiredSpending.min ||
    data.desiredSpending > fieldLimits.desiredSpending.max;
  const isExpectedReturnError =
    data.expectedReturn < fieldLimits.expectedReturn.min ||
    data.expectedReturn > fieldLimits.expectedReturn.max;
  const isStdDevReturnError =
    data.stdDevReturn < fieldLimits.stdDevReturn.min ||
    data.stdDevReturn > fieldLimits.stdDevReturn.max;
  const isHorizonError =
    data.horizon < fieldLimits.horizonYears.min ||
    data.horizon > fieldLimits.horizonYears.max;

  const isSpouseAgeError =
    data.spouseAge !== undefined &&
    (data.spouseAge < fieldLimits.age.min || data.spouseAge > fieldLimits.age.max);
  const isSpouseRrspBalanceError =
    data.spouseRrspBalance !== undefined &&
    (data.spouseRrspBalance < fieldLimits.rrspBalance.min ||
      data.spouseRrspBalance > fieldLimits.rrspBalance.max);
  const isSpouseTfsaBalanceError =
    data.spouseTfsaBalance !== undefined &&
    (data.spouseTfsaBalance < fieldLimits.tfsaBalance.min ||
      data.spouseTfsaBalance > fieldLimits.tfsaBalance.max);
  const isSpouseCppAmountError =
    data.spouseCppAmount !== undefined &&
    (data.spouseCppAmount < fieldLimits.cppAmount.min ||
      data.spouseCppAmount > fieldLimits.cppAmount.max);
  const isSpouseOasAmountError =
    data.spouseOasAmount !== undefined &&
    (data.spouseOasAmount < fieldLimits.oasAmount.min ||
      data.spouseOasAmount > fieldLimits.oasAmount.max);

  const isBracketFillCeilingError =
    data.bracketFillCeiling !== undefined &&
    (data.bracketFillCeiling < fieldLimits.bracketFillCeiling.min ||
      data.bracketFillCeiling > fieldLimits.bracketFillCeiling.max);
  const isCppStartAgeError =
    data.cppStartAge !== undefined &&
    (data.cppStartAge < fieldLimits.cppStartAge.min ||
      data.cppStartAge > fieldLimits.cppStartAge.max);
  const isLumpSumAmountError =
    data.lumpSumAmount !== undefined &&
    (data.lumpSumAmount < fieldLimits.lumpSumAmount.min ||
      data.lumpSumAmount > fieldLimits.lumpSumAmount.max);
  const isLumpSumYearError =
    data.lumpSumYear !== undefined &&
    (data.lumpSumYear < fieldLimits.lumpSumYearOffset.min ||
      data.lumpSumYear > data.horizon);
  const isEmptyByAgeError =
    data.emptyByAge !== undefined &&
    (data.emptyByAge < data.age + 5 || data.emptyByAge > fieldLimits.emptyByAge.max);

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
                <Tooltip title="Your current age (50-100). RRIF withdrawals typically begin at age 65, but planning can start earlier.">
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
            error={isAgeError}
            helperText={
              isAgeError
                ? `Enter between ${fieldLimits.age.min} and ${fieldLimits.age.max}`
                : undefined
            }
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
            error={isCppAmountError || cppGovError}
            helperText={
              cppGovError
                ? `Maximum CPP amount is $${CPP_MAX}`
                : isCppAmountError
                  ? `Enter between ${fieldLimits.cppAmount.min} and ${fieldLimits.cppAmount.max}`
                  : undefined
            }
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
            error={isTfsaBalanceError}
            helperText={
              isTfsaBalanceError
                ? `Enter between ${fieldLimits.tfsaBalance.min} and ${fieldLimits.tfsaBalance.max}`
                : undefined
            }
          />

          {/* Expected return */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                Expected Return %
                <Tooltip title="Expected annual investment return before inflation. Typical ranges: 3-5% conservative to 8-10% aggressive. Allowed range 0.5%-12%. Higher returns increase portfolio longevity but add volatility risk.">
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
            error={isExpectedReturnError}
            helperText={
              isExpectedReturnError
                ? `Enter between ${fieldLimits.expectedReturn.min} and ${fieldLimits.expectedReturn.max}`
                : undefined
            }
          />

          {/* Horizon */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                Horizon (years)
                <Tooltip title="Planning time horizon. Typical retirement planning uses 25-30 years. Up to 40 years supported to show the impact of sustained withdrawals and investment growth.">
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
            error={isHorizonError}
            helperText={
              isHorizonError
                ? `Enter between ${fieldLimits.horizonYears.min} and ${fieldLimits.horizonYears.max}`
                : undefined
            }
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
            error={isRrspBalanceError}
            helperText={
              isRrspBalanceError
                ? `Enter between ${fieldLimits.rrspBalance.min} and ${fieldLimits.rrspBalance.max}`
                : undefined
            }
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
            error={isOasAmountError || oasGovError}
            helperText={
              oasGovError
                ? `Maximum OAS amount is $${OAS_MAX}`
                : isOasAmountError
                  ? `Enter between ${fieldLimits.oasAmount.min} and ${fieldLimits.oasAmount.max}`
                  : undefined
            }
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
            error={isDesiredSpendingError}
            helperText={
              isDesiredSpendingError
                ? `Enter between ${fieldLimits.desiredSpending.min} and ${fieldLimits.desiredSpending.max}`
                : undefined
            }
          />

          {/* Volatility */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                Std Dev Return %
                <Tooltip title="Investment volatility measure. Conservative portfolios: 5-10%, Balanced: 8-15%, Aggressive: 15-25%. Allowed range 0.5%-25%. Higher volatility can improve long-term returns but increases year-to-year variation.">
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
            error={isStdDevReturnError}
            helperText={
              isStdDevReturnError
                ? `Enter between ${fieldLimits.stdDevReturn.min} and ${fieldLimits.stdDevReturn.max}`
                : undefined
            }
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
                    <Tooltip title="Spouse's current age (50-100). Age differences affect optimal withdrawal sequencing and government benefit timing.">
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
                error={isSpouseAgeError}
                helperText={
                  isSpouseAgeError
                    ? `Enter between ${fieldLimits.age.min} and ${fieldLimits.age.max}`
                    : undefined
                }
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
                error={isSpouseCppAmountError || spouseCppGovError}
                helperText={
                  spouseCppGovError
                    ? `Maximum CPP amount is $${CPP_MAX}`
                    : isSpouseCppAmountError
                      ? `Enter between ${fieldLimits.cppAmount.min} and ${fieldLimits.cppAmount.max}`
                      : undefined
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
                error={isSpouseTfsaBalanceError}
                helperText={
                  isSpouseTfsaBalanceError
                    ? `Enter between ${fieldLimits.tfsaBalance.min} and ${fieldLimits.tfsaBalance.max}`
                    : undefined
                }
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
                error={isSpouseRrspBalanceError}
                helperText={
                  isSpouseRrspBalanceError
                    ? `Enter between ${fieldLimits.rrspBalance.min} and ${fieldLimits.rrspBalance.max}`
                    : undefined
                }
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
                error={isSpouseOasAmountError || spouseOasGovError}
                helperText={
                  spouseOasGovError
                    ? `Maximum OAS amount is $${OAS_MAX}`
                    : isSpouseOasAmountError
                      ? `Enter between ${fieldLimits.oasAmount.min} and ${fieldLimits.oasAmount.max}`
                      : undefined
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
                      <Tooltip title="Maximum income target for bracket-filling strategy. Common targets: $55,867 (top of 15% federal bracket), $90,997 (OAS clawback threshold). Allowed range $30k-$250k. Higher ceilings mean more current taxes but potentially lower lifetime taxes.">
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
                  error={isBracketFillCeilingError}
                  helperText={
                    isBracketFillCeilingError
                      ? `Enter between ${fieldLimits.bracketFillCeiling.min} and ${fieldLimits.bracketFillCeiling.max}`
                      : undefined
                  }
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
                  error={isCppStartAgeError}
                  helperText={
                    isCppStartAgeError
                      ? `Enter between ${fieldLimits.cppStartAge.min} and ${fieldLimits.cppStartAge.max}`
                      : undefined
                  }
                />
              </Grid>
            )}

            {hasLS && (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label={
                      <Box display="flex" alignItems="center">
                        Lump-Sum Amount ($)
                        <Tooltip title="Amount to withdraw as a lump sum in the specified year. Range: $1,000 - $500,000. Used for major expenses like home renovation, travel, or gifts to children.">
                          <IconButton size="small" sx={{ ml: 0.5 }}>
                            <InfoOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    }
                    value={data.lumpSumAmount ?? ""}
                    onChange={handleInputChange("lumpSumAmount")}
                    margin="normal"
                    inputProps={fieldLimits.lumpSumAmount}
                    error={isLumpSumAmountError}
                    helperText={
                      isLumpSumAmountError
                        ? `Enter between ${fieldLimits.lumpSumAmount.min} and ${fieldLimits.lumpSumAmount.max}`
                        : undefined
                    }
                  />
                </Grid>
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
                    error={isLumpSumYearError}
                    helperText={
                      isLumpSumYearError
                        ? `Enter between ${fieldLimits.lumpSumYearOffset.min} and ${data.horizon}`
                        : undefined
                    }
                  />
                </Grid>
              </>
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
                  error={isEmptyByAgeError}
                  helperText={
                    isEmptyByAgeError
                      ? `Enter between ${data.age + 5} and ${fieldLimits.emptyByAge.max}`
                      : undefined
                  }
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

