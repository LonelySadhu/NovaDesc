import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '@shared/ui/Card'
import { mockAiQueries } from '@shared/lib/mock-data'

export const AiAssistantPanel = () => {
  const [input, setInput] = useState('')

  return (
    <Card className="flex flex-col">
      <div className="flex items-center justify-between px-5 py-4 border-b border-border-subtle">
        <div className="flex items-center gap-2">
          <h2 className="font-semibold text-sm text-text-primary">AI Assistant</h2>
          <span className="text-[10px] text-text-muted border border-border-subtle px-1.5 py-0.5 rounded-pill">
            Ollama · local
          </span>
        </div>
        <Link to="/ai" className="text-xs text-primary hover:underline">Open chat</Link>
      </div>

      {/* Recent queries */}
      <ul className="divide-y divide-border-subtle flex-1">
        {mockAiQueries.map(q => (
          <li key={q.id} className="flex items-start gap-3 px-5 py-3.5 hover:bg-white/[0.02] transition-colors cursor-pointer">
            <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-primary">
                <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M8 1l1.5 4.5L14 7l-4.5 1.5L8 13l-1.5-4.5L2 7l4.5-1.5L8 1z"/>
                </svg>
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-text-primary line-clamp-2 leading-snug">{q.question}</p>
              <span className="text-[11px] text-text-muted mt-1">{q.timeAgo}</span>
            </div>
          </li>
        ))}
      </ul>

      {/* Input */}
      <div className="px-4 py-3 border-t border-border-subtle">
        <div className="flex items-center gap-2 bg-bg-base rounded-lg border border-border-subtle px-3 py-2">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask about equipment or repairs..."
            className="flex-1 bg-transparent text-sm text-text-primary placeholder-text-muted outline-none"
            onKeyDown={e => e.key === 'Enter' && setInput('')}
          />
          <button
            onClick={() => setInput('')}
            className="w-7 h-7 rounded-md bg-primary/80 hover:bg-primary flex items-center justify-center transition-colors flex-shrink-0"
          >
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="white" strokeWidth="2">
              <path d="M2 8h12M10 4l4 4-4 4"/>
            </svg>
          </button>
        </div>
      </div>
    </Card>
  )
}
