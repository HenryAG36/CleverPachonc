export default function MasteryCard({ mastery, ddVersion }) {
  if (!mastery?.length) {
    return (
      <div className="card text-zar-text-secondary text-sm text-center py-8">
        No mastery data available
      </div>
    )
  }

  return (
    <div className="card">
      {mastery.map((champ, i) => {
        const iconUrl =
          `https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/champion/${champ.championName}.png`

        return (
          <div key={champ.championId} className="flex items-center gap-3 py-3 border-b border-zar-border last:border-0">
            <span className="text-zar-text-tertiary text-xs w-5 shrink-0 font-bold">#{i + 1}</span>
            <img
              src={iconUrl}
              alt={champ.championName}
              className="w-10 h-10 rounded-lg"
              onError={e => { e.target.style.display = 'none' }}
            />
            <div className="flex-1 min-w-0">
              <p className="font-bold text-sm truncate">{champ.championName}</p>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="bg-zar-pink/10 text-zar-pink border border-zar-pink/20 text-[10px] px-1.5 py-0.5 rounded font-bold uppercase tracking-wide">
                  M{champ.championLevel}
                </span>
                <span className="text-zar-text-secondary text-xs">
                  {champ.championPoints.toLocaleString()} pts
                </span>
              </div>
            </div>
            {champ.lastPlayTime && (
              <span className="text-zar-text-tertiary text-xs shrink-0">{champ.lastPlayTime}</span>
            )}
          </div>
        )
      })}
    </div>
  )
}
