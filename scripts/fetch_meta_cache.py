"""
Meta cache builder — fetches champion pick rates from Meraki Analytics CDN.
Writes backend/meta_cache.json for use by the /api/tierlist endpoint.

Data source: https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/championrates.json
Patch version is always fetched dynamically from Riot's Data Dragon API.
"""
import json
import os
import sys

import requests

MERAKI_URL = "https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/championrates.json"

MERAKI_ROLE_TO_LANE: dict[str, str] = {
    "TOP": "top",
    "JUNGLE": "jungle",
    "MIDDLE": "mid",
    "BOTTOM": "adc",
    "UTILITY": "support",
}

OUT_FILE = os.path.join(os.path.dirname(__file__), "..", "backend", "meta_cache.json")

# Minimum pick rate % to include in cache (filters out zero-play off-meta entries)
MIN_PICK_RATE = 0.1


def get_ddragon_data() -> tuple[dict[str, str], str]:
    """Returns {numeric_champion_id: ddragon_name} and latest patch string."""
    r = requests.get(
        "https://ddragon.leagueoflegends.com/api/versions.json", timeout=8
    )
    r.raise_for_status()
    version = r.json()[0]

    r = requests.get(
        f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json",
        timeout=8,
    )
    r.raise_for_status()
    data = r.json()["data"]
    id_to_name = {info["key"]: name for name, info in data.items()}
    print(f"Loaded {len(id_to_name)} champions from Data Dragon (patch {version})")
    return id_to_name, version


def parse_patch(version: str) -> str:
    parts = version.split(".")
    return f"{parts[0]}.{parts[1]}"


def main() -> None:
    id_to_name, version = get_ddragon_data()
    patch = parse_patch(version)
    print(f"Building meta cache for patch {patch}")

    r = requests.get(MERAKI_URL, timeout=10)
    r.raise_for_status()
    meraki_data = r.json()
    champ_rates = meraki_data.get("data", {})
    print(f"Fetched Meraki data for {len(champ_rates)} champions")

    cache: dict = {}

    for champ_id_str, roles in champ_rates.items():
        name = id_to_name.get(str(champ_id_str))
        if not name:
            continue
        for meraki_role, stats in roles.items():
            lane = MERAKI_ROLE_TO_LANE.get(meraki_role)
            if not lane:
                continue
            play_rate_raw = float(stats.get("playRate", 0))
            if play_rate_raw < MIN_PICK_RATE:
                continue
            pick_rate = round(play_rate_raw, 1)
            key = f"{name}_{lane}"
            cache[key] = {
                "win_rate": None,
                "tier": None,
                "pick_rate": pick_rate,
                "ban_rate": None,
                "keystone_id": None,
                "best_items": [],
                "matchups": {},
            }

    print(f"Built {len(cache)} champion-lane entries")

    if not cache:
        print("ERROR: No data fetched — aborting to preserve existing cache")
        sys.exit(1)

    out_path = os.path.abspath(OUT_FILE)
    with open(out_path, "w") as f:
        json.dump({"patch": patch, "data": cache}, f, indent=2)
    print(f"Written to {out_path}")


if __name__ == "__main__":
    main()
