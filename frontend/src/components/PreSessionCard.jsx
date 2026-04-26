import MetaTierBadge from './MetaTierBadge'

const ROLE_DISPLAY = {
  TOP: 'Top', JUNGLE: 'Jungle', MIDDLE: 'Mid',
  BOTTOM: 'ADC', UTILITY: 'Support',
}

export default function PreSessionCard({ meta, ddVersion }) {
  if (!meta) return null

  const { meta_picks, matchup_insights, tilt_flag, consecutive_losses } = meta

  const bestPick = meta_picks?.[0]
  const banSuggestion = matchup_insights?.find(m => m.losses >= 2 && m.meta_wr != null && m.meta_wr < 50)
    ?? matchup_insights?.[0]

  if (!bestPick && !banSuggestion && !tilt_flag) return null

  return (
    <div className="card border border-zar-cyan/20">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-6 h-6 rounded bg-zar-cyan/10 flex items-center justify-center">
          <svg className="w-3.5 h-3.5 text-zar-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <p className="section-title mb-0 text-zar-cyan">Pre-Session Advisor</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {bestPick && (
          <div className="bg-zar-card2 border border-zar-border rounded-lg p-3">
            <p className="text-[10px] text-zar-text-tertiary uppercase tracking-widest font-bold mb-2">Best Pick Today</p>
            <div className="flex items-center gap-2.5">
              <img
                src={`https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/champion/${bestPick.name}.png`}
                alt={bestPick.name}
                className="w-10 h-10 rounded-lg"
                onError={e => { e.target.style.display = 'none' }}
              />
              <div>
                <p className="font-bold text-sm">{bestPick.name}</p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <MetaTierBadge tier={bestPick.tier} wr={bestPick.wr} size="xs" />
                  {bestPick.role && (
                    <span className="text-[10px] text-zar-text-secondary">
                      {ROLE_DISPLAY[bestPick.role] ?? bestPick.role}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {banSuggestion && (
          <div className="bg-zar-card2 border border-zar-border rounded-lg p-3">
            <p className="text-[10px] text-zar-text-tertiary uppercase tracking-widest font-bold mb-2">Consider Banning</p>
            <div className="flex items-center gap-2.5">
              <div className="relative">
                <img
                  src={`https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/champion/${banSuggestion.enemy}.png`}
                  alt={banSuggestion.enemy}
                  className="w-10 h-10 rounded-lg opacity-75"
                  onError={e => { e.target.style.display = 'none' }}
                />
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-zar-red rounded-full flex items-center justify-center">
                  <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
              <div>
                <p className="font-bold text-sm">{banSuggestion.enemy}</p>
                <p className="text-[10px] text-zar-text-secondary mt-0.5">
                  {banSuggestion.losses > 0 ? `You went 0-${banSuggestion.losses} vs them` : 'Hard counter'}
                  {banSuggestion.meta_wr != null && (
                    <span className="text-zar-red ml-1">({banSuggestion.meta_wr.toFixed(1)}% meta WR)</span>
                  )}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {tilt_flag && (
        <div className="mt-3 bg-zar-orange/10 border border-zar-orange/20 rounded-lg px-3 py-2.5 flex items-start gap-2">
          <svg className="w-4 h-4 text-zar-orange mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p className="text-xs text-zar-orange leading-relaxed">
            <span className="font-bold">Heads up:</span> You&apos;ve lost {consecutive_losses} games in a row. Consider taking a short break before queuing again.
          </p>
        </div>
      )}
    </div>
  )
}
