// fetch() wrapper that never surfaces raw JSON parse errors to the UI.
// Gateway timeouts / proxy error pages return HTML — turn those into a
// readable message instead of "Unexpected token 'A'... is not valid JSON".
export async function fetchJson(url, options) {
  const res = await fetch(url, options)
  let json = null
  try {
    json = await res.json()
  } catch {
    // non-JSON response body
  }
  if (!res.ok) {
    throw new Error(
      json?.error || `The server returned an unexpected response (${res.status}). Please try again.`
    )
  }
  if (!json) throw new Error('The server returned an unexpected response. Please try again.')
  return json
}
