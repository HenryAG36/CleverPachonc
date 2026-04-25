from typing import Optional, Dict, Any
import requests
from .utils.constants import REQUEST_TIMEOUT

_cached_version: Optional[str] = None
_FALLBACK_VERSION = "14.22.1"


def get_latest_version() -> str:
    global _cached_version
    if _cached_version:
        return _cached_version
    try:
        r = requests.get(
            "https://ddragon.leagueoflegends.com/api/versions.json",
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        _cached_version = r.json()[0]
        return _cached_version
    except Exception:
        return _FALLBACK_VERSION


def get_champion_map() -> Optional[Dict[str, str]]:
    """Return champion key → name mapping."""
    version = get_latest_version()
    try:
        r = requests.get(
            f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json",
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()["data"]
        return {info["key"]: name for name, info in data.items()}
    except Exception:
        return None


def get_item_data() -> Optional[Dict[str, Any]]:
    version = get_latest_version()
    try:
        r = requests.get(
            f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json",
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def get_rune_data() -> Optional[Dict[str, Any]]:
    """Return runesReforged data keyed by rune ID for fast lookup."""
    version = get_latest_version()
    try:
        r = requests.get(
            f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/runesReforged.json",
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        runes: Dict[str, Any] = {}
        for path in r.json():
            for slot in path.get("slots", []):
                for rune in slot.get("runes", []):
                    runes[str(rune["id"])] = {
                        "name": rune["name"],
                        "icon": rune["icon"],
                        "path": path["name"],
                    }
            # Include keystone entries at path level too
            runes[str(path["id"])] = {
                "name": path["name"],
                "icon": path["icon"],
                "path": path["name"],
            }
        return runes
    except Exception:
        return None
