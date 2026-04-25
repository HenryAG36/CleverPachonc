"""Tests for the deterministic coach pre-analysis module."""
import pytest
from backend.analysis.coach_analysis import (
    analyze_for_coaching,
    _classify_pool,
    _best_role,
    _find_weaknesses,
    _find_strength,
    _find_cross_flags,
    KEEP_WR, DROP_WR, MIN_GAMES_FOR_POOL,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

def make_summoner(name="TestPlayer", tag="NA1"):
    return {"gameName": name, "tagLine": tag}


def make_ranked(tier="GOLD", rank="II", lp=45, wins=67, losses=43, streak=3):
    return [
        {
            "queueType": "RANKED_SOLO_5x5",
            "tier": tier, "rank": rank, "leaguePoints": lp,
            "wins": wins, "losses": losses, "streak": streak,
            "mostPlayedRole": "BOTTOM",
            "avgKDA": {"kills": 6, "deaths": 3, "assists": 8},
        }
    ]


def make_champ(
    games=5, wins=3, winrate=60.0, kda=3.0,
    cs_per_min=7.0, damage_per_min=620.0, vision_per_game=22.0,
    main_role="BOTTOM",
):
    return {
        "games": games, "wins": wins, "winrate": winrate, "kda": kda,
        "avg_kills": 5.0, "avg_deaths": 2.0, "avg_assists": 7.0,
        "cs_per_min": cs_per_min, "gold_per_min": 450.0,
        "damage_per_min": damage_per_min, "vision_per_game": vision_per_game,
        "main_role": main_role, "core_items": [],
    }


def make_match_analysis(total=20, wins=12, wr=60.0, dur=1800, roles=None):
    roles = roles or {
        "BOTTOM": {"games": 15, "wins": 10, "winrate": 66.7, "avg_kda": 4.2},
        "MIDDLE": {"games": 5, "wins": 2, "winrate": 40.0, "avg_kda": 2.1},
    }
    return {
        "total_games": total, "wins": wins, "losses": total - wins,
        "winrate": wr, "avg_game_duration": dur,
        "performance_by_role": roles,
        "role_preferences": {"BOTTOM": 75.0, "MIDDLE": 25.0},
    }


# ── Champion pool classification ─────────────────────────────────────────────

def test_classify_pool_keep():
    champs = {"Jinx": make_champ(games=5, winrate=62.0)}
    keep, drop = _classify_pool(champs)
    assert len(keep) == 1
    assert keep[0]["name"] == "Jinx"


def test_classify_pool_drop_low_wr():
    champs = {"Jhin": make_champ(games=4, winrate=35.0)}
    keep, drop = _classify_pool(champs)
    assert len(keep) == 0
    assert drop[0]["reason"] == "low_wr"


def test_classify_pool_drop_too_few_games():
    champs = {"Jinx": make_champ(games=2, winrate=100.0)}
    keep, drop = _classify_pool(champs)
    assert drop[0]["reason"] == "too_few_games"


def test_classify_pool_situational():
    champs = {"Ezreal": make_champ(games=4, winrate=45.0)}
    keep, drop = _classify_pool(champs)
    assert drop[0]["reason"] == "situational"


def test_classify_pool_capped_at_8():
    champs = {f"Champ{i}": make_champ(games=10 - i, winrate=55.0) for i in range(12)}
    keep, drop = _classify_pool(champs)
    assert len(keep) + len(drop) == 8


# ── Best role ─────────────────────────────────────────────────────────────────

def test_best_role_picks_highest_score():
    analysis = make_match_analysis(roles={
        "BOTTOM": {"games": 10, "wins": 7, "winrate": 70.0, "avg_kda": 4.0},
        "MIDDLE": {"games": 5, "wins": 2, "winrate": 40.0, "avg_kda": 2.0},
    })
    result = _best_role(analysis)
    assert result["role"] == "BOTTOM"


def test_best_role_skips_low_game_count():
    analysis = make_match_analysis(roles={
        "BOTTOM": {"games": 1, "wins": 1, "winrate": 100.0, "avg_kda": 10.0},
        "MIDDLE": {"games": 5, "wins": 3, "winrate": 60.0, "avg_kda": 3.0},
    })
    result = _best_role(analysis)
    assert result["role"] == "MIDDLE"


def test_best_role_delta_pp():
    analysis = make_match_analysis(wr=50.0, roles={
        "BOTTOM": {"games": 10, "wins": 6, "winrate": 60.0, "avg_kda": 3.0},
    })
    result = _best_role(analysis)
    assert result["delta_pp"] == pytest.approx(10.0, abs=0.1)


# ── Weakness detection ────────────────────────────────────────────────────────

def test_weakness_cs_low():
    champs = {"Jinx": make_champ(games=4, winrate=55.0, cs_per_min=5.0, main_role="BOTTOM")}
    keep = [{"name": "Jinx"}]
    weaknesses = _find_weaknesses(champs, keep, "GOLD", make_match_analysis())
    types = [w["type"] for w in weaknesses]
    assert "cs_low" in types


def test_weakness_dmg_low():
    champs = {"Jinx": make_champ(games=4, winrate=55.0, damage_per_min=400.0, main_role="BOTTOM")}
    keep = [{"name": "Jinx"}]
    weaknesses = _find_weaknesses(champs, keep, "GOLD", make_match_analysis())
    types = [w["type"] for w in weaknesses]
    assert "dmg_low" in types


def test_weakness_vision_low():
    champs = {"Soraka": make_champ(games=4, winrate=55.0, vision_per_game=25.0, main_role="UTILITY")}
    keep = [{"name": "Soraka"}]
    weaknesses = _find_weaknesses(champs, keep, "GOLD", make_match_analysis())
    types = [w["type"] for w in weaknesses]
    assert "vision_low" in types


def test_weakness_kda_low():
    champs = {"Jinx": make_champ(games=4, winrate=55.0, kda=1.2)}
    keep = [{"name": "Jinx"}]
    weaknesses = _find_weaknesses(champs, keep, "GOLD", make_match_analysis())
    types = [w["type"] for w in weaknesses]
    assert "kda_low" in types


def test_weakness_always_returns_3():
    champs = {"Jinx": make_champ(games=5, winrate=65.0, cs_per_min=8.0,
                                  damage_per_min=700.0, vision_per_game=25.0, kda=4.0)}
    keep = [{"name": "Jinx"}]
    analysis = make_match_analysis()
    weaknesses = _find_weaknesses(champs, keep, "GOLD", analysis)
    assert len(weaknesses) == 3


def test_weakness_fallback_to_role_data():
    champs = {"Jinx": make_champ(games=5, winrate=65.0, cs_per_min=8.0,
                                  damage_per_min=700.0, vision_per_game=30.0, kda=4.0)}
    keep = [{"name": "Jinx"}]
    analysis = make_match_analysis(wr=60.0, roles={
        "BOTTOM": {"games": 5, "wins": 3, "winrate": 60.0, "avg_kda": 3.0},
        "MIDDLE": {"games": 5, "wins": 2, "winrate": 40.0, "avg_kda": 2.0},  # -20pp
    })
    weaknesses = _find_weaknesses(champs, keep, "GOLD", analysis)
    types = [w["type"] for w in weaknesses]
    assert "role_wr_low" in types or "sample_size" in types


# ── Cross flags ───────────────────────────────────────────────────────────────

def test_cross_flag_cs_good_dmg_low():
    champs = {"Jinx": make_champ(games=5, winrate=55.0, cs_per_min=7.0, damage_per_min=400.0, main_role="BOTTOM")}
    flags = _find_cross_flags(champs, "GOLD")
    assert any(f["type"] == "cs_good_dmg_low" for f in flags)


def test_cross_flag_wr_low_kda_ok():
    champs = {"Jhin": make_champ(games=5, winrate=40.0, kda=3.5, cs_per_min=7.0, damage_per_min=700.0)}
    flags = _find_cross_flags(champs, "GOLD")
    assert any(f["type"] == "wr_low_kda_ok" for f in flags)


def test_cross_flags_capped_at_2():
    champs = {
        f"Champ{i}": make_champ(games=5, winrate=40.0, kda=3.5, cs_per_min=7.0, damage_per_min=400.0)
        for i in range(5)
    }
    flags = _find_cross_flags(champs, "GOLD")
    assert len(flags) <= 2


# ── Weekly focus ──────────────────────────────────────────────────────────────

def test_weekly_focus_from_weakness():
    summoner = make_summoner()
    ranked = make_ranked()
    champs = {"Jinx": make_champ(games=5, winrate=55.0, cs_per_min=4.5)}
    analysis = make_match_analysis()
    result = analyze_for_coaching(summoner, ranked, champs, analysis)
    assert result["weekly_focus"].startswith("cs_low:")


def test_weekly_focus_fallback_consistency():
    summoner = make_summoner()
    ranked = make_ranked()
    champs = {"Jinx": make_champ(games=5, winrate=65.0, cs_per_min=8.0,
                                  damage_per_min=700.0, vision_per_game=30.0, kda=4.0)}
    analysis = make_match_analysis(roles={
        "BOTTOM": {"games": 15, "wins": 10, "winrate": 66.0, "avg_kda": 4.0},
    })
    result = analyze_for_coaching(summoner, ranked, champs, analysis)
    assert result["weekly_focus"] is not None


# ── Full integration ──────────────────────────────────────────────────────────

def test_full_output_shape():
    summoner = make_summoner()
    ranked = make_ranked()
    champs = {
        "Jinx": make_champ(games=8, winrate=62.0, cs_per_min=7.2),
        "Jhin": make_champ(games=3, winrate=33.0, cs_per_min=5.5),
        "Ezreal": make_champ(games=2, winrate=50.0),
    }
    analysis = make_match_analysis()
    result = analyze_for_coaching(summoner, ranked, champs, analysis)

    assert "player" in result
    assert "recent" in result
    assert "champion_pool" in result
    assert "best_role" in result
    assert "weaknesses" in result
    assert len(result["weaknesses"]) == 3
    assert "strength" in result
    assert "cross_flags" in result
    assert "weekly_focus" in result
    assert result["player"]["name"] == "TestPlayer#NA1"
    assert result["player"]["tier"] == "GOLD"
