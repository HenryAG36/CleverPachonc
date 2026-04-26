export default function ProfileHeader({ summoner, ddVersion }) {
  const iconUrl =
    `https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/profileicon/${summoner.profileIconId}.png`

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

      <div>
        <h2 className="text-2xl font-black leading-tight tracking-tight">
          {summoner.gameName}
          {summoner.tagLine && (
            <span className="text-zar-text-secondary text-base font-medium"> #{summoner.tagLine}</span>
          )}
        </h2>
        <p className="text-zar-text-tertiary text-xs uppercase tracking-widest mt-1 font-semibold">
          Summoner Profile
        </p>
      </div>
    </div>
  )
}
