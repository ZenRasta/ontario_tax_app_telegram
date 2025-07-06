// frontend/src/App.tsx
import React, { useState } from "react";
import { Container, Paper, Typography, Alert, Box } from "@mui/material";
import GoalStep from "./components/GoalStep";
import StrategyStep from "./components/StrategyStep";
import InputFormStep from "./components/InputFormStep";
import ResultsPage from "./components/ResultsPage";
import PrivacyDisclaimer from "./components/PrivacyDisclaimer";
import type { FormData } from "./types/formData";
import type { ComparisonResponseItem, ScenarioInput } from "./types/api";

const API_PREFIX = import.meta.env.VITE_API_PREFIX ?? '/v1';

/* ------------------------------------------------------------------ */
const App: React.FC = () => {
  /* state ----------------------------------------------------------- */
  const [formData, setFormData] = useState<FormData>({
    age: 65,
    rrspBalance: 500_000,
    tfsaBalance: 100_000,
    cppAmount: 12_000,
    oasAmount: 8_000,
    desiredSpending: 60_000,
    expectedReturn: 5,
    stdDevReturn: 8,
    horizon: 30,
    married: false,
    lumpSumAmount: undefined,
    goal: "",
    strategies: [],
  });
  const [currentStep, setCurrentStep] = useState(1);
  const [resultsData, setResultsData] = useState<ComparisonResponseItem[] | null>(
    null,
  );
  const [scenarioData, setScenarioData] = useState<ScenarioInput | null>(null);
  const [error, setError] = useState<string | null>(null);

  /* helpers --------------------------------------------------------- */
  const updateFormData = (u: Partial<FormData>) =>
    setFormData((prev) => ({ ...prev, ...u }));

  const goNext = () => setCurrentStep((p) => p + 1);
  const goBack = () => setCurrentStep((p) => p - 1);

  /* backend call ---------------------------------------------------- */
  const handleRunSimulation = async () => {
    setError(null);

    /* ----------------------------------------------
     * 1) Map pretty goal → enum code
     * ---------------------------------------------- */
    const goalEnum =
      formData.goal === "Minimize Tax"
        ? "minimize_tax"
        : formData.goal === "Maximize Spending"
        ? "maximize_spending"
        : formData.goal === "Preserve Estate"
        ? "preserve_estate"
        : "simplify"; // default / “Simplify Cash-Flow”

    /* ----------------------------------------------
     * 2) Build ScenarioInput payload (snake_case)
     * ---------------------------------------------- */
    // Build strategy_params_override object, only including defined values
    const strategyParamsOverride: Record<string, any> = {};
    if (formData.bracketFillCeiling !== undefined && formData.bracketFillCeiling !== null) {
      strategyParamsOverride.bracket_fill_ceiling = formData.bracketFillCeiling;
    }
    if (formData.cppStartAge !== undefined && formData.cppStartAge !== null) {
      strategyParamsOverride.cpp_start_age = formData.cppStartAge;
    }
    if (formData.lumpSumAmount !== undefined && formData.lumpSumAmount !== null) {
      strategyParamsOverride.lump_sum_amount = formData.lumpSumAmount;
    }
    if (formData.lumpSumYear !== undefined && formData.lumpSumYear !== null) {
      strategyParamsOverride.lump_sum_year_offset = formData.lumpSumYear;
    }
    if (formData.emptyByAge !== undefined && formData.emptyByAge !== null) {
      strategyParamsOverride.target_depletion_age = formData.emptyByAge;
    }

    const scenarioPayload = {
      age: formData.age,
      rrsp_balance: formData.rrspBalance,
      tfsa_balance: formData.tfsaBalance,
      cpp_at_65: formData.cppAmount,
      oas_at_65: formData.oasAmount,
      desired_spending: formData.desiredSpending,
      expect_return_pct: formData.expectedReturn,
      stddev_return_pct: formData.stdDevReturn,
      life_expectancy_years: formData.horizon,
      province: "ON",
      goal: goalEnum,
      spouse: formData.married
        ? {
            age: formData.spouseAge,
            rrsp_balance: formData.spouseRrspBalance,
            tfsa_balance: formData.spouseTfsaBalance,
            cpp_at_65: formData.spouseCppAmount,
            oas_at_65: formData.spouseOasAmount,
          }
        : undefined,
      params: Object.keys(strategyParamsOverride).length > 0 ? strategyParamsOverride : undefined,
    };
    setScenarioData(scenarioPayload as ScenarioInput);

    /* ----------------------------------------------
     * 3) Decide which strategies to run
     * ---------------------------------------------- */
    const strategyList =
      formData.strategies.length > 0 ? formData.strategies : ["GM"];

    /* ----------------------------------------------
     * 4) POST to /api/v1/compare
     * ---------------------------------------------- */
    try {
        const res = await fetch(`${API_PREFIX}/compare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          request_id: crypto.randomUUID(),
          scenario: scenarioPayload,
          strategies: strategyList,
        }),
      });

      if (!res.ok) {
        const msg = await res.text();
        throw new Error(`HTTP ${res.status}: ${msg}`);
      }

      const result: { comparisons: ComparisonResponseItem[] } = await res.json();
      setResultsData(result.comparisons);
      setCurrentStep(4);
    } catch (err: unknown) {
      console.error("Simulation failed", err);
      setError(
        err instanceof Error ? err.message : "Failed to reach simulation API",
      );
      setResultsData(null);
    }
  };

  /* view ------------------------------------------------------------ */
  return (
    <Container maxWidth="md" sx={{ my: 4 }}>
      <Paper elevation={2} sx={{ p: 4 }}>
        {/* Header with Title and Privacy Disclaimer */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box sx={{ flex: 1 }} />
          <Typography variant="h4" align="center" sx={{ flex: 2 }}>
            Ontario RRIF Strategy
          </Typography>
          <Box sx={{ flex: 1, display: 'flex', justifyContent: 'flex-end' }}>
            <PrivacyDisclaimer />
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* ── Step 1 – goal ───────────────────────────────────────── */}
        {currentStep === 1 && (
          <GoalStep
            goal={formData.goal}
            onSelectGoal={(goal) => {
              updateFormData({ goal });
              goNext();
            }}
          />
        )}

        {/* ── Step 2 – pick strategies ───────────────────────────── */}
        {currentStep === 2 && (
          <StrategyStep
            selectedStrategies={formData.strategies}
            onToggleStrategy={(codes) => {
              const updates: Partial<FormData> = { strategies: codes };
              
              // Set default values for strategies that require them
              if (codes.includes("LS") && !formData.lumpSumAmount) {
                updates.lumpSumAmount = 90000;
                updates.lumpSumYear = 20;
              }
              if (codes.includes("BF") && !formData.bracketFillCeiling) {
                updates.bracketFillCeiling = 90000;
              }
              if (codes.includes("CD") && !formData.cppStartAge) {
                updates.cppStartAge = 70;
              }
              if (codes.includes("EBX") && !formData.emptyByAge) {
                updates.emptyByAge = 90;
              }
              
              updateFormData(updates);
            }}
            onNext={() => {
              if (formData.strategies.includes("SEQ")) {
                updateFormData({ married: true });
              }
              goNext();
            }}
            onBack={goBack}
          />
        )}

        {/* ── Step 3 – detailed inputs ───────────────────────────── */}
        {currentStep === 3 && (
          <InputFormStep
            data={formData}
            onChange={updateFormData}
            onBack={goBack}
            onSubmit={handleRunSimulation}
          />
        )}

        {/* ── Step 4 – results ───────────────────────────────────── */}
        {currentStep === 4 && resultsData && resultsData.length > 0 && (
          <ResultsPage
            goal={formData.goal}
            strategies={formData.strategies}
            horizon={formData.horizon}
            results={resultsData}
            scenario={scenarioData}
            onBack={() => {
              setResultsData(null);
              setCurrentStep(2);
            }}
            onStartOver={() => {
              setFormData({
                ...formData,
                goal: "",
                strategies: [],
                married: false,
              });
              setResultsData(null);
              setCurrentStep(1);
            }}
          />
        )}
      </Paper>
    </Container>
  );
};

export default App;
