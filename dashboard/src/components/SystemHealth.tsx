import { Heart, AlertTriangle, Info as InfoIcon } from 'lucide-react'

interface SystemHealthProps {
  data: any
}

export default function SystemHealth({ data }: SystemHealthProps) {
  const health = data?.system_health || { overall: 'unknown', issues: [] }

  const getOverallColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-50 dark:bg-green-900/20'
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20'
      case 'critical':
        return 'text-red-600 bg-red-50 dark:bg-red-900/20'
      default:
        return 'text-slate-600 bg-slate-50 dark:bg-slate-700/20'
    }
  }

  const getIssueIcon = (severity: string) => {
    switch (severity) {
      case 'warning':
        return AlertTriangle
      case 'info':
        return InfoIcon
      default:
        return AlertTriangle
    }
  }

  const getIssueColor = (severity: string) => {
    switch (severity) {
      case 'warning':
        return 'text-yellow-600'
      case 'info':
        return 'text-blue-600'
      case 'critical':
        return 'text-red-600'
      default:
        return 'text-slate-600'
    }
  }

  return (
    <div className="space-y-4">
      <p className="text-xs text-slate-600 dark:text-slate-400">
        Overall system health status with component-level issues and warnings for monitoring platform reliability.
      </p>
      {/* Overall Status */}
      <div className={`flex items-center space-x-3 p-4 rounded-lg ${getOverallColor(health.overall)}`}>
        <Heart className="h-6 w-6" />
        <div>
          <p className="text-sm font-medium capitalize">{health.overall}</p>
          <p className="text-xs opacity-75">System Status</p>
        </div>
      </div>

      {/* Issues */}
      {health.issues && health.issues.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300">
            Issues & Warnings
          </h4>
          {health.issues.map((issue: any, index: number) => {
            const Icon = getIssueIcon(issue.severity)
            const colorClass = getIssueColor(issue.severity)
            return (
              <div
                key={index}
                className="flex items-start space-x-2 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg"
              >
                <Icon className={`h-4 w-4 ${colorClass} mt-0.5 flex-shrink-0`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-slate-900 dark:text-white">
                    {issue.message}
                  </p>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                    {issue.component}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
