import { useState } from 'react'
import SearchBar from './components/SearchBar'
import StatsView from './components/StatsView'
import TierList from './components/TierList'
import Footer from './components/Footer'
import { fetchJson } from './utils/fetchJson'

const LOADING_MESSAGES = [
  'Looking up account...',
  'Fetching ranked stats...',
  'Loading match history...',
  'Crunching the numbers...',
]

const FEATURES = [
  {
    title: 'Stats Tracker',
    desc: 'Ranked, mastery, matches and per-champion breakdowns',
    icon: (
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    ),
  },
  {
    title: 'AI Coaching',
    desc: 'Personalized strengths, weaknesses and a path to climb',
    icon: (
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    ),
  },
  {
    title: 'Meta Insights',
    desc: 'Daily pick rates, tier list and pre-session advice',
    icon: (
      <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
    ),
  },
]

function LoadingSkeleton({ message }) {
  return (
    <div className="mt-8 space-y-6" role="status" aria-live="polite">
      <div className="flex items-center justify-center gap-3 py-2">
        <div className="w-5 h-5 border-2 border-zar-pink border-t-transparent rounded-full animate-spin" />
        <p className="text-zar-text-secondary text-sm tracking-wide">{message}</p>
      </div>
      <div className="card flex items-center gap-5">
        <div className="skeleton w-20 h-20 rounded-full shrink-0" />
        <div className="space-y-2.5 flex-1">
          <div className="skeleton h-6 w-48 max-w-full" />
          <div className="skeleton h-3.5 w-32" />
        </div>
      </div>
      <div className="skeleton h-40 w-full" />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="skeleton h-56" />
        <div className="skeleton h-56" />
      </div>
    </div>
  )
}

export default function App() {
  const [view, setView] = useState('search') // 'search' | 'tierlist'
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [loadingMsg, setLoadingMsg] = useState('Searching...')
  const [searchState, setSearchState] = useState({ name: '', region: 'NA' })

  async function handleSearch(name, region) {
    setLoading(true)
    setError(null)
    setData(null)
    setSearchState({ name, region })
    setLoadingMsg(LOADING_MESSAGES[0])
    let msgIdx = 0
    const msgTimer = setInterval(() => {
      msgIdx = (msgIdx + 1) % LOADING_MESSAGES.length
      setLoadingMsg(LOADING_MESSAGES[msgIdx])
    }, 3000)
    try {
      const json = await fetchJson(
        `/api/summoner?name=${encodeURIComponent(name)}&region=${encodeURIComponent(region)}`
      )
      setData(json)
    } catch (e) {
      setError(
        e.message === 'Failed to fetch'
          ? 'Could not reach the server. Check your connection and try again.'
          : e.message
      )
    } finally {
      clearInterval(msgTimer)
      setLoading(false)
    }
  }

  const showHero = view === 'search' && !data && !loading && !error

  return (
    <div className="min-h-screen font-zar flex flex-col">
      {/* Top nav */}
      <header className="border-b border-zar-border bg-zar-bg/80 backdrop-blur-zar sticky top-0 z-40">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center gap-3">
          <button
            onClick={() => setView('search')}
            className="flex items-center gap-2.5 group"
            aria-label="CleverPachonc home"
          >
            <img src="/logo.png" alt="" className="w-7 h-7 transition-transform group-hover:scale-110" />
            <span className="font-black text-white tracking-tight text-sm sm:text-base">
              Clever<span className="text-zar-pink">Pachonc</span>
            </span>
          </button>
          <nav className="ml-auto flex gap-2" aria-label="Main">
            {[
              { id: 'search', label: 'Search' },
              { id: 'tierlist', label: 'Tier List' },
            ].map(item => (
              <button
                key={item.id}
                onClick={() => setView(item.id)}
                aria-current={view === item.id ? 'page' : undefined}
                className={`px-2.5 sm:px-4 py-1.5 rounded-xl text-xs sm:text-sm font-bold transition-all whitespace-nowrap ${
                  view === item.id
                    ? 'bg-zar-pink text-white shadow-[0_0_16px_rgba(255,45,107,0.35)]'
                    : 'border border-zar-border text-zar-text-secondary hover:text-white hover:border-white/20'
                }`}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 pt-10 pb-4 flex-1 w-full">
        {view === 'tierlist' ? (
          <TierList />
        ) : (
          <>
            {/* Hero — only shown before any search */}
            {showHero && (
              <div className="text-center mb-10 fade-in-up">
                <div className="inline-flex items-center gap-2 bg-zar-pink/10 border border-zar-pink/25 text-zar-pink text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-widest mb-6">
                  <span className="w-1.5 h-1.5 rounded-full bg-zar-pink animate-pulse" />
                  AI-Powered Coaching
                </div>
                <h1 className="text-4xl sm:text-5xl font-black text-white tracking-tight leading-none mb-4">
                  Your personal<br />
                  <span className="bg-gradient-to-r from-zar-pink to-zar-cyan bg-clip-text text-transparent">
                    League coach
                  </span>
                </h1>
                <p className="text-zar-text-secondary text-sm sm:text-base mb-10 max-w-md mx-auto leading-relaxed">
                  Search any Riot ID to get ranked stats, match analysis and
                  AI coaching built from your own games.
                </p>
              </div>
            )}

            <SearchBar onSearch={handleSearch} disabled={loading} compact={!!data} />

            {/* Feature cards under the hero search */}
            {showHero && (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-10 fade-in-up">
                {FEATURES.map(f => (
                  <div key={f.title} className="card-sm text-left hover:border-white/15 transition-colors">
                    <div className="w-8 h-8 rounded-lg bg-zar-cyan/10 border border-zar-cyan/20 flex items-center justify-center mb-3">
                      <svg className="w-4 h-4 text-zar-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
                        {f.icon}
                      </svg>
                    </div>
                    <p className="font-bold text-sm text-white mb-1">{f.title}</p>
                    <p className="text-zar-text-secondary text-xs leading-relaxed">{f.desc}</p>
                  </div>
                ))}
              </div>
            )}

            {loading && <LoadingSkeleton message={loadingMsg} />}

            {error && (
              <div className="mt-6 bg-zar-red/10 border border-zar-red/25 rounded-xl p-5 text-center fade-in-up" role="alert">
                <div className="flex items-center justify-center gap-2 text-zar-red text-sm font-semibold mb-1">
                  <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  {error}
                </div>
                <p className="text-zar-text-tertiary text-xs">
                  Double-check the Riot ID (Name#TAG) and region, then try again.
                </p>
              </div>
            )}

            {data && (
              <StatsView
                data={data}
                region={searchState.region}
                playerName={data.summoner?.gameName || searchState.name}
              />
            )}
          </>
        )}
      </div>

      <Footer />
    </div>
  )
}
