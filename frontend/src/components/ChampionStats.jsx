import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts'

export default function ChampionStats({ stats, ddVersion }) {
  const [sortKey, setSortKey] = useState('games')

  const rows = Object.entries(stats)
    .map(([name, s]) => ({ name, ...s }))
    .filter(r => r.games >= 2)
    .sort((a, b) => b[sortKey] - a[sortKey])
    .slice(0, 10)

  if (!rows.length) return null

  const chartData = rows.map(r => ({
    name: r.name,
    winrate: parseFloat(r.winrate.toFixed(1)),
  }))

  const cols = [
    { key: 'games', label: 'Games' },
    { key: 'winrate', label: 'Win%' },
    { key: 'kda', label: 'KDA' },
    { key: 'avg_kills', label: 'K' },
    { key: 'avg_deaths', label: 'D' },
    { key: 'avg_assists', label: 'A' },
    { key: 'cs_per_min', label: 'CS/m' },
  ]

  return (
    <div className="space-y-5">
      <div className="card">
        <p className="section-title">Win rate by champion (≥2 games)</p>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
            <XAxis dataKey="name" tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 11 }} />
            <YAxis domain={[0, 100]} tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#2c2c2e', border: 'none', borderRadius: 12, boxShadow: '0 4px 20px rgba(0,0,0,0.4)' }}
              labelStyle={{ color: '#ffffff', fontWeight: 600 }}
              itemStyle={{ color: 'rgba(255,255,255,0.7)' }}
              formatter={v => [`${v}%`, 'Win rate']}
            />
            <ReferenceLine y={50} stroke="rgba(255,255,255,0.15)" strokeDasharray="4 4" />
            <Bar dataKey="winrate" radius={[6, 6, 0, 0]}>
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={entry.winrate >= 50 ? '#30D158' : '#FF453A'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wider border-b border-apple-separator" style={{ color: 'rgba(255,255,255,0.4)' }}>
              <th className="pb-2 pr-3">Champion</th>
              {cols.map(c => (
                <th
                  key={c.key}
                  className={`pb-2 px-2 text-right cursor-pointer transition-colors ${
                    sortKey === c.key ? 'text-apple-blue' : 'hover:text-white'
                  }`}
                  onClick={() => setSortKey(c.key)}
                >
                  {c.label} {sortKey === c.key ? '↓' : ''}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => {
              const iconUrl = `https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/champion/${r.name}.png`
              return (
                <tr key={r.name} className="border-b border-apple-separator hover:bg-white/5 transition-colors">
                  <td className="py-2 pr-3">
                    <div className="flex items-center gap-2">
                      <img src={iconUrl} alt={r.name} className="w-7 h-7 rounded"
                        onError={e => { e.target.style.display = 'none' }} />
                      <span className="font-medium">{r.name}</span>
                    </div>
                  </td>
                  <td className="px-2 text-right">{r.games}</td>
                  <td className={`px-2 text-right font-semibold ${r.winrate >= 50 ? 'text-apple-green' : 'text-apple-red'}`}>
                    {r.winrate.toFixed(1)}%
                  </td>
                  <td className={`px-2 text-right ${r.kda >= 3 ? 'text-apple-yellow' : ''}`}>
                    {r.kda.toFixed(2)}
                  </td>
                  <td className="px-2 text-right text-apple-text-secondary">{r.avg_kills.toFixed(1)}</td>
                  <td className="px-2 text-right text-apple-text-secondary">{r.avg_deaths.toFixed(1)}</td>
                  <td className="px-2 text-right text-apple-text-secondary">{r.avg_assists.toFixed(1)}</td>
                  <td className="px-2 text-right text-apple-text-secondary">{r.cs_per_min.toFixed(1)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
        <p className="text-xs mt-3" style={{ color: 'rgba(255,255,255,0.3)' }}>Click a column header to sort</p>
      </div>
    </div>
  )
}
