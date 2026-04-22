"""
Shared fixtures for CleverPachonc tests.

All match/participant dicts use the minimal fields that the analysis
functions actually access, so tests stay readable and self-contained.
"""
import pytest


def make_participant(
    puuid: str = "test-puuid",
    champion_name: str = "Jinx",
    champion_id: int = 222,
    win: bool = True,
    kills: int = 5,
    deaths: int = 2,
    assists: int = 8,
    team_position: str = "BOTTOM",
    total_minions_killed: int = 150,
    neutral_minions_killed: int = 10,
    gold_earned: int = 12000,
    total_damage: int = 25000,
    vision_score: int = 20,
    **perks_override,
) -> dict:
    participant = {
        "puuid": puuid,
        "championName": champion_name,
        "championId": champion_id,
        "win": win,
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "teamPosition": team_position,
        "totalMinionsKilled": total_minions_killed,
        "neutralMinionsKilled": neutral_minions_killed,
        "goldEarned": gold_earned,
        "totalDamageDealtToChampions": total_damage,
        "visionScore": vision_score,
        "item0": 3031, "item1": 3094, "item2": 3085,
        "item3": 3006, "item4": 3033, "item5": 0, "item6": 3364,
        "perks": {
            "styles": [
                {
                    "style": 8000,  # Precision
                    "selections": [{"perk": 8008}],  # Lethal Tempo
                },
                {
                    "style": 8300,  # Inspiration
                    "selections": [],
                },
            ]
        },
    }
    return participant


def make_match(
    game_duration: int = 1800,
    participants: list = None,
) -> dict:
    if participants is None:
        participants = [make_participant()]
    return {
        "info": {
            "gameDuration": game_duration,
            "participants": participants,
        }
    }


@pytest.fixture
def puuid() -> str:
    return "test-puuid"


@pytest.fixture
def single_win_match(puuid):
    return make_match(participants=[make_participant(puuid=puuid, win=True)])


@pytest.fixture
def single_loss_match(puuid):
    return make_match(participants=[make_participant(puuid=puuid, win=False)])


@pytest.fixture
def multi_match_history(puuid):
    """Three matches: 2 wins (BOTTOM), 1 loss (MIDDLE)."""
    return [
        make_match(participants=[make_participant(puuid=puuid, win=True, team_position="BOTTOM")]),
        make_match(participants=[make_participant(puuid=puuid, win=True, team_position="BOTTOM",
                                                  champion_name="Caitlyn", kills=8)]),
        make_match(participants=[make_participant(puuid=puuid, win=False, team_position="MIDDLE",
                                                  champion_name="Lux", kills=3, deaths=5)]),
    ]
