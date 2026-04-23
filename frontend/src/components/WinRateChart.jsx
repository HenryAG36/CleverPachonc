import { PieChart, Pie, Cell } from 'recharts'

export default function WinRateChart({ matches }) {
  if (!matches?.length) return null

  const wins = matches.filter(m => m.win).length
  const losses = matches.length - wins
  const winPct = ((wins / matches.length) * 100).toFixed(1)

  const ringData = [
    { value: wins },
    { value: losses },
  ]

  return (
    <div className="card mt-4">
      <div className="flex items-center gap-6">
        <div className="relative shrink-0" style={{ width: 180, height: 180 }}>
          <PieChart width={180} height={180} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
            <Pie
              data={ringData}
              cx={90}
              cy={90}
              innerRadius={60}
              outerRadius={80}
              startAngle={90}
              endAngle={-270}
              dataKey="value"
              strokeWidth={0}
            >
              <Cell fill="#30D158" />
              <Cell fill="#FF453A" />
            </Pie>
          </PieChart>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-3xl font-bold text-white leading-none">{winPct}%</span>
            <span className="text-xs text-apple-text-secondary mt-1">Win Rate</span>
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <div>
            <span className="text-2xl font-bold text-apple-green">{wins}</span>
            <span className="text-apple-text-secondary text-sm ml-1">Wins</span>
          </div>
          <div>
            <span className="text-2xl font-bold text-apple-red">{losses}</span>
            <span className="text-apple-text-secondary text-sm ml-1">Losses</span>
          </div>
          <span className="section-title mb-0 mt-1">Recent {matches.length} Games</span>
        </div>
      </div>

      <div className="flex flex-wrap gap-1 mt-4">
        {matches.map((match, i) => (
          <div
            key={`${match.champion}-${i}`}
            title={`${match.champion} — ${match.result} (${match.kills}/${match.deaths}/${match.assists})`}
            className={`w-6 h-6 rounded-md transition-opacity hover:opacity-70 ${
              match.win ? 'bg-apple-green' : 'bg-apple-red'
            }`}
          />
        ))}
      </div>
    </div>
  )
}
