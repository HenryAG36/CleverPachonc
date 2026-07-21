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

function formatTier(tier, rank) {
  const display = tier.charAt(0).toUpperCase() + tier.slice(1).toLowerCase()
  const noDivision = ['MASTER', 'GRANDMASTER', 'CHALLENGER'].includes(tier.toUpperCase())
  return noDivision ? display : `${display} ${rank}`
}

export default function ProfileHeader({ summoner, ddVersion, ranked, region }) {
  const iconUrl =
    `https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/profileicon/${summoner.profileIconId}.png`
  const solo = ranked?.find(q => q.queueType === 'RANKED_SOLO_5x5')

  return (
    <div className="card flex items-center gap-5 mt-6">
      <div className="relative shrink-0">
        <div className="w-20 h-20 rounded-full ring-2 ring-zar-pink/50 ring-offset-2 ring-offset-zar-card overflow-hidden">
          <img
            src={iconUrl}
            alt="Profile icon"
            className="w-full h-full object-cover"
            onError={e => { e.target.style.display = 'none' }}
          />
        </div>
        <span className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 bg-zar-card2 border border-zar-border text-zar-cyan text-[10px] font-bold px-2 py-0.5 rounded-full whitespace-nowrap uppercase tracking-wider">
          Lv {summoner.summonerLevel}
        </span>
      </div>

      <div className="min-w-0">
        <h2 className="text-2xl font-black leading-tight tracking-tight truncate">
          {summoner.gameName}
          {summoner.tagLine && (
            <span className="text-zar-text-secondary text-base font-medium"> #{summoner.tagLine}</span>
          )}
        </h2>
        <div className="flex items-center flex-wrap gap-1.5 mt-1.5">
          {region && (
            <span className="bg-zar-card2 border border-zar-border text-zar-text-secondary text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
              {region}
            </span>
          )}
          {solo?.tier ? (
            <span
              className="bg-zar-card2 border border-zar-border text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider"
              style={{ color: TIER_COLORS[solo.tier.toUpperCase()] ?? '#ffffff' }}
            >
              {formatTier(solo.tier, solo.rank)} · {solo.leaguePoints} LP
            </span>
          ) : (
            <span className="bg-zar-card2 border border-zar-border text-zar-text-tertiary text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
              Unranked
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
