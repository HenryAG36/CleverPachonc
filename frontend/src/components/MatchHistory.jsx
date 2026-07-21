import { useState } from 'react'
import { championDisplayName } from '../utils/champions'
import { timeAgo } from '../utils/timeAgo'

const QUEUE_LABELS = {
  420: 'Ranked Solo',
  440: 'Ranked Flex',
}

const QUEUE_TABS = [
  { label: 'All', filter: null },
  { label: 'Ranked Solo', filter: 420 },
  { label: 'Ranked Flex', filter: 440 },
]

export default function MatchHistory({ matches, ddVersion, onMatchClick }) {
  const [activeTab, setActiveTab] = useState(null) // null = All

  if (!matches?.length) return null

  const filtered = activeTab === null ? matches : matches.filter(m => m.queueId === activeTab)
  const wins = filtered.filter(m => m.win).length
  const losses = filtered.length - wins
  const winrate = filtered.length > 0 ? Math.round((wins / filtered.length) * 100) : 0

  return (
    <div>
      {/* Queue filter tabs + summary */}
      <div className="flex flex-wrap items-center gap-1 mb-3">
        {QUEUE_TABS.map(tab => (
          <button
            key={tab.label}
            onClick={() => setActiveTab(tab.filter)}
            aria-pressed={activeTab === tab.filter}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold tracking-wide transition-all ${
              activeTab === tab.filter
                ? 'bg-zar-pink text-white'
                : 'text-zar-text-secondary hover:text-white border border-zar-border'
            }`}
          >
            {tab.label}
          </button>
        ))}
        {filtered.length > 0 && (
          <span className="ml-auto text-xs text-zar-text-secondary">
            <span className="text-zar-green font-bold">{wins}W</span>
            {' '}<span className="text-zar-red font-bold">{losses}L</span>
            {' '}· {winrate}%
          </span>
        )}
      </div>

      <div className="space-y-1.5">
        {filtered.map((match, i) => (
          <MatchRow
            key={`${match.matchId || match.champion}-${i}`}
            match={match}
            ddVersion={ddVersion}
            onClick={() => onMatchClick(match)}
          />
        ))}
        {filtered.length === 0 && (
          <p className="text-zar-text-tertiary text-sm text-center py-8">No games in this queue</p>
        )}
      </div>
    </div>
  )
}

function MatchRow({ match, ddVersion, onClick }) {
  const champUrl = `https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/champion/${match.champion}.png`
  const champName = championDisplayName(match.champion)
  const kdaRatio = ((match.kills + match.assists) / Math.max(match.deaths, 1)).toFixed(2)
  const isGoodKda = parseFloat(kdaRatio) >= 3
  const queueLabel = QUEUE_LABELS[match.queueId] || 'Ranked'
  const played = timeAgo(match.gameEndTimestamp)
  const items = match.items?.filter(id => id !== 0) ?? []

  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={`${match.result} as ${champName}, ${match.kills}/${match.deaths}/${match.assists} — view details`}
      className={`w-full text-left flex items-center gap-3 rounded-xl px-3 py-2.5 border-l-2 cursor-pointer transition-all hover:brightness-125 ${
        match.win
          ? 'bg-zar-green/5 border-l-zar-win'
          : 'bg-zar-red/5 border-l-zar-loss'
      } border border-zar-border`}
    >
      <img
        src={champUrl}
        alt=""
        className="w-10 h-10 rounded-lg shrink-0"
        onError={e => { e.target.style.display = 'none' }}
      />

      {/* Flexible below sm so the row never overflows a 320px viewport */}
      <div className="flex-1 sm:flex-none sm:w-24 min-w-0">
        <p className="text-sm font-bold text-white truncate">{champName}</p>
        <p className={`text-[10px] font-black uppercase tracking-wider ${match.win ? 'text-zar-green' : 'text-zar-red'}`}>
          {match.result}
        </p>
      </div>

      <div className="w-20 sm:w-24 shrink-0">
        <p className="text-sm font-bold font-mono text-white">
          {match.kills}/{match.deaths}/{match.assists}
        </p>
        <p className={`text-[10px] font-semibold ${isGoodKda ? 'text-zar-yellow' : 'text-zar-text-secondary'}`}>
          {kdaRatio} KDA
        </p>
      </div>

      <div className="w-20 shrink-0 hidden sm:block">
        <p className="text-sm font-semibold text-white">{match.cs} CS</p>
        <p className="text-[10px] text-zar-text-tertiary">
          {match.role ? match.role.charAt(0) + match.role.slice(1).toLowerCase() : '—'} · {match.duration}m
        </p>
      </div>

      <div className="hidden md:flex gap-1 flex-wrap">
        {items.map((itemId, j) => (
          <img
            key={`${itemId}-${j}`}
            src={`https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/item/${itemId}.png`}
            alt=""
            className="w-7 h-7 rounded"
            onError={e => { e.target.style.display = 'none' }}
          />
        ))}
      </div>

      <div className="ml-auto flex items-center gap-2 shrink-0">
        <div className="text-right hidden lg:block">
          <p className="text-[10px] text-zar-text-tertiary">{queueLabel}</p>
          {played && <p className="text-[10px] text-zar-text-tertiary">{played}</p>}
        </div>
        <svg className="w-4 h-4 text-zar-text-tertiary shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </button>
  )
}
