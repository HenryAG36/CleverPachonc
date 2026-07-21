import { useState } from 'react'

const REGIONS = ['NA', 'EUW', 'EUNE', 'KR', 'BR', 'LAN', 'LAS', 'OCE', 'TR', 'RU', 'JP']
const REGION_KEY = 'cleverpachonc_region'
const RECENT_KEY = 'cleverpachonc_recent'
const MAX_RECENT = 5

function loadRecent() {
  try {
    const saved = JSON.parse(localStorage.getItem(RECENT_KEY) || '[]')
    return Array.isArray(saved)
      ? saved.filter(r => r && typeof r.name === 'string' && REGIONS.includes(r.region))
      : []
  } catch {
    return []
  }
}

export default function SearchBar({ onSearch, disabled, compact }) {
  const [name, setName] = useState('')
  const [region, setRegion] = useState(() => {
    try {
      const saved = localStorage.getItem(REGION_KEY)
      return REGIONS.includes(saved) ? saved : 'NA'
    } catch {
      return 'NA' // storage blocked (sandboxed iframe / cookies disabled)
    }
  })
  const [recent, setRecent] = useState(loadRecent)

  function saveRecent(searchName, searchRegion) {
    const entry = { name: searchName, region: searchRegion }
    const next = [
      entry,
      ...recent.filter(r => !(r.name.toLowerCase() === searchName.toLowerCase() && r.region === searchRegion)),
    ].slice(0, MAX_RECENT)
    setRecent(next)
    try {
      localStorage.setItem(RECENT_KEY, JSON.stringify(next))
    } catch {
      // storage full / private mode — recents just won't persist
    }
  }

  function submitSearch(searchName, searchRegion) {
    saveRecent(searchName, searchRegion)
    onSearch(searchName, searchRegion)
  }

  function handleSubmit(e) {
    e.preventDefault()
    const trimmed = name.trim()
    if (trimmed) submitSearch(trimmed, region)
  }

  function clearRecent() {
    setRecent([])
    try {
      localStorage.removeItem(RECENT_KEY)
    } catch {
      // ignore
    }
  }

  return (
    <div className={compact ? 'max-w-xl mx-auto' : 'max-w-lg mx-auto'}>
      <form
        onSubmit={handleSubmit}
        className="flex items-center bg-zar-card border border-zar-border rounded-xl overflow-hidden transition-all focus-within:border-zar-pink/50 focus-within:shadow-[0_0_20px_rgba(255,45,107,0.12)]"
      >
        <select
          value={region}
          onChange={e => {
            setRegion(e.target.value)
            try { localStorage.setItem(REGION_KEY, e.target.value) } catch { /* storage blocked */ }
          }}
          disabled={disabled}
          aria-label="Region"
          className="bg-transparent text-zar-cyan text-xs font-bold focus:outline-none disabled:opacity-50 px-3 py-3 cursor-pointer uppercase tracking-wider shrink-0"
        >
          {REGIONS.map(r => <option key={r} value={r} className="bg-zar-card text-white">{r}</option>)}
        </select>
        <div className="w-px h-5 bg-zar-border shrink-0" />
        <input
          type="text"
          placeholder="Summoner#TAG"
          value={name}
          onChange={e => setName(e.target.value)}
          disabled={disabled}
          aria-label="Riot ID"
          className="flex-1 min-w-0 bg-transparent text-white placeholder:text-zar-text-tertiary text-sm focus:outline-none disabled:opacity-50 px-3 py-3"
        />
        <button
          type="submit"
          disabled={disabled || !name.trim()}
          className="bg-zar-pink hover:bg-zar-pink-light text-white font-bold px-5 py-3 text-sm tracking-wide transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed shrink-0 flex items-center gap-1.5"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5} aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          Search
        </button>
      </form>

      {recent.length > 0 && !disabled && (
        <div className="flex items-center flex-wrap gap-1.5 mt-3 justify-center">
          <span className="text-[10px] text-zar-text-tertiary uppercase tracking-widest font-bold mr-1">Recent</span>
          {recent.map(r => (
            <button
              key={`${r.name}-${r.region}`}
              onClick={() => { setName(r.name); setRegion(r.region); submitSearch(r.name, r.region) }}
              className="text-xs bg-zar-card border border-zar-border hover:border-zar-cyan/40 hover:text-zar-cyan text-zar-text-secondary px-2.5 py-1 rounded-full transition-colors"
            >
              {r.name} <span className="text-zar-text-tertiary">· {r.region}</span>
            </button>
          ))}
          <button
            onClick={clearRecent}
            aria-label="Clear recent searches"
            className="text-[10px] text-zar-text-tertiary hover:text-zar-red px-1.5 py-1 transition-colors uppercase tracking-wider font-bold"
          >
            Clear
          </button>
        </div>
      )}
    </div>
  )
}
