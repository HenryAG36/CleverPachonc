"""
Async Riot API client.

Key design decisions vs the old desktop client:
- get_summoner_data_async() fetches match details ONCE (fixes double-fetch bug).
- _compute_streak() returns the current consecutive run, not the historical max.
- All network calls run inside a single aiohttp.ClientSession per invocation.
- Concurrent requests are capped by an asyncio.Semaphore (CONCURRENCY_LIMIT=5).
"""
import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

import aiohttp

from .utils.constants import (
    REGION_ROUTING, MATCH_ROUTING,
    REQUEST_TIMEOUT, RETRY_ATTEMPTS, RETRY_BACKOFF, get_api_key,
)
from .utils.exceptions import (
    APIError, AuthError, ConfigError, NetworkError, NotFoundError, RateLimitError,
)
from .utils.rate_limiter import make_semaphore


# ---------------------------------------------------------------------------
# Low-level async helpers
# ---------------------------------------------------------------------------

async def _get(
    session: aiohttp.ClientSession,
    url: str,
    headers: Dict[str, str],
    params: Dict[str, Any] = None,
    semaphore: asyncio.Semaphore = None,
) -> Optional[Any]:
    """Single GET with exponential backoff on 429 and transient server errors."""
    async def _do():
        for attempt in range(RETRY_ATTEMPTS):
            try:
                async with session.get(
                    url, headers=headers, params=params,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    if resp.status == 404:
                        raise NotFoundError("Resource not found.", resp.status)
                    if resp.status in (401, 403):
                        raise AuthError("API key invalid or unauthorized.", resp.status)
                    if resp.status == 429:
                        if attempt < RETRY_ATTEMPTS - 1:
                            wait = int(resp.headers.get("Retry-After", 1))
                            await asyncio.sleep(min(wait, 10))
                            continue
                        raise RateLimitError("Rate limit exceeded.", resp.status)
                    if resp.status >= 500:
                        if attempt < RETRY_ATTEMPTS - 1:
                            await asyncio.sleep(RETRY_BACKOFF * (2 ** attempt))
                            continue
                        raise APIError(f"Riot server error ({resp.status}).", resp.status)
                    return None
            except (NotFoundError, AuthError, RateLimitError, APIError):
                raise
            except aiohttp.ClientError as exc:
                if attempt < RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(RETRY_BACKOFF * (2 ** attempt))
                    continue
                raise NetworkError(str(exc)) from exc
        return None

    if semaphore:
        async with semaphore:
            return await _do()
    return await _do()


# ---------------------------------------------------------------------------
# Streak helper (Bug fix #2)
# ---------------------------------------------------------------------------

def _compute_streak(match_details: List[Dict], puuid: str) -> int:
    """
    Return the player's current consecutive win/loss streak.

    Positive = wins, negative = losses.
    Riot returns matches newest-first, so we walk forward and stop
    the moment the result flips.
    """
    streak = 0
    for match in match_details:
        p = next(
            (x for x in match["info"]["participants"] if x["puuid"] == puuid),
            None,
        )
        if not p:
            continue
        won = p["win"]
        if streak == 0:
            streak = 1 if won else -1
        elif (won and streak > 0) or (not won and streak < 0):
            streak += 1 if won else -1
        else:
            break
    return streak


# ---------------------------------------------------------------------------
# Core async data-fetch (Bug fix #1: single match-detail pass)
# ---------------------------------------------------------------------------

async def _fetch_summoner(
    game_name: str,
    tag_line: str,
    region: str,
    api_key: str,
    session: aiohttp.ClientSession,
) -> Dict:
    """Resolve Riot ID → account → summoner, merging gameName/tagLine in."""
    routing = MATCH_ROUTING.get(region.upper(), "americas")
    platform_url = REGION_ROUTING.get(region.upper())
    if not platform_url:
        raise APIError(f"Unsupported region: {region}")

    headers = {"X-Riot-Token": api_key}

    account = await _get(
        session,
        f"https://{routing}.api.riotgames.com/riot/account/v1/accounts"
        f"/by-riot-id/{game_name}/{tag_line}",
        headers,
    )
    if not account:
        raise NotFoundError("Account not found.")

    summoner = await _get(
        session,
        f"{platform_url}/lol/summoner/v4/summoners/by-puuid/{account['puuid']}",
        headers,
    )
    if not summoner:
        raise NotFoundError("Summoner data not found.")

    summoner["gameName"] = account.get("gameName", game_name)
    summoner["tagLine"] = account.get("tagLine", tag_line)
    return summoner


async def get_summoner_data_async(
    summoner_name: str,
    region: str,
) -> Tuple[Dict, List, List, List]:
    """
    Fetch everything needed for the stats page in one optimised async pass.

    Returns: (summoner, ranked_data, mastery_data, match_details)

    Match details are fetched ONCE and reused for both analytics and display.
    """
    api_key = get_api_key()
    if not api_key:
        raise ConfigError("RIOT_API_KEY environment variable is not set.")

    if "#" not in summoner_name:
        raise APIError("Riot ID tag required — format: Name#TAG")

    game_name, tag_line = summoner_name.split("#", 1)
    region_upper = region.upper()
    platform_url = REGION_ROUTING.get(region_upper)
    routing = MATCH_ROUTING.get(region_upper, "americas")
    headers = {"X-Riot-Token": api_key}

    async with aiohttp.ClientSession() as session:
        # ── Step 1: resolve summoner ────────────────────────────────
        summoner = await _fetch_summoner(game_name, tag_line, region, api_key, session)
        puuid = summoner["puuid"]

        # ── Step 2: ranked + mastery + match IDs (concurrent) ───────
        ranked_data, mastery_data, match_ids = await asyncio.gather(
            _get(session, f"{platform_url}/lol/league/v4/entries/by-puuid/{puuid}", headers),
            _get(session, f"{platform_url}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}", headers),
            _get(
                session,
                f"https://{routing}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids",
                headers,
                params={"queue": 420, "count": 20},
            ),
        )

        ranked_data = ranked_data or []
        mastery_data = mastery_data or []
        match_ids = match_ids or []

        # ── Step 3: match details — ONE fetch, semaphore-capped ─────
        sem = make_semaphore()
        match_details = []
        if match_ids:
            results = await asyncio.gather(*[
                _get(
                    session,
                    f"https://{routing}.api.riotgames.com/lol/match/v5/matches/{mid}",
                    headers,
                    semaphore=sem,
                )
                for mid in match_ids[:20]
            ], return_exceptions=True)
            match_details = [m for m in results if isinstance(m, dict)]

    # ── Step 4: compute analytics from the same match_details ───────
    streak = _compute_streak(match_details, puuid)

    roles: Dict[str, int] = defaultdict(int)
    kda_totals = {"kills": 0, "deaths": 0, "assists": 0}
    games_counted = 0

    for match in match_details:
        p = next((x for x in match["info"]["participants"] if x["puuid"] == puuid), None)
        if not p:
            continue
        roles[p["teamPosition"]] += 1
        kda_totals["kills"] += p["kills"]
        kda_totals["deaths"] += p["deaths"]
        kda_totals["assists"] += p["assists"]
        games_counted += 1

    avg_kda = {k: kda_totals[k] / games_counted if games_counted else 0 for k in kda_totals}
    most_played_role = max(roles, key=roles.get) if roles else "Unknown"

    for queue in ranked_data:
        queue["streak"] = streak
        queue["mostPlayedRole"] = most_played_role
        queue["avgKDA"] = avg_kda
        queue["recentGames"] = games_counted

    return summoner, ranked_data, mastery_data, match_details
