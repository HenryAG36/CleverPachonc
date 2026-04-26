import { useState } from 'react'

const REGIONS = ['NA', 'EUW', 'EUNE', 'KR', 'BR', 'LAN', 'LAS', 'OCE', 'TR', 'RU', 'JP']

export default function SearchBar({ onSearch, disabled, compact }) {
  const [name, setName] = useState('')
  const [region, setRegion] = useState(() => {
    const saved = localStorage.getItem('cleverpachonc_region')
    return REGIONS.includes(saved) ? saved : 'NA'
  })

  function handleSubmit(e) {
    e.preventDefault()
    const trimmed = name.trim()
    if (trimmed) onSearch(trimmed, region)
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={`flex items-center bg-zar-card border border-zar-border rounded-xl overflow-hidden ${compact ? 'max-w-xl mx-auto' : 'max-w-lg mx-auto'}`}
    >
      <select
        value={region}
        onChange={e => { setRegion(e.target.value); localStorage.setItem('cleverpachonc_region', e.target.value) }}
        disabled={disabled}
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
        className="flex-1 bg-transparent text-white placeholder:text-zar-text-tertiary text-sm focus:outline-none disabled:opacity-50 px-3 py-3"
      />
      <button
        type="submit"
        disabled={disabled || !name.trim()}
        className="bg-zar-pink hover:bg-zar-pink-light text-white font-bold px-5 py-3 text-sm tracking-wide transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
      >
        Search
      </button>
    </form>
  )
}
