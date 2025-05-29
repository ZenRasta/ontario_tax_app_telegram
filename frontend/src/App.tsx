// frontend/src/App.tsx
import React, { useState } from "react";
import { Container, Paper, Typography, Alert } from "@mui/material";
import GoalStep from "./components/GoalStep";
import StrategyStep from "./components/StrategyStep";
import InputFormStep from "./components/InputFormStep";
import ResultsPage from "./components/ResultsPage";
import type { FormData } from "./types/formData";
import type { ComparisonResponseItem } from "./types/api";

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
    goal: "",
    strategies: [],
  });
  const [currentStep, setCurrentStep] = useState(1);
  const [resultsData, setResultsData] = useState<ComparisonResponseItem[] | null>(
    null,
  );
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
      strategy_params_override: {
        bracket_fill_ceiling: formData.bracketFillCeiling,
        cpp_start_age: formData.cppStartAge,
        lump_sum_year_offset: formData.lumpSumYear,
        target_depletion_age: formData.emptyByAge,
      },
    };

    /* ----------------------------------------------
     * 3) Decide which strategies to run
     * ---------------------------------------------- */
    const strategyList =
      formData.strategies.length > 0 ? formData.strategies : ["GM"];

    /* ----------------------------------------------
     * 4) POST to /api/v1/compare
     * ---------------------------------------------- */
    try {
      const res = await fetch("/api/v1/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
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
        <Typography variant="h4" align="center" gutterBottom>
          Ontario RRIF Strategy Tester
        </Typography>

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
            onToggleStrategy={(codes) => updateFormData({ strategies: codes })}
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

