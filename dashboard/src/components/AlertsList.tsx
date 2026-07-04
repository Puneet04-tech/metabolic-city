import { AlertTriangle, CheckCircle } from 'lucide-react'

interface AlertsListProps {
  data: any
}

export default function AlertsList({ data }: AlertsListProps) {
  const alerts = data?.alerts || data?.pipeline_results?.alerts || []

  if (alerts.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-3" />
          <p className="text-slate-600 dark:text-slate-400">
            No active alerts. All systems operating normally.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert: any, index: number) => (
        <div
          key={index}
          className="flex items-start space-x-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
        >
          <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-red-900 dark:text-red-100">
              {alert.type || 'High Risk Alert'}
            </p>
            <p className="text-sm text-red-700 dark:text-red-300 mt-1">
              {alert.message || `Risk index of ${alert.risk_index} detected in ${alert.geohash}`}
            </p>
            <p className="text-xs text-red-600 dark:text-red-400 mt-2">
              {alert.timestamp || new Date().toLocaleString()}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}
