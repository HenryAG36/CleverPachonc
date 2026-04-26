import { useState } from 'react'
import ProfileHeader from './ProfileHeader'
import WinRateChart from './WinRateChart'
import RankedCard from './RankedCard'
import MasteryCard from './MasteryCard'
import MatchHistory from './MatchHistory'
import ChampionStats from './ChampionStats'
import AICoach from './AICoach'
import PreSessionCard from './PreSessionCard'

const TABS = [
  { id: 'overview',  label: 'Overview' },
  { id: 'matches',   label: 'Matches' },
  { id: 'champions', label: 'Champions' },
  { id: 'coach',     label: 'AI Coach' },
]

export default function StatsView({ data }) {
  const [activeTab, setActiveTab] = useState('overview')
  const { dd_version, summoner, ranked, mastery, matches, champion_stats, meta } = data
  const hasRanked = ranked?.length > 0
  const hasMatches = matches?.length > 0
  const hasChampStats = champion_stats && Object.keys(champion_stats).length > 0

  return (
    <div className="mt-2">
      {/* Persistent profile header */}
      <ProfileHeader summoner={summoner} ddVersion={dd_version} />

      {/* Tab bar */}
      <div className="mt-6 border-b border-zar-border">
        <nav className="flex gap-0" aria-label="Profile sections">
          {TABS.map(tab => {
            const isActive = activeTab === tab.id
            const isDisabled =
              (tab.id === 'matches' && !hasMatches) ||
              (tab.id === 'champions' && !hasChampStats) ||
              (tab.id === 'coach' && !hasMatches)
            return (
              <button
                key={tab.id}
                onClick={() => !isDisabled && setActiveTab(tab.id)}
                disabled={isDisabled}
                className={`
                  relative px-4 py-3 text-xs font-bold uppercase tracking-widest transition-colors
                  ${isActive
                    ? 'text-white after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-zar-pink after:rounded-t'
                    : isDisabled
                      ? 'text-zar-text-tertiary cursor-default'
                      : 'text-zar-text-secondary hover:text-white'
                  }
                `}
              >
                {tab.label}
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
          <MatchHistory matches={matches} ddVersion={dd_version} />
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
    </div>
  )
}
