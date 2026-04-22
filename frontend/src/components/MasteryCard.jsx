export default function MasteryCard({ mastery, ddVersion }) {
  if (!mastery?.length) {
    return (
      <div className="card text-gray-400 text-sm text-center py-8">
        No mastery data available
      </div>
    )
  }

  return (
    <div className="card">
      <div className="space-y-3">
        {mastery.map((champ, i) => {
          const iconUrl =
            `https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/champion/${champ.championName}.png`

          return (
            <div key={i} className="flex items-center gap-3">
              <img
                src={iconUrl}
                alt={champ.championName}
                className="w-11 h-11 rounded-lg border border-lol-border"
                onError={e => { e.target.style.display = 'none' }}
              />
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-sm truncate">{champ.championName}</p>
                <p className="text-xs text-gray-400">
                  M{champ.championLevel} · {champ.championPoints.toLocaleString()} pts
                </p>
              </div>
              {champ.lastPlayTime && (
                <span className="text-xs text-gray-500 shrink-0">{champ.lastPlayTime}</span>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
