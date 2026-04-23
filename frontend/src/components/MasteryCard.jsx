export default function MasteryCard({ mastery, ddVersion }) {
  if (!mastery?.length) {
    return (
      <div className="card text-apple-text-secondary text-sm text-center py-8">
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
          <div key={champ.championId} className="flex items-center gap-3 py-3 border-b border-apple-separator last:border-0">
            <span className="text-apple-text-tertiary text-xs w-5 shrink-0">#{i + 1}</span>
            <img
              src={iconUrl}
              alt={champ.championName}
              className="w-10 h-10 rounded-xl"
              onError={e => { e.target.style.display = 'none' }}
            />
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-sm truncate">{champ.championName}</p>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="bg-apple-blue/10 text-apple-blue text-xs px-1.5 py-0.5 rounded-md font-medium">
                  M{champ.championLevel}
                </span>
                <span className="text-apple-text-secondary text-xs">
                  {champ.championPoints.toLocaleString()} pts
                </span>
              </div>
            </div>
            {champ.lastPlayTime && (
              <span className="text-apple-text-tertiary text-xs shrink-0">{champ.lastPlayTime}</span>
            )}
          </div>
        )
      })}
    </div>
  )
}
