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
    <div className="min-h-screen bg-zar-bg font-zar flex flex-col">
      {/* Top nav bar */}
      <header className="border-b border-zar-border bg-zar-bg/80 backdrop-blur-zar sticky top-0 z-40">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center gap-3">
          <img src="/logo.png" alt="CleverPachonc" className="w-7 h-7" />
          <span className="font-black text-white tracking-tight text-base">
            Clever<span className="text-zar-pink">Pachonc</span>
          </span>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 pt-10 pb-4 flex-1 w-full">
        {/* Hero / search area */}
        {!data && !loading && !error && (
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 bg-zar-pink/10 border border-zar-pink/25 text-zar-pink text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-widest mb-6">
              <span className="w-1.5 h-1.5 rounded-full bg-zar-pink animate-pulse" />
              AI-Powered Coaching
            </div>
            <h1 className="text-4xl font-black text-white tracking-tight leading-none mb-3">
              Your personal<br />
              <span className="text-zar-pink">League coach</span>
            </h1>
            <p className="text-zar-text-secondary text-sm mb-8">
              Stats tracker · AI analysis · Meta insights
            </p>
          </div>
        )}

        <SearchBar onSearch={handleSearch} disabled={loading} compact={!!data} />

        {loading && (
          <div className="mt-16 flex flex-col items-center gap-4">
            <div className="w-10 h-10 border-2 border-zar-pink border-t-transparent rounded-full animate-spin" />
            <p className="text-zar-text-secondary text-sm animate-pulse tracking-wide">{loadingMsg}</p>
          </div>
        )}

        {error && (
          <div className="mt-6 bg-zar-red/10 border border-zar-red/25 text-zar-red rounded-xl p-4 text-sm text-center">
            {error}
          </div>
        )}

        {data && <StatsView data={data} />}
      </div>

      <Footer />
    </div>
  )
}
