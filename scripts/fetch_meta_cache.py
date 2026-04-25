"""
Daily meta cache builder — runs from GitHub Actions (not Vercel cloud IPs).
Fetches champion tier data from Lolalytics and writes backend/meta_cache.json.
Vercel reads the committed file at runtime instead of hitting Lolalytics live.
"""
import json
import os
import sys
import time

import requests

# Champions to fetch per role — top players in each lane by play rate.
# Update this list when new champions are added or the meta shifts significantly.
CHAMPIONS_BY_ROLE: dict[str, list[str]] = {
    "adc": [
        "Jinx", "Caitlyn", "Jhin", "Ezreal", "Kai'Sa", "Ashe", "Varus",
        "Sivir", "Lucian", "MissFortune", "Twitch", "Draven", "Tristana",
        "Xayah", "Zeri", "Samira", "Smolder", "Nilah", "Aphelios", "Kog'Maw",
    ],
    "mid": [
        "Yasuo", "Zed", "Ahri", "Lux", "Syndra", "Viktor", "Orianna",
        "Fizz", "Katarina", "Akali", "Vex", "Cassiopeia", "Yone", "Qiyana",
        "Naafiri", "Hwei", "Aurora",
    ],
    "top": [
        "Darius", "Garen", "Fiora", "Camille", "Mordekaiser", "Sett",
        "Irelia", "Renekton", "Teemo", "Malphite", "Aatrox", "Jax",
        "Gwen", "Volibear", "Ambessa",
    ],
    "jungle": [
        "Vi", "LeeSin", "Hecarim", "Amumu", "Ekko", "Kindred", "Nunu",
        "Viego", "Kayn", "Warwick", "Lillia", "Briar", "Nocturne", "Zyra",
    ],
    "support": [
        "Thresh", "Lulu", "Nautilus", "Leona", "Janna", "Soraka", "Alistar",
        "Blitzcrank", "Zyra", "Senna", "Milio", "Seraphine", "Karma", "Renata",
    ],
}

TIER_SLUGS = ["gold_plus", "platinum_plus", "diamond_plus"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://lolalytics.com/",
    "Origin": "https://lolalytics.com",
}

OUT_FILE = os.path.join(os.path.dirname(__file__), "..", "backend", "meta_cache.json")


def get_champion_ids() -> dict[str, str]:
    """Fetch champion name → numeric ID from Data Dragon."""
    r = requests.get(
        "https://ddragon.leagueoflegends.com/api/versions.json", timeout=8
    )
    version = r.json()[0]
    r = requests.get(
        f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json",
        timeout=8,
    )
    data = r.json()["data"]
    ids = {name: info["key"] for name, info in data.items()}
    print(f"Loaded {len(ids)} champion IDs (patch {version})")
    return ids, version


def parse_patch(version: str) -> str:
    parts = version.split(".")
    return f"{parts[0]}.{parts[1]}"


def tier_label(wr: float) -> str:
    if wr >= 54:
        return "OP"
    if wr >= 52:
        return "S"
    if wr >= 50:
        return "A"
    if wr >= 48:
        return "B"
    return "C"


