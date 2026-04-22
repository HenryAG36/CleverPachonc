export default function ProfileHeader({ summoner, ddVersion }) {
  const iconUrl =
    `https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/profileicon/${summoner.profileIconId}.png`

  return (
    <div className="card flex items-center gap-5 mt-8">
      <div className="relative shrink-0">
        <img
          src={iconUrl}
          alt="Profile icon"
          className="w-20 h-20 rounded-full border-2 border-lol-gold"
          onError={e => { e.target.style.display = 'none' }}
        />
        <span className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-lol-bg text-xs font-semibold px-2 py-0.5 rounded-full border border-lol-gold text-lol-gold whitespace-nowrap">
          {summoner.summonerLevel}
        </span>
      </div>

      <div>
        <h2 className="text-2xl font-bold leading-tight">
          {summoner.gameName}
          {summoner.tagLine && (
            <span className="text-gray-400 text-lg font-normal"> #{summoner.tagLine}</span>
          )}
        </h2>
        <p className="text-gray-500 text-sm mt-0.5">Level {summoner.summonerLevel}</p>
      </div>
    </div>
  )
}
