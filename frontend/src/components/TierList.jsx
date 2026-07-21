import { useState, useEffect } from 'react'
import ChampionMetaModal from './ChampionMetaModal'
import MetaTierBadge from './MetaTierBadge'
import { championDisplayName } from '../utils/champions'
import { fetchJson } from '../utils/fetchJson'

const ROLES = [
  { lane: 'top',     label: 'TOP' },
  { lane: 'jungle',  label: 'JGL' },
  { lane: 'mid',     label: 'MID' },
  { lane: 'adc',     label: 'BOT' },
  { lane: 'support', label: 'SUP' },
]

export default function TierList() {
  const [lane, setLane]         = useState('adc')
  const [search, setSearch]     = useState('')
  const [data, setData]         = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    const controller = new AbortController()
    setSearch('')
    setError(null)
    setLoading(true)
    fetchJson(`/api/tierlist?role=${lane}`, { signal: controller.signal })
      .then(json => {
        if (json.error) throw new Error(json.error)
        setData(json)
        setLoading(false)
      })
      .catch(e => {
        if (e.name === 'AbortError') return // stale request — a newer one is in flight
        setError(e.message)
        setLoading(false)
      })
    return () => controller.abort()
  }, [lane])

  const champions = data?.champions || []
  const filtered = champions.filter(c =>
    championDisplayName(c.name).toLowerCase().includes(search.toLowerCase()) ||
    c.name.toLowerCase().includes(search.toLowerCase())
  )
  // Rank comes from the full (unfiltered) ordering so filtering keeps real ranks
  const ranks = new Map(champions.map((c, i) => [c.name, i + 1]))

  const hasTiers = champions.some(c => c.tier)
  const hasWr = champions.some(c => c.win_rate != null)
  const currentRole = ROLES.find(r => r.lane === lane)?.label ?? lane.toUpperCase()
  // Full literal class strings — Tailwind's scanner can't see interpolated names
  const gridCols =
    hasTiers && hasWr ? 'grid-cols-[1.5rem_1fr_3rem_3.5rem_4.5rem]'
    : hasTiers ? 'grid-cols-[1.5rem_1fr_3rem_4.5rem]'
    : hasWr ? 'grid-cols-[1.5rem_1fr_3.5rem_4.5rem]'
    : 'grid-cols-[1.5rem_1fr_4.5rem]'

  return (
    <div className="mt-6">
      {/* Controls row */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        {/* Role tabs */}
        <div className="flex gap-1 bg-zar-card border border-zar-border rounded-xl p-1" role="tablist" aria-label="Role">
          {ROLES.map(r => (
            <button
              key={r.lane}
              role="tab"
              aria-selected={lane === r.lane}
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
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zar-text-tertiary" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Filter champions…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            aria-label="Filter champions"
            className="bg-zar-card border border-zar-border rounded-xl pl-8 pr-3 py-1.5 text-sm text-white placeholder:text-zar-text-tertiary focus:outline-none focus:border-zar-pink/40 w-48"
          />
        </div>
      </div>

      {/* Patch + source label */}
      {data?.patch && !loading && (
        <p className="text-[10px] text-zar-text-tertiary mb-3 tabular-nums">
          Patch {data.patch} · {currentRole} ·
          {hasTiers || hasWr ? ' Sorted by tier & win rate' : ' Sorted by pick rate'} · Data: Meraki Analytics
        </p>
      )}

      {/* Column headers */}
      {!loading && !error && data && (
        <div className={`grid ${gridCols} gap-x-3 px-3 mb-1.5`}>
          <span className="text-[10px] font-bold uppercase tracking-widest text-zar-text-tertiary">#</span>
          <span className="text-[10px] font-bold uppercase tracking-widest text-zar-text-tertiary">Champion</span>
          {hasTiers && <span className="text-[10px] font-bold uppercase tracking-widest text-zar-text-tertiary text-right">Tier</span>}
          {hasWr && <span className="text-[10px] font-bold uppercase tracking-widest text-zar-text-tertiary text-right">Win %</span>}
          <span className="text-[10px] font-bold uppercase tracking-widest text-zar-text-tertiary text-right">Pick %</span>
        </div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="card p-0 overflow-hidden divide-y divide-zar-border" role="status" aria-label={`Loading ${currentRole} pick rates`}>
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="flex items-center gap-3 px-3 py-2">
              <div className="skeleton w-5 h-3.5" />
              <div className="skeleton w-7 h-7 rounded" />
              <div className="skeleton h-3.5 flex-1 max-w-40" />
              <div className="skeleton w-10 h-3.5 ml-auto" />
            </div>
          ))}
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="bg-zar-red/10 border border-zar-red/25 text-zar-red rounded-xl p-4 text-sm text-center" role="alert">
          {error}
        </div>
      )}

      {/* Champion list */}
      {data && !loading && !error && (
        <>
          <div className="card p-0 overflow-hidden divide-y divide-zar-border">
            {filtered.map(champ => (
              <button
                key={champ.name}
                onClick={() => setSelected(champ)}
                className={`w-full grid ${gridCols} gap-x-3 px-3 py-2 items-center hover:bg-zar-card3 transition-colors text-left`}
              >
                <span className="text-[11px] text-zar-text-tertiary tabular-nums">{ranks.get(champ.name)}</span>
                <div className="flex items-center gap-2 min-w-0">
                  <img
                    src={`https://ddragon.leagueoflegends.com/cdn/${data.dd_version}/img/champion/${champ.name}.png`}
                    alt=""
                    className="w-7 h-7 rounded shrink-0"
                    onError={e => { e.target.style.display = 'none' }}
                  />
                  <span className="text-sm text-white font-medium truncate">{championDisplayName(champ.name)}</span>
                </div>
                {hasTiers && (
                  <span className="text-right">
                    {champ.tier ? <MetaTierBadge tier={champ.tier} size="xs" /> : <span className="text-zar-text-tertiary text-xs">—</span>}
                  </span>
                )}
                {hasWr && (
                  <span className={`text-xs font-bold tabular-nums text-right ${
                    champ.win_rate == null ? 'text-zar-text-tertiary'
                      : champ.win_rate >= 50 ? 'text-zar-green' : 'text-zar-red'
                  }`}>
                    {champ.win_rate != null ? `${champ.win_rate}%` : '—'}
                  </span>
                )}
                <span className="text-xs text-zar-cyan font-bold tabular-nums text-right">
                  {champ.pick_rate != null ? `${champ.pick_rate}%` : '—'}
                </span>
              </button>
            ))}

            {filtered.length === 0 && !search && (
              <p className="text-center text-zar-text-tertiary text-sm py-8">
                No {currentRole} champions found.
              </p>
            )}

            {filtered.length === 0 && search && (
              <p className="text-center text-zar-text-tertiary text-sm py-8">
                No champions match &quot;{search}&quot;
              </p>
            )}
          </div>

          {filtered.length > 0 && (
            <p className="text-[10px] text-zar-text-tertiary text-center mt-3">
              {filtered.length} champions · Click any row for details
            </p>
          )}
        </>
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
