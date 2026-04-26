"""
Champion meta statistics — reads from committed backend/meta_cache.json when available,
falls back to Meraki Analytics (play rates only) otherwise.

meta_cache.json is populated daily by the GitHub Actions workflow in
.github/workflows/fetch_meta.yml which fetches Lolalytics from GitHub's IPs.
"""
import json
import logging
import os
import time

import requests

from backend.data_dragon import get_latest_version

logger = logging.getLogger(__name__)

# Committed meta cache (populated by GitHub Actions)
META_CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", "meta_cache.json")

# Meraki fallback (cloud-IP friendly, play rates only)
MERAKI_URL = "https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/championrates.json"
TMPDIR = os.path.join(os.environ.get("TMPDIR", "/tmp"), "cleverpachonc_cache")
MERAKI_CACHE = os.path.join(TMPDIR, "meraki_rates.json")
CACHE_TTL = 86400

ROLE_TO_LANE: dict[str, str] = {
    "TOP": "top", "JUNGLE": "jungle", "MIDDLE": "mid",
    "BOTTOM": "adc", "UTILITY": "support", "DEFAULT": "adc",
}

_champ_id_map: dict[str, str] = {}
_meta_cache: dict | None = None  # in-memory loaded cache


def _get_champion_ids() -> dict[str, str]:
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


def _load_meta_cache() -> dict | None:
    """Load backend/meta_cache.json committed by GitHub Actions."""
    global _meta_cache
    if _meta_cache is not None:
        return _meta_cache
    path = os.path.abspath(META_CACHE_FILE)
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            payload = json.load(f)
        _meta_cache = payload.get("data", {})
        patch = payload.get("patch", "?")
        print(f"[meta] loaded meta_cache.json patch={patch} entries={len(_meta_cache)}")
        return _meta_cache
    except Exception as exc:
        logger.warning("meta_cache.json load error: %s", exc)
        return None


def _get_meraki_data() -> dict | None:
    """Fetch/cache Meraki champion rates (one call for all champions)."""
    try:
        os.makedirs(TMPDIR, exist_ok=True)
    except OSError:
        pass
    try:
        if os.path.exists(MERAKI_CACHE):
            if time.time() - os.path.getmtime(MERAKI_CACHE) < CACHE_TTL:
                with open(MERAKI_CACHE) as f:
                    return json.load(f).get("data", {})
    except Exception:
        pass
    try:
        r = requests.get(MERAKI_URL, timeout=8)
        r.raise_for_status()
        data = r.json()
        print(f"[meta] Meraki fallback patch={data.get('patch', '?')} champions={len(data.get('data', {}))}")
        try:
            with open(MERAKI_CACHE, "w") as f:
                json.dump(data, f)
        except OSError:
            pass
        return data.get("data", {})
    except Exception as exc:
        print(f"[meta] Meraki fetch error: {exc}")
        return None


def _tier_label(wr: float) -> str:
    if wr >= 54:
        return "OP"
    if wr >= 52:
        return "S"
    if wr >= 50:
        return "A"
    if wr >= 48:
        return "B"
    return "C"


def get_champion_meta(champion_name: str, role: str, tier: str) -> dict | None:
    """
    Return meta stats for a champion.

    Priority:
    1. backend/meta_cache.json — full data (WR, items, matchups) from GitHub Actions
    2. Meraki Analytics CDN — play rate only (no WR), always available from cloud IPs

    Returns None if champion not found in either source.
    """
    lane = ROLE_TO_LANE.get(role.upper(), "adc")

    # ── Primary: committed cache from GitHub Actions ──────────────────────────
    cache = _load_meta_cache()
    if cache is not None:
        key = f"{champion_name}_{lane}"
        entry = cache.get(key)
        if entry:
            return {
                "win_rate": entry.get("win_rate"),
                "tier": entry.get("tier") or (
                    _tier_label(entry["win_rate"]) if entry.get("win_rate") else None
                ),
                "best_items": entry.get("best_items", []),
                "keystone": entry.get("keystone"),
                "matchups": entry.get("matchups", {}),
            }
        # Cache exists but champion missing — return None rather than falling back
        return None

    # ── Fallback: Meraki (play rate only) ────────────────────────────────────
    champ_ids = _get_champion_ids()
    champ_id = champ_ids.get(champion_name)
    if not champ_id:
        return None

    meraki_data = _get_meraki_data()
    if not meraki_data:
        return None

    champ_rates = meraki_data.get(str(champ_id))
    if not champ_rates:
        return None

    primary_role = max(champ_rates, key=lambda r: champ_rates[r].get("playRate", 0))
    meraki_key = role.upper() if role.upper() in champ_rates else primary_role
    play_rate = round(champ_rates[meraki_key].get("playRate", 0) * 100, 1)

    return {
        "win_rate": None,   # Meraki doesn't provide WR
        "tier": None,
        "best_items": [],
        "keystone": None,
        "matchups": {},
        "play_rate": play_rate,
        "primary_role": primary_role,
    }


def get_full_meta_cache() -> dict:
    """Return the full meta cache dict (all champions, all roles)."""
    return _load_meta_cache() or {}


def get_cache_patch() -> str:
    """Return the patch string stored in meta_cache.json."""
    path = os.path.abspath(META_CACHE_FILE)
    if not os.path.exists(path):
        return "unknown"
    try:
        with open(path) as f:
            return json.load(f).get("patch", "unknown")
    except Exception:
        return "unknown"
