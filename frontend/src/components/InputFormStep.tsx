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
                <Tooltip title="Your current age in years.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.age}
            onChange={handleInputChange("age")}
            margin="normal"
          />

          {/* CPP at 65 */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                CPP @ 65
                <Tooltip title="Annual CPP benefit if you started it exactly at age 65.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.cppAmount}
            onChange={handleInputChange("cppAmount")}
            margin="normal"
            inputProps={{ min: 0, max: CPP_MAX }}
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
                <Tooltip title="Current value of your Tax-Free Savings Account.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.tfsaBalance}
            onChange={handleInputChange("tfsaBalance")}
            margin="normal"
          />

          {/* Expected return */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                Expected Return %
                <Tooltip title="Average annual investment return (nominal, before inflation).">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.expectedReturn}
            onChange={handleInputChange("expectedReturn")}
            margin="normal"
          />

          {/* Horizon */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                Horizon (years)
                <Tooltip title="How many years to project forward.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.horizon}
            onChange={handleInputChange("horizon")}
            margin="normal"
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
                <Tooltip title="Current value of your RRSP or RRIF.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.rrspBalance}
            onChange={handleInputChange("rrspBalance")}
            margin="normal"
          />

          {/* OAS @65 */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                OAS @ 65
                <Tooltip title="Annual OAS benefit at age 65 (before any delay).">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.oasAmount}
            onChange={handleInputChange("oasAmount")}
            margin="normal"
            inputProps={{ min: 0, max: OAS_MAX }}
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
                <Tooltip title="Target after-tax spending you’d like each year.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.desiredSpending}
            onChange={handleInputChange("desiredSpending")}
            margin="normal"
          />

          {/* Volatility */}
          <TextField
            fullWidth
            type="number"
            label={
              <Box display="flex" alignItems="center">
                Std Dev Return %
                <Tooltip title="Expected year-to-year volatility (standard deviation).">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
            value={data.stdDevReturn}
            onChange={handleInputChange("stdDevReturn")}
            margin="normal"
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
                label="Spouse Age"
                value={data.spouseAge ?? ""}
                onChange={handleInputChange("spouseAge")}
                margin="normal"
              />
              {/* Spouse CPP */}
              <TextField
                fullWidth
                type="number"
                label="Spouse CPP @ 65"
                value={data.spouseCppAmount ?? ""}
                onChange={handleInputChange("spouseCppAmount")}
                margin="normal"
                inputProps={{ min: 0, max: CPP_MAX }}
                error={spouseCppAmountError}
                helperText={
                  spouseCppAmountError ? `Maximum CPP amount is $${CPP_MAX}` : undefined
                }
              />
              {/* Spouse TFSA */}
              <TextField
                fullWidth
                type="number"
                label="Spouse TFSA Balance"
                value={data.spouseTfsaBalance ?? ""}
                onChange={handleInputChange("spouseTfsaBalance")}
                margin="normal"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              {/* Spouse RRSP */}
              <TextField
                fullWidth
                type="number"
                label="Spouse RRSP Balance"
                value={data.spouseRrspBalance ?? ""}
                onChange={handleInputChange("spouseRrspBalance")}
                margin="normal"
              />
              {/* Spouse OAS */}
              <TextField
                fullWidth
                type="number"
                label="Spouse OAS @ 65"
                value={data.spouseOasAmount ?? ""}
                onChange={handleInputChange("spouseOasAmount")}
                margin="normal"
                inputProps={{ min: 0, max: OAS_MAX }}
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
                  label="Bracket-Fill Ceiling ($)"
                  value={data.bracketFillCeiling ?? ""}
                  onChange={handleInputChange("bracketFillCeiling")}
                  margin="normal"
                />
              </Grid>
            )}

            {hasDelay && (
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="CPP Start Age"
                  value={data.cppStartAge ?? ""}
                  onChange={handleInputChange("cppStartAge")}
                  margin="normal"
                />
              </Grid>
            )}

            {hasLS && (
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Lump-Sum Year Offset"
                  value={data.lumpSumYear ?? ""}
                  onChange={handleInputChange("lumpSumYear")}
                  margin="normal"
                />
              </Grid>
            )}

            {hasEBX && (
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Empty-by Age"
                  value={data.emptyByAge ?? ""}
                  onChange={handleInputChange("emptyByAge")}
                  margin="normal"
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

