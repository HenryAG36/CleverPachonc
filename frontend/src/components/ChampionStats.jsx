import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

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
      {/* Bar chart */}
      <div className="card">
        <p className="text-xs text-gray-400 mb-3 uppercase tracking-wider">Win rate by champion (≥2 games)</p>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
            <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} />
            <YAxis domain={[0, 100]} tick={{ fill: '#9ca3af', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#1a2035', border: '1px solid #2d3748', borderRadius: 8 }}
              labelStyle={{ color: '#c89b3c' }}
              formatter={v => [`${v}%`, 'Win rate']}
            />
            <Bar dataKey="winrate" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, i) => (
                <Cell key={i} fill={entry.winrate >= 50 ? '#3b82f6' : '#ef4444'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Table */}
      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 text-xs uppercase tracking-wider border-b border-lol-border">
              <th className="pb-2 pr-3">Champion</th>
              {cols.map(c => (
                <th
                  key={c.key}
                  className={`pb-2 px-2 text-right cursor-pointer hover:text-lol-gold transition-colors ${
                    sortKey === c.key ? 'text-lol-gold' : ''
                  }`}
                  onClick={() => setSortKey(c.key)}
                >
                  {c.label} {sortKey === c.key ? '↓' : ''}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => {
              const iconUrl = `https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/champion/${r.name}.png`
              return (
                <tr key={i} className="border-b border-lol-border/50 hover:bg-white/5 transition-colors">
                  <td className="py-2 pr-3">
                    <div className="flex items-center gap-2">
                      <img src={iconUrl} alt={r.name} className="w-7 h-7 rounded"
                        onError={e => { e.target.style.display = 'none' }} />
                      <span className="font-medium">{r.name}</span>
                    </div>
                  </td>
                  <td className="px-2 text-right">{r.games}</td>
                  <td className={`px-2 text-right font-semibold ${r.winrate >= 50 ? 'text-blue-400' : 'text-red-400'}`}>
                    {r.winrate.toFixed(1)}%
                  </td>
                  <td className={`px-2 text-right ${r.kda >= 3 ? 'text-lol-gold' : ''}`}>
                    {r.kda.toFixed(2)}
                  </td>
                  <td className="px-2 text-right text-gray-300">{r.avg_kills.toFixed(1)}</td>
                  <td className="px-2 text-right text-gray-300">{r.avg_deaths.toFixed(1)}</td>
                  <td className="px-2 text-right text-gray-300">{r.avg_assists.toFixed(1)}</td>
                  <td className="px-2 text-right text-gray-300">{r.cs_per_min.toFixed(1)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
        <p className="text-xs text-gray-500 mt-3">Click a column header to sort</p>
      </div>
    </div>
  )
}
