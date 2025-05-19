import { useState } from 'react'
import './App.css'
import { Tooltip } from 'react-tooltip'
import 'react-tooltip/dist/react-tooltip.css'

function App() {
  const [apiStatus, setApiStatus] = useState<string | null>(null);
  const [results] = useState([
    { year: 2024, rrsp: 10000, tfsa: 6000, oasClawback: 0 },
    { year: 2025, rrsp: 10500, tfsa: 7000, oasClawback: 50 },
  ]);

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

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-8 font-sans">
      <h1 className="text-2xl font-bold mb-4">Ontario Retirement Planner</h1>
      <button
        onClick={checkHealth}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Check API Health
      </button>
      {apiStatus && (
        <p className="mt-4">API status: {apiStatus}</p>
      )}
      <table className="mt-8 border-collapse border text-left">
        <thead>
          <tr>
            <th className="border px-4 py-2">Year</th>
            <th className="border px-4 py-2">RRSP Balance</th>
            <th className="border px-4 py-2">TFSA Balance</th>
            <th className="border px-4 py-2">
              <div className="flex items-center">
                OAS Clawback
                <span
                  className="ml-1 text-sm text-blue-600 cursor-pointer"
                  data-tooltip-id="oas-info"
                  data-tooltip-content="Old Age Security payments are reduced by 15% of net income over the threshold."
                  aria-label="Explanation of OAS clawback calculation"
                  aria-describedby="oas-info"
                  role="button"
                  tabIndex={0}
                >
                  ℹ️
                </span>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          {results.map((row) => (
            <tr key={row.year}>
              <td className="border px-4 py-2">{row.year}</td>
              <td className="border px-4 py-2">{row.rrsp}</td>
              <td className="border px-4 py-2">{row.tfsa}</td>
              <td className="border px-4 py-2">{row.oasClawback}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <Tooltip id="oas-info" place="top" />
    </div>
  )
}

export default App
