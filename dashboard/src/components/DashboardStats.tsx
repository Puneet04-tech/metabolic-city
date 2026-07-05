import { Activity, AlertTriangle, MapPin, Clock } from 'lucide-react'

interface DashboardStatsProps {
  data: any
}

export default function DashboardStats({ data }: DashboardStatsProps) {
  const stats = [
    {
      label: 'Locations Monitored',
      value: data?.pipeline_results?.unified_data_count || 0,
      icon: MapPin,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      description: 'Number of geohash locations being tracked by the pipeline'
    },
    {
      label: 'Risk Scores Generated',
      value: data?.pipeline_results?.risk_scores_count || 0,
      icon: Activity,
      color: 'text-green-600',
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      description: 'Composite risk scores calculated from mobility, climate, and vulnerability data'
    },
    {
      label: 'Active Alerts',
      value: data?.pipeline_results?.alerts_generated || 0,
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      description: 'High-priority alerts triggered when risk exceeds threshold'
    },
    {
      label: 'Last Cycle Duration',
      value: `${data?.pipeline_results?.duration_seconds?.toFixed(2) || 0}s`,
      icon: Clock,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
      description: 'Time taken to complete the last pipeline cycle'
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => {
        const Icon = stat.icon
        return (
          <div
            key={stat.label}
            className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
                  {stat.label}
                </p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
                  {stat.value}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
                  {stat.description}
                </p>
              </div>
              <div className={`${stat.bgColor} ${stat.color} p-3 rounded-lg`}>
                <Icon className="h-6 w-6" />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
