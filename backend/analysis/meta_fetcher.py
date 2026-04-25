"""
Fetch champion meta statistics from Meraki Analytics (public CDN, cloud-IP friendly).
Lolalytics/U.GG block Vercel IPs via Cloudflare; Meraki does not.

Meraki provides play rates only — no win rates. Win-rate-based features (tier badges,
meta_picks sorting) are disabled until a WR source is available. Tilt detection and
matchup loss tracking work without this module.
"""
import json
import logging
import os
import time

import requests

from backend.data_dragon import get_latest_version

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(os.environ.get("TMPDIR", "/tmp"), "cleverpachonc_cache")
CACHE_TTL = 86400  # 24 hours

MERAKI_URL = "https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/championrates.json"
MERAKI_CACHE = os.path.join(CACHE_DIR, "meraki_rates.json")

# Map our role names to Meraki's role keys (they match Riot's teamPosition names)
ROLE_TO_MERAKI: dict[str, str] = {
    "TOP": "TOP",
    "JUNGLE": "JUNGLE",
    "MIDDLE": "MIDDLE",
    "BOTTOM": "BOTTOM",
    "UTILITY": "UTILITY",
    "DEFAULT": "BOTTOM",
}

_champ_id_map: dict[str, str] = {}


def _get_champion_ids() -> dict[str, str]:
    """Return champion name → numeric Riot ID mapping (e.g. {'Jinx': '222'})."""
    global _champ_id_map
    if _champ_id_map:
        return _champ_id_map
    try:
        version = get_latest_version()
        r = requests.get(
            f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json",
            timeout=8,
        )
        r.raise_for_status()
        _champ_id_map = {name: info["key"] for name, info in r.json()["data"].items()}
    except Exception as exc:
        logger.warning("Champion ID fetch failed: %s", exc)
    return _champ_id_map


def _get_meraki_data() -> dict | None:
    """Fetch and cache the full Meraki champion rates JSON (one call covers all champs)."""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
    except OSError:
        pass

    # Serve from cache if fresh
    try:
        if os.path.exists(MERAKI_CACHE):
            age = time.time() - os.path.getmtime(MERAKI_CACHE)
            if age < CACHE_TTL:
                with open(MERAKI_CACHE) as f:
                    cached = json.load(f)
                    return cached.get("data", {})
    except Exception:
        pass

    try:
        r = requests.get(MERAKI_URL, timeout=8)
        r.raise_for_status()
        data = r.json()
        print(f"[meta] Meraki fetched patch={data.get('patch', '?')} champions={len(data.get('data', {}))}")
        try:
            with open(MERAKI_CACHE, "w") as f:
                json.dump(data, f)
        except OSError:
            pass
        return data.get("data", {})
    except Exception as exc:
        print(f"[meta] Meraki fetch error: {exc}")
        return None


def get_champion_meta(champion_name: str, role: str, tier: str) -> dict | None:
    """
    Return meta stats for a champion. Only play rate is available (Meraki source).
    win_rate and tier will be None — callers must handle gracefully.
    Returns None if champion not found.
    """
    champ_ids = _get_champion_ids()
    champ_id = champ_ids.get(champion_name)
    if not champ_id:
        return None

    meraki_data = _get_meraki_data()
    if not meraki_data:
        return None

    # Meraki keys by string champion ID
    champ_rates = meraki_data.get(str(champ_id))
    if not champ_rates:
        return None

    # Determine primary role (highest play rate)
    primary_role = max(champ_rates, key=lambda r: champ_rates[r].get("playRate", 0))
    target_key = ROLE_TO_MERAKI.get(role.upper(), "BOTTOM")
    if target_key not in champ_rates:
        target_key = primary_role
    play_rate = round(champ_rates[target_key].get("playRate", 0) * 100, 1)

    return {
        "win_rate": None,   # not available from Meraki
        "tier": None,       # cannot compute without WR
        "best_items": [],   # not available from Meraki
        "keystone": None,
        "matchups": {},     # not available from Meraki
        "play_rate": play_rate,
        "primary_role": primary_role,
    }
