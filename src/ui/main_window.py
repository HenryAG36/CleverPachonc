"""
Main window module
"""
from typing import Dict, Any, Type, List
import customtkinter as ctk
from .search_page import SearchPage
from .stats_page import StatsPage
from .api_key_dialog import APIKeyDialog
from ..utils.constants import set_api_key, get_api_key

class Controller:
    """Base controller interface"""
    def show_search_page(self) -> None:
        pass
    
    def show_stats_page(
        self,
        summoner_name: str,
        ranked_stats: Dict[str, Any],
        mastery_data: List[Dict[str, Any]],
        champion_map: Dict[str, str],
        summoner_data: Dict[str, Any],
        region: str,
        match_history: List[Dict[str, Any]],
        item_data: Dict[str, Any]
    ) -> None:
        pass

class LeagueStatsApp(ctk.CTk, Controller):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("League Stats")
        self.geometry("1280x720")
        self.minsize(1280, 720)
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Initialize frames dictionary
        self.frames = {}
        
        # Create frames
        for F in (SearchPage, StatsPage):
            frame = F(self, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Show initial frame
        self.show_search_page()
        
        # Check for API key
        if not get_api_key():
            self.after(100, self.get_api_key)  # Show dialog after window is ready
    
    def show_frame(self, cont: Type) -> None:
        """Show a frame for the given page class"""
        frame = self.frames[cont]
        frame.tkraise()
    
    def show_search_page(self) -> None:
        """Show search page"""
        self.show_frame(SearchPage)
    
    def show_stats_page(
        self,
        summoner_name: str,
        ranked_stats: Dict[str, Any],
        mastery_data: List[Dict[str, Any]],
        champion_map: Dict[str, str],
        summoner_data: Dict[str, Any],
        region: str,
        match_history: List[Dict[str, Any]],
        item_data: Dict[str, Any]
    ) -> None:
        """Show stats page with data"""
        stats_page = self.frames[StatsPage]
        stats_page.update_stats(
            summoner_name,
            ranked_stats,
            mastery_data,
            champion_map,
            summoner_data,
            region,
            match_history,
            item_data
        )
        self.show_frame(StatsPage)
    
    def get_api_key(self) -> None:
        """Get API key from user"""
        dialog = APIKeyDialog(self)
        self.wait_window(dialog)
        if dialog.api_key:
            set_api_key(dialog.api_key)
