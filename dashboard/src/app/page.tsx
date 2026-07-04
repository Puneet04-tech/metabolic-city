'use client'

import { useState, useEffect } from 'react'
import { Activity, AlertTriangle, TrendingUp, MapPin, Download, RefreshCw } from 'lucide-react'
import DashboardStats from '@/components/DashboardStats'
import RiskMap from '@/components/RiskMap'
import AlertsList from '@/components/AlertsList'
import TrendChart from '@/components/TrendChart'
import RecentActivity from '@/components/RecentActivity'
import SystemHealth from '@/components/SystemHealth'
import DataSources from '@/components/DataSources'

export default function Home() {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  const fetchData = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/dashboard')
      if (response.ok) {
        const result = await response.json()
        setData(result)
        setLastUpdate(new Date())
      }
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 60000) // Refresh every minute
    return () => clearInterval(interval)
  }, [])

  const handleExport = async () => {
    if (!data) return
    
    const exportData = {
      timestamp: new Date().toISOString(),
      pipelineResults: data,
    }
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `metabolic-city-export-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Activity className="h-8 w-8 text-primary-600" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                  MetabolicCity AI
                </h1>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Real-time Urban Decision Intelligence
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={fetchData}
                className="flex items-center space-x-2 px-4 py-2 bg-slate-100 dark:bg-slate-700 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  Refresh
                </span>
              </button>
              <button
                onClick={handleExport}
                disabled={!data || loading}
                className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="h-4 w-4" />
                <span className="text-sm font-medium">Export</span>
              </button>
            </div>
          </div>
          {lastUpdate && (
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </p>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading && !data ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : data ? (
          <div className="space-y-6">
            {/* Stats Cards */}
            <DashboardStats data={data} />

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Risk Map */}
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <MapPin className="h-5 w-5 text-primary-600" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Risk Distribution by Location
                  </h2>
                </div>
                <RiskMap data={data} />
              </div>

              {/* Trend Chart */}
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <TrendingUp className="h-5 w-5 text-primary-600" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Risk Trends Over Time
                  </h2>
                </div>
                <TrendChart data={data} />
              </div>
            </div>

            {/* Secondary Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Recent Activity */}
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Activity className="h-5 w-5 text-primary-600" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Recent Activity
                  </h2>
                </div>
                <RecentActivity data={data} />
              </div>

              {/* System Health */}
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <AlertTriangle className="h-5 w-5 text-primary-600" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                    System Health
                  </h2>
                </div>
                <SystemHealth data={data} />
              </div>

              {/* Data Sources */}
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <MapPin className="h-5 w-5 text-primary-600" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Data Sources
                  </h2>
                </div>
                <DataSources data={data} />
              </div>
            </div>

            {/* Alerts */}
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
              <div className="flex items-center space-x-2 mb-4">
                <AlertTriangle className="h-5 w-5 text-primary-600" />
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                  Active Alerts
                </h2>
              </div>
              <AlertsList data={data} />
            </div>
          </div>
        ) : (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-12 text-center">
            <Activity className="h-16 w-16 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
              No Data Available
            </h3>
            <p className="text-slate-600 dark:text-slate-400">
              Start the MetabolicCity AI pipeline to see real-time data
            </p>
          </div>
        )}
      </div>
    </main>
  )
}
