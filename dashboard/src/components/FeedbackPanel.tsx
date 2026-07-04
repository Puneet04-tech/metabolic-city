import { MessageSquare, Send } from 'lucide-react'
import { useState } from 'react'

interface FeedbackPanelProps {
  data: any
}

export default function FeedbackPanel({ data }: FeedbackPanelProps) {
  const [message, setMessage] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<any>(null)

  const submitFeedback = async () => {
    if (!message.trim()) return
    
    setSubmitting(true)
    try {
      const response = await fetch('http://localhost:8000/api/feedback/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          timestamp: new Date().toISOString(),
          location: 'user_reported'
        })
      })
      const data = await response.json()
      setResult(data)
      setMessage('')
    } catch (error) {
      console.error('Feedback error:', error)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Input */}
      <div>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Describe the issue or observation..."
          className="w-full p-3 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white resize-none"
          rows={4}
        />
      </div>

      {/* Submit Button */}
      <button
        onClick={submitFeedback}
        disabled={submitting || !message.trim()}
        className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Send className="h-4 w-4" />
        <span>{submitting ? 'Submitting...' : 'Submit Feedback'}</span>
      </button>

      {/* Result */}
      {result && (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div className="flex items-center space-x-2">
            <MessageSquare className="h-4 w-4 text-green-600" />
            <p className="text-sm text-green-800 dark:text-green-200">
              {result.message}
            </p>
          </div>
          <p className="text-xs text-green-600 dark:text-green-400 mt-1">
            ID: {result.feedback_id}
          </p>
        </div>
      )}
    </div>
  )
}
