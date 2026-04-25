const TIER_STYLES = {
  OP: 'text-yellow-400 bg-yellow-400/10 ring-1 ring-yellow-400/30',
  S:  'text-apple-yellow bg-apple-yellow/10',
  A:  'text-apple-green bg-apple-green/10',
  B:  'text-apple-blue bg-apple-blue/10',
  C:  'text-apple-text-secondary bg-white/5',
}

export default function MetaTierBadge({ tier, wr, size = 'sm' }) {
  if (!tier) return null
  const style = TIER_STYLES[tier] ?? TIER_STYLES.C
  const textSize = size === 'xs' ? 'text-[10px]' : 'text-xs'
  return (
    <span className={`${textSize} font-bold px-1.5 py-0.5 rounded-full whitespace-nowrap ${style}`}>
      {tier}{wr != null ? <span className="font-normal opacity-70"> {wr}%</span> : null}
    </span>
  )
}
