import { useState } from 'react'

const QUEUE_LABELS = {
  420: 'Ranked Solo',
  440: 'Ranked Flex',
  450: 'ARAM',
  400: 'Normal',
  430: 'Normal',
  700: 'Clash',
}

const QUEUE_TABS = [
  { label: 'All', filter: null },
  { label: 'Ranked Solo', filter: 420 },
  { label: 'Ranked Flex', filter: 440 },
]

export default function MatchHistory({ matches, ddVersion, runeTree, onMatchClick, playerPuuid, region }) {
  const [activeTab, setActiveTab] = useState(null) // null = All

  if (!matches?.length) return null

  const filtered = activeTab === null ? matches : matches.filter(m => m.queueId === activeTab)

  return (
    <div>
      {/* Queue filter tabs */}
      <div className="flex gap-1 mb-3">
        {QUEUE_TABS.map(tab => (
          <button
            key={tab.label}
            onClick={() => setActiveTab(tab.filter)}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold tracking-wide transition-all ${
              activeTab === tab.filter
                ? 'bg-zar-pink text-white'
                : 'text-zar-text-secondary hover:text-white border border-zar-border'
            }`}
          >
            {tab.label}
          </button>
        ))}
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
  const kdaRatio = ((match.kills + match.assists) / Math.max(match.deaths, 1)).toFixed(2)
  const isGoodKda = parseFloat(kdaRatio) >= 3
  const queueLabel = QUEUE_LABELS[match.queueId] || 'Game'

  return (
    <div
      onClick={onClick}
      className={`flex items-center gap-3 rounded-xl px-3 py-2.5 border-l-2 cursor-pointer transition-all hover:brightness-125 ${
        match.win
          ? 'bg-zar-green/5 border-l-zar-green'
          : 'bg-zar-red/5 border-l-zar-red'
      } border border-zar-border`}
    >
      <img
        src={champUrl}
        alt={match.champion}
        className="w-10 h-10 rounded-lg shrink-0"
        onError={e => { e.target.style.display = 'none' }}
      />

      <div className="w-14 shrink-0">
        <p className={`text-xs font-black uppercase tracking-wider ${match.win ? 'text-zar-green' : 'text-zar-red'}`}>
          {match.result}
        </p>
        <p className="text-[10px] text-zar-text-tertiary">{match.duration}m</p>
      </div>

      <div className="w-24 shrink-0">
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
          {match.role ? match.role.charAt(0) + match.role.slice(1).toLowerCase() : '—'}
        </p>
      </div>

      <div className="hidden md:flex gap-1 flex-wrap">
        {match.items.filter(id => id !== 0).map((itemId, j) => (
          <img
            key={`${itemId}-${j}`}
            src={`https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/item/${itemId}.png`}
            alt=""
            className="w-7 h-7 rounded"
            onError={e => { e.target.style.display = 'none' }}
          />
        ))}
      </div>

      <div className="ml-auto flex items-center gap-2">
        <span className="text-[10px] text-zar-text-tertiary hidden lg:block">{queueLabel}</span>
        <svg className="w-4 h-4 text-zar-text-tertiary shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  )
}
