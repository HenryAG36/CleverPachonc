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
        <div className="relative shrink-0" style={{ width: 160, height: 160 }}>
          <PieChart width={160} height={160} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
            <Pie
              data={ringData}
              cx={80}
              cy={80}
              innerRadius={52}
              outerRadius={72}
              startAngle={90}
              endAngle={-270}
              dataKey="value"
              strokeWidth={0}
            >
              <Cell fill="#2ECC71" />
              <Cell fill="#FF4757" />
            </Pie>
          </PieChart>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-2xl font-black text-white leading-none">{winPct}%</span>
            <span className="text-[10px] text-zar-text-secondary mt-1 uppercase tracking-widest font-bold">Win Rate</span>
          </div>
        </div>

        <div className="flex flex-col gap-3">
          <div>
            <span className="text-2xl font-black text-zar-green">{wins}</span>
            <span className="text-zar-text-secondary text-sm ml-1.5 font-semibold">Wins</span>
          </div>
          <div>
            <span className="text-2xl font-black text-zar-red">{losses}</span>
            <span className="text-zar-text-secondary text-sm ml-1.5 font-semibold">Losses</span>
          </div>
          <p className="text-[10px] text-zar-text-tertiary uppercase tracking-widest font-bold">
            Last {matches.length} Games
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-1 mt-4">
        {matches.map((match, i) => (
          <div
            key={`${match.champion}-${i}`}
            title={`${match.champion} — ${match.result} (${match.kills}/${match.deaths}/${match.assists})`}
            className={`w-5 h-5 rounded transition-opacity hover:opacity-70 ${
              match.win ? 'bg-zar-green' : 'bg-zar-red'
            }`}
          />
        ))}
      </div>
    </div>
  )
}
