export default function WinRateChart({ matches }) {
  if (!matches?.length) return null

  const wins = matches.filter(m => m.win).length
  const losses = matches.length - wins
  const winPct = ((wins / matches.length) * 100).toFixed(1)

  return (
    <div className="card mt-4">
      <div className="flex items-center justify-between mb-3">
        <span className="section-title mb-0">Recent {matches.length} Games</span>
        <span className="text-sm text-gray-400">
          <span className="text-blue-400 font-semibold">{wins}W</span>
          {' '}<span className="text-red-400 font-semibold">{losses}L</span>
          {' '}<span className="text-lol-gold">{winPct}%</span>
        </span>
      </div>

      {/* Win/loss squares — newest game on the left */}
      <div className="flex flex-wrap gap-1">
        {matches.map((match, i) => (
          <div
            key={i}
            title={`${match.champion} — ${match.result} (${match.kills}/${match.deaths}/${match.assists})`}
            className={`w-5 h-5 rounded-sm transition-opacity hover:opacity-80 ${
              match.win ? 'bg-blue-500' : 'bg-red-500'
            }`}
          />
        ))}
      </div>

      {/* Win rate bar */}
      <div className="mt-3 h-1.5 bg-lol-border rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-500 rounded-full transition-all"
          style={{ width: `${winPct}%` }}
        />
      </div>
    </div>
  )
}
