const QUEUE_LABELS = {
  RANKED_SOLO_5x5: 'Ranked Solo / Duo',
  RANKED_FLEX_SR: 'Ranked Flex',
  RANKED_TFT: 'TFT',
}

const TIER_COLORS = {
  IRON: '#7a7a7a',
  BRONZE: '#a0522d',
  SILVER: '#9aa4ae',
  GOLD: '#c89b3c',
  PLATINUM: '#0e9b80',
  EMERALD: '#2ecc71',
  DIAMOND: '#5d6fc4',
  MASTER: '#9d48e0',
  GRANDMASTER: '#e05252',
  CHALLENGER: '#f0e6d2',
}

export default function RankedCard({ queue }) {
  const { queueType, tier, rank, leaguePoints, wins, losses, streak, mostPlayedRole, avgKDA } = queue
  const total = wins + losses
  const winrate = total > 0 ? ((wins / total) * 100).toFixed(1) : '0.0'
  const kdaRatio = avgKDA
    ? ((avgKDA.kills + avgKDA.assists) / Math.max(avgKDA.deaths, 1)).toFixed(2)
    : null
  const tierColor = TIER_COLORS[tier?.toUpperCase()] ?? '#ffffff'
  const emblemUrl =
    `https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/ranked-emblem/emblem-${tier?.toLowerCase()}.png`

  return (
    <div className="card">
      <p className="text-xs text-gray-400 mb-3 font-medium uppercase tracking-wider">
        {QUEUE_LABELS[queueType] ?? queueType}
      </p>

      <div className="flex items-center gap-4 mb-4">
        <img
          src={emblemUrl}
          alt={tier}
          className="w-20 h-auto"
          onError={e => { e.target.style.display = 'none' }}
        />
        <div>
          <p className="text-xl font-bold" style={{ color: tierColor }}>
            {tier} {rank}
          </p>
          <p className="text-gray-300 text-sm">{leaguePoints} LP</p>
        </div>
      </div>

      <div className="space-y-1.5">
        <div className="stat-row">
          <span className="stat-label">W / L</span>
          <span>
            <span className="text-green-400">{wins}W</span>
            {' '}<span className="text-red-400">{losses}L</span>
            {' '}<span className="text-gray-400">({winrate}%)</span>
          </span>
        </div>

        {/* Win rate bar */}
        <div className="h-1.5 bg-lol-border rounded-full overflow-hidden">
          <div className="h-full bg-blue-500 rounded-full" style={{ width: `${winrate}%` }} />
        </div>

        {streak !== 0 && (
          <div className="stat-row">
            <span className="stat-label">Streak</span>
            <span className={`font-semibold ${streak > 0 ? 'text-blue-400' : 'text-red-400'}`}>
              {Math.abs(streak)}{streak > 0 ? 'W' : 'L'} streak
            </span>
          </div>
        )}

        {mostPlayedRole && mostPlayedRole !== 'Unknown' && (
          <div className="stat-row">
            <span className="stat-label">Main role</span>
            <span>{mostPlayedRole.charAt(0) + mostPlayedRole.slice(1).toLowerCase()}</span>
          </div>
        )}

        {avgKDA && (
          <div className="stat-row">
            <span className="stat-label">Avg KDA</span>
            <span>
              {avgKDA.kills.toFixed(1)} / {avgKDA.deaths.toFixed(1)} / {avgKDA.assists.toFixed(1)}
              {' '}<span className="text-lol-gold">({kdaRatio})</span>
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
