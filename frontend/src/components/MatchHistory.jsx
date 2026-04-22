export default function MatchHistory({ matches, ddVersion }) {
  if (!matches?.length) return null
  return (
    <div className="space-y-2">
      {matches.map((match, i) => (
        <MatchRow key={i} match={match} ddVersion={ddVersion} />
      ))}
    </div>
  )
}

function MatchRow({ match, ddVersion }) {
  const champUrl =
    `https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/champion/${match.champion}.png`
  const kdaRatio = ((match.kills + match.assists) / Math.max(match.deaths, 1)).toFixed(2)
  const isGoodKda = parseFloat(kdaRatio) >= 3

  return (
    <div
      className={`flex items-center gap-3 rounded-xl p-3 border-l-4 ${
        match.win
          ? 'bg-blue-950/30 border-blue-500'
          : 'bg-red-950/30 border-red-500'
      }`}
    >
      {/* Champion icon */}
      <img
        src={champUrl}
        alt={match.champion}
        className="w-10 h-10 rounded-lg shrink-0"
        onError={e => { e.target.style.display = 'none' }}
      />

      {/* Result + duration */}
      <div className="w-16 shrink-0">
        <p className={`text-sm font-semibold ${match.win ? 'text-blue-400' : 'text-red-400'}`}>
          {match.result}
        </p>
        <p className="text-xs text-gray-500">{match.duration}m</p>
      </div>

      {/* KDA */}
      <div className="w-24 shrink-0">
        <p className="text-sm font-mono">
          {match.kills}/{match.deaths}/{match.assists}
        </p>
        <p className={`text-xs ${isGoodKda ? 'text-lol-gold' : 'text-gray-500'}`}>
          {kdaRatio} KDA
        </p>
      </div>

      {/* CS + role */}
      <div className="w-20 shrink-0 hidden sm:block">
        <p className="text-sm">{match.cs} CS</p>
        <p className="text-xs text-gray-500">
          {match.role ? match.role.charAt(0) + match.role.slice(1).toLowerCase() : '—'}
        </p>
      </div>

      {/* Items */}
      <div className="flex gap-1 ml-auto flex-wrap justify-end">
        {match.items
          .filter(id => id !== 0)
          .map((itemId, j) => (
            <img
              key={j}
              src={`https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/item/${itemId}.png`}
              alt={`Item ${itemId}`}
              className="w-7 h-7 rounded"
              onError={e => { e.target.style.display = 'none' }}
            />
          ))}
      </div>
    </div>
  )
}
