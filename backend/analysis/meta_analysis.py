"""
Compare player data against the current patch meta.
All public functions return gracefully when meta data is unavailable.
"""
from __future__ import annotations

import logging
from typing import Any

from .meta_fetcher import get_champion_meta

logger = logging.getLogger(__name__)

MIN_GAMES = 3
TILT_THRESHOLD = 3  # consecutive losses before flagging


def _consecutive_losses(matches: list[dict]) -> int:
    """Count losses from the start of match list (most-recent first)."""
    count = 0
    for m in matches:
        if not m.get("win", True):
            count += 1
        else:
            break
    return count


def _build_gap(player_items: list[dict], meta_items: list[dict]) -> list[dict]:
    """Return meta items the player didn't build (up to 2 suggestions)."""
    if not player_items or not meta_items:
        return []
    player_ids = {item["item_id"] for item in player_items if item.get("item_id")}
    gaps = [m for m in meta_items[:6] if m.get("id") not in player_ids]
    return gaps[:2]


def _losses_per_enemy(matches: list[dict]) -> dict[str, int]:
    """Count how many times the player lost against each enemy carry."""
    tally: dict[str, int] = {}
    for m in matches:
        if not m.get("win", True):
            enemy = m.get("enemy_carry")
            if enemy and enemy != "Unknown":
                tally[enemy] = tally.get(enemy, 0) + 1
    return tally


def analyze_meta_gaps(
    champion_stats: dict[str, Any],
    match_analysis: dict,
    matches: list[dict],
    tier: str,
) -> dict:
    """
    Return meta-context dict for use in coaching findings.

    Keys:
        per_champ_meta  – {champion: {meta_wr, tier, build_gaps, worst_matchups}}
        matchup_insights – [{enemy, losses, meta_wr}] from player history
        meta_picks       – [{name, wr, tier, role}] top champs by meta WR
        tilt_flag        – bool
        consecutive_losses – int
    """
    tilt_count = _consecutive_losses(matches)

    # Primary role
    role_prefs: dict[str, float] = match_analysis.get("role_preferences", {})
    primary_role = max(role_prefs, key=role_prefs.get) if role_prefs else "DEFAULT"

    per_champ_meta: dict[str, dict] = {}
    meta_wrs: list[tuple[str, float, str, str]] = []  # (name, wr, tier, role)

    for champ_name, stats in champion_stats.items():
        if stats.get("games", 0) < MIN_GAMES:
            continue
        role = stats.get("main_role", primary_role) or primary_role
        try:
            meta = get_champion_meta(champ_name, role, tier)
        except Exception as exc:
            logger.debug("Meta fetch error for %s: %s", champ_name, exc)
            meta = None
        if not meta:
            continue

        build_gaps = _build_gap(stats.get("core_items", []), meta.get("best_items", []))

        worst_matchups = sorted(
            meta.get("matchups", {}).items(),
            key=lambda kv: kv[1]["wr"],
        )[:3]

        per_champ_meta[champ_name] = {
            "meta_wr": meta["win_rate"],
            "tier": meta["tier"],
            "build_gaps": build_gaps,
            "keystone": meta.get("keystone"),
            "worst_matchups": [
                {"enemy": k, "meta_wr": v["wr"]} for k, v in worst_matchups
            ],
        }
        meta_wrs.append((champ_name, meta["win_rate"], meta["tier"], role))

    # Matchup insights: recurring losses cross-referenced with meta data
    losses_vs = _losses_per_enemy(matches)
    matchup_insights: list[dict] = []
    for enemy, losses in sorted(losses_vs.items(), key=lambda kv: -kv[1])[:3]:
        if losses < 2:
            continue
        meta_wr: float | None = None
        for champ_meta in per_champ_meta.values():
            for mu in champ_meta.get("worst_matchups", []):
                if mu["enemy"].lower() == enemy.lower():
                    meta_wr = mu["meta_wr"]
                    break
            if meta_wr is not None:
                break
        matchup_insights.append({"enemy": enemy, "losses": losses, "meta_wr": meta_wr})

    # Top 3 champions from the player's pool by meta WR
    meta_picks = [
        {"name": n, "wr": w, "tier": t, "role": r}
        for n, w, t, r in sorted(meta_wrs, key=lambda x: -x[1])[:3]
    ]

    return {
        "per_champ_meta": per_champ_meta,
        "matchup_insights": matchup_insights,
        "meta_picks": meta_picks,
        "tilt_flag": tilt_count >= TILT_THRESHOLD,
        "consecutive_losses": tilt_count,
    }
