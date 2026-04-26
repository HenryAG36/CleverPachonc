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
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from backend.riot_api import get_summoner_data_async
from backend.data_dragon import get_champion_map, get_item_data, get_latest_version, get_rune_tree
from backend.analysis.match_analysis import analyze_match_history
from backend.analysis.champion_stats import analyze_champion_stats
from backend.ai_coach import generate_coaching

try:
    from backend.analysis.meta_analysis import analyze_meta_gaps as _analyze_meta_gaps
    _META_AVAILABLE = True
except Exception:
    _META_AVAILABLE = False
from backend.utils.exceptions import (
    APIError, AuthError, ConfigError, NetworkError, NotFoundError, RateLimitError,
)

app = Flask(__name__)
CORS(app)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Module-level cache — reused across warm invocations on Vercel
_champion_map = None
_item_data = None
_rune_tree = None


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


def _get_rune_tree():
    global _rune_tree
    if _rune_tree is None:
        _rune_tree = get_rune_tree()
    return _rune_tree


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
    RANKED_QUEUES = {420, 440}  # solo, flex — filter everything else

    formatted_matches = []
    for match in matches:
        queue_id = match["info"].get("queueId", 0)
        if queue_id not in RANKED_QUEUES:
            continue
        try:
            p = next(x for x in match["info"]["participants"] if x["puuid"] == puuid)
        except StopIteration:
            continue

        champ_id = str(p["championId"])
        player_position = p.get("teamPosition", "")

        enemy_carry = None
        if player_position:
            enemy_carry = next(
                (
                    champion_map.get(str(x["championId"]), "Unknown")
                    for x in match["info"]["participants"]
                    if x["teamId"] != p["teamId"] and x.get("teamPosition") == player_position
                ),
                None,
            )

        # Build full 10-player scoreboard (no rank — avoids 10 extra API calls on personal key)
        all_participants = []
        for part in match["info"]["participants"]:
            pid = str(part["championId"])
            all_participants.append({
                "puuid": part.get("puuid", ""),
                "riotIdGameName": part.get("riotIdGameName") or part.get("summonerName", ""),
                "riotIdTagline": part.get("riotIdTagline", ""),
                "championName": champion_map.get(pid, "Unknown"),
                "championId": part["championId"],
                "teamId": part["teamId"],
                "teamPosition": part.get("teamPosition", ""),
                "kills": part["kills"],
                "deaths": part["deaths"],
                "assists": part["assists"],
                "damage": part.get("totalDamageDealtToChampions", 0),
                "gold": part.get("goldEarned", 0),
                "cs": part.get("totalMinionsKilled", 0) + part.get("neutralMinionsKilled", 0),
                "items": [part.get(f"item{i}", 0) for i in range(7)],
                "perks": part.get("perks", {}),
                "win": part["win"],
            })

        formatted_matches.append({
            "matchId": match["metadata"]["matchId"],
            "queueId": queue_id,
            "champion": champion_map.get(champ_id, "Unknown"),
            "championId": p["championId"],
            "win": p["win"],
            "result": "Victory" if p["win"] else "Defeat",
            "kills": p["kills"],
            "deaths": p["deaths"],
            "assists": p["assists"],
            "cs": p.get("totalMinionsKilled", 0) + p.get("neutralMinionsKilled", 0),
            "duration": match["info"]["gameDuration"] // 60,
            "role": player_position,
            "items": [p.get(f"item{i}", 0) for i in range(7)],
            "enemy_carry": enemy_carry,
            "participants": all_participants,
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

    # Best-effort meta pre-analysis for PreSessionCard (no API cost, uses cache)
    meta_summary: dict | None = None
    if _META_AVAILABLE and champ_stats:
        try:
            solo = next((q for q in ranked if q.get("queueType") == "RANKED_SOLO_5x5"), None)
            tier = solo.get("tier", "DEFAULT") if solo else "DEFAULT"
            meta_summary = _analyze_meta_gaps(champ_stats, serialised_analysis, formatted_matches, tier)
        except Exception:
            pass

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
        "meta": meta_summary,
        "rune_tree": _get_rune_tree(),
    })


@app.route("/api/coach", methods=["POST"])
def coach():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "JSON body required"}), 400
    try:
        result = generate_coaching(payload)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Coach error: {e}"}), 500


@app.route("/api/match/timeline")
def match_timeline():
    match_id = request.args.get("id", "").strip()
    region = request.args.get("region", "NA").strip()
    puuid = request.args.get("puuid", "").strip()

    if not match_id or not puuid:
        return jsonify({"error": "id and puuid required"}), 400

    from backend.utils.constants import MATCH_ROUTING, get_api_key
    import aiohttp
    from backend.riot_api import _get

    routing = MATCH_ROUTING.get(region.upper(), "americas")
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key not configured"}), 500

    async def _fetch():
        async with aiohttp.ClientSession() as session:
            return await _get(
                session,
                f"https://{routing}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline",
                {"X-Riot-Token": api_key},
            )

    try:
        timeline = asyncio.run(_fetch())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    if not timeline:
        return jsonify({"ward_events": []})

    # Find the player's participantId from timeline metadata
    participants_meta = timeline.get("info", {}).get("participants", [])
    player_pid = next(
        (p["participantId"] for p in participants_meta if p.get("puuid") == puuid),
        None,
    )

    ward_events = []
    for frame in timeline.get("info", {}).get("frames", []):
        for event in frame.get("events", []):
            if event.get("type") != "WARD_PLACED":
                continue
            pos = event.get("position", {})
            if not pos:
                continue
            creator_id = event.get("creatorId")
            if player_pid is not None and creator_id != player_pid:
                continue
            ward_events.append({
                "x": pos["x"],
                "y": pos["y"],
                "type": event.get("wardType", "UNKNOWN"),
                "t": event.get("timestamp", 0),
            })

    return jsonify({"ward_events": ward_events})


@app.route("/api/coach/match", methods=["POST"])
def coach_match():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "JSON body required"}), 400
    try:
        from backend.ai_coach import generate_match_coaching
        result = generate_match_coaching(
            payload.get("match", {}),
            payload.get("player_puuid", ""),
            payload.get("ranked", []),
        )
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": f"Coach error: {exc}"}), 500


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
