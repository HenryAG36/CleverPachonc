const TIER_STYLES = {
  OP: 'text-zar-yellow bg-zar-yellow/10 border border-zar-yellow/30',
  S:  'text-zar-pink bg-zar-pink/10 border border-zar-pink/25',
  A:  'text-zar-green bg-zar-green/10 border border-zar-green/20',
  B:  'text-zar-cyan bg-zar-cyan/10 border border-zar-cyan/20',
  C:  'text-zar-text-secondary bg-white/5 border border-zar-border',
}

export default function MetaTierBadge({ tier, wr, size = 'sm' }) {
  if (!tier) return null
  const style = TIER_STYLES[tier] ?? TIER_STYLES.C
  const textSize = size === 'xs' ? 'text-[9px]' : 'text-[10px]'
  return (
    <span className={`${textSize} font-black px-1.5 py-0.5 rounded uppercase tracking-wider whitespace-nowrap ${style}`}>
      {tier}{wr != null ? <span className="font-normal opacity-75"> {wr}%</span> : null}
    </span>
  )
}
