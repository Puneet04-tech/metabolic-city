import { Database, Cloud, Users } from 'lucide-react'

interface DataSourcesProps {
  data: any
}

export default function DataSources({ data }: DataSourcesProps) {
  const sources = data?.data_sources || []

  const getIcon = (name: string) => {
    if (name.includes('GTFS') || name.includes('Transit')) return Database
    if (name.includes('Weather')) return Cloud
    if (name.includes('Demographic')) return Users
    return Database
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-50 dark:bg-green-900/20'
      case 'partial':
        return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20'
      case 'inactive':
        return 'text-red-600 bg-red-50 dark:bg-red-900/20'
      default:
        return 'text-slate-600 bg-slate-50 dark:bg-slate-700/20'
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'partial':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'inactive':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      default:
        return 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-200'
    }
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString()
  }

  return (
    <div className="space-y-3">
      <p className="text-xs text-slate-600 dark:text-slate-400">
        External data sources feeding the pipeline with real-time transit, weather, and demographic information.
      </p>
      {sources.map((source: any, index: number) => {
        const Icon = getIcon(source.name)
        const colorClass = getStatusColor(source.status)
        const badgeClass = getStatusBadge(source.status)
        return (
          <div
            key={index}
            className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg"
          >
            <div className="flex items-center space-x-3">
              <div className={`${colorClass} p-2 rounded-lg`}>
                <Icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900 dark:text-white">
                  {source.name}
                </p>
                <p className="text-xs text-slate-600 dark:text-slate-400">
                  {source.records} records
                </p>
              </div>
            </div>
            <div className="text-right">
              <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${badgeClass}`}>
                {source.status}
              </span>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                {formatTime(source.last_fetch)}
              </p>
            </div>
          </div>
        )
      })}
    </div>
  )
}
