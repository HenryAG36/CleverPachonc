import ProfileHeader from './ProfileHeader'
import WinRateChart from './WinRateChart'
import RankedCard from './RankedCard'
import MasteryCard from './MasteryCard'
import MatchHistory from './MatchHistory'
import ChampionStats from './ChampionStats'

export default function StatsView({ data }) {
  const { dd_version, summoner, ranked, mastery, matches, champion_stats } = data
  const hasRanked = ranked?.length > 0
  const hasMatches = matches?.length > 0
  const hasChampStats = champion_stats && Object.keys(champion_stats).length > 0

  return (
    <div className="space-y-8 mt-6">
      <ProfileHeader summoner={summoner} ddVersion={dd_version} />

      {hasMatches && <WinRateChart matches={matches} />}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="section-title">Ranked</h2>
          {hasRanked ? (
            <div className="space-y-4">
              {ranked.map(q => <RankedCard key={q.queueType} queue={q} />)}
            </div>
          ) : (
            <div className="card text-apple-text-secondary text-sm text-center py-10">
              No ranked data this season
            </div>
          )}
        </div>

        <div>
          <h2 className="section-title">Top Champions</h2>
          <MasteryCard mastery={mastery} ddVersion={dd_version} />
        </div>
      </div>

      {hasMatches && (
        <div>
          <h2 className="section-title">Recent Matches</h2>
          <MatchHistory matches={matches} ddVersion={dd_version} />
        </div>
      )}

      {hasChampStats && (
        <div>
          <h2 className="section-title">Champion Stats</h2>
          <ChampionStats stats={champion_stats} ddVersion={dd_version} />
        </div>
      )}
    </div>
  )
}
