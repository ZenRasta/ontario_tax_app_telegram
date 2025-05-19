import { useState } from 'react'
import SimulationForm from './components/SimulationForm'
import './App.css'

function App() {
  const [apiStatus, setApiStatus] = useState<string | null>(null);

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
      {apiStatus && <p className="mt-4">API status: {apiStatus}</p>}
      <div className="w-full max-w-2xl mt-6">
        <SimulationForm />
      </div>
    </div>
  )
}

export default App
