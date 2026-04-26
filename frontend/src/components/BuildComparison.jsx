export default function BuildComparison({ championName, playerItems, metaItems, ddVersion }) {
  if (!playerItems?.length && !metaItems?.length) return null

  const playerIds = new Set(playerItems?.map(i => i.item_id).filter(Boolean) ?? [])

  function ItemIcon({ itemId, isMismatch }) {
    if (!itemId || itemId === 0) return null
    const url = `https://ddragon.leagueoflegends.com/cdn/${ddVersion}/img/item/${itemId}.png`
    return (
      <div className={`relative w-8 h-8 rounded overflow-hidden ${isMismatch ? 'ring-2 ring-zar-yellow/60' : ''}`}>
        <img
          src={url}
          alt={String(itemId)}
          className="w-full h-full object-cover"
          onError={e => { e.target.style.display = 'none' }}
        />
      </div>
    )
  }

  return (
    <div className="bg-zar-card2 border border-zar-border rounded-lg p-3 space-y-2">
      <p className="text-xs font-bold text-white">{championName}</p>

      {playerItems?.length > 0 && (
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-zar-text-tertiary w-14 shrink-0 uppercase tracking-wide font-semibold">Your build</span>
          <div className="flex gap-1 flex-wrap">
            {playerItems.slice(0, 6).map((item, i) => (
              <ItemIcon key={i} itemId={item.item_id} isMismatch={false} />
            ))}
          </div>
        </div>
      )}

      {metaItems?.length > 0 && (
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-zar-text-tertiary w-14 shrink-0 uppercase tracking-wide font-semibold">Meta best</span>
          <div className="flex gap-1 flex-wrap">
            {metaItems.slice(0, 6).map((item, i) => (
              <ItemIcon key={i} itemId={item.id} isMismatch={!playerIds.has(item.id)} />
            ))}
          </div>
          <span className="text-[10px] text-zar-yellow ml-1">← consider swapping</span>
        </div>
      )}
    </div>
  )
}
