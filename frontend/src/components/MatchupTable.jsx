/**
 * Shows recent difficult matchups from the player's match history,
 * cross-referenced with the meta matchup win rate where available.
 */
export default function MatchupTable({ matchupInsights, ddVersion }) {
  if (!matchupInsights?.length) return null

  function WrPill({ wr }) {
    if (wr == null) return <span className="text-apple-text-tertiary text-xs">—</span>
    const color = wr >= 50 ? 'text-apple-green' : 'text-apple-red'
    return <span className={`text-xs font-semibold ${color}`}>{wr.toFixed(1)}%</span>
  }

  return (
    <div className="card">
      <p className="section-title">Difficult Matchups</p>
      <div className="space-y-0">
        {matchupInsights.map((mu, i) => {
          const iconUrl = `https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/champion/${mu.enemy}.png`
          const unfavorable = mu.meta_wr != null && mu.meta_wr < 50
          return (
            <div key={i} className="stat-row items-center">
              <div className="flex items-center gap-2">
                <img
                  src={iconUrl}
                  alt={mu.enemy}
                  className="w-7 h-7 rounded"
                  onError={e => { e.target.style.display = 'none' }}
                />
                <span className="text-sm font-medium">{mu.enemy}</span>
              </div>
              <div className="flex items-center gap-4 text-right">
                <div className="text-center">
                  <p className="text-[10px] text-apple-text-tertiary uppercase tracking-wide">Your record</p>
                  <p className="text-xs font-semibold text-apple-red">0-{mu.losses}</p>
                </div>
                <div className="text-center">
                  <p className="text-[10px] text-apple-text-tertiary uppercase tracking-wide">Meta WR</p>
                  <WrPill wr={mu.meta_wr} />
                </div>
                {unfavorable && (
                  <span className="text-[10px] bg-apple-red/10 text-apple-red px-2 py-0.5 rounded-full">
                    Counter
                  </span>
                )}
              </div>
            </div>
          )
        })}
      </div>
      <p className="text-[10px] text-apple-text-tertiary mt-2">
        Meta WR = how your champion performs vs this opponent at your tier
      </p>
    </div>
  )
}
