import os
from typing import Optional

QUEUE_NAMES = {
    "RANKED_SOLO_5x5": "Ranked Solo/Duo",
    "RANKED_FLEX_SR": "Ranked Flex",
    "RANKED_TFT": "Ranked TFT",
}

# Platform base URLs (for league/mastery/summoner endpoints)
REGION_ROUTING = {
    'BR': 'https://br1.api.riotgames.com',
    'BR1': 'https://br1.api.riotgames.com',
    'EUNE': 'https://eun1.api.riotgames.com',
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
    'OC1': 'https://oc1.api.riotgames.com',
    'OCE': 'https://oc1.api.riotgames.com',
    'TR': 'https://tr1.api.riotgames.com',
    'TR1': 'https://tr1.api.riotgames.com',
    'RU': 'https://ru.api.riotgames.com',
}

# Continental routing for account/match v5 endpoints
MATCH_ROUTING = {
    'NA': 'americas', 'NA1': 'americas',
    'BR': 'americas', 'BR1': 'americas',
    'LAN': 'americas', 'LA1': 'americas',
    'LAS': 'americas', 'LA2': 'americas',
    'OCE': 'americas', 'OC1': 'americas',
    'KR': 'asia',
    'JP': 'asia', 'JP1': 'asia',
    'EUW': 'europe', 'EUW1': 'europe',
    'EUNE': 'europe', 'EUN1': 'europe',
    'TR': 'europe', 'TR1': 'europe',
    'RU': 'europe',
}

REQUEST_TIMEOUT = 10
RETRY_ATTEMPTS = 3
RETRY_BACKOFF = 0.5


def get_api_key() -> Optional[str]:
    return os.getenv('RIOT_API_KEY')
