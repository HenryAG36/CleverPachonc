from backend.analysis.rune_analysis import analyze_runes
from .conftest import make_match, make_participant


def test_empty_returns_empty_collections(puuid):
    result = analyze_runes([], puuid)
    assert result["keystone_usage"] == {}
    assert result["primary_paths"] == {}
    assert result["secondary_paths"] == {}


def test_keystone_tracked(puuid):
    match = make_match(participants=[make_participant(puuid=puuid)])
    result = analyze_runes([match], puuid)
    # keystone = 8008 (Lethal Tempo) set in conftest make_participant
    assert 8008 in result["keystone_usage"]
    assert result["keystone_usage"][8008] == 1


def test_primary_path_tracked(puuid):
    match = make_match(participants=[make_participant(puuid=puuid)])
    result = analyze_runes([match], puuid)
    assert 8000 in result["primary_paths"]  # Precision


def test_secondary_path_tracked(puuid):
    match = make_match(participants=[make_participant(puuid=puuid)])
    result = analyze_runes([match], puuid)
    assert 8300 in result["secondary_paths"]  # Inspiration


def test_combination_key_format(puuid):
    match = make_match(participants=[make_participant(puuid=puuid)])
    result = analyze_runes([match], puuid)
    assert "8000_8300" in result["rune_combinations"]


def test_combination_winrate(puuid):
    win = make_match(participants=[make_participant(puuid=puuid, win=True)])
    loss = make_match(participants=[make_participant(puuid=puuid, win=False)])
    result = analyze_runes([win, loss], puuid)
    combo = result["rune_combinations"]["8000_8300"]
    assert combo["winrate"] == 50.0


def test_keystone_performance_winrate(puuid):
    win = make_match(participants=[make_participant(puuid=puuid, win=True)])
    loss = make_match(participants=[make_participant(puuid=puuid, win=False)])
    result = analyze_runes([win, loss], puuid)
    assert result["performance_by_keystone"][8008]["winrate"] == 50.0


def test_multiple_games_accumulate(puuid):
    matches = [
        make_match(participants=[make_participant(puuid=puuid)]),
        make_match(participants=[make_participant(puuid=puuid)]),
    ]
    result = analyze_runes(matches, puuid)
    assert result["keystone_usage"][8008] == 2
    assert result["primary_paths"][8000] == 2


def test_missing_perks_skipped(puuid):
    """Participants without perks data should not crash the analyzer."""
    participant = make_participant(puuid=puuid)
    del participant["perks"]
    match = make_match(participants=[participant])
    # Should not raise
    result = analyze_runes([match], puuid)
    assert result["keystone_usage"] == {}
