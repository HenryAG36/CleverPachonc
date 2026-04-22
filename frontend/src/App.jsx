import { useState } from 'react'
import SearchBar from './components/SearchBar'
import StatsView from './components/StatsView'
import Footer from './components/Footer'

export default function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [loadingMsg, setLoadingMsg] = useState('Searching...')

  async function handleSearch(name, region) {
    setLoading(true)
    setError(null)
    setData(null)
    setLoadingMsg('Looking up account...')

    // Cycle loading messages to give feedback during the ~5-15s fetch
    const messages = [
      'Looking up account...',
      'Fetching ranked stats...',
      'Loading match history...',
      'Crunching the numbers...',
    ]
    let msgIdx = 0
    const msgTimer = setInterval(() => {
      msgIdx = (msgIdx + 1) % messages.length
      setLoadingMsg(messages[msgIdx])
    }, 3000)

    try {
      const res = await fetch(
        `/api/summoner?name=${encodeURIComponent(name)}&region=${encodeURIComponent(region)}`
      )
      const json = await res.json()
      if (!res.ok) throw new Error(json.error || 'Something went wrong.')
      setData(json)
    } catch (e) {
      setError(e.message)
    } finally {
      clearInterval(msgTimer)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-lol-bg flex flex-col">
      <div className="max-w-5xl mx-auto px-4 py-8 flex-1 w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-lol-gold tracking-wide">CleverPachonc</h1>
          <p className="text-gray-500 mt-1 text-sm">League of Legends stats tracker</p>
        </div>

        <SearchBar onSearch={handleSearch} disabled={loading} />

        {/* Loading */}
        {loading && (
          <div className="mt-10 flex flex-col items-center gap-3">
            <div className="w-10 h-10 border-4 border-lol-gold border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-400 text-sm animate-pulse">{loadingMsg}</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mt-6 card border-red-800 bg-red-900/20 text-red-300 text-center">
            {error}
          </div>
        )}

        {/* Results */}
        {data && <StatsView data={data} />}
      </div>
      <Footer />
    </div>
  )
}
