import { useState } from 'react'
import ProfileHeader from './ProfileHeader'
import WinRateChart from './WinRateChart'
import RankedCard from './RankedCard'
import MasteryCard from './MasteryCard'
import MatchHistory from './MatchHistory'
import ChampionStats from './ChampionStats'
import AICoach from './AICoach'
import PreSessionCard from './PreSessionCard'
import MatchDetailModal from './MatchDetailModal'

export default function StatsView({ data, region, playerName }) {
  const [activeTab, setActiveTab] = useState('overview')
  const [selectedMatch, setSelectedMatch] = useState(null)
  const { dd_version, summoner, ranked, mastery, matches, champion_stats, meta } = data
  const playerPuuid = summoner?.puuid || null
  const hasRanked = ranked?.length > 0
  const hasMatches = matches?.length > 0
  // ChampionStats only shows champions with >= 2 games — gate the tab the same way
  const hasChampStats =
    champion_stats && Object.values(champion_stats).some(s => s?.games >= 2)

  const TABS = [
    { id: 'overview', label: 'Overview', disabled: false },
    { id: 'matches', label: 'Matches', disabled: !hasMatches, count: matches?.length },
    { id: 'champions', label: 'Champions', disabled: !hasChampStats },
    { id: 'coach', label: 'AI Coach', disabled: !hasMatches },
  ]

  return (
    <div className="mt-2 fade-in-up">
      {/* Persistent profile header */}
      <ProfileHeader summoner={summoner} ddVersion={dd_version} ranked={ranked} region={region} />

      {/* Tab bar */}
      <div className="mt-6 border-b border-zar-border overflow-x-auto">
        <nav className="flex gap-0 min-w-max" role="tablist" aria-label="Profile sections">
          {TABS.map(tab => {
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                role="tab"
                aria-selected={isActive}
                onClick={() => !tab.disabled && setActiveTab(tab.id)}
                disabled={tab.disabled}
                className={`
                  relative px-4 py-3 text-xs font-bold uppercase tracking-widest transition-colors whitespace-nowrap
                  ${isActive
                    ? 'text-white after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-zar-pink after:rounded-t'
                    : tab.disabled
                      ? 'text-zar-text-tertiary cursor-default'
                      : 'text-zar-text-secondary hover:text-white'
                  }
                `}
              >
                {tab.label}
                {tab.count > 0 && (
                  <span className={`ml-1.5 text-[9px] px-1.5 py-0.5 rounded-full font-black ${
                    isActive ? 'bg-zar-pink/15 text-zar-pink' : 'bg-white/5 text-zar-text-tertiary'
                  }`}>
                    {tab.count}
                  </span>
                )}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab content */}
      <div className="pt-6 space-y-6">

        {/* Overview */}
        {activeTab === 'overview' && (
          <>
            {meta && <PreSessionCard meta={meta} ddVersion={dd_version} />}

            {hasMatches && <WinRateChart matches={matches} />}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h2 className="section-title">Ranked</h2>
                {hasRanked ? (
                  <div className="space-y-4">
                    {ranked.map(q => <RankedCard key={q.queueType} queue={q} />)}
                  </div>
                ) : (
                  <div className="card text-zar-text-secondary text-sm text-center py-10">
                    No ranked data this season
                  </div>
                )}
              </div>

              <div>
                <h2 className="section-title">Top Champions</h2>
                <MasteryCard mastery={mastery} ddVersion={dd_version} />
              </div>
            </div>
          </>
        )}

        {/* Matches */}
        {activeTab === 'matches' && hasMatches && (
          <MatchHistory
            matches={matches}
            ddVersion={dd_version}
            onMatchClick={setSelectedMatch}
          />
        )}

        {/* Champions */}
        {activeTab === 'champions' && hasChampStats && (
          <ChampionStats stats={champion_stats} ddVersion={dd_version} meta={meta} />
        )}

        {/* AI Coach */}
        {activeTab === 'coach' && hasMatches && (
          <AICoach data={data} />
        )}

      </div>

      {selectedMatch && (
        <MatchDetailModal
          match={selectedMatch}
          ddVersion={dd_version}
          runeTree={data.rune_tree || []}
          ranked={ranked}
          playerPuuid={playerPuuid}
          playerName={playerName}
          region={region}
          onClose={() => setSelectedMatch(null)}
        />
      )}
    </div>
  )
}
