import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface TrendChartProps {
  data: any
}

export default function TrendChart({ data }: TrendChartProps) {
  // Mock trend data - in production, this would come from memory matrix
  const trendData = [
    { time: '00:00', risk: 3.2 },
    { time: '04:00', risk: 2.8 },
    { time: '08:00', risk: 4.5 },
    { time: '12:00', risk: 5.2 },
    { time: '16:00', risk: 4.8 },
    { time: '20:00', risk: 3.9 },
    { time: 'Now', risk: data?.average_risk || 4.1 },
  ]

  return (
    <div className="space-y-4">
      <p className="text-xs text-slate-600 dark:text-slate-400">
        Tracks average risk scores over time to identify patterns and trends in urban system performance.
      </p>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-700" />
            <XAxis
              dataKey="time"
              className="text-xs text-slate-600 dark:text-slate-400"
            />
            <YAxis
              className="text-xs text-slate-600 dark:text-slate-400"
              domain={[0, 10]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgb(30, 41, 59)',
                border: '1px solid rgb(51, 65, 85)',
                borderRadius: '0.5rem',
              }}
              itemStyle={{ color: 'rgb(248, 250, 252)' }}
            />
            <Line
              type="monotone"
              dataKey="risk"
              stroke="#0ea5e9"
              strokeWidth={2}
              dot={{ fill: '#0ea5e9' }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
