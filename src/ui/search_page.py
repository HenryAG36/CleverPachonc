"""
Search page module for summoner lookup
"""
from typing import Any, Dict, List
import customtkinter as ctk
import webbrowser
from . import BaseFrame
from ..api.riot_api import (
    get_summoner_by_name,
    get_ranked_stats,
    get_mastery_champions,
    get_match_history,
    get_match_details,
    get_summoner_data
)
from ..api.data_dragon import get_champion_map, get_item_data
from ..utils.constants import ERROR_MESSAGES
from ..utils.recent_searches import RecentSearches
import tkinter.messagebox as messagebox
from .components.loading_indicator import LoadingIndicator
from ..utils.cache_manager import CacheManager

class SearchPage(BaseFrame):
    """Search page for looking up summoner stats"""
    def __init__(self, parent: Any, controller: Any):
        super().__init__(parent, controller)
        self.recent_searches = RecentSearches()
        
        # Initialize data
        self.champion_map = get_champion_map()
        self.item_data = get_item_data()
        
        # Create main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Create title
        title = ctk.CTkLabel(
            self.main_frame,
            text="League Stats",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=20)
        
        # Create search frame
        search_frame = ctk.CTkFrame(self.main_frame)
        search_frame.pack(pady=20)
        
        # Create region dropdown
        self.region_var = ctk.StringVar(value="NA")
        self.region_dropdown = ctk.CTkOptionMenu(
            search_frame,
            values=["NA", "EUW", "EUNE", "KR", "BR", "LAN", "LAS", "OCE", "TR", "RU", "JP"],
            variable=self.region_var
        )
        self.region_dropdown.pack(side="left", padx=10)
        
        # Create search entry
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Enter summoner name...",
            width=200
        )
        self.search_entry.pack(side="left", padx=10)
        
        # Create search button
        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_summoner
        )
        search_button.pack(side="left", padx=10)
        
        # Create error label
        self.error_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            text_color="red"
        )
        self.error_label.pack(pady=10)
        
        # Create social links
        social_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        social_frame.pack(side="bottom", pady=20)
        
        twitch_button = ctk.CTkButton(
            social_frame,
            text="Follow on Twitch",
            command=self.open_twitch
        )
        twitch_button.pack(side="left", padx=5)
        
        # Add cache management button
        self.cache_manager = CacheManager()
        cache_button = ctk.CTkButton(
            social_frame,
            text="Clear Cache",
            command=self.clear_cache
        )
        cache_button.pack(side="left", padx=5)
        
        # Add recent searches frame
        self.recent_frame = ctk.CTkFrame(self)
        self.recent_frame.pack(pady=20, padx=20, fill="x")
        
        self.recent_label = ctk.CTkLabel(
            self.recent_frame,
            text="Recent Searches",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.recent_label.pack(pady=10)
        
        # Add clear button
        self.clear_button = ctk.CTkButton(
            self.recent_frame,
            text="Clear History",
            command=self.clear_recent_searches
        )
        self.clear_button.pack(pady=5)
        
        # Container for recent search buttons
        self.recent_buttons_frame = ctk.CTkFrame(self.recent_frame, fg_color="transparent")
        self.recent_buttons_frame.pack(fill="x", padx=10)
        
        # Load recent searches
        self.update_recent_searches()
    
    def update_recent_searches(self) -> None:
        """Update recent searches display"""
        # Clear existing buttons
        for widget in self.recent_buttons_frame.winfo_children():
            widget.destroy()
        
        # Add buttons for recent searches
        for search in self.recent_searches.get_searches():
            search_button = ctk.CTkButton(
                self.recent_buttons_frame,
                text=f"{search['summoner_name']} ({search['region']})",
                command=lambda s=search: self.load_recent_search(s)
            )
            search_button.pack(pady=2, fill="x")
    
    def load_recent_search(self, search: Dict) -> None:
        """Load a recent search"""
        self.search_entry.delete(0, 'end')
        self.search_entry.insert(0, search['summoner_name'])
        self.region_var.set(search['region'])
        self.search_summoner()
    
    def clear_recent_searches(self) -> None:
        """Clear recent searches"""
        self.recent_searches.clear_searches()
        self.update_recent_searches()
    
    def search_summoner(self) -> None:
        """Search for a summoner"""
        summoner_name = self.search_entry.get().strip()
        region = self.region_var.get().lower()
        
        if not summoner_name:
            return
        
        try:
            # Show loading indicator
            loading = LoadingIndicator(self, "Fetching summoner data...")
            
            # Fetch all data concurrently
            summoner_data, ranked_stats, mastery_data, match_history = get_summoner_data(
                summoner_name,
                region
            )
            
            # Add to recent searches
            self.recent_searches.add_search(summoner_name, region.upper())
            self.update_recent_searches()
            
            # Show stats page
            self.controller.show_stats_page(
                summoner_name,
                ranked_stats,
                mastery_data,
                self.champion_map,
                summoner_data,
                region,
                match_history,
                self.item_data
            )
            
        except Exception as e:
            error_message = str(e)
            messagebox.showerror("Error", error_message)
        finally:
            if 'loading' in locals():
                loading.destroy()
    
    def show_stats(
        self,
        summoner_name: str,
        ranked_stats: List[Dict[str, Any]],
        mastery_data: List[Dict[str, Any]],
        champion_map: Dict[str, str],
        summoner_data: Dict[str, Any],
        region: str,
        match_history: List[Dict[str, Any]],
        item_data: Dict[str, Any]
    ) -> None:
        """Show stats page with data"""
        self.controller.show_stats_page(
            summoner_name,
            ranked_stats,
            mastery_data,
            champion_map,
            summoner_data,
            region,
            match_history,
            item_data
        )
    
    def open_twitch(self) -> None:
        """Open Twitch channel"""
        webbrowser.open("https://twitch.tv/Kaseash")
    
    def clear_cache(self) -> None:
        """Clear old cache files"""
        try:
            files_removed, space_cleared = self.cache_manager.clear_old_files()
            if files_removed > 0:
                messagebox.showinfo(
                    "Cache Cleared",
                    f"Removed {files_removed} old files\nFreed {space_cleared / 1024 / 1024:.2f} MB"
                )
            else:
                messagebox.showinfo("Cache", "No old files to remove")
        except Exception as e:
            messagebox.showerror("Error", f"Error clearing cache: {e}")
