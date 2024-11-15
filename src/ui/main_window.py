"""
Main window module
"""
from . import ctk
from .search_page import SearchPage
from .stats_page import StatsPage
from .login_window import APIKeyWindow
from typing import Dict, List, Any, Type
from .controller import Controller
from ..utils.constants import APP_VERSION
from ..utils.image_utils import get_app_icon
from PIL import ImageTk
import os
import platform

class LeagueStatsApp(ctk.CTk, Controller):
    """Main application window"""
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title(f"Clever Pachonc v{APP_VERSION}")
        self.geometry("800x600")
        
        # Set window icon based on platform
        if platform.system() == "Windows":
            icon_path = os.path.abspath(os.path.join("src", "assets", "icons", "app_icon.ico"))
            self.after(200, lambda: self.iconbitmap(icon_path))
        
        # Create container
        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Initialize frames dictionary
        self.frames: Dict[Type, Any] = {}
        
        # Create frames
        for F in (SearchPage, StatsPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Show initial frame
        self.show_frame(SearchPage)
        
        # Show API key window
        self.after(100, self.show_api_key_window)

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

    def show_api_key_window(self) -> None:
        """Show API key input window"""
        APIKeyWindow(self)
