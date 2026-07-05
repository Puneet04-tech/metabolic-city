import { TrendingUp, Clock, AlertTriangle } from 'lucide-react'

interface ForecastingPanelProps {
  data: any
}

export default function ForecastingPanel({ data }: ForecastingPanelProps) {
  const forecasting = data?.forecasting || { enabled: false, forecasts_generated: 0, alert_forecasts: 0, horizon_hours: 24 }

  if (!forecasting.enabled) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Clock className="h-12 w-12 text-slate-400 mx-auto mb-3" />
          <p className="text-slate-600 dark:text-slate-400">
            Forecasting is disabled
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <p className="text-xs text-slate-600 dark:text-slate-400">
        Predictive analysis using historical data to forecast future risk levels and identify potential alerts.
      </p>
      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
              Forecasts Generated
            </p>
          </div>
          <p className="text-2xl font-bold text-slate-900 dark:text-white">
            {forecasting.forecasts_generated}
          </p>
        </div>

        <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
              Alert Forecasts
            </p>
          </div>
          <p className="text-2xl font-bold text-slate-900 dark:text-white">
            {forecasting.alert_forecasts}
          </p>
        </div>
      </div>

      {/* Horizon Info */}
      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <div className="flex items-center space-x-2">
          <Clock className="h-5 w-5 text-blue-600" />
          <div>
            <p className="text-sm font-medium text-slate-900 dark:text-white">
              Forecasting Horizon
            </p>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              {forecasting.horizon_hours} hours ahead
            </p>
          </div>
        </div>
      </div>

      {/* Status */}
      <div className="text-center py-4">
        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
          Forecasting Active
        </span>
      </div>
    </div>
  )
}
