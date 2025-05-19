
import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useState } from 'react'
import SimulationForm from './components/SimulationForm'
import './App.css'
import type { StrategyParamsInput, ScenarioInput, SimulateRequest } from './types'

const BASE_SCENARIO: ScenarioInput = {
  age: 65,
  rrsp_balance: 500_000,
  defined_benefit_pension: 20_000,
  cpp_at_65: 12_000,
  oas_at_65: 8_000,
  tfsa_balance: 100_000,
  desired_spending: 60_000,
  expect_return_pct: 5,
  stddev_return_pct: 8,
  life_expectancy_years: 25,
  province: 'ON',
  goal: 'maximize_spending',
  spouse: {
    age: 63,
    rrsp_balance: 250_000,
    other_income: 10_000,
    cpp_at_65: 9_000,
    oas_at_65: 7_000,
    tfsa_balance: 50_000,
    defined_benefit_pension: 0,
  },
}

function App() {
  const [apiStatus, setApiStatus] = useState<string | null>(null)
  const [paramsState, setParamsState] = useState<StrategyParamsInput>({})

  const { register, handleSubmit, reset, formState: { errors } } = useForm<StrategyParamsInput>({
    defaultValues: paramsState,
  })

  useEffect(() => {
    reset(paramsState)
  }, [paramsState, reset])

  const checkHealth = async () => {
    try {
      const resp = await fetch('/api/v1/health');
      if (!resp.ok) throw new Error('Request failed');
      const data = await resp.json();
      setApiStatus(data.status);
    } catch (err) {
      setApiStatus('error');
    }
  };

  const submitParams = async (data: StrategyParamsInput) => {
    setParamsState(data)
    const req: SimulateRequest = {
      scenario: { ...BASE_SCENARIO, params: data },
      strategy_code: 'GM',
    }
    try {
      const resp = await fetch('/api/v1/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
      })
      if (!resp.ok) throw new Error('Request failed')
      const resData = await resp.json()
      console.log(resData)
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-8 font-sans">
      <h1 className="text-2xl font-bold mb-4">Ontario Retirement Planner</h1>
      <button
        onClick={checkHealth}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Check API Health
      </button>
      {apiStatus && <p className="mt-2">API status: {apiStatus}</p>}

      <form
        onSubmit={handleSubmit(submitParams)}
        className="w-full max-w-md mt-6 space-y-4"
      >
        <div>
          <label className="block text-left">Bracket Fill Ceiling</label>
          <input
            type="number"
            step="any"
            className="w-full border p-2 rounded"
            {...register('bracket_fill_ceiling', { min: 0 })}
          />
        </div>

        <div>
          <label className="block text-left">RRIF Conversion Age</label>
          <input
            type="number"
            className="w-full border p-2 rounded"
            {...register('rrif_conversion_age', { min: 55, max: 71 })}
          />
        </div>

        <div>
          <label className="block text-left">CPP Start Age</label>
          <input
            type="number"
            className="w-full border p-2 rounded"
            {...register('cpp_start_age', { min: 60, max: 70 })}
          />
        </div>

        <div>
          <label className="block text-left">OAS Start Age</label>
          <input
            type="number"
            className="w-full border p-2 rounded"
            {...register('oas_start_age', { min: 65, max: 70 })}
          />
        </div>

        <div>
          <label className="block text-left">Target Depletion Age</label>
          <input
            type="number"
            className="w-full border p-2 rounded"
            {...register('target_depletion_age', { min: 70, max: 120 })}
          />
        </div>

        <div>
          <label className="block text-left">Lump Sum Year Offset</label>
          <input
            type="number"
            className="w-full border p-2 rounded"
            {...register('lump_sum_year_offset', { min: 0 })}
          />
        </div>

        <div>
          <label className="block text-left">Lump Sum Amount</label>
          <input
            type="number"
            step="any"
            className="w-full border p-2 rounded"
            {...register('lump_sum_amount', { min: 0 })}
          />
        </div>

        <div>
          <label className="block text-left">Loan Interest Rate (%)</label>
          <input
            type="number"
            step="any"
            className="w-full border p-2 rounded"
            {...register('loan_interest_rate_pct', { min: 0, max: 100 })}
          />
        </div>

        <div>
          <label className="block text-left">Loan Amount as % of RRIF</label>
          <input
            type="number"
            step="any"
            className="w-full border p-2 rounded"
            {...register('loan_amount_as_pct_of_rrif', { min: 0, max: 100 })}
          />
        </div>

        <button
          type="submit"
          className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Run Simulation
        </button>
      </form>

      <pre className="mt-4 w-full max-w-md bg-gray-100 p-2 text-left overflow-x-auto text-xs">
        {JSON.stringify(paramsState, null, 2)}
      </pre>
      {apiStatus && <p className="mt-4">API status: {apiStatus}</p>}
      <div className="w-full max-w-2xl mt-6">
        <SimulationForm />
      </div>
    </div>
  )
}

export default App
