from backend.analysis.match_analysis import analyze_match_history
from .conftest import make_match, make_participant


def test_empty_match_list(puuid):
    result = analyze_match_history([], puuid)
    assert result["total_games"] == 0
    assert result["wins"] == 0
    assert result["losses"] == 0
    assert result["recent_performance"] == []


def test_single_win(puuid, single_win_match):
    result = analyze_match_history([single_win_match], puuid)
    assert result["total_games"] == 1
    assert result["wins"] == 1
    assert result["losses"] == 0
    assert result["winrate"] == 100.0


def test_single_loss(puuid, single_loss_match):
    result = analyze_match_history([single_loss_match], puuid)
    assert result["wins"] == 0
    assert result["losses"] == 1
    assert result["winrate"] == 0.0


def test_winrate_calculation(puuid, multi_match_history):
    result = analyze_match_history(multi_match_history, puuid)
    assert result["total_games"] == 3
    assert result["wins"] == 2
    assert result["losses"] == 1
    assert abs(result["winrate"] - 66.67) < 0.01


def test_role_tracking(puuid, multi_match_history):
    result = analyze_match_history(multi_match_history, puuid)
    assert result["roles"]["BOTTOM"] == 2
    assert result["roles"]["MIDDLE"] == 1


def test_role_preferences_sum_to_100(puuid, multi_match_history):
    result = analyze_match_history(multi_match_history, puuid)
    total = sum(result["role_preferences"].values())
    assert abs(total - 100.0) < 0.01


def test_performance_by_role_winrate(puuid, multi_match_history):
    result = analyze_match_history(multi_match_history, puuid)
    assert result["performance_by_role"]["BOTTOM"]["winrate"] == 100.0
    assert result["performance_by_role"]["MIDDLE"]["winrate"] == 0.0


def test_recent_performance_entry_shape(puuid, single_win_match):
    result = analyze_match_history([single_win_match], puuid)
    entry = result["recent_performance"][0]
    assert "champion" in entry
    assert "result" in entry
    assert "kda" in entry
    assert "role" in entry
    assert "cs" in entry


def test_recent_performance_result_label(puuid, single_win_match, single_loss_match):
    results = analyze_match_history([single_win_match, single_loss_match], puuid)
    labels = [r["result"] for r in results["recent_performance"]]
    assert "Victory" in labels
    assert "Defeat" in labels


def test_avg_game_duration(puuid):
    m1 = make_match(game_duration=1200, participants=[make_participant(puuid=puuid)])
    m2 = make_match(game_duration=1800, participants=[make_participant(puuid=puuid)])
    result = analyze_match_history([m1, m2], puuid)
    assert result["avg_game_duration"] == 1500.0
