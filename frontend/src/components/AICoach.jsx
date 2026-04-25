import { useState } from 'react'

const ROLE_DISPLAY = {
  TOP: 'Top',
  JUNGLE: 'Jungle',
  MIDDLE: 'Mid',
  BOTTOM: 'ADC',
  UTILITY: 'Support',
}

export default function AICoach({ data }) {
  const [coaching, setCoaching] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function analyze() {
    setLoading(true)
    setError(null)
    setCoaching(null)
    try {
      const res = await fetch('/api/coach', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json.error || 'Analysis failed')
      setCoaching(json)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="section-title">AI Coach</h2>

      {!coaching && !loading && (
        <div className="card flex flex-col items-center py-10 gap-4">
          <div className="w-12 h-12 rounded-full bg-apple-blue/10 flex items-center justify-center">
            <svg className="w-6 h-6 text-apple-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div className="text-center">
            <p className="text-sm font-medium mb-1">Personalized coaching</p>
            <p className="text-apple-text-secondary text-xs max-w-xs">
              AI analysis of your last 20 games — strengths, weaknesses, and a clear path to climb
            </p>
          </div>
          <button onClick={analyze} className="apple-btn hover:opacity-80 active:scale-95">
            Analyze My Gameplay
          </button>
        </div>
      )}

      {loading && (
        <div className="card flex flex-col items-center py-12 gap-4">
          <div className="w-6 h-6 border-2 border-apple-blue border-t-transparent rounded-full animate-spin" />
          <p className="text-apple-text-secondary text-sm">Analyzing your last 20 games…</p>
        </div>
      )}

      {error && !loading && (
        <div className="card flex flex-col items-center py-8 gap-3">
          <p className="text-apple-red text-sm">{error}</p>
          <button onClick={analyze} className="apple-btn hover:opacity-80">Retry</button>
        </div>
      )}

      {coaching && !loading && (
        <div className="space-y-4">
          {/* Assessment */}
          <div className="card">
            <p className="section-title">Overall Assessment</p>
            <p className="text-sm leading-relaxed">{coaching.assessment}</p>
          </div>

          {/* Weaknesses */}
          {coaching.weaknesses?.length > 0 && (
            <div className="card">
              <p className="section-title">Areas to Improve</p>
              <div className="space-y-3">
                {coaching.weaknesses.map((w, i) => (
                  <div key={i} className="bg-apple-card2 rounded-xl p-4">
                    <p className="font-semibold text-sm mb-1">{w.title}</p>
                    <p className="text-apple-text-secondary text-xs leading-relaxed">{w.detail}</p>
                    <p className="text-apple-blue text-xs mt-2 font-medium">→ {w.action}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Strength */}
          {coaching.strength && (
            <div className="card">
              <p className="section-title">What You're Doing Well</p>
              <div className="flex items-start gap-3">
                <span className="text-apple-green text-base font-bold mt-0.5">↑</span>
                <p className="text-sm leading-relaxed">{coaching.strength}</p>
              </div>
            </div>
          )}

          {/* Champion Pool */}
          {coaching.champion_pool && (
            <div className="card">
              <p className="section-title">Champion Pool</p>
              <div className="space-y-0">
                {coaching.champion_pool.keep?.length > 0 && (
                  <div className="stat-row">
                    <span className="stat-label">Keep</span>
                    <div className="flex gap-1.5 flex-wrap justify-end">
                      {coaching.champion_pool.keep.map(c => (
                        <span key={c} className="text-xs bg-apple-green/10 text-apple-green px-2.5 py-0.5 rounded-full font-medium">{c}</span>
                      ))}
                    </div>
                  </div>
                )}
                {coaching.champion_pool.drop?.length > 0 && (
                  <div className="stat-row">
                    <span className="stat-label">Drop</span>
                    <div className="flex gap-1.5 flex-wrap justify-end">
                      {coaching.champion_pool.drop.map(c => (
                        <span key={c} className="text-xs bg-apple-red/10 text-apple-red px-2.5 py-0.5 rounded-full font-medium">{c}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <p className="text-apple-text-secondary text-xs mt-3 leading-relaxed">{coaching.champion_pool.reasoning}</p>
            </div>
          )}

          {/* Role + Weekly Focus */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {coaching.role_recommendation && (
              <div className="card">
                <p className="section-title">Recommended Role</p>
                <p className="text-2xl font-bold text-apple-blue mb-2">
                  {ROLE_DISPLAY[coaching.role_recommendation.recommended] ?? coaching.role_recommendation.recommended}
                </p>
                <p className="text-apple-text-secondary text-xs leading-relaxed">{coaching.role_recommendation.reasoning}</p>
              </div>
            )}

            {coaching.weekly_focus && (
              <div className="card" style={{ borderColor: 'rgba(0,122,255,0.25)', borderWidth: 1, borderStyle: 'solid' }}>
                <p className="section-title">This Week's Focus</p>
                <p className="text-sm leading-relaxed">{coaching.weekly_focus}</p>
              </div>
            )}
          </div>

          <button
            onClick={analyze}
            className="w-full text-apple-text-tertiary text-xs py-2 hover:text-apple-text-secondary transition-colors"
          >
            Regenerate analysis
          </button>
        </div>
      )}
    </div>
  )
}
