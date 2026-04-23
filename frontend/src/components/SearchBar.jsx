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
    <form onSubmit={handleSubmit} className="bg-apple-card rounded-2xl flex items-center p-1.5 gap-2 max-w-xl mx-auto">
      <select
        value={region}
        onChange={e => setRegion(e.target.value)}
        disabled={disabled}
        className="bg-transparent text-white text-sm focus:outline-none disabled:opacity-50 px-2 py-2 cursor-pointer"
      >
        {REGIONS.map(r => <option key={r} className="bg-apple-card">{r}</option>)}
      </select>
      <div className="w-px h-5 bg-apple-separator flex-shrink-0" />
      <input
        type="text"
        placeholder="Name#TAG"
        value={name}
        onChange={e => setName(e.target.value)}
        disabled={disabled}
        className="flex-1 bg-transparent text-white placeholder:text-apple-text-tertiary text-sm focus:outline-none disabled:opacity-50 px-2 py-2"
      />
      <button
        type="submit"
        disabled={disabled || !name.trim()}
        className="bg-apple-blue text-white font-semibold rounded-xl px-5 py-2 text-sm transition-all duration-200 ease-out disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
      >
        Search
      </button>
    </form>
  )
}
