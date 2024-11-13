import requests
from typing import Dict, Any, Optional

def get_latest_version() -> str:
    """Get the latest version of Data Dragon"""
    version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    try:
        response = requests.get(version_url)
        response.raise_for_status()
        return response.json()[0]
    except Exception as e:
        print(f"Error getting latest version: {e}")
        return "13.24.1"  # Fallback version

def get_champion_data() -> Optional[Dict[str, Any]]:
    """Get champion data from Data Dragon"""
    version = get_latest_version()
    champion_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    
    try:
        response = requests.get(champion_url)
        response.raise_for_status()
        return response.json()['data']
    except Exception as e:
        print(f"Error getting champion data: {e}")
        return None

def get_rune_data() -> Optional[Dict[str, Any]]:
    """Get rune data from Data Dragon"""
    version = get_latest_version()
    runes_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/runesReforged.json"
    
    try:
        response = requests.get(runes_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting rune data: {e}")
        return None

def get_item_data() -> Optional[Dict[str, Any]]:
    """Get item data from Data Dragon"""
    version = get_latest_version()
    items_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"
    
    try:
        response = requests.get(items_url)
        response.raise_for_status()
        return response.json()['data']
    except Exception as e:
        print(f"Error getting item data: {e}")
        return None

def get_asset_url(asset_type: str, asset_name: str) -> str:
    """
    Get the URL for various game assets
    
    asset_type: 'champion', 'item', 'rune', 'profileicon'
    asset_name: Name or ID of the asset
    """
    version = get_latest_version()
    base_url = f"https://ddragon.leagueoflegends.com/cdn/{version}"
    
    urls = {
        'champion': f"{base_url}/img/champion/{asset_name}.png",
        'item': f"{base_url}/img/item/{asset_name}.png",
        'rune': f"{base_url}/img/rune/{asset_name}.png",
        'profileicon': f"{base_url}/img/profileicon/{asset_name}.png"
    }
    
    return urls.get(asset_type, '')
