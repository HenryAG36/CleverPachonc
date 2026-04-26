import { useState, useEffect } from 'react'
import RuneTooltip from './RuneTooltip'
import WardMap from './WardMap'

const QUEUE_NAMES = { 420: 'Ranked Solo', 440: 'Ranked Flex', 450: 'ARAM', 400: 'Normal', 430: 'Normal' }
const ROLE_LABELS = { TOP: 'Top', JUNGLE: 'JGL', MIDDLE: 'Mid', BOTTOM: 'Bot', UTILITY: 'Sup' }

const DDR = (version) => `https://ddragon.leagueoflegends.com/cdn/${version}/img`

export default function MatchDetailModal({ match, ddVersion, runeTree, ranked, playerPuuid, playerName, region, onClose }) {
  const [coaching, setCoaching] = useState(null)
  const [coachLoading, setCoachLoading] = useState(false)
  const [coachError, setCoachError] = useState(null)

  // Derive player puuid from participants if not directly available
  const resolvedPuuid = playerPuuid || match.participants?.find(
    p => p.riotIdGameName?.toLowerCase() === (playerName?.split('#')[0] || '').toLowerCase()
  )?.puuid || ''

  // Close on backdrop click or Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  const blueTeam = match.participants?.filter(p => p.teamId === 100) || []
  const redTeam = match.participants?.filter(p => p.teamId === 200) || []

  // Max damage in match for damage bar scaling
  const maxDamage = Math.max(...(match.participants?.map(p => p.damage) || [1]), 1)

  async function analyzeMatch() {
    setCoachLoading(true)
    setCoachError(null)
    setCoaching(null)
    try {
      const res = await fetch('/api/coach/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          match: { ...match, duration: match.duration },
          player_puuid: resolvedPuuid,
          ranked,
        }),
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json.error || 'Analysis failed')
      setCoaching(json)
    } catch (e) {
      setCoachError(e.message)
    } finally {
      setCoachLoading(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)' }}
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div
        className="bg-zar-bg2 border border-zar-border rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto"
        style={{ boxShadow: '0 25px 80px rgba(0,0,0,0.6)' }}
      >
        {/* Header */}
        <div
          className={`px-5 py-4 border-b border-zar-border flex items-center justify-between sticky top-0 z-10 rounded-t-2xl`}
          style={{ backdropFilter: 'blur(12px)', background: match.win ? 'rgba(46,204,113,0.08)' : 'rgba(255,71,87,0.08)' }}
        >
          <div className="flex items-center gap-3">
            <img
              src={`${DDR(ddVersion)}/champion/${match.champion}.png`}
              alt={match.champion}
              className="w-10 h-10 rounded-lg"
              onError={e => { e.target.style.display = 'none' }}
            />
            <div>
              <div className="flex items-center gap-2">
                <span className={`text-sm font-black uppercase tracking-wider ${match.win ? 'text-zar-green' : 'text-zar-red'}`}>
                  {match.result}
                </span>
                <span className="text-xs text-zar-text-tertiary">{QUEUE_NAMES[match.queueId] || 'Game'} · {match.duration}m</span>
              </div>
              <p className="text-sm font-semibold text-white">
                {match.champion} · {match.kills}/{match.deaths}/{match.assists}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="text-zar-text-secondary hover:text-white transition-colors p-1">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-5 space-y-5">
          {/* Scoreboard */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <TeamPanel
              team={blueTeam}
              teamColor="text-blue-400"
              teamLabel="Blue Team"
              ddVersion={ddVersion}
              runeTree={runeTree}
              maxDamage={maxDamage}
              playerPuuid={resolvedPuuid}
            />
            <TeamPanel
              team={redTeam}
              teamColor="text-zar-red"
              teamLabel="Red Team"
              ddVersion={ddVersion}
              runeTree={runeTree}
              maxDamage={maxDamage}
              playerPuuid={resolvedPuuid}
            />
          </div>

          {/* Ward Map */}
          {resolvedPuuid && (
            <WardMap matchId={match.matchId} region={region} puuid={resolvedPuuid} />
          )}

          {/* Match AI Coach */}
          <div>
            <p className="section-title">Match Coach</p>
            {!coaching && !coachLoading && (
              <div className="card flex flex-col items-center py-8 gap-3">
                <p className="text-zar-text-secondary text-sm text-center max-w-xs">
                  Get AI coaching specific to this game — build decisions, key mistakes, and one drill to improve
                </p>
                <button onClick={analyzeMatch} className="zar-btn">
                  Analyze This Game
                </button>
              </div>
            )}
            {coachLoading && (
              <div className="card flex items-center justify-center gap-2 py-8">
                <div className="w-4 h-4 border-2 border-zar-pink border-t-transparent rounded-full animate-spin" />
                <span className="text-zar-text-secondary text-sm">Analyzing…</span>
              </div>
            )}
            {coachError && !coachLoading && (
              <div className="card flex flex-col items-center gap-3 py-6">
                <p className="text-zar-red text-sm">{coachError}</p>
                <button onClick={analyzeMatch} className="zar-btn-ghost">Retry</button>
              </div>
            )}
            {coaching && !coachLoading && (
              <div className="space-y-3">
                <div className="card">
                  <p className="text-sm leading-relaxed">{coaching.assessment}</p>
                </div>
                {coaching.key_mistake && (
                  <div className="card border-l-2 border-l-zar-red">
                    <p className="text-xs font-bold uppercase tracking-widest text-zar-text-secondary mb-1.5">Key Mistake</p>
                    <p className="text-sm font-semibold mb-1">{coaching.key_mistake.what}</p>
                    <p className="text-xs text-zar-text-secondary mb-2">{coaching.key_mistake.why}</p>
                    <div className="flex gap-1.5 items-start">
                      <span className="text-zar-cyan mt-0.5 shrink-0">→</span>
                      <p className="text-xs text-zar-cyan font-medium">{coaching.key_mistake.fix}</p>
                    </div>
                  </div>
                )}
                {coaching.strength && (
                  <div className="card border-l-2 border-l-zar-green">
                    <p className="text-xs font-bold uppercase tracking-widest text-zar-text-secondary mb-1.5">Strength</p>
                    <p className="text-sm">{coaching.strength}</p>
                  </div>
                )}
                {coaching.improvement && (
                  <div className="card border-l-2 border-l-zar-cyan">
                    <p className="text-xs font-bold uppercase tracking-widest text-zar-text-secondary mb-1.5">This Game's Focus</p>
                    <p className="text-sm">{coaching.improvement}</p>
                  </div>
                )}
                <button
                  onClick={analyzeMatch}
                  className="w-full text-zar-text-tertiary text-xs py-2 hover:text-zar-text-secondary transition-colors"
                >
                  Regenerate
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function TeamPanel({ team, teamColor, teamLabel, ddVersion, runeTree, maxDamage, playerPuuid }) {
  return (
    <div>
      <p className={`text-[10px] font-bold uppercase tracking-widest mb-2 ${teamColor}`}>{teamLabel}</p>
      <div className="space-y-1">
        {team.map((p, i) => {
          const isPlayer = p.puuid === playerPuuid
          const kdaRatio = ((p.kills + p.assists) / Math.max(p.deaths, 1)).toFixed(1)
          const damageWidth = Math.round((p.damage / maxDamage) * 100)
          const keystoneId = p.perks?.styles?.[0]?.selections?.[0]?.perk
          const keystoneRune = runeTree
            ?.flatMap(path => path.slots?.[0]?.runes || [])
            .find(r => r.id === keystoneId)

          return (
            <div
              key={i}
              className={`flex items-center gap-2 rounded-lg px-2.5 py-1.5 ${
                isPlayer ? 'bg-zar-card3 border border-zar-cyan/20' : 'bg-zar-card2'
              }`}
            >
              <img
                src={`https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/champion/${p.championName}.png`}
                alt={p.championName}
                className="w-7 h-7 rounded shrink-0"
                onError={e => { e.target.style.display = 'none' }}
              />

              {/* Rune keystone tooltip trigger */}
              <RuneTooltip perks={p.perks} runeTree={runeTree}>
                <div className="w-5 h-5 shrink-0 cursor-pointer">
                  {keystoneRune ? (
                    <img
                      src={`https://ddragon.leagueoflegends.com/cdn/img/${keystoneRune.icon}`}
                      alt={keystoneRune.name}
                      className="w-5 h-5 rounded-full"
                      onError={e => { e.target.style.display = 'none' }}
                    />
                  ) : (
                    <div className="w-5 h-5 rounded-full bg-zar-card3" />
                  )}
                </div>
              </RuneTooltip>

              <div className="flex-1 min-w-0">
                <p className={`text-xs font-semibold truncate ${isPlayer ? 'text-zar-cyan' : 'text-white'}`}>
                  {p.riotIdGameName || p.championName}
                </p>
                <p className="text-[10px] text-zar-text-tertiary">
                  {p.kills}/{p.deaths}/{p.assists} · {p.cs}CS
                </p>
              </div>

              <div className="w-16 shrink-0">
                <div className="h-1.5 bg-zar-card3 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-zar-pink"
                    style={{ width: `${damageWidth}%` }}
                  />
                </div>
                <p className="text-[10px] text-zar-text-tertiary text-right mt-0.5">
                  {(p.damage / 1000).toFixed(1)}k
                </p>
              </div>

              {/* Items (compact) */}
              <div className="flex gap-0.5 shrink-0">
                {p.items.filter(id => id !== 0).slice(0, 4).map((itemId, j) => (
                  <img
                    key={j}
                    src={`https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/item/${itemId}.png`}
                    alt=""
                    className="w-5 h-5 rounded"
                    onError={e => { e.target.style.display = 'none' }}
                  />
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
