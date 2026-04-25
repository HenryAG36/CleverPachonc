"""
Fetch and cache champion meta statistics from Lolalytics.
All results are cached to backend/cache/ for 24 hours so the same
champion is never fetched more than once per patch cycle.
Returns None on any failure — all callers must handle None gracefully.
"""
import json
import logging
import os
import time

import requests

from backend.data_dragon import get_latest_version

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
CACHE_TTL = 86400  # 24 hours

ROLE_TO_LANE: dict[str, str] = {
    "TOP": "top",
    "JUNGLE": "jungle",
    "MIDDLE": "mid",
    "BOTTOM": "adc",
    "UTILITY": "support",
    "DEFAULT": "adc",
}

TIER_TO_SLUG: dict[str, str] = {
    "IRON": "iron_plus",
    "BRONZE": "bronze_plus",
    "SILVER": "silver_plus",
    "GOLD": "gold_plus",
    "PLATINUM": "platinum_plus",
    "EMERALD": "emerald_plus",
    "DIAMOND": "diamond_plus",
    "MASTER": "diamond_plus",
    "GRANDMASTER": "diamond_plus",
    "CHALLENGER": "diamond_plus",
    "DEFAULT": "gold_plus",
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


def _parse_patch(version: str) -> str:
    """Convert '15.8.1' → '15.8'."""
    parts = version.split(".")
    return f"{parts[0]}.{parts[1]}" if len(parts) >= 2 else version


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


def _safe_get(obj: dict, *keys):
    for key in keys:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def _parse_lolalytics(data: dict) -> dict | None:
    """Normalise a raw Lolalytics response into our standard meta dict."""
    try:
        # Win rate — Lolalytics nests it under head.wr (× or %) or stats.wr
        wr = _safe_get(data, "head", "wr")
        if wr is None:
            wr = _safe_get(data, "stats", "wr")
        if wr is None:
            wr = data.get("wr")
        if not isinstance(wr, (int, float)):
            return None
        # Lolalytics sometimes returns wr as a fraction (0.524), sometimes as percent
        if wr < 1:
            wr = wr * 100
        wr = round(float(wr), 1)

        # Best items
        best_items: list[dict] = []
        for key in ("best_items", "items", "item_sets", "best_item_sets"):
            raw = data.get(key)
            if isinstance(raw, list):
                for entry in raw[:6]:
                    if not isinstance(entry, dict):
                        continue
                    item_id = entry.get("id") or entry.get("item_id")
                    item_wr = entry.get("wr") or entry.get("win_rate") or wr
                    if item_id:
                        try:
                            best_items.append({"id": int(item_id), "wr": float(item_wr)})
                        except (TypeError, ValueError):
                            pass
                if best_items:
                    break

        # Keystone rune
        keystone: dict | None = None
        for key in ("best_runes", "runes", "rune_sets", "best_rune_sets"):
            raw = data.get(key)
            if isinstance(raw, list) and raw:
                first = raw[0]
                if isinstance(first, dict):
                    ks_id = first.get("keystone") or first.get("keystone_id") or first.get("id")
                    ks_wr = first.get("wr") or first.get("win_rate") or wr
                    if ks_id:
                        try:
                            keystone = {"id": int(ks_id), "wr": float(ks_wr)}
                        except (TypeError, ValueError):
                            pass
                break

        # Matchups (champion_name → {wr, games})
        matchups: dict[str, dict] = {}
        for key in ("vs", "matchups", "counters", "enemy"):
            raw = data.get(key)
            if isinstance(raw, dict):
                for enemy, stats in raw.items():
                    if not isinstance(stats, dict):
                        continue
                    m_wr = stats.get("wr") or stats.get("win_rate")
                    m_games = stats.get("n") or stats.get("games") or 0
                    if m_wr is not None:
                        try:
                            m_wr_f = float(m_wr)
                            if m_wr_f < 1:
                                m_wr_f *= 100
                            matchups[enemy] = {"wr": round(m_wr_f, 1), "games": int(m_games)}
                        except (TypeError, ValueError):
                            pass
                break

        return {
            "win_rate": wr,
            "tier": _tier_label(wr),
            "best_items": best_items,
            "keystone": keystone,
            "matchups": matchups,
        }
    except Exception as exc:
        logger.warning("Lolalytics parse error: %s", exc)
        return None


def get_champion_meta(champion_name: str, role: str, tier: str) -> dict | None:
    """
    Return meta stats for champion+role+tier. Cached 24h.
    Returns None if data is unavailable (caller must handle).
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    safe_name = champion_name.replace(" ", "").replace("'", "").replace(".", "")
    lane = ROLE_TO_LANE.get(role.upper(), "adc")
    tier_slug = TIER_TO_SLUG.get(tier.upper(), "gold_plus")
    cache_file = os.path.join(CACHE_DIR, f"{safe_name}_{lane}_{tier_slug}.json")

    # Serve from cache if fresh
    if os.path.exists(cache_file):
        age = time.time() - os.path.getmtime(cache_file)
        if age < CACHE_TTL:
            try:
                with open(cache_file) as f:
                    return json.load(f)
            except Exception:
                pass

    result: dict | None = None
    try:
        champ_ids = _get_champion_ids()
        champ_id = champ_ids.get(champion_name)
        if not champ_id:
            return None

        version = get_latest_version()
        patch = _parse_patch(version)

        url = (
            "https://lolalytics.com/mega/"
            f"?ep=champion&p=d&v=1&patch={patch}"
            f"&cid={champ_id}&lane={lane}&tier={tier_slug}&queue=420&region=all"
        )
        r = requests.get(
            url, timeout=8,
            headers={"User-Agent": "Mozilla/5.0 (compatible; CleverPachonc/1.0)"},
        )
        r.raise_for_status()
        result = _parse_lolalytics(r.json())
    except Exception as exc:
        logger.info("Meta fetch failed for %s (%s/%s): %s", champion_name, role, tier, exc)

    if result is not None:
        try:
            with open(cache_file, "w") as f:
                json.dump(result, f)
        except Exception:
            pass

    return result
