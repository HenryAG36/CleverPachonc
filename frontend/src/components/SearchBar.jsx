import { useState } from 'react'

const REGIONS = ['NA', 'EUW', 'EUNE', 'KR', 'BR', 'LAN', 'LAS', 'OCE', 'TR', 'RU', 'JP']

export default function SearchBar({ onSearch, disabled }) {
  const [name, setName] = useState('')
  const [region, setRegion] = useState('NA')

  function handleSubmit(e) {
    e.preventDefault()
    const trimmed = name.trim()
    if (trimmed) onSearch(trimmed, region)
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 max-w-xl mx-auto">
      <select
        value={region}
        onChange={e => setRegion(e.target.value)}
        disabled={disabled}
        className="bg-lol-card border border-lol-border rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-lol-gold disabled:opacity-50"
      >
        {REGIONS.map(r => <option key={r}>{r}</option>)}
      </select>

      <input
        type="text"
        placeholder="Name#TAG"
        value={name}
        onChange={e => setName(e.target.value)}
        disabled={disabled}
        className="flex-1 bg-lol-card border border-lol-border rounded-lg px-4 py-2 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-lol-gold disabled:opacity-50"
      />

      <button
        type="submit"
        disabled={disabled || !name.trim()}
        className="bg-lol-gold hover:bg-lol-gold-dark text-black font-semibold px-5 py-2 rounded-lg text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Search
      </button>
    </form>
  )
}
