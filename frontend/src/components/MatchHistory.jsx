export default function MatchHistory({ matches, ddVersion }) {
  if (!matches?.length) return null
  return (
    <div className="space-y-2">
      {matches.map((match, i) => (
        <MatchRow key={`${match.champion}-${match.duration}-${i}`} match={match} ddVersion={ddVersion} />
      ))}
    </div>
  )
}

function MatchRow({ match, ddVersion }) {
  const champUrl = `https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/champion/${match.champion}.png`
  const kdaRatio = ((match.kills + match.assists) / Math.max(match.deaths, 1)).toFixed(2)
  const isGoodKda = parseFloat(kdaRatio) >= 3

  return (
    <div
      className={`flex items-center gap-3 rounded-2xl p-3 ${
        match.win ? 'bg-apple-green/8' : 'bg-apple-red/8'
      }`}
    >
      <img
        src={champUrl}
        alt={match.champion}
        className="w-11 h-11 rounded-xl shrink-0"
        onError={e => { e.target.style.display = 'none' }}
      />

      <div className="w-16 shrink-0">
        <p className={`text-sm font-semibold ${match.win ? 'text-apple-green' : 'text-apple-red'}`}>
          {match.result}
        </p>
        <p className="text-xs text-apple-text-tertiary">{match.duration}m</p>
      </div>

      <div className="w-24 shrink-0">
        <p className="text-sm font-mono text-white">
          {match.kills}/{match.deaths}/{match.assists}
        </p>
        <p className={`text-xs ${isGoodKda ? 'text-apple-yellow' : 'text-apple-text-secondary'}`}>
          {kdaRatio} KDA
        </p>
      </div>

      <div className="w-20 shrink-0 hidden sm:block">
        <p className="text-sm text-white">{match.cs} CS</p>
        <p className="text-xs text-apple-text-tertiary">
          {match.role ? match.role.charAt(0) + match.role.slice(1).toLowerCase() : '—'}
        </p>
      </div>

      <div className="flex gap-1 ml-auto flex-wrap justify-end">
        {match.items
          .filter(id => id !== 0)
          .map((itemId, j) => (
            <img
              key={`${itemId}-${j}`}
              src={`https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/item/${itemId}.png`}
              alt={`Item ${itemId}`}
              className="w-7 h-7 rounded-lg"
              onError={e => { e.target.style.display = 'none' }}
            />
          ))}
      </div>
    </div>
  )
}
