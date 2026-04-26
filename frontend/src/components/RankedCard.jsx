const QUEUE_LABELS = {
  RANKED_SOLO_5x5: 'Ranked Solo / Duo',
  RANKED_FLEX_SR: 'Ranked Flex',
  RANKED_TFT: 'TFT',
}

const TIER_COLORS = {
  IRON: '#7a7a7a',
  BRONZE: '#cd7f32',
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
  const NO_DIVISION_TIERS = ['MASTER', 'GRANDMASTER', 'CHALLENGER']
  const tierUpper = tier?.toUpperCase()
  const displayTier = tier ? tier.charAt(0).toUpperCase() + tier.slice(1).toLowerCase() : ''
  const displayRank = NO_DIVISION_TIERS.includes(tierUpper) ? '' : rank

  return (
    <div className="card">
      <p className="section-title">{QUEUE_LABELS[queueType] ?? queueType}</p>

      <div className="flex items-center gap-4 mb-4">
        <img
          src={emblemUrl}
          alt={tier}
          className="w-24 h-auto drop-shadow-lg"
          onError={e => { e.target.style.display = 'none' }}
        />
        <div>
          <p className="text-xl font-black tracking-tight" style={{ color: tierColor }}>
            {displayTier}{displayRank ? ` ${displayRank}` : ''}
          </p>
          <p className="text-zar-cyan font-bold text-sm mt-0.5">{leaguePoints} <span className="text-zar-text-secondary font-normal">LP</span></p>
        </div>
      </div>

      <div className="space-y-0">
        <div className="stat-row">
          <span className="stat-label">W / L</span>
          <span>
            <span className="text-zar-green font-semibold">{wins}W</span>
            {' '}<span className="text-zar-text-secondary">/</span>{' '}
            <span className="text-zar-red font-semibold">{losses}L</span>
            {' '}<span className="text-zar-text-secondary">({winrate}%)</span>
          </span>
        </div>

        <div className="h-1.5 bg-zar-card2 rounded-full overflow-hidden mt-1 mb-2">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{ width: `${winrate}%`, background: 'linear-gradient(90deg, #00CFDD, #00CFDD99)' }}
          />
        </div>

        {streak !== 0 && (
          <div className="stat-row">
            <span className="stat-label">Streak</span>
            <span
              className={`text-xs font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider ${
                streak > 0
                  ? 'bg-zar-green/10 text-zar-green'
                  : 'bg-zar-red/10 text-zar-red'
              }`}
            >
              {Math.abs(streak)}{streak > 0 ? 'W' : 'L'} Streak
            </span>
          </div>
        )}

        {mostPlayedRole && mostPlayedRole !== 'Unknown' && (
          <div className="stat-row">
            <span className="stat-label">Main Role</span>
            <span className="font-semibold">{mostPlayedRole.charAt(0) + mostPlayedRole.slice(1).toLowerCase()}</span>
          </div>
        )}

        {avgKDA && (
          <div className="stat-row">
            <span className="stat-label">Avg KDA</span>
            <span>
              <span className="font-mono">{avgKDA.kills.toFixed(1)} / {avgKDA.deaths.toFixed(1)} / {avgKDA.assists.toFixed(1)}</span>
              {' '}
              <span className={`font-bold ${parseFloat(kdaRatio) >= 3 ? 'text-zar-yellow' : 'text-zar-text-secondary'}`}>
                ({kdaRatio})
              </span>
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
