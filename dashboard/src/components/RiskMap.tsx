interface RiskMapProps {
  data: any
}

export default function RiskMap({ data }: RiskMapProps) {
  const totalLocations = data?.pipeline_results?.unified_data_count || 0
  
  // Mock data for visualization - in production, this would use actual geohash data
  const riskLevels = [
    { level: 'Low', count: 35, color: 'bg-green-500' },
    { level: 'Medium', count: 10, color: 'bg-yellow-500' },
    { level: 'High', count: 4, color: 'bg-orange-500' },
    { level: 'Critical', count: 0, color: 'bg-red-500' },
  ]

  return (
    <div className="space-y-4">
      <p className="text-xs text-slate-600 dark:text-slate-400 mb-4">
        Visualizes risk distribution across monitored locations based on composite risk scores from mobility, climate, and vulnerability analysis.
      </p>
      
      <div className="grid grid-cols-2 gap-4">
        {riskLevels.map((item) => (
          <div
            key={item.level}
            className="flex items-center space-x-3 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg"
          >
            <div className={`w-3 h-3 ${item.color} rounded-full`} />
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-900 dark:text-white">
                {item.level}
              </p>
              <p className="text-xs text-slate-600 dark:text-slate-400">
                {item.count} locations
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4">
        <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
          Risk Distribution
        </h3>
        <div className="space-y-2">
          {riskLevels.map((item) => {
            const percentage = totalLocations > 0
              ? (item.count / totalLocations) * 100
              : 0
            return (
              <div key={item.level}>
                <div className="flex justify-between text-xs text-slate-600 dark:text-slate-400 mb-1">
                  <span>{item.level}</span>
                  <span>{percentage.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                  <div
                    className={`${item.color} h-2 rounded-full transition-all duration-500`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
