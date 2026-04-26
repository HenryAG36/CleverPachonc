import { useState, useRef } from 'react'
import { createPortal } from 'react-dom'

const DDR_BASE = 'https://ddragon.leagueoflegends.com/cdn/img/'
const TOOLTIP_WIDTH = 288 // w-72

function getPathById(runeTree, id) {
  return runeTree.find(p => p.id === id) || null
}

function getSelectedIds(perks) {
  if (!perks?.styles) return new Set()
  const ids = new Set()
  for (const style of perks.styles) {
    for (const sel of style.selections || []) ids.add(sel.perk)
  }
  return ids
}

function RunePath({ path, selectedIds, isSecondary }) {
  if (!path) return null
  const slots = isSecondary ? path.slots.slice(1) : path.slots
  return (
    <div className="flex-1 min-w-0">
      <div className="flex items-center gap-2 mb-2 pb-1.5 border-b border-zar-border">
        <img
          src={`${DDR_BASE}${path.icon}`}
          alt={path.name}
          className="w-5 h-5 rounded"
          onError={e => { e.target.style.display = 'none' }}
        />
        <span className="text-xs font-bold text-white">{path.name}</span>
      </div>
      <div className="space-y-1.5">
        {slots.map((slot, si) => (
          <div key={si} className="flex gap-1.5 justify-center">
            {slot.runes.map(rune => {
              const selected = selectedIds.has(rune.id)
              return (
                <img
                  key={rune.id}
                  src={`${DDR_BASE}${rune.icon}`}
                  alt={rune.name}
                  title={rune.name}
                  className={`rounded-full transition-opacity ${
                    isSecondary ? 'w-6 h-6' : si === 0 ? 'w-8 h-8' : 'w-6 h-6'
                  } ${selected ? 'opacity-100 ring-1 ring-zar-cyan' : 'opacity-25 grayscale'}`}
                  onError={e => { e.target.style.display = 'none' }}
                />
              )
            })}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function RuneTooltip({ perks, runeTree, children }) {
  const [tooltipStyle, setTooltipStyle] = useState(null)
  const triggerRef = useRef(null)

  if (!perks?.styles?.length || !runeTree?.length) return <>{children}</>

  const primaryStyle = perks.styles[0]
  const secondaryStyle = perks.styles[1]
  const primaryPath = getPathById(runeTree, primaryStyle?.style)
  const secondaryPath = getPathById(runeTree, secondaryStyle?.style)
  const selectedIds = getSelectedIds(perks)

  function handleMouseEnter() {
    if (!triggerRef.current) return
    const rect = triggerRef.current.getBoundingClientRect()

    // Center the tooltip horizontally over the trigger, clamped to viewport
    let left = rect.left + rect.width / 2 - TOOLTIP_WIDTH / 2
    if (left < 8) left = 8
    if (left + TOOLTIP_WIDTH > window.innerWidth - 8) {
      left = window.innerWidth - 8 - TOOLTIP_WIDTH
    }

    setTooltipStyle({
      position: 'fixed',
      top: rect.top - 8,
      left,
      // translateY(-100%) moves the tooltip above the trigger
      transform: 'translateY(-100%)',
      width: TOOLTIP_WIDTH,
      zIndex: 9999,
      pointerEvents: 'none',
    })
  }

  return (
    <div
      ref={triggerRef}
      className="relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={() => setTooltipStyle(null)}
    >
      {children}
      {tooltipStyle && createPortal(
        <div style={tooltipStyle}>
          <div className="bg-zar-bg2 border border-zar-border rounded-xl p-3 shadow-2xl">
            <div className="flex gap-3">
              <RunePath path={primaryPath} selectedIds={selectedIds} isSecondary={false} />
              <div className="w-px bg-zar-border shrink-0" />
              <RunePath path={secondaryPath} selectedIds={selectedIds} isSecondary={true} />
            </div>
            {perks.statPerks && (
              <div className="mt-2 pt-2 border-t border-zar-border flex gap-1 justify-center">
                <span className="text-[10px] text-zar-text-tertiary">Stat shards:</span>
                <span className="text-[10px] text-zar-text-secondary">
                  {[perks.statPerks.offense, perks.statPerks.flex, perks.statPerks.defense].join(' · ')}
                </span>
              </div>
            )}
          </div>
          <div className="w-2 h-2 bg-zar-bg2 border-r border-b border-zar-border rotate-45 mx-auto -mt-1" />
        </div>,
        document.body
      )}
    </div>
  )
}
