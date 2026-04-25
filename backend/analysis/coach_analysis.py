from typing import Any

CS_BENCHMARKS = {
    "IRON": 4.5, "BRONZE": 5.0, "SILVER": 5.5, "GOLD": 6.5,
    "PLATINUM": 7.0, "EMERALD": 7.5, "DIAMOND": 8.0,
    "MASTER": 8.5, "GRANDMASTER": 8.5, "CHALLENGER": 9.0, "DEFAULT": 6.5,
}
VISION_BENCHMARKS = {
    "UTILITY": 50, "JUNGLE": 28, "TOP": 18, "MIDDLE": 20, "BOTTOM": 18, "DEFAULT": 20,
}
DAMAGE_BENCHMARKS = {
    "BOTTOM": 600, "MIDDLE": 550, "TOP": 450, "JUNGLE": 380, "UTILITY": 180, "DEFAULT": 450,
}

MIN_GAMES_FOR_POOL = 3
KEEP_WR = 50.0
DROP_WR = 40.0
KDA_LOW_THRESHOLD = 2.0
WEAKNESS_CS_RATIO = 0.90
WEAKNESS_DMG_RATIO = 0.90
WEAKNESS_VISION_RATIO = 0.80
CROSS_CS_OK_RATIO = 0.95
CROSS_DMG_LOW_RATIO = 0.85


def _severity(gap_ratio: float) -> tuple[str, float]:
    """gap_ratio = (benchmark - value) / benchmark. Returns (label, score)."""
    if gap_ratio > 0.20:
        return "high", gap_ratio
    if gap_ratio > 0.10:
        return "medium", gap_ratio
    return "low", gap_ratio


def _classify_pool(champion_stats: dict) -> tuple[list, list]:
    keep, drop = [], []
    sorted_champs = sorted(champion_stats.items(), key=lambda x: x[1].get("games", 0), reverse=True)
    for name, s in sorted_champs[:8]:
        games = s.get("games", 0)
        wr = s.get("winrate", 0.0)
        kda = s.get("kda", 0.0)
        entry = {"name": name, "games": games, "wr": round(wr, 1), "kda": round(kda, 2)}
        if games < MIN_GAMES_FOR_POOL:
            drop.append({**entry, "reason": "too_few_games"})
        elif wr >= KEEP_WR:
            keep.append(entry)
        elif wr < DROP_WR:
            drop.append({**entry, "reason": "low_wr"})
        else:
            drop.append({**entry, "reason": "situational"})
    return keep, drop


def _best_role(match_analysis: dict) -> dict | None:
    perf = match_analysis.get("performance_by_role", {})
    overall_wr = match_analysis.get("winrate", 50.0)
    best = None
    best_score = -1.0
    for role, stats in perf.items():
        if not role or stats.get("games", 0) < 2:
            continue
        wr = stats.get("winrate", 0.0)
        kda = stats.get("avg_kda", 0.0)
        score = wr * 0.6 + kda * 10 * 0.4
        if score > best_score:
            best_score = score
            best = {
                "role": role,
                "wr": round(wr, 1),
                "kda": round(kda, 2),
                "delta_pp": round(wr - overall_wr, 1),
            }
    return best


