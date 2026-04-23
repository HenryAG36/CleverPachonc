export default function ProfileHeader({ summoner, ddVersion }) {
  const iconUrl =
    `https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/profileicon/${summoner.profileIconId}.png`

  return (
    <div className="card flex items-center gap-5">
      <div className="relative shrink-0">
        <img
          src={iconUrl}
          alt="Profile icon"
          className="w-20 h-20 rounded-full ring-2 ring-white/20"
          onError={e => { e.target.style.display = 'none' }}
        />
        <span className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-apple-card2 text-apple-text-secondary text-xs font-semibold px-2.5 py-0.5 rounded-full whitespace-nowrap">
          {summoner.summonerLevel}
        </span>
      </div>

      <div>
        <h2 className="text-2xl font-bold leading-tight">
          {summoner.gameName}
          {summoner.tagLine && (
            <span className="text-apple-text-secondary text-lg font-normal"> #{summoner.tagLine}</span>
          )}
        </h2>
        <p className="text-apple-text-secondary text-sm mt-0.5">Level {summoner.summonerLevel}</p>
      </div>
    </div>
  )
}
