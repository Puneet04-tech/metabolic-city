import { Lightbulb, Zap, Shield, TrendingUp, Globe, Users, Clock, CheckCircle } from 'lucide-react'

export default function PitchCards() {
  const cards = [
    {
      icon: Lightbulb,
      title: "The Problem",
      content: "Cities face coordination crises. Departments operate in silos - transit doesn't talk to emergency services, weather data doesn't inform public works, citizen reports get lost in bureaucratic channels.",
      color: "text-red-600",
      bgColor: "bg-red-50 dark:bg-red-900/20"
    },
    {
      icon: Zap,
      title: "Our Solution",
      content: "MetabolicCity AI treats the entire city as a unified data network. A fully automated four-stage pipeline continuously monitors urban systems and generates coordinated response plans.",
      color: "text-blue-600",
      bgColor: "bg-blue-50 dark:bg-blue-900/20"
    },
    {
      icon: Shield,
      title: "Four-Stage Pipeline",
      content: "1) Unified Ingestion - GTFS-RT, weather, demographic data normalized to geohash grid. 2) Isolated Analysis - AI nodes evaluate mobility, climate, vulnerability independently. 3) Deterministic Triage - Mathematical risk scoring with weighted formulas. 4) Constrained Prescription - Pre-approved response templates with natural-language narration.",
      color: "text-purple-600",
      bgColor: "bg-purple-50 dark:bg-purple-900/20"
    },
    {
      icon: TrendingUp,
      title: "Enhanced Features",
      content: "Temporal Forecasting - Predictive analysis using historical data. Simulation Sandbox - What-If testing for infrastructure changes. Citizen Feedback Loop - NLP-powered report integration. Multi-Agency Dispatch - Automated routing to departmental systems.",
      color: "text-green-600",
      bgColor: "bg-green-50 dark:bg-green-900/20"
    },
    {
      icon: Globe,
      title: "Real-Time Dashboard",
      content: "Live monitoring with 10-second refresh cycles. Risk distribution maps, trend charts, system health indicators, data source status, recent activity feed. Export functionality for results.",
      color: "text-orange-600",
      bgColor: "bg-orange-50 dark:bg-orange-900/20"
    },
    {
      icon: Users,
      title: "Impact",
      content: "Transforms reactive urban management into proactive, data-driven coordination. Cities can respond faster, allocate resources smarter, and prevent emergencies before they escalate.",
      color: "text-teal-600",
      bgColor: "bg-teal-50 dark:bg-teal-900/20"
    },
    {
      icon: Clock,
      title: "Key Metrics",
      content: "49 locations monitored in real-time. 49 risk scores generated per cycle. 4-stage pipeline with graceful degradation. 10-second dashboard refresh. 24-hour forecasting horizon.",
      color: "text-indigo-600",
      bgColor: "bg-indigo-50 dark:bg-indigo-900/20"
    },
    {
      icon: CheckCircle,
      title: "Technology Stack",
      content: "Backend: FastAPI, Python, GTFS-RT, Gemini/Mistral AI. Frontend: Next.js 14, TypeScript, Tailwind CSS, Recharts. Architecture: Microservices, async processing, geohash spatial normalization.",
      color: "text-pink-600",
      bgColor: "bg-pink-50 dark:bg-pink-900/20"
    }
  ]

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
          MetabolicCity AI - Pitch Overview
        </h2>
        <p className="text-slate-600 dark:text-slate-400">
          Key talking points for your presentation
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {cards.map((card, index) => {
          const Icon = card.icon
          return (
            <div
              key={index}
              className={`${card.bgColor} rounded-xl p-6 border border-slate-200 dark:border-slate-700`}
            >
              <div className="flex items-start space-x-3">
                <div className={`${card.bgColor} p-3 rounded-lg`}>
                  <Icon className={`h-6 w-6 ${card.color}`} />
                </div>
                <div className="flex-1">
                  <h3 className={`text-lg font-semibold ${card.color} mb-2`}>
                    {card.title}
                  </h3>
                  <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                    {card.content}
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl p-6 text-white">
        <div className="flex items-center space-x-3 mb-3">
          <CheckCircle className="h-6 w-6" />
          <h3 className="text-lg font-semibold">
            The Future of Urban Intelligence
          </h3>
        </div>
        <p className="text-sm leading-relaxed opacity-90">
          MetabolicCity AI transforms how cities manage crises through automated, data-driven coordination. 
          By treating urban systems as a unified network, we enable faster response times, smarter resource allocation, 
          and proactive emergency prevention.
        </p>
      </div>
    </div>
  )
}
