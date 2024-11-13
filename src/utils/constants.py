# API Key management
API_KEY = ""

def set_api_key(key: str) -> None:
    """Set the API key globally"""
    global API_KEY
    API_KEY = key
    print(f"API Key set in constants (length: {len(API_KEY)})")  # Debug print length instead

# Regions for server selection
REGIONS = [
    "BR1",
    "EUN1",
    "EUW1",
    "JP1",
    "KR",
    "LA1",
    "LA2",
    "NA1",
    "OC1",
    "TR1",
    "RU"
]

# Region routing values
REGION_ROUTING = {
    "BR1": "americas",
    "LA1": "americas",
    "LA2": "americas",
    "NA1": "americas",
    "EUN1": "europe",
    "EUW1": "europe",
    "TR1": "europe",
    "RU": "europe",
    "JP1": "asia",
    "KR": "asia",
    "OC1": "sea"
}

# Queue types
QUEUE_TYPES = {
    "RANKED_SOLO_5x5": "Ranked Solo/Duo",
    "RANKED_FLEX_SR": "Ranked Flex",
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

# Fun messages for when summoner is not in game
NOT_IN_GAME_MESSAGES = [
    "Looks like they're touching grass right now... 🌱",
    "Plot twist: They have a life outside League! 😱",
    "Probably making a sandwich between queue times 🥪",
    "404: Game not found. Have you tried turning the summoner on and off? 🔌",
    "Breaking news: Not everyone plays League 24/7! 📰",
    "They're taking a break... or their mom called for dinner 🍽️",
    "Currently in their gaming chair, but not gaming 🪑",
    "Legend says they're still in queue ⏳"
]

# Version
APP_VERSION = "α0.1.0"
APP_STAGE = "alpha"
