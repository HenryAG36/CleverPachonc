import os
from typing import Optional

# Queue types with common names
QUEUE_NAMES = {
    "RANKED_SOLO_5x5": "Ranked Solo/Duo",
    "RANKED_FLEX_SR": "Ranked Flex",
    "RANKED_TFT": "Ranked TFT",
    "NORMAL_DRAFT_5x5": "Normal Draft",
    "NORMAL_BLIND_5x5": "Normal Blind",
    "ARAM": "ARAM"
}

# Error messages
ERROR_MESSAGES = {
    "summoner_not_found": "Could not find summoner",
    "ranked_error": "Could not fetch ranked stats",
    "mastery_error": "Could not fetch mastery data",
    "match_error": "Could not fetch match history",
    "api_error": "Error connecting to Riot API"
}

# Region routing map
REGION_ROUTING = {
    'BR': 'https://br1.api.riotgames.com',
    'BR1': 'https://br1.api.riotgames.com',
    'EUN': 'https://eun1.api.riotgames.com',
    'EUN1': 'https://eun1.api.riotgames.com',
    'EUW': 'https://euw1.api.riotgames.com',
    'EUW1': 'https://euw1.api.riotgames.com',
    'JP': 'https://jp1.api.riotgames.com',
    'JP1': 'https://jp1.api.riotgames.com',
    'KR': 'https://kr.api.riotgames.com',
    'LA1': 'https://la1.api.riotgames.com',
    'LA2': 'https://la2.api.riotgames.com',
    'LAN': 'https://la1.api.riotgames.com',
    'LAS': 'https://la2.api.riotgames.com',
    'NA': 'https://na1.api.riotgames.com',
    'NA1': 'https://na1.api.riotgames.com',
    'OC': 'https://oc1.api.riotgames.com',
    'OC1': 'https://oc1.api.riotgames.com',
    'TR': 'https://tr1.api.riotgames.com',
    'TR1': 'https://tr1.api.riotgames.com',
    'RU': 'https://ru.api.riotgames.com'
}

def get_api_key() -> Optional[str]:
    """Get API key from environment variable"""
    return os.getenv('RIOT_API_KEY')

def set_api_key(key: str) -> None:
    """Set API key in environment variable"""
    os.environ['RIOT_API_KEY'] = key
