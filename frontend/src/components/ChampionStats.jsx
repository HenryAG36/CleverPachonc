import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts'
import MetaTierBadge from './MetaTierBadge'
import { championDisplayName } from '../utils/champions'

const WIN_FILL = '#4ADE80'
const LOSS_FILL = '#E5384C'

export default function ChampionStats({ stats, ddVersion, meta }) {
  const [sortKey, setSortKey] = useState('games')
  const [sortDir, setSortDir] = useState('desc')

  const rows = Object.entries(stats)
    .map(([name, s]) => ({ name, ...s }))
    .filter(r => r.games >= 2)
    .sort((a, b) => (sortDir === 'desc' ? b[sortKey] - a[sortKey] : a[sortKey] - b[sortKey]))
    .slice(0, 10)

  if (!rows.length) {
    return (
      <div className="card text-zar-text-secondary text-sm text-center py-10">
        Play at least 2 recent games on a champion to see per-champion stats.
      </div>
    )
  }

  function handleSort(key) {
    if (key === sortKey) {
      setSortDir(d => (d === 'desc' ? 'asc' : 'desc'))
    } else {
      setSortKey(key)
      setSortDir('desc')
    }
  }

  const chartData = rows.map(r => ({
    name: championDisplayName(r.name),
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
        <p className="section-title">Win Rate by Champion (≥2 games)</p>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
            <XAxis
              dataKey="name"
              tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 10 }}
              interval={0}
              tickFormatter={n => (n.length > 9 ? `${n.slice(0, 8)}…` : n)}
            />
            <YAxis domain={[0, 100]} tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 10 }} />
            <Tooltip
              cursor={{ fill: 'rgba(255,255,255,0.04)' }}
              contentStyle={{ background: '#1e2745', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 8, boxShadow: '0 8px 32px rgba(0,0,0,0.5)' }}
              labelStyle={{ color: '#ffffff', fontWeight: 700, fontSize: 13 }}
              itemStyle={{ color: 'rgba(255,255,255,0.7)', fontSize: 12 }}
              formatter={v => [`${v}%`, 'Win rate']}
            />
            <ReferenceLine y={50} stroke="rgba(255,255,255,0.1)" strokeDasharray="4 4" />
            <Bar dataKey="winrate" radius={[4, 4, 0, 0]} isAnimationActive={false}>
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={entry.winrate >= 50 ? WIN_FILL : LOSS_FILL} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <p className="text-[10px] text-zar-text-tertiary mt-2 uppercase tracking-widest font-semibold">
          Dashed line = 50% · green ≥ 50%, red &lt; 50%
        </p>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b border-zar-border">
              <th className="pb-3 pr-3 text-[10px] font-bold uppercase tracking-widest text-zar-text-tertiary">Champion</th>
              {cols.map(c => (
                <th
                  key={c.key}
                  className="pb-3 px-2 text-right"
                  aria-sort={sortKey === c.key ? (sortDir === 'desc' ? 'descending' : 'ascending') : undefined}
                >
                  <button
                    onClick={() => handleSort(c.key)}
                    className={`text-[10px] font-bold uppercase tracking-widest transition-colors ${
                      sortKey === c.key
                        ? 'text-zar-cyan'
                        : 'text-zar-text-tertiary hover:text-white'
                    }`}
                  >
                    {c.label}{sortKey === c.key ? (sortDir === 'desc' ? ' ↓' : ' ↑') : ''}
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => {
              const iconUrl = `https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/champion/${r.name}.png`
              const champMeta = meta?.per_champ_meta?.[r.name]
              return (
                <tr key={r.name} className="border-b border-zar-border hover:bg-white/5 transition-colors">
                  <td className="py-2.5 pr-3">
                    <div className="flex items-center gap-2">
                      <img src={iconUrl} alt="" className="w-7 h-7 rounded"
                        onError={e => { e.target.style.display = 'none' }} />
                      <span className="font-semibold whitespace-nowrap">{championDisplayName(r.name)}</span>
                      {champMeta && (
                        <MetaTierBadge tier={champMeta.tier} wr={champMeta.meta_wr} size="xs" />
                      )}
                    </div>
                  </td>
                  <td className="px-2 text-right text-zar-text-secondary">{r.games}</td>
                  <td className={`px-2 text-right font-bold ${r.winrate >= 50 ? 'text-zar-green' : 'text-zar-red'}`}>
                    {r.winrate.toFixed(1)}%
                  </td>
                  <td className={`px-2 text-right font-semibold ${r.kda >= 3 ? 'text-zar-yellow' : 'text-white'}`}>
                    {r.kda.toFixed(2)}
                  </td>
                  <td className="px-2 text-right text-zar-text-secondary">{r.avg_kills.toFixed(1)}</td>
                  <td className="px-2 text-right text-zar-text-secondary">{r.avg_deaths.toFixed(1)}</td>
                  <td className="px-2 text-right text-zar-text-secondary">{r.avg_assists.toFixed(1)}</td>
                  <td className="px-2 text-right text-zar-text-secondary">{r.cs_per_min.toFixed(1)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
        <p className="text-[10px] mt-3 text-zar-text-tertiary uppercase tracking-widest font-semibold">
          Click a column header to sort · click again to flip direction
        </p>
      </div>
    </div>
  )
}
