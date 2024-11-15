"""
Utility functions for handling images
"""
import requests
from PIL import Image
import customtkinter as ctk
from io import BytesIO
from typing import Optional
import os

def get_champion_icon(champion_id: str, size: tuple = (50, 50)) -> Optional[ctk.CTkImage]:
    """Get champion icon from Data Dragon"""
    try:
        # Create cache directory if it doesn't exist
        cache_dir = os.path.join("src", "cache", "champions")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Check cache first
        cache_path = os.path.join(cache_dir, f"{champion_id}.png")
        if os.path.exists(cache_path):
            img = Image.open(cache_path)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        
        # If not in cache, download it
        version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champion_id}.png"
        
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        
        # Save to cache
        img.save(cache_path)
        
        # Return CTkImage
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        
    except Exception as e:
        print(f"Error loading champion icon: {e}")
        return None

def get_rank_icon(rank: str, size: tuple = (50, 50)) -> Optional[ctk.CTkImage]:
    """Get rank icon from local assets"""
    try:
        cache_dir = os.path.join("src", "cache", "ranks")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Check cache first
        cache_path = os.path.join(cache_dir, f"{rank.lower()}.png")
        if os.path.exists(cache_path):
            img = Image.open(cache_path)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
            
        # If not in cache, use default rank icon
        default_path = os.path.join("src", "assets", "ranks", "unranked.png")
        if os.path.exists(default_path):
            img = Image.open(default_path)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
            
        return None
        
    except Exception as e:
        print(f"Error loading rank icon: {e}")
        return None

def get_item_icon(item_id: str, size: tuple = (50, 50)) -> Optional[ctk.CTkImage]:
    """Get item icon from Data Dragon"""
    try:
        # Create cache directory if it doesn't exist
        cache_dir = os.path.join("src", "cache", "items")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Check cache first
        cache_path = os.path.join(cache_dir, f"{item_id}.png")
        if os.path.exists(cache_path):
            img = Image.open(cache_path)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        
        # If not in cache, download it
        version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{item_id}.png"
        
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        
        # Save to cache
        img.save(cache_path)
        
        # Return CTkImage
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        
    except Exception as e:
        print(f"Error loading item icon: {e}")
        return None

def get_pachonc_icon(size: tuple = (32, 32)) -> Optional[ctk.CTkImage]:
    """Get Pink Pachonc icon for the app"""
    try:
        # Create cache directory if it doesn't exist
        cache_dir = os.path.join("src", "cache", "app")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Check cache first
        cache_path = os.path.join(cache_dir, "pink_pachonc.png")
        if os.path.exists(cache_path):
            img = Image.open(cache_path)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        
        # If not in cache, download it
        url = "https://raw.communitydragon.org/latest/game/assets/characters/tft/littlelegends/pachonc/hud/tft_pachonc_pink.png"
        
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        
        # Save to cache
        img.save(cache_path)
        
        # Return CTkImage
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        
    except Exception as e:
        print(f"Error loading Pachonc icon: {e}")
        return None

def setup_app_icon():
    """One-time setup to download and save the app icon"""
    try:
        # Create assets directory if it doesn't exist
        icons_dir = os.path.join("src", "assets", "icons")
        os.makedirs(icons_dir, exist_ok=True)
        
        icon_path = os.path.join(icons_dir, "app_icon.png")
        if not os.path.exists(icon_path):
            url = "https://raw.communitydragon.org/latest/game/assets/characters/tft/littlelegends/pachonc/hud/tft_pachonc_pink.png"
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            img.save(icon_path)
            print("✨ App icon downloaded successfully!")
    except Exception as e:
        print(f"Error setting up app icon: {e}")

def get_app_icon(size: tuple = (32, 32)) -> Optional[ctk.CTkImage]:
    """Get the app icon from assets"""
    try:
        icon_path = os.path.join("src", "assets", "icons", "app_icon.png")
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        return None
    except Exception as e:
        print(f"Error loading app icon: {e}")
        return None 