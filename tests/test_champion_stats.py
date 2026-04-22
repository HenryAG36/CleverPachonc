from backend.analysis.champion_stats import analyze_champion_stats
from .conftest import make_match, make_participant


def test_empty_returns_empty(puuid):
    assert analyze_champion_stats([], puuid) == {}


def test_single_game_stats(puuid):
    match = make_match(participants=[
        make_participant(puuid=puuid, champion_name="Jinx", win=True,
                         kills=5, deaths=2, assists=8,
                         total_minions_killed=150, neutral_minions_killed=10)
    ])
    stats = analyze_champion_stats([match], puuid)
    jinx = stats["Jinx"]
    assert jinx["games"] == 1
    assert jinx["wins"] == 1
    assert jinx["winrate"] == 100.0
    assert jinx["avg_kills"] == 5.0
    assert jinx["avg_deaths"] == 2.0
    assert jinx["avg_assists"] == 8.0
    assert jinx["cs"] == 160  # 150 + 10


def test_kda_ratio(puuid):
    match = make_match(participants=[
        make_participant(puuid=puuid, kills=4, deaths=2, assists=6)
    ])
    stats = analyze_champion_stats([match], puuid)
    jinx = stats["Jinx"]
    # (4 + 6) / 2 = 5.0
    assert jinx["kda"] == 5.0


def test_perfect_kda_no_division_by_zero(puuid):
    match = make_match(participants=[
        make_participant(puuid=puuid, kills=10, deaths=0, assists=5)
    ])
    stats = analyze_champion_stats([match], puuid)
    assert stats["Jinx"]["kda"] == 15.0  # (10+5) / max(1, 0)


def test_multiple_champions(puuid):
    m1 = make_match(participants=[make_participant(puuid=puuid, champion_name="Jinx")])
    m2 = make_match(participants=[make_participant(puuid=puuid, champion_name="Caitlyn")])
    stats = analyze_champion_stats([m1, m2], puuid)
    assert "Jinx" in stats
    assert "Caitlyn" in stats
    assert stats["Jinx"]["games"] == 1
    assert stats["Caitlyn"]["games"] == 1


def test_accumulates_across_games(puuid):
    m1 = make_match(participants=[make_participant(puuid=puuid, kills=4)])
    m2 = make_match(participants=[make_participant(puuid=puuid, kills=6)])
    stats = analyze_champion_stats([m1, m2], puuid)
    assert stats["Jinx"]["games"] == 2
    assert stats["Jinx"]["avg_kills"] == 5.0


def test_main_role_is_most_frequent(puuid):
    bottom = make_participant(puuid=puuid, team_position="BOTTOM")
    middle = make_participant(puuid=puuid, team_position="MIDDLE")
    matches = [
        make_match(participants=[bottom]),
        make_match(participants=[bottom]),
        make_match(participants=[middle]),
    ]
    stats = analyze_champion_stats(matches, puuid)
    assert stats["Jinx"]["main_role"] == "BOTTOM"


def test_per_minute_stats_positive(puuid):
    match = make_match(game_duration=1800, participants=[
        make_participant(puuid=puuid, total_minions_killed=180, gold_earned=15000)
    ])
    stats = analyze_champion_stats([match], puuid)
    assert stats["Jinx"]["cs_per_min"] == pytest.approx(190 / 30, rel=1e-3)
    assert stats["Jinx"]["gold_per_min"] > 0


import pytest