def _find_weaknesses(champion_stats: dict, keep: list, tier: str, match_analysis: dict) -> list:
    cs_bench = CS_BENCHMARKS.get(tier.upper(), CS_BENCHMARKS["DEFAULT"])
    candidates = []
    keep_names = {c["name"] for c in keep}

    for name, s in champion_stats.items():
        if s.get("games", 0) < MIN_GAMES_FOR_POOL:
            continue
        role = s.get("main_role", "DEFAULT")
        dmg_bench = DAMAGE_BENCHMARKS.get(role, DAMAGE_BENCHMARKS["DEFAULT"])
        vis_bench = VISION_BENCHMARKS.get(role, VISION_BENCHMARKS["DEFAULT"])

        cs_val = s.get("cs_per_min", 0.0)
        if cs_val < cs_bench * WEAKNESS_CS_RATIO:
            sev, score = _severity((cs_bench - cs_val) / cs_bench)
            candidates.append({
                "type": "cs_low", "champion": name,
                "value": round(cs_val, 1), "benchmark": cs_bench,
                "severity": sev, "_score": score,
            })

        dmg_val = s.get("damage_per_min", 0.0)
        if dmg_val < dmg_bench * WEAKNESS_DMG_RATIO:
            sev, score = _severity((dmg_bench - dmg_val) / dmg_bench)
            candidates.append({
                "type": "dmg_low", "champion": name,
                "value": round(dmg_val), "benchmark": dmg_bench,
                "severity": sev, "_score": score,
            })

        vis_val = s.get("vision_per_game", 0.0)
        if vis_val < vis_bench * WEAKNESS_VISION_RATIO:
            sev, score = _severity((vis_bench - vis_val) / vis_bench)
            candidates.append({
                "type": "vision_low", "champion": name,
                "value": round(vis_val, 1), "benchmark": vis_bench,
                "severity": sev, "_score": score,
            })

        kda_val = s.get("kda", 0.0)
        if kda_val < KDA_LOW_THRESHOLD:
            gap = (KDA_LOW_THRESHOLD - kda_val) / KDA_LOW_THRESHOLD
            sev, score = _severity(gap)
            candidates.append({
                "type": "kda_low", "champion": name,
                "value": round(kda_val, 2), "benchmark": KDA_LOW_THRESHOLD,
                "severity": sev, "_score": score,
            })

    # Deduplicate: per type, keep worst (highest _score)
    by_type: dict[str, dict] = {}
    for c in candidates:
        key = c["type"]
        if key not in by_type or c["_score"] > by_type[key]["_score"]:
            by_type[key] = c

    # Sort by severity bucket then score
    sev_order = {"high": 0, "medium": 1, "low": 2}
    ranked = sorted(by_type.values(), key=lambda x: (sev_order[x["severity"]], -x["_score"]))
    result = [{k: v for k, v in w.items() if k != "_score"} for w in ranked[:3]]

    # Fallback: role-level weaknesses if < 3
    if len(result) < 3:
        perf = match_analysis.get("performance_by_role", {})
        overall_wr = match_analysis.get("winrate", 50.0)
        for role, stats in perf.items():
            if len(result) >= 3:
                break
            if not role or stats.get("games", 0) < 2:
                continue
            role_wr = stats.get("winrate", 0.0)
            if role_wr < overall_wr - 10:
                result.append({
                    "type": "role_wr_low", "champion": role,
                    "value": round(role_wr, 1), "benchmark": round(overall_wr, 1),
                    "severity": "medium",
                })

    # Last resort: soft pass — find metrics closest to threshold even if above it
    if len(result) < 3:
        existing_types = {w["type"] for w in result}
        soft: list[dict] = []
        for name, s in champion_stats.items():
            if s.get("games", 0) < MIN_GAMES_FOR_POOL:
                continue
            role = s.get("main_role", "DEFAULT")
            cs_b = CS_BENCHMARKS.get(tier.upper(), CS_BENCHMARKS["DEFAULT"])
            checks = [
                ("cs_low",     s.get("cs_per_min", 0.0),      cs_b),
                ("dmg_low",    s.get("damage_per_min", 0.0),   DAMAGE_BENCHMARKS.get(role, DAMAGE_BENCHMARKS["DEFAULT"])),
                ("vision_low", s.get("vision_per_game", 0.0),  VISION_BENCHMARKS.get(role, VISION_BENCHMARKS["DEFAULT"])),
                ("kda_low",    s.get("kda", 0.0),              KDA_LOW_THRESHOLD),
            ]
            for metric_type, val, bench in checks:
                if metric_type in existing_types or bench <= 0:
                    continue
                gap = (bench - val) / bench
                soft.append({
                    "type": metric_type, "champion": name,
                    "value": round(val, 1), "benchmark": bench,
                    "severity": "low", "_score": gap,
                })
        soft.sort(key=lambda x: -x["_score"])
        seen = {w["type"] for w in result}
        for c in soft:
            if len(result) >= 3:
                break
            if c["type"] not in seen:
                result.append({k: v for k, v in c.items() if k != "_score"})
                seen.add(c["type"])

    # Absolute last resort: generic sample size flag
    if len(result) < 3:
        total = match_analysis.get("total_games", 0)
        result.append({
            "type": "sample_size", "champion": "overall",
            "value": total, "benchmark": 30,
            "severity": "low",
        })

    return result[:3]


