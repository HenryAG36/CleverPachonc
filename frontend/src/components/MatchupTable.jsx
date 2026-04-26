export default function MatchupTable({ matchupInsights, ddVersion }) {
  if (!matchupInsights?.length) return null

  function WrPill({ wr }) {
    if (wr == null) return <span className="text-zar-text-tertiary text-xs">—</span>
    const color = wr >= 50 ? 'text-zar-green' : 'text-zar-red'
    return <span className={`text-xs font-bold ${color}`}>{wr.toFixed(1)}%</span>
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
                <span className="text-sm font-semibold">{mu.enemy}</span>
              </div>
              <div className="flex items-center gap-4 text-right">
                <div className="text-center">
                  <p className="text-[10px] text-zar-text-tertiary uppercase tracking-widest font-bold">Your Record</p>
                  <p className="text-xs font-bold text-zar-red">0-{mu.losses}</p>
                </div>
                <div className="text-center">
                  <p className="text-[10px] text-zar-text-tertiary uppercase tracking-widest font-bold">Meta WR</p>
                  <WrPill wr={mu.meta_wr} />
                </div>
                {unfavorable && (
                  <span className="text-[10px] bg-zar-red/10 text-zar-red border border-zar-red/20 px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                    Counter
                  </span>
                )}
              </div>
            </div>
          )
        })}
      </div>
      <p className="text-[10px] text-zar-text-tertiary mt-2 uppercase tracking-widest font-semibold">
        Meta WR = how your champion performs vs this opponent at your tier
      </p>
    </div>
  )
}
