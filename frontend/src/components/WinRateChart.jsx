import { PieChart, Pie, Cell } from 'recharts'
import { championDisplayName } from '../utils/champions'

const WIN_FILL = '#4ADE80'
const LOSS_FILL = '#E5384C'

export default function WinRateChart({ matches }) {
  if (!matches?.length) return null

  const wins = matches.filter(m => m.win).length
  const losses = matches.length - wins
  const winPct = ((wins / matches.length) * 100).toFixed(1)

  const totals = matches.reduce(
    (acc, m) => ({
      kills: acc.kills + m.kills,
      deaths: acc.deaths + m.deaths,
      assists: acc.assists + m.assists,
      cs: acc.cs + m.cs,
      minutes: acc.minutes + (m.duration || 0),
    }),
    { kills: 0, deaths: 0, assists: 0, cs: 0, minutes: 0 }
  )
  const kdaRatio = ((totals.kills + totals.assists) / Math.max(totals.deaths, 1)).toFixed(2)
  const csPerMin = totals.minutes > 0 ? (totals.cs / totals.minutes).toFixed(1) : null

  const ringData = [{ value: wins }, { value: losses }]

  return (
    <div className="card mt-4">
      <div className="flex items-center gap-6 flex-wrap">
        <div
          className="relative shrink-0"
          style={{ width: 160, height: 160 }}
          role="img"
          aria-label={`Win rate ${winPct}% — ${wins} wins, ${losses} losses in the last ${matches.length} ranked games`}
        >
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
              stroke="#161c2d"
              strokeWidth={2}
              isAnimationActive={false}
            >
              <Cell fill={WIN_FILL} />
              <Cell fill={LOSS_FILL} />
            </Pie>
          </PieChart>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-2xl font-black text-white leading-none">{winPct}%</span>
            <span className="text-[10px] text-zar-text-secondary mt-1 uppercase tracking-widest font-bold">Win Rate</span>
          </div>
        </div>

        <div className="flex-1 min-w-[220px]">
          <div className="grid grid-cols-2 gap-3">
            <div className="card-sm py-3">
              <p className="text-xl font-black leading-none">
                <span className="text-zar-green">{wins}W</span>
                <span className="text-zar-text-tertiary mx-1">/</span>
                <span className="text-zar-red">{losses}L</span>
              </p>
              <p className="text-[10px] text-zar-text-tertiary mt-1.5 uppercase tracking-widest font-bold">Record</p>
            </div>
            <div className="card-sm py-3">
              <p className={`text-xl font-black leading-none ${parseFloat(kdaRatio) >= 3 ? 'text-zar-yellow' : 'text-white'}`}>
                {kdaRatio}
              </p>
              <p className="text-[10px] text-zar-text-tertiary mt-1.5 uppercase tracking-widest font-bold">Avg KDA</p>
            </div>
            <div className="card-sm py-3">
              <p className="text-xl font-black leading-none text-white">{csPerMin ?? '—'}</p>
              <p className="text-[10px] text-zar-text-tertiary mt-1.5 uppercase tracking-widest font-bold">CS / Min</p>
            </div>
            <div className="card-sm py-3">
              <p className="text-xl font-black leading-none text-white">{matches.length}</p>
              <p className="text-[10px] text-zar-text-tertiary mt-1.5 uppercase tracking-widest font-bold">Ranked Games</p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-1 mt-4" aria-label="Result of each game, most recent first">
        {matches.map((match, i) => (
          <div
            key={`${match.matchId || match.champion}-${i}`}
            title={`${championDisplayName(match.champion)} — ${match.result} (${match.kills}/${match.deaths}/${match.assists})`}
            className="w-5 h-5 rounded transition-opacity hover:opacity-70"
            style={{ background: match.win ? WIN_FILL : LOSS_FILL }}
          />
        ))}
      </div>
      <p className="text-[10px] text-zar-text-tertiary mt-2 uppercase tracking-widest font-bold">
        Last {matches.length} games · newest first · green = win, red = loss
      </p>
    </div>
  )
}
