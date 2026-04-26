"""
Daily meta cache builder — runs from GitHub Actions (not Vercel cloud IPs).
Fetches champion tier data from Lolalytics and writes backend/meta_cache.json.
Vercel reads the committed file at runtime instead of hitting Lolalytics live.

Patch version is always fetched dynamically from Riot's Data Dragon API.
"""
import json
import os
import sys
import time

import requests

CHAMPIONS_BY_ROLE: dict[str, list[str]] = {
    "adc": [
        "Jinx", "Caitlyn", "Jhin", "Ezreal", "KaiSa", "Ashe", "Varus",
        "Sivir", "Lucian", "MissFortune", "Twitch", "Draven", "Tristana",
        "Xayah", "Zeri", "Samira", "Smolder", "Nilah", "Aphelios", "KogMaw",
        "Kalista", "Vayne", "Corki", "Senna", "Seraphine", "Ziggs",
        "Heimerdinger", "Yasuo", "Cassiopeia",
    ],
    "mid": [
        "Yasuo", "Zed", "Ahri", "Lux", "Syndra", "Viktor", "Orianna",
        "Fizz", "Katarina", "Akali", "Vex", "Cassiopeia", "Yone", "Qiyana",
        "Naafiri", "Hwei", "Aurora", "Azir", "Galio", "Malzahar", "Veigar",
        "TwistedFate", "Annie", "Ekko", "Talon", "LeBlanc", "Sylas", "Corki",
        "Anivia", "Diana", "Irelia", "Jayce", "Lissandra", "Neeko",
        "Pantheon", "Ryze", "Vladimir", "Xerath", "Zoe", "AurelionSol",
    ],
    "top": [
        "Darius", "Garen", "Fiora", "Camille", "Mordekaiser", "Sett",
        "Irelia", "Renekton", "Teemo", "Malphite", "Aatrox", "Jax",
        "Gwen", "Volibear", "Ambessa", "Kennen", "Nasus", "Ornn",
        "Chogath", "Kayle", "Tryndamere", "Urgot", "Wukong", "Yasuo",
        "Gangplank", "Illaoi", "Maokai", "Pantheon", "Riven", "Shen",
        "Singed", "TahmKench", "Trundle", "Vayne", "Yorick", "Jayce",
    ],
    "jungle": [
        "Vi", "LeeSin", "Hecarim", "Amumu", "Ekko", "Kindred", "Nunu",
        "Viego", "Kayn", "Warwick", "Lillia", "Briar", "Nocturne", "Graves",
        "Nidalee", "Shaco", "Elise", "Evelynn", "JarvanIV", "Khazix",
        "Rengar", "Sejuani", "Udyr", "XinZhao", "Diana", "Fiddlesticks",
        "Ivern", "Rammus", "Shyvana", "Talon", "Wukong", "Zac", "Zyra",
        "Poppy", "Skarner", "Volibear",
    ],
    "support": [
        "Thresh", "Lulu", "Nautilus", "Leona", "Janna", "Soraka", "Alistar",
        "Blitzcrank", "Zyra", "Senna", "Milio", "Seraphine", "Karma", "Renata",
        "Bard", "Brand", "Pyke", "Rakan", "Swain", "Xerath", "Zilean",
        "Nami", "Lux", "Morgana", "Yuumi", "Amumu", "Braum", "Pantheon",
        "Velkoz", "Shaco", "Sona",
    ],
}

# Keystone rune IDs — used to identify the keystone from Lolalytics rune data
KEYSTONES = {
    8005, 8008, 8021, 8010,   # Precision
    8112, 8124, 8128, 9923,   # Domination
    8214, 8229, 8230,          # Sorcery
    8437, 8439, 8465,          # Resolve
    8351, 8360, 8369,          # Inspiration
}

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


def get_champion_ids() -> tuple[dict[str, str], str]:
    """Fetch champion name → numeric ID and latest patch version from Data Dragon."""
    r = requests.get(
        "https://ddragon.leagueoflegends.com/api/versions.json", timeout=8
    )
    version = r.json()[0]  # always the latest released patch
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


def _normalise_rate(val) -> float | None:
    if val is None:
        return None
    f = float(val)
    return round(f * 100 if f < 1 else f, 1)


