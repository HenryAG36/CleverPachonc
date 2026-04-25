"""Tests for meta analysis module (does not make live network calls)."""
import pytest
from unittest.mock import patch, MagicMock
from backend.analysis.meta_analysis import (
    analyze_meta_gaps,
    _consecutive_losses,
    _build_gap,
    _losses_per_enemy,
    TILT_THRESHOLD,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_matches(results):
    """results = list of bool (True=win, False=loss), most-recent first."""
    return [{"win": r, "enemy_carry": f"Champ{i}" if not r else None} for i, r in enumerate(results)]


def make_champ(games=5, winrate=55.0, main_role="BOTTOM", core_items=None):
    return {
        "games": games, "winrate": winrate, "kda": 3.0,
        "cs_per_min": 7.0, "damage_per_min": 600.0,
        "vision_per_game": 20.0, "main_role": main_role,
        "core_items": core_items or [],
    }


def make_match_analysis(wr=55.0, roles=None):
    return {
        "winrate": wr,
        "role_preferences": roles or {"BOTTOM": 80.0, "MIDDLE": 20.0},
        "performance_by_role": {},
    }


MOCK_META = {
    "win_rate": 52.4,
    "tier": "S",
    "best_items": [{"id": 3031, "wr": 54.1}, {"id": 3094, "wr": 53.8}],
    "keystone": {"id": 8008, "wr": 53.2},
    "matchups": {"Draven": {"wr": 47.2, "games": 8420}},
}


# ── Consecutive losses ────────────────────────────────────────────────────────

def test_consecutive_losses_zero():
    matches = make_matches([True, False, False])
    assert _consecutive_losses(matches) == 0


def test_consecutive_losses_streak():
    matches = make_matches([False, False, False, True])
    assert _consecutive_losses(matches) == 3


def test_consecutive_losses_all_wins():
    matches = make_matches([True, True, True])
    assert _consecutive_losses(matches) == 0


def test_consecutive_losses_all_losses():
    matches = make_matches([False, False, False])
    assert _consecutive_losses(matches) == 3


# ── Build gap ─────────────────────────────────────────────────────────────────

def test_build_gap_returns_missing_items():
    player = [{"item_id": 3031, "count": 4}]
    meta = [{"id": 3031, "wr": 54.0}, {"id": 3094, "wr": 53.0}, {"id": 3153, "wr": 52.0}]
    gaps = _build_gap(player, meta)
    assert all(g["id"] != 3031 for g in gaps)
    assert len(gaps) <= 2


def test_build_gap_empty_player_items():
    meta = [{"id": 3031, "wr": 54.0}]
    assert _build_gap([], meta) == []


def test_build_gap_capped_at_two():
    player = []
    meta = [{"id": i, "wr": 53.0} for i in range(6)]
    assert len(_build_gap(player, meta)) <= 2


# ── Losses per enemy ──────────────────────────────────────────────────────────

def test_losses_per_enemy_counts_correctly():
    matches = [
        {"win": False, "enemy_carry": "Draven"},
        {"win": False, "enemy_carry": "Draven"},
        {"win": True, "enemy_carry": "Jinx"},
        {"win": False, "enemy_carry": "Caitlyn"},
    ]
    result = _losses_per_enemy(matches)
    assert result["Draven"] == 2
    assert result.get("Jinx", 0) == 0
    assert result["Caitlyn"] == 1


def test_losses_per_enemy_ignores_none():
    matches = [{"win": False, "enemy_carry": None}]
    assert _losses_per_enemy(matches) == {}


# ── analyze_meta_gaps ─────────────────────────────────────────────────────────

@patch("backend.analysis.meta_analysis.get_champion_meta", return_value=MOCK_META)
def test_meta_gaps_basic_structure(mock_meta):
    champ_stats = {"Jinx": make_champ()}
    result = analyze_meta_gaps(champ_stats, make_match_analysis(), [], "GOLD")
    assert "per_champ_meta" in result
    assert "matchup_insights" in result
    assert "meta_picks" in result
    assert "tilt_flag" in result
    assert "consecutive_losses" in result


@patch("backend.analysis.meta_analysis.get_champion_meta", return_value=MOCK_META)
def test_tilt_flag_set_on_streak(mock_meta):
    matches = make_matches([False] * TILT_THRESHOLD)
    result = analyze_meta_gaps({}, make_match_analysis(), matches, "GOLD")
    assert result["tilt_flag"] is True
    assert result["consecutive_losses"] == TILT_THRESHOLD


@patch("backend.analysis.meta_analysis.get_champion_meta", return_value=MOCK_META)
def test_no_tilt_on_short_streak(mock_meta):
    matches = make_matches([False, False, True])
    result = analyze_meta_gaps({}, make_match_analysis(), matches, "GOLD")
    assert result["tilt_flag"] is False


@patch("backend.analysis.meta_analysis.get_champion_meta", return_value=MOCK_META)
def test_per_champ_meta_populated(mock_meta):
    champ_stats = {"Jinx": make_champ()}
    result = analyze_meta_gaps(champ_stats, make_match_analysis(), [], "GOLD")
    assert "Jinx" in result["per_champ_meta"]
    jinx = result["per_champ_meta"]["Jinx"]
    assert jinx["meta_wr"] == 52.4
    assert jinx["tier"] == "S"


@patch("backend.analysis.meta_analysis.get_champion_meta", return_value=None)
def test_graceful_when_meta_unavailable(mock_meta):
    champ_stats = {"Jinx": make_champ()}
    result = analyze_meta_gaps(champ_stats, make_match_analysis(), [], "GOLD")
    assert result["per_champ_meta"] == {}
    assert result["meta_picks"] == []


@patch("backend.analysis.meta_analysis.get_champion_meta", return_value=MOCK_META)
def test_matchup_insights_from_history(mock_meta):
    matches = [
        {"win": False, "enemy_carry": "Draven"},
        {"win": False, "enemy_carry": "Draven"},
        {"win": True, "enemy_carry": "Caitlyn"},
    ]
    champ_stats = {"Jinx": make_champ()}
    result = analyze_meta_gaps(champ_stats, make_match_analysis(), matches, "GOLD")
    enemies = [m["enemy"] for m in result["matchup_insights"]]
    assert "Draven" in enemies


@patch("backend.analysis.meta_analysis.get_champion_meta", return_value=MOCK_META)
def test_skips_champs_below_min_games(mock_meta):
    champ_stats = {"Jinx": make_champ(games=1)}
    result = analyze_meta_gaps(champ_stats, make_match_analysis(), [], "GOLD")
    assert "Jinx" not in result["per_champ_meta"]
