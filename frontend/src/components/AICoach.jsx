import { useState } from 'react'
import MetaTierBadge from './MetaTierBadge'
import BuildComparison from './BuildComparison'
import MatchupTable from './MatchupTable'

const ROLE_DISPLAY = {
  TOP: 'Top', JUNGLE: 'Jungle', MIDDLE: 'Mid',
  BOTTOM: 'ADC', UTILITY: 'Support',
}

// Safety net: translate any raw metric keys the LLM might slip through
const RAW_KEY_MAP = {
  kda_high: 'Strong KDA / Clean Survival Mechanics',
  cs_high: 'Strong CS / Farming Efficiency',
  dmg_high: 'High Damage Output',
  vision_high: 'Excellent Vision Control',
  maintain_consistency: 'Keep your current consistency — fundamentals look solid.',
}
function safeText(text) {
  if (!text) return ''
  // Detect raw metric key pattern like "kda_high" or "role_wr_low:MIDDLE"
  const raw = text.match(/^([a-z]+_[a-z]+)(:[\w]+)?$/)
  if (!raw) return text
  const mapped = RAW_KEY_MAP[raw[1]]
  if (mapped) return mapped
  // Generic humanize: "role_wr_low:MIDDLE" → "Role Win Rate Low — MIDDLE"
  return text.replace(/_/g, ' ').replace(':', ' — ').replace(/\b\w/g, c => c.toUpperCase())
}

const WEAKNESS_BORDER = [
  'border-l-2 border-apple-red',
  'border-l-2 border-amber-500',
  'border-l-2 border-apple-blue',
]

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
              AI analysis of your last 20 games — strengths, weaknesses, meta comparison, and a clear path to climb
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
                  <div key={i} className={`bg-apple-card2 rounded-xl p-4 ${WEAKNESS_BORDER[i] ?? WEAKNESS_BORDER[2]}`}>
                    <p className="font-semibold text-sm mb-1.5">{w.title}</p>
                    <p className="text-apple-text-secondary text-xs leading-relaxed">{w.detail}</p>
                    <div className="mt-2.5 flex items-start gap-1.5">
                      <span className="text-apple-blue mt-0.5">→</span>
                      <p className="text-apple-blue text-xs font-medium leading-relaxed">{w.action}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Build comparisons from meta */}
          {coaching.meta?.per_champ_meta && (() => {
            const entries = Object.entries(coaching.meta.per_champ_meta)
              .filter(([, cm]) => cm.build_gaps?.length > 0)
              .slice(0, 2)
            if (!entries.length) return null
            return (
              <div className="card">
                <p className="section-title">Build Comparison</p>
                <div className="space-y-3">
                  {entries.map(([champ]) => (
                    <BuildComparison
                      key={champ}
                      championName={champ}
                      playerItems={data.champion_stats?.[champ]?.core_items}
                      metaItems={coaching.meta.per_champ_meta[champ]?.build_gaps}
                      ddVersion={data.dd_version}
                    />
                  ))}
                </div>
              </div>
            )
          })()}

          {/* Matchup insights */}
          {coaching.meta?.matchup_insights?.length > 0 && (
            <MatchupTable
              matchupInsights={coaching.meta.matchup_insights}
              ddVersion={data.dd_version}
            />
          )}

          {/* Pool vs meta */}
          {coaching.meta?.meta_picks?.length > 0 && (
            <div className="card">
              <p className="section-title">Your Pool vs the Meta</p>
              <div className="space-y-0">
                {coaching.meta.meta_picks.map((pick, i) => {
                  const iconUrl = `https://ddragon.leagueoflegends.com/cdn/${data.dd_version}/img/champion/${pick.name}.png`
                  return (
                    <div key={i} className="stat-row items-center">
                      <div className="flex items-center gap-2">
                        <img src={iconUrl} alt={pick.name} className="w-7 h-7 rounded"
                          onError={e => { e.target.style.display = 'none' }} />
                        <span className="text-sm font-medium">{pick.name}</span>
                        <MetaTierBadge tier={pick.tier} wr={pick.wr} size="xs" />
                      </div>
                      <span className="text-xs text-apple-text-secondary">
                        {ROLE_DISPLAY[pick.role] ?? pick.role}
                      </span>
                    </div>
                  )
                })}
              </div>
              <p className="text-[10px] text-apple-text-tertiary mt-2">Meta win rates at your tier this patch</p>
            </div>
          )}

          {/* Strength */}
          {coaching.strength && (
            <div className="card border border-apple-green/20">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-6 h-6 rounded-full bg-apple-green/15 flex items-center justify-center flex-shrink-0">
                  <svg className="w-3.5 h-3.5 text-apple-green" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                </div>
                <p className="text-xs font-semibold text-apple-text-secondary uppercase tracking-widest">What You're Doing Well</p>
              </div>
              <p className="text-sm leading-relaxed text-apple-text-primary">{safeText(coaching.strength)}</p>
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
                      {coaching.champion_pool.keep.map(c => {
                        const champMeta = coaching.meta?.per_champ_meta?.[c]
                        return (
                          <span key={c} className="text-xs bg-apple-green/10 text-apple-green px-2.5 py-0.5 rounded-full font-medium flex items-center gap-1">
                            {c}
                            {champMeta && <MetaTierBadge tier={champMeta.tier} size="xs" />}
                          </span>
                        )
                      })}
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
              <div className="card" style={{ borderColor: 'rgba(0,122,255,0.3)', borderWidth: 1, borderStyle: 'solid' }}>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-6 h-6 rounded-full bg-apple-blue/15 flex items-center justify-center flex-shrink-0">
                    <svg className="w-3.5 h-3.5 text-apple-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="text-xs font-semibold text-apple-text-secondary uppercase tracking-widest">This Week's Focus</p>
                </div>
                <p className="text-sm leading-relaxed">{safeText(coaching.weekly_focus)}</p>
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
