import { useState, useEffect } from 'react'
import MetaTierBadge from './MetaTierBadge'
import ChampionMetaModal from './ChampionMetaModal'

const ROLES = [
  { lane: 'top',     label: 'TOP' },
  { lane: 'jungle',  label: 'JGL' },
  { lane: 'mid',     label: 'MID' },
  { lane: 'adc',     label: 'BOT' },
  { lane: 'support', label: 'SUP' },
]

const TIERS = ['OP', 'S', 'A', 'B', 'C']

const TIER_LABEL_COLORS = {
  OP: 'text-zar-yellow',
  S:  'text-zar-pink',
  A:  'text-zar-green',
  B:  'text-zar-cyan',
  C:  'text-zar-text-tertiary',
}

export default function TierList() {
  const [lane, setLane]       = useState('adc')
  const [search, setSearch]   = useState('')
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    setSearch('')
    setError(null)
    setLoading(true)
    fetch(`/api/tierlist?role=${lane}`)
      .then(r => r.json())
      .then(json => {
        if (json.error) throw new Error(json.error)
        setData(json)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [lane])

  const filtered = (data?.champions || []).filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase())
  )

  // Group into tier buckets preserving sorted order
  const grouped = Object.fromEntries(TIERS.map(t => [t, []]))
  for (const c of filtered) {
    (grouped[c.tier] ?? grouped['C']).push(c)
  }

  const currentRole = ROLES.find(r => r.lane === lane)?.label ?? lane.toUpperCase()

  return (
    <div className="mt-6">
      {/* Controls row */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        {/* Role tabs */}
        <div className="flex gap-1 bg-zar-card border border-zar-border rounded-xl p-1">
          {ROLES.map(r => (
            <button
              key={r.lane}
              onClick={() => setLane(r.lane)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-widest transition-all ${
                lane === r.lane
                  ? 'bg-zar-pink text-white shadow-sm'
                  : 'text-zar-text-secondary hover:text-white'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative ml-auto">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zar-text-tertiary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Filter champions…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="bg-zar-card border border-zar-border rounded-xl pl-8 pr-3 py-1.5 text-sm text-white placeholder:text-zar-text-tertiary focus:outline-none focus:border-zar-pink/40 w-48"
          />
        </div>
      </div>

      {/* Patch label */}
      {data?.patch && (
        <p className="text-[10px] text-zar-text-tertiary mb-3 tabular-nums">
          Patch {data.patch} · Gold+ Solo Queue · Updated daily
        </p>
      )}

      {/* Column headers */}
      {!loading && !error && data && (
        <div className="grid grid-cols-[1.5rem_1fr_auto_5rem_5rem_5rem] gap-x-3 px-3 mb-1.5">
          <span className="text-[10px] font-bold uppercase tracking-widest text-zar-text-tertiary">#</span>
          <span className="text-[10px] font-bold uppercase tracking-widest text-zar-text-tertiary">Champion</span>
          <span className="text-[10px] font-bold uppercase tracking-widest text-zar-text-tertiary">Tier</span>
          <span className="text-[10px] font-bold uppercase tracking-widest text-zar-text-tertiary text-right">WR</span>
          <span className="text-[10px] font-bold uppercase tracking-widest text-zar-text-tertiary text-right">Pick</span>
          <span className="text-[10px] font-bold uppercase tracking-widest text-zar-text-tertiary text-right">Ban</span>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-20 gap-2">
          <div className="w-5 h-5 border-2 border-zar-pink border-t-transparent rounded-full animate-spin" />
          <span className="text-zar-text-secondary text-sm">Loading {currentRole} tier list…</span>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="bg-zar-red/10 border border-zar-red/25 text-zar-red rounded-xl p-4 text-sm text-center">
          {error}
        </div>
      )}

      {/* Tier sections */}
      {data && !loading && (
        <div className="space-y-5">
          {TIERS.map(tier => {
            const champs = grouped[tier]
            if (!champs.length) return null
            return (
              <div key={tier}>
                <p className={`text-[10px] font-black uppercase tracking-widest mb-1.5 ${TIER_LABEL_COLORS[tier]}`}>
                  {tier} Tier · {champs.length} champions
                </p>
                <div className="card p-0 overflow-hidden divide-y divide-zar-border">
                  {champs.map((champ, idx) => (
                    <button
                      key={champ.name}
                      onClick={() => setSelected(champ)}
                      className="w-full grid grid-cols-[1.5rem_1fr_auto_5rem_5rem_5rem] gap-x-3 px-3 py-2 items-center hover:bg-zar-card3 transition-colors text-left"
                    >
                      <span className="text-[11px] text-zar-text-tertiary tabular-nums">{idx + 1}</span>
                      <div className="flex items-center gap-2 min-w-0">
                        <img
                          src={`https://ddragon.leagueoflegends.com/cdn/${data.dd_version}/img/champion/${champ.name}.png`}
                          alt={champ.name}
                          className="w-7 h-7 rounded shrink-0"
                          onError={e => { e.target.style.display = 'none' }}
                        />
                        <span className="text-sm text-white font-medium truncate">{champ.name}</span>
                      </div>
                      <MetaTierBadge tier={champ.tier} />
                      <span className={`text-xs font-bold tabular-nums text-right ${
                        (champ.win_rate ?? 50) >= 52 ? 'text-zar-green' :
                        (champ.win_rate ?? 50) < 48  ? 'text-zar-red'   : 'text-white'
                      }`}>
                        {champ.win_rate != null ? `${champ.win_rate}%` : '—'}
                      </span>
                      <span className="text-xs text-zar-text-secondary tabular-nums text-right">
                        {champ.pick_rate != null ? `${champ.pick_rate}%` : '—'}
                      </span>
                      <span className="text-xs text-zar-text-secondary tabular-nums text-right">
                        {champ.ban_rate != null ? `${champ.ban_rate}%` : '—'}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )
          })}

          {filtered.length === 0 && search && (
            <p className="text-center text-zar-text-tertiary text-sm py-8">
              No champions match "{search}"
            </p>
          )}
        </div>
      )}

      {/* Champion detail modal */}
      {selected && (
        <ChampionMetaModal
          champion={selected}
          ddVersion={data?.dd_version}
          runeTree={data?.rune_tree}
          lane={currentRole}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  )
}
