"""
End-to-end test of the /api/summoner route with mocked Riot API data.

Verifies the full formatting pipeline: response shape, per-queue ranked
stats, ranked-only analytics, and the fields the frontend depends on
(summoner.puuid, gameEndTimestamp, participants).
"""
import pytest

import api.index as api_index
from tests.conftest import make_match, make_participant

PUUID = "test-puuid"


def _full_match(queue_id=420, win=True, champion="Jinx", champion_id=222, end_ts=1750000000000):
    """A match with the searched player plus one enemy, realistic metadata."""
    player = make_participant(puuid=PUUID, win=win, champion_name=champion, champion_id=champion_id)
    enemy = make_participant(
        puuid="enemy-puuid", win=not win, champion_name="Caitlyn", champion_id=51,
    )
    match = make_match(participants=[player, enemy])
    match["metadata"] = {"matchId": f"NA1_{queue_id}_{win}_{champion_id}"}
    match["info"]["queueId"] = queue_id
    match["info"]["gameEndTimestamp"] = end_ts
    # teamIds so the scoreboard split works
    player["teamId"] = 100
    enemy["teamId"] = 200
    return match


@pytest.fixture
def client(monkeypatch):
    summoner = {
        "puuid": PUUID,
        "gameName": "TestPlayer",
        "tagLine": "NA1",
        "summonerLevel": 250,
        "profileIconId": 123,
    }
    ranked = [{
        "queueType": "RANKED_SOLO_5x5",
        "tier": "GOLD", "rank": "II", "leaguePoints": 42,
        "wins": 30, "losses": 25,
        # per-queue extras attached by riot_api in production
        "streak": 2, "mostPlayedRole": "BOTTOM",
        "avgKDA": {"kills": 5.0, "deaths": 2.0, "assists": 8.0},
        "recentGames": 3,
    }]
    mastery = [{
        "championId": 222, "championLevel": 7,
        "championPoints": 123456, "lastPlayTime": 1750000000000,
    }]
    matches = [
        _full_match(queue_id=420, win=True),
        _full_match(queue_id=440, win=False, champion="Lux", champion_id=99),
        _full_match(queue_id=450, win=True, champion="Sona", champion_id=37),  # ARAM — excluded
    ]

    async def fake_fetch(name, region):
        return summoner, ranked, mastery, matches

    monkeypatch.setattr(api_index, "get_summoner_data_async", fake_fetch)
    monkeypatch.setattr(api_index, "get_latest_version", lambda: "16.14.1")
    monkeypatch.setattr(api_index, "_champion_map", {"222": "Jinx", "51": "Caitlyn", "99": "Lux", "37": "Sona"})
    monkeypatch.setattr(api_index, "_rune_tree", [])
    return api_index.app.test_client()


def test_summoner_response_shape(client):
    res = client.get("/api/summoner?name=TestPlayer%23NA1&region=NA")
    assert res.status_code == 200
    data = res.get_json()

    # Frontend contract: puuid must be exposed for scoreboard identification
    assert data["summoner"]["puuid"] == PUUID
    assert data["summoner"]["gameName"] == "TestPlayer"

    # ARAM (queue 450) must be excluded from the displayed match list
    assert len(data["matches"]) == 2
    assert {m["queueId"] for m in data["matches"]} == {420, 440}

    # Fields the UI depends on
    for m in data["matches"]:
        assert m["gameEndTimestamp"] == 1750000000000
        assert m["matchId"]
        assert len(m["participants"]) == 2
        assert m["participants"][0]["puuid"] == PUUID

    # Analytics must only include ranked games (no Sona from the ARAM game)
    assert set(data["champion_stats"]) == {"Jinx", "Lux"}
    assert data["match_analysis"]["total_games"] == 2

    # Mastery is resolved to names
    assert data["mastery"][0]["championName"] == "Jinx"


def test_summoner_requires_riot_id_format(client):
    res = client.get("/api/summoner?name=NoTag&region=NA")
    assert res.status_code == 400
    assert "Name#TAG" in res.get_json()["error"]


def test_summoner_requires_name(client):
    res = client.get("/api/summoner?region=NA")
    assert res.status_code == 400
