import { Send, Building2 } from 'lucide-react'
import { useState } from 'react'

interface DispatchPanelProps {
  data: any
}

export default function DispatchPanel({ data }: DispatchPanelProps) {
  const [agency, setAgency] = useState('')
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [result, setResult] = useState<any>(null)

  const agencies = [
    'Transit Authority',
    'Emergency Services',
    'Public Works',
    'Health Department'
  ]

  const sendDispatch = async () => {
    if (!agency || !message.trim()) return
    
    setSending(true)
    try {
      const response = await fetch('http://localhost:8000/api/dispatch/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agency,
          message,
          priority: 'normal',
          timestamp: new Date().toISOString()
        })
      })
      const data = await response.json()
      setResult(data)
      setMessage('')
    } catch (error) {
      console.error('Dispatch error:', error)
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Agency Selection */}
      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
          Target Agency
        </label>
        <select
          value={agency}
          onChange={(e) => setAgency(e.target.value)}
          className="w-full p-3 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
        >
          <option value="">Select agency...</option>
          {agencies.map((a) => (
            <option key={a} value={a}>{a}</option>
          ))}
        </select>
      </div>

      {/* Message */}
      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
          Dispatch Message
        </label>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Enter dispatch instructions..."
          className="w-full p-3 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white resize-none"
          rows={3}
        />
      </div>

      {/* Send Button */}
      <button
        onClick={sendDispatch}
        disabled={sending || !agency || !message.trim()}
        className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Send className="h-4 w-4" />
        <span>{sending ? 'Sending...' : 'Send Dispatch'}</span>
      </button>

      {/* Result */}
      {result && (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div className="flex items-center space-x-2">
            <Building2 className="h-4 w-4 text-green-600" />
            <p className="text-sm text-green-800 dark:text-green-200">
              {result.message}
            </p>
          </div>
          <p className="text-xs text-green-600 dark:text-green-400 mt-1">
            ID: {result.dispatch_id} | Agency: {result.agency}
          </p>
        </div>
      )}
    </div>
  )
}
