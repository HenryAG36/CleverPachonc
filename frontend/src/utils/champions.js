// Data Dragon champion ids whose display name differs from the id.
// The API (and all image URLs) use the id; only user-facing text should
// go through championDisplayName().
const DISPLAY_NAMES = {
  AurelionSol: 'Aurelion Sol',
  Belveth: "Bel'Veth",
  FiddleSticks: 'Fiddlesticks', // raw Riot match data uses this casing
  Chogath: "Cho'Gath",
  DrMundo: 'Dr. Mundo',
  JarvanIV: 'Jarvan IV',
  KSante: "K'Sante",
  Kaisa: "Kai'Sa",
  Khazix: "Kha'Zix",
  KogMaw: "Kog'Maw",
  Leblanc: 'LeBlanc',
  LeeSin: 'Lee Sin',
  MasterYi: 'Master Yi',
  MissFortune: 'Miss Fortune',
  MonkeyKing: 'Wukong',
  Nunu: 'Nunu & Willump',
  RekSai: "Rek'Sai",
  Renata: 'Renata Glasc',
  TahmKench: 'Tahm Kench',
  TwistedFate: 'Twisted Fate',
  Velkoz: "Vel'Koz",
  XinZhao: 'Xin Zhao',
}

export function championDisplayName(id) {
  if (!id) return ''
  if (DISPLAY_NAMES[id]) return DISPLAY_NAMES[id]
  // Future champions not in the map: split CamelCase into words
  return id.replace(/([a-z])([A-Z])/g, '$1 $2')
}
