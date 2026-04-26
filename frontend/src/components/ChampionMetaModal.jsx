import { useEffect } from 'react'
import MetaTierBadge from './MetaTierBadge'

const DDR_BASE = 'https://ddragon.leagueoflegends.com/cdn/img/'

export default function ChampionMetaModal({ champion, ddVersion, runeTree, lane, onClose }) {
  useEffect(() => {
    const handler = e => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  const keystone = champion.keystone_id
    ? runeTree?.flatMap(path => path.slots?.[0]?.runes || []).find(r => r.id === champion.keystone_id)
    : null

  const primaryPath = keystone
    ? runeTree?.find(path => path.slots?.[0]?.runes?.some(r => r.id === champion.keystone_id))
    : null

  const stats = [
    {
      label: 'Win Rate',
      val: champion.win_rate,
      color: champion.win_rate >= 52 ? 'text-zar-green' : champion.win_rate < 48 ? 'text-zar-red' : 'text-white',
    },
    { label: 'Pick Rate', val: champion.pick_rate, color: 'text-white' },
    { label: 'Ban Rate',  val: champion.ban_rate,  color: 'text-white' },
  ]

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)' }}
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div
        className="bg-zar-bg2 border border-zar-border rounded-2xl w-full max-w-sm overflow-hidden"
        style={{ boxShadow: '0 25px 80px rgba(0,0,0,0.6)' }}
      >
        {/* Splash art header */}
        <div className="relative h-40 overflow-hidden">
          <img
            src={`https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${champion.name}_0.jpg`}
            alt={champion.name}
            className="w-full h-full object-cover object-top"
            onError={e => { e.target.style.background = '#161c2d' }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-zar-bg2 via-zar-bg2/20 to-transparent" />
          <button
            onClick={onClose}
            className="absolute top-2 right-2 bg-black/50 text-white rounded-full p-1 hover:bg-black/70 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <div className="absolute bottom-2.5 left-3 flex items-end gap-2">
            <div>
              <p className="text-lg font-black text-white leading-none">{champion.name}</p>
              <p className="text-[10px] text-zar-text-secondary uppercase tracking-widest">{lane}</p>
            </div>
            <MetaTierBadge tier={champion.tier} />
          </div>
        </div>

        <div className="p-4 space-y-4">
          {/* Stats row */}
          <div className="grid grid-cols-3 gap-2">
            {stats.map(({ label, val, color }) => (
              <div key={label} className="bg-zar-card rounded-xl p-2.5 text-center">
                <p className={`text-base font-black tabular-nums ${color}`}>
                  {val != null ? `${val}%` : '—'}
                </p>
                <p className="text-[9px] text-zar-text-tertiary uppercase tracking-widest mt-0.5">{label}</p>
              </div>
            ))}
          </div>

          {/* Core build */}
          {champion.best_items?.length > 0 && (
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-zar-text-secondary mb-2">Core Build</p>
              <div className="flex gap-1.5 flex-wrap">
                {champion.best_items.slice(0, 6).map((item, i) => (
                  <div key={i} className="relative group">
                    <img
                      src={`https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/item/${item.id}.png`}
                      alt=""
                      className="w-10 h-10 rounded-lg border border-zar-border"
                      onError={e => { e.target.style.display = 'none' }}
                    />
                    {item.wr > 0 && (
                      <span className="absolute -bottom-1 -right-1 bg-zar-card2 text-[8px] text-zar-green font-bold px-0.5 rounded border border-zar-border leading-tight hidden group-hover:block">
                        {item.wr}%
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Keystone */}
          {keystone && (
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-zar-text-secondary mb-2">Keystone</p>
              <div className="flex items-center gap-3 bg-zar-card rounded-xl p-3">
                <img
                  src={`${DDR_BASE}${keystone.icon}`}
                  alt={keystone.name}
                  className="w-10 h-10 rounded-full border border-zar-border shrink-0"
                  onError={e => { e.target.style.display = 'none' }}
                />
                <div>
                  <p className="text-sm font-semibold text-white">{keystone.name}</p>
                  {primaryPath && (
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <img
                        src={`${DDR_BASE}${primaryPath.icon}`}
                        alt={primaryPath.name}
                        className="w-3.5 h-3.5 rounded"
                        onError={e => { e.target.style.display = 'none' }}
                      />
                      <p className="text-[10px] text-zar-text-tertiary">{primaryPath.name}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* No data fallback */}
          {!champion.best_items?.length && !keystone && (
            <p className="text-xs text-zar-text-tertiary text-center py-2">
              Build and rune data will appear after the next cache refresh.
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
