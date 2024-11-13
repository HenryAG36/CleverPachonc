import requests
from typing import Dict, List, Any, Optional
from ..utils.constants import API_KEY, REGION_ROUTING

def get_summoner_data(summoner_name: str, tag: str, region: str = "na1") -> Optional[Dict[str, Any]]:
    """Get basic summoner information"""
    from ..utils.constants import API_KEY  # Import here to get latest value
    
    if not API_KEY:
        print("No API key set!")
        return None
        
    base_url = f"https://{region}.api.riotgames.com"
    headers = {"X-Riot-Token": API_KEY}
    
    try:
        # Get account info using Riot ID (name + tag)
        platform = REGION_ROUTING.get(region, 'americas')
        account_url = f"https://{platform}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}"
        print(f"Using API key (length: {len(API_KEY)})")  # Debug print
        
        account_response = requests.get(account_url, headers=headers)
        account_response.raise_for_status()
        account_data = account_response.json()
        
        # Get summoner data using PUUID
        summoner_url = f"{base_url}/lol/summoner/v4/summoners/by-puuid/{account_data['puuid']}"
        summoner_response = requests.get(summoner_url, headers=headers)
        summoner_response.raise_for_status()
        summoner_data = summoner_response.json()
        
        # Combine the data
        return {**summoner_data, **account_data}
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(f"API Key error (length: {len(API_KEY)})")
            return None
        elif e.response.status_code == 404:
            print(f"Summoner not found: {summoner_name}#{tag}")
            return None
        else:
            print(f"HTTP Error: {e}")
            return None
    except Exception as e:
        print(f"Error getting summoner data: {e}")
        return None

def get_ranked_stats(summoner_id: str, region: str = "na1") -> Optional[Dict[str, Any]]:
    """Get ranked stats for a summoner"""
    from ..utils.constants import API_KEY  # Import here to get latest value
    
    url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
    headers = {"X-Riot-Token": API_KEY}
    
    try:
        print(f"Getting ranked stats with API key (length: {len(API_KEY)})")  # Debug print
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting ranked stats: {e}")
        return None

def get_mastery_champions(puuid: str, region: str = "na1") -> Optional[List[Dict[str, Any]]]:
    """Get champion mastery data"""
    from ..utils.constants import API_KEY  # Import here to get latest value
    
    url = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
    headers = {"X-Riot-Token": API_KEY}
    
    try:
        print(f"Getting mastery data with API key (length: {len(API_KEY)})")  # Debug print
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting mastery data: {e}")
        return None

def get_match_history(puuid: str, region: str = "na1", count: int = 10) -> Optional[List[Dict[str, Any]]]:
    """Get match history for a summoner"""
    from ..utils.constants import API_KEY  # Import here to get latest value
    
    platform = REGION_ROUTING.get(region, 'americas')
    headers = {"X-Riot-Token": API_KEY}
    
    try:
        # Get match IDs
        matches_url = f"https://{platform}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
        print(f"Getting match history with API key (length: {len(API_KEY)})")  # Debug print
        match_ids_response = requests.get(matches_url, headers=headers)
        match_ids_response.raise_for_status()
        match_ids = match_ids_response.json()
        
        # Get detailed match data
        matches_data = []
        for match_id in match_ids:
            match_url = f"https://{platform}.api.riotgames.com/lol/match/v5/matches/{match_id}"
            match_response = requests.get(match_url, headers=headers)
            match_response.raise_for_status()
            matches_data.append(match_response.json())
            
        return matches_data
    except Exception as e:
        print(f"Error fetching match history: {e}")
        return None

def get_live_game(summoner_id: str, region: str = "na1") -> Optional[Dict[str, Any]]:
    """Get current game information"""
    url = f"https://{region}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summoner_id}"
    headers = {"X-Riot-Token": API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            return {"message": "Not in game"}
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting live game: {e}")
        return None
