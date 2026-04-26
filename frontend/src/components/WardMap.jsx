import { useState, useEffect, useRef } from 'react'

// Common high-elo vision control zones on Summoner's Rift
// Coordinates match League's game coordinate system (0–14870)
const IDEAL_ZONES = [
  { x: 9700, y: 4300, label: 'Dragon entrance' },
  { x: 4700, y: 10500, label: 'Baron entrance' },
  { x: 7200, y: 5500, label: 'Blue side river' },
  { x: 7600, y: 8600, label: 'Red side river' },
  { x: 10100, y: 3300, label: 'Bot tri-brush' },
  { x: 4000, y: 11700, label: 'Top tri-brush' },
  { x: 3900, y: 8200, label: 'Top river' },
  { x: 10900, y: 6000, label: 'Bot river' },
]

const MAP_SIZE = 14870
const CANVAS_SIZE = 400

function toCanvas(x, y) {
  return {
    cx: (x / MAP_SIZE) * CANVAS_SIZE,
    cy: CANVAS_SIZE - (y / MAP_SIZE) * CANVAS_SIZE,
  }
}

const WARD_COLORS = {
  CONTROL_WARD: '#FF2D6B',
  YELLOW_TRINKET: '#FFD60A',
  BLUE_TRINKET: '#00CFDD',
  SIGHT_WARD: '#FFD60A',
  UNDEFINED: 'rgba(255,255,255,0.5)',
}

export default function WardMap({ matchId, region, puuid }) {
  const [state, setState] = useState('idle') // idle | loading | done | error
  const [wards, setWards] = useState([])
  const [error, setError] = useState(null)
  const canvasRef = useRef(null)

  async function loadWards() {
    setState('loading')
    try {
      const res = await fetch(
        `/api/match/timeline?id=${encodeURIComponent(matchId)}&region=${encodeURIComponent(region)}&puuid=${encodeURIComponent(puuid)}`
      )
      const json = await res.json()
      if (!res.ok) throw new Error(json.error || 'Failed to load ward data')
      setWards(json.ward_events || [])
      setState('done')
    } catch (e) {
      setError(e.message)
      setState('error')
    }
  }

  useEffect(() => {
    if (state !== 'done' || !canvasRef.current) return
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE)

    // Draw ideal zones (semi-transparent green rings)
    for (const zone of IDEAL_ZONES) {
      const { cx, cy } = toCanvas(zone.x, zone.y)
      ctx.beginPath()
      ctx.arc(cx, cy, 16, 0, Math.PI * 2)
      ctx.fillStyle = 'rgba(46,204,113,0.12)'
      ctx.fill()
      ctx.strokeStyle = 'rgba(46,204,113,0.35)'
      ctx.lineWidth = 1
      ctx.stroke()
    }

    // Draw ward events
    for (const w of wards) {
      const { cx, cy } = toCanvas(w.x, w.y)
      const color = WARD_COLORS[w.type] || WARD_COLORS.UNDEFINED
      ctx.beginPath()
      ctx.arc(cx, cy, 5, 0, Math.PI * 2)
      ctx.fillStyle = color + 'cc'
      ctx.fill()
      ctx.strokeStyle = color
      ctx.lineWidth = 1
      ctx.stroke()
    }
  }, [state, wards])

  if (state === 'idle') {
    return (
      <button onClick={loadWards} className="zar-btn-ghost w-full mt-4">
        View Ward Map
      </button>
    )
  }

  if (state === 'loading') {
    return (
      <div className="flex items-center justify-center gap-2 py-6 text-zar-text-secondary text-sm mt-4">
        <div className="w-4 h-4 border-2 border-zar-cyan border-t-transparent rounded-full animate-spin" />
        Loading timeline…
      </div>
    )
  }

  if (state === 'error') {
    return (
      <div className="mt-4 text-zar-red text-sm text-center py-4">
        {error}
        <button onClick={loadWards} className="ml-2 underline text-zar-text-secondary">Retry</button>
      </div>
    )
  }

  return (
    <div className="mt-4">
      <p className="section-title mb-2">Ward Map</p>
      <div className="relative inline-block rounded-xl overflow-hidden border border-zar-border">
        <img
          src="https://ddragon.leagueoflegends.com/cdn/img/map/map11.png"
          alt="Summoner's Rift"
          width={CANVAS_SIZE}
          height={CANVAS_SIZE}
          className="block opacity-70"
        />
        <canvas
          ref={canvasRef}
          width={CANVAS_SIZE}
          height={CANVAS_SIZE}
          className="absolute inset-0"
        />
      </div>
      {/* Legend */}
      <div className="flex gap-4 mt-2 text-xs text-zar-text-secondary flex-wrap">
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-zar-pink inline-block" /> Control Ward
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-zar-yellow inline-block" /> Trinket Ward
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-zar-green/40 border border-zar-green/60 inline-block" /> Common vision zones
        </span>
      </div>
      <p className="text-[10px] text-zar-text-tertiary mt-1">{wards.length} wards placed this game</p>
    </div>
  )
}