def fetch_champion(champ: str, champ_id: str, lane: str, tier_slug: str) -> dict | None:
    tier_simple = tier_slug.replace("_plus", "")
    url_variants = [
        f"https://lolalytics.com/mega/?ep=champion&p=d&v=1&cid={champ_id}&lane={lane}&tier={tier_slug}&queue=420&region=all",
        f"https://lolalytics.com/mega/?ep=champion&p=d&v=1&cid={champ_id}&lane={lane}&tier={tier_simple}&queue=420&region=all",
        f"https://lolalytics.com/mega/?ep=champion&p=d&v=2&cid={champ_id}&lane={lane}&tier={tier_slug}&queue=420&region=all",
        f"https://lolalytics.com/mega/?ep=champion&p=d&v=2&cid={champ_id}&lane={lane}&tier={tier_simple}&queue=420&region=all",
        f"https://lolalytics.com/mega/?ep=champion&p=d&v=1&patch=0&cid={champ_id}&lane={lane}&tier={tier_slug}&queue=420&region=all",
        f"https://lolalytics.com/mega/?ep=champion&p=d&v=1&cid={champ_id}&lane={lane}&queue=420&region=all",
    ]

    for i, url in enumerate(url_variants):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 403:
                print(f"  403 blocked — {champ}")
                return None
            if r.status_code != 200:
                continue

            data = r.json()
            head = data.get("head", {})

            wr = head.get("wr") or data.get("wr")
            if wr is None:
                continue
            wr = float(wr)
            if wr < 1:
                wr *= 100
            wr = round(wr, 1)

            pick_rate = _normalise_rate(head.get("pick") or data.get("pick") or head.get("pr"))
            ban_rate  = _normalise_rate(head.get("ban")  or data.get("ban")  or head.get("br"))

            # Keystone: find the keystone rune with most games in response
            keystone_id: int | None = None
            for rune_key in ("rune", "runes"):
                rune_data = data.get(rune_key)
                if not isinstance(rune_data, dict):
                    continue
                ks_candidates = []
                for rid, stats in rune_data.items():
                    try:
                        rid_int = int(rid)
                    except (ValueError, TypeError):
                        continue
                    if rid_int in KEYSTONES and isinstance(stats, dict):
                        ks_candidates.append((rid_int, stats.get("n", 0)))
                if ks_candidates:
                    keystone_id = max(ks_candidates, key=lambda x: x[1])[0]
                break

            # Items: try multiple response key names, prefer dict keyed by item ID
            best_items: list[dict] = []
            for item_key in ("items", "item_sets", "best_items", "item3"):
                raw = data.get(item_key)
                if isinstance(raw, dict) and raw:
                    sorted_items = sorted(
                        raw.items(),
                        key=lambda x: x[1].get("n", 0) if isinstance(x[1], dict) else 0,
                        reverse=True,
                    )
                    for item_id_str, stats in sorted_items[:6]:
                        if not str(item_id_str).isdigit():
                            continue
                        iwr = float(stats.get("wr", 0)) if isinstance(stats, dict) else 0
                        if iwr < 1:
                            iwr *= 100
                        best_items.append({"id": int(item_id_str), "wr": round(iwr, 1)})
                    if best_items:
                        break
                elif isinstance(raw, list):
                    for entry in raw[:6]:
                        if not isinstance(entry, dict):
                            continue
                        iid = entry.get("id") or entry.get("item_id")
                        iwr = float(entry.get("wr") or entry.get("win_rate") or 0)
                        if iid:
                            if iwr < 1:
                                iwr *= 100
                            best_items.append({"id": int(iid), "wr": round(iwr, 1)})
                    if best_items:
                        break

            matchups: dict = {}
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
                            matchups[enemy] = {
                                "wr": round(mf, 1),
                                "games": int(stats.get("n") or stats.get("games") or 0),
                            }
                    break

            return {
                "win_rate": wr,
                "tier": tier_label(wr),
                "pick_rate": pick_rate,
                "ban_rate": ban_rate,
                "keystone_id": keystone_id,
                "best_items": best_items,
                "matchups": matchups,
            }

        except Exception as exc:
            print(f"  Error {champ} {lane} variant {i + 1}: {exc}")

    print(f"  All variants failed for {champ} {lane}")
    return None


def main():
    champ_ids, version = get_champion_ids()
    patch = parse_patch(version)
    print(f"Building meta cache for patch {patch}")

    cache: dict = {}
    total = sum(len(v) for v in CHAMPIONS_BY_ROLE.values())
    done = 0
    errors = 0

    for lane, champs in CHAMPIONS_BY_ROLE.items():
        for champ in champs:
            cid = champ_ids.get(champ)
            ddragon_name = champ
            if not cid:
                alt = champ.replace("'", "").replace(" ", "")
                cid = champ_ids.get(alt)
                if cid:
                    ddragon_name = alt
            if not cid:
                print(f"  Unknown champion: {champ}")
                continue

            result = fetch_champion(ddragon_name, cid, lane, "gold_plus")
            if result:
                key = f"{ddragon_name}_{lane}"
                cache[key] = result
                print(
                    f"  OK {ddragon_name} {lane}: {result['tier']} {result['win_rate']}% "
                    f"pick={result['pick_rate']} ban={result['ban_rate']} ks={result['keystone_id']}"
                )
            else:
                errors += 1

            done += 1
            if done % 10 == 0:
                print(f"Progress: {done}/{total} ({errors} errors)")
            time.sleep(0.15)

    print(f"\nFetched {len(cache)} entries ({errors} failed)")

    if not cache:
        print("WARNING: No data fetched — keeping existing meta_cache.json unchanged")
        sys.exit(0)

    out_path = os.path.abspath(OUT_FILE)
    with open(out_path, "w") as f:
        json.dump({"patch": patch, "data": cache}, f, indent=2)
    print(f"Written to {out_path} (patch {patch})")


if __name__ == "__main__":
    main()
