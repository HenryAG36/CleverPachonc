import MetaTierBadge from './MetaTierBadge'

const ROLE_DISPLAY = {
  TOP: 'Top', JUNGLE: 'Jungle', MIDDLE: 'Mid',
  BOTTOM: 'ADC', UTILITY: 'Support',
}

/**
 * Zar-inspired pre-session advisor — shown right after searching.
 * No extra API call required; uses meta data already fetched with the summoner.
 */
export default function PreSessionCard({ meta, ddVersion }) {
  if (!meta) return null

  const { meta_picks, matchup_insights, tilt_flag, consecutive_losses, per_champ_meta } = meta

  const bestPick = meta_picks?.[0]
  const banSuggestion = matchup_insights?.find(m => m.losses >= 2 && m.meta_wr != null && m.meta_wr < 50)
    ?? matchup_insights?.[0]

  if (!bestPick && !banSuggestion && !tilt_flag) return null

  return (
    <div className="card" style={{ borderColor: 'rgba(0,122,255,0.2)', borderWidth: 1, borderStyle: 'solid' }}>
      <div className="flex items-center gap-2 mb-3">
        <div className="w-7 h-7 rounded-full bg-apple-blue/10 flex items-center justify-center">
          <svg className="w-4 h-4 text-apple-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <p className="section-title mb-0">Pre-Session Advisor</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* Best pick today */}
        {bestPick && (
          <div className="bg-apple-card2 rounded-xl p-3">
            <p className="text-[10px] text-apple-text-tertiary uppercase tracking-wider mb-2">Best pick from your pool</p>
            <div className="flex items-center gap-2.5">
              <div className="relative">
                <img
                  src={`https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/champion/${bestPick.name}.png`}
                  alt={bestPick.name}
                  className="w-10 h-10 rounded-lg"
                  onError={e => { e.target.style.display = 'none' }}
                />
              </div>
              <div>
                <p className="font-semibold text-sm">{bestPick.name}</p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <MetaTierBadge tier={bestPick.tier} wr={bestPick.wr} size="xs" />
                  {bestPick.role && (
                    <span className="text-[10px] text-apple-text-secondary">
                      {ROLE_DISPLAY[bestPick.role] ?? bestPick.role}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Ban suggestion */}
        {banSuggestion && (
          <div className="bg-apple-card2 rounded-xl p-3">
            <p className="text-[10px] text-apple-text-tertiary uppercase tracking-wider mb-2">Consider banning</p>
            <div className="flex items-center gap-2.5">
              <div className="relative">
                <img
                  src={`https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/champion/${banSuggestion.enemy}.png`}
                  alt={banSuggestion.enemy}
                  className="w-10 h-10 rounded-lg opacity-80"
                  onError={e => { e.target.style.display = 'none' }}
                />
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-apple-red rounded-full flex items-center justify-center">
                  <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
              <div>
                <p className="font-semibold text-sm">{banSuggestion.enemy}</p>
                <p className="text-[10px] text-apple-text-secondary mt-0.5">
                  {banSuggestion.losses > 0 ? `You went 0-${banSuggestion.losses} vs them` : 'Hard counter'}
                  {banSuggestion.meta_wr != null && (
                    <span className="text-apple-red ml-1">({banSuggestion.meta_wr.toFixed(1)}% meta WR)</span>
                  )}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Tilt alert */}
      {tilt_flag && (
        <div className="mt-3 bg-apple-orange/10 border border-apple-orange/20 rounded-xl px-3 py-2.5 flex items-start gap-2">
          <svg className="w-4 h-4 text-apple-orange mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p className="text-xs text-apple-orange leading-relaxed">
            <span className="font-semibold">Heads up:</span> You've lost {consecutive_losses} games in a row. Consider taking a short break or switching to a comfort pick before queuing again.
          </p>
        </div>
      )}
    </div>
  )
}