def _find_strength(champion_stats: dict, keep: list, tier: str) -> dict | None:
    cs_bench = CS_BENCHMARKS.get(tier.upper(), CS_BENCHMARKS["DEFAULT"])
    best = None
    best_delta = -1.0
    keep_names = {c["name"] for c in keep}

    for name, s in champion_stats.items():
        if name not in keep_names or s.get("games", 0) < MIN_GAMES_FOR_POOL:
            continue
        role = s.get("main_role", "DEFAULT")
        checks = [
            ("cs_high", s.get("cs_per_min", 0.0), cs_bench),
            ("vision_high", s.get("vision_per_game", 0.0), VISION_BENCHMARKS.get(role, VISION_BENCHMARKS["DEFAULT"])),
            ("dmg_high", s.get("damage_per_min", 0.0), DAMAGE_BENCHMARKS.get(role, DAMAGE_BENCHMARKS["DEFAULT"])),
            ("kda_high", s.get("kda", 0.0), KDA_LOW_THRESHOLD),
        ]
        for metric_type, val, bench in checks:
            if bench <= 0:
                continue
            delta_pct = (val - bench) / bench * 100
            if delta_pct > best_delta:
                best_delta = delta_pct
                best = {
                    "type": metric_type, "champion": name,
                    "value": round(val, 1), "benchmark": bench,
                    "delta_pct": round(delta_pct, 1),
                }
    return best


def _find_cross_flags(champion_stats: dict, tier: str) -> list:
    cs_bench = CS_BENCHMARKS.get(tier.upper(), CS_BENCHMARKS["DEFAULT"])
    flags = []
    for name, s in champion_stats.items():
        if s.get("games", 0) < MIN_GAMES_FOR_POOL or len(flags) >= 2:
            break
        role = s.get("main_role", "DEFAULT")
        dmg_bench = DAMAGE_BENCHMARKS.get(role, DAMAGE_BENCHMARKS["DEFAULT"])
        cs_val = s.get("cs_per_min", 0.0)
        dmg_val = s.get("damage_per_min", 0.0)

        cs_ratio = cs_val / cs_bench if cs_bench > 0 else 0
        dmg_ratio = dmg_val / dmg_bench if dmg_bench > 0 else 0

        if cs_ratio >= CROSS_CS_OK_RATIO and dmg_ratio < CROSS_DMG_LOW_RATIO:
            flags.append({
                "type": "cs_good_dmg_low", "champion": name,
                "note": f"cs:{cs_val:.1f}(ok) dmg:{dmg_val:.0f}(below)",
            })

        wr = s.get("winrate", 0.0)
        kda = s.get("kda", 0.0)
        if wr < 45.0 and kda > 3.0 and len(flags) < 2:
            flags.append({
                "type": "wr_low_kda_ok", "champion": name,
                "note": f"wr:{wr:.0f}% kda:{kda:.2f}",
            })
    return flags


def analyze_for_coaching(
    summoner: dict,
    ranked: list,
    champion_stats: dict[str, Any],
    match_analysis: dict,
) -> dict:
    name = f"{summoner.get('gameName', '')}#{summoner.get('tagLine', '')}"
    solo = next((q for q in ranked if q.get("queueType") == "RANKED_SOLO_5x5"), None)

    tier = "DEFAULT"
    player_block: dict = {"name": name, "tier": "Unranked", "rank": "", "lp": 0, "season_wr": 0.0, "streak": 0}
    if solo:
        wins = solo.get("wins", 0)
        losses = solo.get("losses", 0)
        total = wins + losses
        tier = solo.get("tier", "DEFAULT")
        player_block = {
            "name": name,
            "tier": tier,
            "rank": solo.get("rank", ""),
            "lp": solo.get("leaguePoints", 0),
            "season_wr": round((wins / total * 100) if total > 0 else 0.0, 1),
            "streak": solo.get("streak", 0),
        }

    recent_block = {
        "games": match_analysis.get("total_games", 0),
        "wr": round(match_analysis.get("winrate", 0.0), 1),
    }

    keep, drop = _classify_pool(champion_stats)
    best_role = _best_role(match_analysis)
    weaknesses = _find_weaknesses(champion_stats, keep, tier, match_analysis)
    strength = _find_strength(champion_stats, keep, tier)
    cross_flags = _find_cross_flags(champion_stats, tier)

    if weaknesses:
        weekly_focus = f"{weaknesses[0]['type']}:{weaknesses[0]['champion']}"
    elif cross_flags:
        weekly_focus = f"{cross_flags[0]['type']}:{cross_flags[0]['champion']}"
    else:
        weekly_focus = "maintain_consistency"

    return {
        "player": player_block,
        "recent": recent_block,
        "champion_pool": {"keep": keep, "drop": drop},
        "best_role": best_role,
        "weaknesses": weaknesses,
        "strength": strength,
        "cross_flags": cross_flags,
        "weekly_focus": weekly_focus,
    }
