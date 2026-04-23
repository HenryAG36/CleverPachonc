"""
Vercel serverless entry point.

Flask is detected automatically by Vercel's Python runtime as a WSGI app.
The async Riot API calls run inside asyncio.run() so they don't conflict
with Flask's synchronous request handling.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from backend.riot_api import get_summoner_data_async
from backend.data_dragon import get_champion_map, get_item_data, get_latest_version
from backend.analysis.match_analysis import analyze_match_history
from backend.analysis.champion_stats import analyze_champion_stats
from backend.utils.exceptions import (
    APIError, AuthError, ConfigError, NetworkError, NotFoundError, RateLimitError,
)

app = Flask(__name__)
CORS(app)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Module-level cache — reused across warm invocations on Vercel
_champion_map = None
_item_data = None


def _get_champion_map():
    global _champion_map
    if _champion_map is None:
        _champion_map = get_champion_map()
    return _champion_map


def _get_item_data():
    global _item_data
    if _item_data is None:
        _item_data = get_item_data()
    return _item_data


@app.route("/api/summoner")
def summoner():
    name = request.args.get("name", "").strip()
    region = request.args.get("region", "NA").strip()

    if not name:
        return jsonify({"error": "name is required"}), 400
    if "#" not in name:
        return jsonify({"error": "Use Riot ID format: Name#TAG"}), 400

    try:
        summoner_data, ranked, mastery, matches = asyncio.run(
            get_summoner_data_async(name, region)
        )
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except RateLimitError:
        return jsonify({"error": "Rate limit exceeded — please wait and try again."}), 429
    except AuthError:
        return jsonify({"error": "Server API key is invalid or expired."}), 401
    except ConfigError as e:
        return jsonify({"error": str(e)}), 500
    except NetworkError as e:
        return jsonify({"error": f"Network error: {e}"}), 502
    except APIError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500

    champion_map = _get_champion_map() or {}
    item_data = _get_item_data() or {}
    dd_version = get_latest_version()
    puuid = summoner_data["puuid"]

    # ── Format mastery (resolve champion names server-side) ──────────
    formatted_mastery = []
    for champ in mastery[:5]:
        champ_id = str(champ["championId"])
        champ_name = champion_map.get(champ_id)
        if not champ_name:
            continue
        last_played = None
        if "lastPlayTime" in champ:
            last_played = datetime.fromtimestamp(
                champ["lastPlayTime"] / 1000, tz=timezone.utc
            ).strftime("%Y-%m-%d")
        formatted_mastery.append({
            "championName": champ_name,
            "championId": champ["championId"],
            "championLevel": champ["championLevel"],
            "championPoints": champ["championPoints"],
            "lastPlayTime": last_played,
        })

    # ── Format match list ────────────────────────────────────────────
    formatted_matches = []
    for match in matches:
        try:
            p = next(x for x in match["info"]["participants"] if x["puuid"] == puuid)
        except StopIteration:
            continue
        champ_id = str(p["championId"])
        formatted_matches.append({
            "champion": champion_map.get(champ_id, "Unknown"),
            "championId": p["championId"],
            "win": p["win"],
            "result": "Victory" if p["win"] else "Defeat",
            "kills": p["kills"],
            "deaths": p["deaths"],
            "assists": p["assists"],
            "cs": p["totalMinionsKilled"] + p.get("neutralMinionsKilled", 0),
            "duration": match["info"]["gameDuration"] // 60,
            "role": p.get("teamPosition", ""),
            "items": [p.get(f"item{i}", 0) for i in range(7)],
        })

    # ── Run analysis on raw match data ───────────────────────────────
    match_analysis = analyze_match_history(matches, puuid) if matches else {}
    champ_stats_raw = analyze_champion_stats(matches, puuid) if matches else {}

    # Serialise champion_stats (core_items contains tuples → convert to lists)
    champ_stats = {}
    for champ_name, stats in champ_stats_raw.items():
        champ_stats[champ_name] = {
            **{k: v for k, v in stats.items() if k != "core_items"},
            "core_items": [
                {"item_id": item_id, "count": count}
                for item_id, count in (stats.get("core_items") or [])
            ],
        }

    # Serialise match_analysis (drop raw list fields not needed by frontend)
    serialised_analysis = {
        k: v for k, v in match_analysis.items()
        if k not in ("game_durations", "recent_performance")
    }

    return jsonify({
        "dd_version": dd_version,
        "summoner": {
            "gameName": summoner_data.get("gameName", name.split("#")[0]),
            "tagLine": summoner_data.get("tagLine", ""),
            "summonerLevel": summoner_data.get("summonerLevel", 0),
            "profileIconId": summoner_data.get("profileIconId", 0),
        },
        "ranked": ranked,
        "mastery": formatted_mastery,
        "matches": formatted_matches,
        "champion_stats": champ_stats,
        "match_analysis": serialised_analysis,
    })


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if not os.path.isdir(STATIC_DIR):
        return "Frontend not built", 404
    file_path = os.path.join(STATIC_DIR, path)
    if path and os.path.isfile(file_path):
        return send_from_directory(STATIC_DIR, path)
    # Return 404 for missing assets (e.g. .js/.css) instead of falling back
    # to index.html — prevents wrong MIME type being served and cached.
    if path and "." in os.path.basename(path):
        return "Not found", 404
    return send_from_directory(STATIC_DIR, "index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