def fetch_champion(champ: str, champ_id: str, lane: str, tier_slug: str, patch: str) -> dict | None:
    # Try URL variants in order — Lolalytics changes API format between patches.
    # No-patch URL uses the current patch by default.
    tier_simple = tier_slug.replace("_plus", "")  # gold_plus → gold
    url_variants = [
        # v1 no-patch (current)
        f"https://lolalytics.com/mega/?ep=champion&p=d&v=1&cid={champ_id}&lane={lane}&tier={tier_slug}&queue=420&region=all",
        # v1 with tier without _plus suffix
        f"https://lolalytics.com/mega/?ep=champion&p=d&v=1&cid={champ_id}&lane={lane}&tier={tier_simple}&queue=420&region=all",
        # v2 variants
        f"https://lolalytics.com/mega/?ep=champion&p=d&v=2&cid={champ_id}&lane={lane}&tier={tier_slug}&queue=420&region=all",
        f"https://lolalytics.com/mega/?ep=champion&p=d&v=2&cid={champ_id}&lane={lane}&tier={tier_simple}&queue=420&region=all",
        # patch=0 (all patches)
        f"https://lolalytics.com/mega/?ep=champion&p=d&v=1&patch=0&cid={champ_id}&lane={lane}&tier={tier_slug}&queue=420&region=all",
        # explicit patch version
        f"https://lolalytics.com/mega/?ep=champion&p=d&v=1&patch={patch}&cid={champ_id}&lane={lane}&tier={tier_slug}&queue=420&region=all",
        # no tier parameter
        f"https://lolalytics.com/mega/?ep=champion&p=d&v=1&cid={champ_id}&lane={lane}&queue=420&region=all",
    ]
    for i, url in enumerate(url_variants):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if champ == "Jinx":
                print(f"  [probe] variant {i+1} → HTTP {r.status_code}")
            if r.status_code == 403:
                print(f"  403 blocked on all variants for {champ}")
                return None
            if r.status_code != 200:
                continue  # try next variant
            r.raise_for_status()

            data = r.json()
            # Print keys on first success to help debug format changes
            if champ == "Jinx":
                print(f"  [debug] Jinx response keys: {list(data.keys())[:12]}")

            wr = data.get("head", {}).get("wr") or data.get("wr")
            if wr is None:
                print(f"  No WR field for {champ} {lane} — keys: {list(data.keys())[:8]}")
                continue  # try next variant

            if wr < 1:
                wr *= 100
            wr = round(float(wr), 1)

            # Items
            best_items: list[dict] = []
            for key in ("best_items", "items", "item_sets"):
                raw = data.get(key)
                if isinstance(raw, list):
                    for entry in raw[:6]:
                        if not isinstance(entry, dict):
                            continue
                        iid = entry.get("id") or entry.get("item_id")
                        iwr = entry.get("wr") or entry.get("win_rate") or wr
                        if iid:
                            best_items.append({"id": int(iid), "wr": float(iwr)})
                    if best_items:
                        break

            # Matchups
            matchups: dict[str, dict] = {}
            for key in ("vs", "matchups", "counters"):
                raw = data.get(key)
                if isinstance(raw, dict):
                    for enemy, stats in raw.items():
                        if not isinstance(stats, dict):
                            continue
                        m_wr = stats.get("wr") or stats.get("win_rate")
                        if m_wr is not None:
                            mf = float(m_wr)
                            if mf < 1:
                                mf *= 100
                            matchups[enemy] = {"wr": round(mf, 1), "games": int(stats.get("n") or stats.get("games") or 0)}
                    break

            return {
                "win_rate": wr,
                "tier": tier_label(wr),
                "best_items": best_items,
                "matchups": matchups,
            }
        except Exception as exc:
            print(f"  Error {champ} {lane} {tier_slug} ({url.split('?')[0]}...): {exc}")

    print(f"  All variants failed for {champ} {lane}")
    return None


def main():
    champ_ids, version = get_champion_ids()
    patch = parse_patch(version)

    cache: dict = {}
    total = sum(len(v) for v in CHAMPIONS_BY_ROLE.values())
    done = 0
    errors = 0

    for lane, champs in CHAMPIONS_BY_ROLE.items():
        for champ in champs:
            cid = champ_ids.get(champ)
            if not cid:
                # Try alternate name format (e.g. "Kai'Sa" → "KaiSa")
                alt = champ.replace("'", "").replace(" ", "")
                cid = champ_ids.get(alt)
                if not cid:
                    print(f"  Unknown champion: {champ}")
                    continue

            # Fetch gold+ as primary tier; others as bonus
            result = fetch_champion(champ, cid, lane, "gold_plus", patch)
            if result:
                key = f"{champ}_{lane}"
                cache[key] = result
                print(f"  OK {champ} {lane}: {result['tier']} {result['win_rate']}%")
            else:
                errors += 1

            done += 1
            if done % 10 == 0:
                print(f"Progress: {done}/{total} ({errors} errors)")
            time.sleep(0.15)  # be polite to Lolalytics

    print(f"\nFetched {len(cache)} entries ({errors} failed)")

    if not cache:
        print("WARNING: No data fetched — keeping existing meta_cache.json unchanged")
        sys.exit(0)

    out_path = os.path.abspath(OUT_FILE)
    with open(out_path, "w") as f:
        json.dump({"patch": patch, "data": cache}, f, indent=2)
    print(f"Written to {out_path}")


if __name__ == "__main__":
    main()
