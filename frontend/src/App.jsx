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
    const messages = ['Looking up account...', 'Fetching ranked stats...', 'Loading match history...', 'Crunching the numbers...']
    let msgIdx = 0
    const msgTimer = setInterval(() => {
      msgIdx = (msgIdx + 1) % messages.length
      setLoadingMsg(messages[msgIdx])
    }, 3000)
    try {
      const res = await fetch(`/api/summoner?name=${encodeURIComponent(name)}&region=${encodeURIComponent(region)}`)
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
    <div className="min-h-screen bg-apple-bg font-apple flex flex-col">
      <div className="max-w-5xl mx-auto px-4 py-10 flex-1 w-full">
        <div className="text-center mb-10">
          <img src="/logo.png" alt="CleverPachonc logo" className="w-16 h-16 mx-auto mb-3" />
          <h1 className="text-3xl font-bold text-white tracking-tight">CleverPachonc</h1>
          <p className="text-apple-text-secondary mt-1 text-sm">League of Legends stats tracker</p>
        </div>
        <SearchBar onSearch={handleSearch} disabled={loading} />
        {loading && (
          <div className="mt-12 flex flex-col items-center gap-3">
            <div className="w-9 h-9 border-[3px] border-apple-blue border-t-transparent rounded-full animate-spin" />
            <p className="text-apple-text-secondary text-sm animate-pulse">{loadingMsg}</p>
          </div>
        )}
        {error && (
          <div className="mt-6 bg-apple-red/10 text-apple-red rounded-2xl p-4 text-sm text-center">
            {error}
          </div>
        )}
        {data && <StatsView data={data} />}
      </div>
      <Footer />
    </div>
  )
}
