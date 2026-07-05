import { Play, Settings, AlertTriangle } from 'lucide-react'
import { useState } from 'react'

interface SimulationPanelProps {
  data: any
}

export default function SimulationPanel({ data }: SimulationPanelProps) {
  const [running, setRunning] = useState(false)
  const [results, setResults] = useState<any>(null)

  const runSimulation = async () => {
    setRunning(true)
    try {
      const response = await fetch('http://localhost:8000/api/simulation/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario_id: 'test_scenario',
          name: 'Test Scenario',
          description: 'Test simulation scenario'
        })
      })
      const data = await response.json()
      setResults(data)
    } catch (error) {
      console.error('Simulation error:', error)
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="space-y-4">
      <p className="text-xs text-slate-600 dark:text-slate-400">
        What-If scenario testing to simulate infrastructure changes and evaluate their impact on risk levels.
      </p>
      {/* Controls */}
      <div className="flex space-x-2">
        <button
          onClick={runSimulation}
          disabled={running}
          className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play className="h-4 w-4" />
          <span>{running ? 'Running...' : 'Run Simulation'}</span>
        </button>
        <button className="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-300 dark:hover:bg-slate-600">
          <Settings className="h-4 w-4" />
        </button>
      </div>

      {/* Results */}
      {results ? (
        <div className="space-y-3">
          <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <AlertTriangle className="h-4 w-4 text-blue-600" />
              <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                Risk Change
              </p>
            </div>
            <p className="text-2xl font-bold text-slate-900 dark:text-white">
              {results.results.risk_change > 0 ? '+' : ''}{results.results.risk_change.toFixed(2)}
            </p>
          </div>

          <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
            <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">
              Risk Level Change
            </p>
            <p className="text-lg font-semibold text-slate-900 dark:text-white capitalize">
              {results.results.risk_level_change}
            </p>
          </div>

          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">
              Recommendation
            </p>
            <p className="text-sm text-slate-900 dark:text-white">
              {results.results.recommendation}
            </p>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <p className="text-slate-600 dark:text-slate-400">
            Run a simulation to see results
          </p>
        </div>
      )}
    </div>
  )
}
