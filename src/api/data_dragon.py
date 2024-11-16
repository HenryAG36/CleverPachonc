from typing import Optional, Dict, Any
import requests

def get_latest_version() -> str:
    """Get latest game version"""
    try:
        response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
        response.raise_for_status()
        return response.json()[0]
    except Exception as e:
        print(f"Error getting latest version: {e}")
        return "13.24.1"  # Fallback version

def get_champion_map() -> Optional[Dict[str, str]]:
    """Get champion ID to name mapping"""
    version = get_latest_version()
    champions_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    
    try:
        response = requests.get(champions_url)
        response.raise_for_status()
        data = response.json()['data']
        
        # Create id -> name mapping
        return {
            champ_data['key']: champ_name 
            for champ_name, champ_data in data.items()
        }
    except Exception as e:
        print(f"Error getting champion data: {e}")
        return None

def get_item_data() -> Optional[Dict[str, Any]]:
    """Get item data from Data Dragon"""
    version = get_latest_version()
    items_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"
    
    try:
        response = requests.get(items_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting item data: {e}")
        return None

def get_asset_url(asset_type: str, asset_name: str) -> str:
    """
    Get the URL for various game assets
    
    asset_type: 'champion', 'item', 'profileicon'
    asset_name: Name or ID of the asset
    """
    version = get_latest_version()
    base_url = f"https://ddragon.leagueoflegends.com/cdn/{version}"
    
    urls = {
        'champion': f"{base_url}/img/champion/{asset_name}.png",
        'item': f"{base_url}/img/item/{asset_name}.png",
        'profileicon': f"{base_url}/img/profileicon/{asset_name}.png"
    }
    
    return urls.get(asset_type, '')
