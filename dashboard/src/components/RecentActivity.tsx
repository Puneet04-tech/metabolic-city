import { Activity, CheckCircle, AlertCircle, Info } from 'lucide-react'

interface RecentActivityProps {
  data: any
}

export default function RecentActivity({ data }: RecentActivityProps) {
  const activities = data?.recent_activity || []

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return CheckCircle
      case 'warning':
        return AlertCircle
      case 'info':
        return Info
      default:
        return Activity
    }
  }

  const getColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'text-green-600 bg-green-50 dark:bg-green-900/20'
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20'
      case 'info':
        return 'text-blue-600 bg-blue-50 dark:bg-blue-900/20'
      default:
        return 'text-slate-600 bg-slate-50 dark:bg-slate-700/20'
    }
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString()
  }

  return (
    <div className="space-y-3">
      {activities.map((activity: any, index: number) => {
        const Icon = getIcon(activity.type)
        const colorClass = getColor(activity.type)
        return (
          <div
            key={index}
            className="flex items-start space-x-3 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg"
          >
            <div className={`${colorClass} p-2 rounded-lg flex-shrink-0`}>
              <Icon className="h-4 w-4" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-900 dark:text-white">
                {activity.message}
              </p>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                {formatTime(activity.timestamp)}
              </p>
            </div>
          </div>
        )
      })}
    </div>
  )
}
