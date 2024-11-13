"""
Search page module for summoner lookup
"""
from . import (
    ctk,
    messagebox,
    webbrowser,
    Any,
    BaseFrame
)
from ..api.riot_api import (
    get_summoner_data,
    get_ranked_stats,
    get_mastery_champions,
    get_match_history
)
from ..utils.constants import (
    REGIONS,
    REGION_ROUTING
)

class SearchPage(BaseFrame):
    """Search page for looking up summoner stats"""
    def __init__(self, parent: Any, controller: Any):
        super().__init__(parent, controller)
        
        # Create main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, padx=20, pady=20)
        
        # Title
        self.title = ctk.CTkLabel(
            self.main_frame,
            text="League Stats Tracker",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.pack(pady=20)
        
        # Search frame
        self.search_frame = ctk.CTkFrame(self.main_frame)
        self.search_frame.pack(pady=20)
        
        # Name entry
        self.name_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Summoner Name",
            width=200
        )
        self.name_entry.pack(side="left", padx=5)
        
        # Tag entry
        self.tag_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="#TAG",
            width=80
        )
        self.tag_entry.pack(side="left", padx=5)
        
        # Region selector
        self.region_var = ctk.StringVar(value=REGIONS[0])
        self.region_selector = ctk.CTkOptionMenu(
            self.search_frame,
            values=REGIONS,
            variable=self.region_var,
            width=100
        )
        self.region_selector.pack(side="left", padx=5)
        
        # Search button
        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Search",
            command=self.search_summoner
        )
        self.search_button.pack(side="left", padx=5)

        # Help text
        self.help_text = ctk.CTkLabel(
            self.main_frame,
            text="Enter Riot ID (e.g., Kaseash#NA1) and select server region",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.help_text.pack(pady=(0, 20))

        # Credits frame
        self.credits_frame = ctk.CTkFrame(self.main_frame)
        self.credits_frame.pack(pady=20)

        # Social media links
        self.social_links = ctk.CTkLabel(
            self.credits_frame,
            text="Twitch/TikTok/YouTube: @Kaseash",
            font=ctk.CTkFont(size=12),
            text_color=("purple", "purple")
        )
        self.social_links.pack(pady=(0,5))
        self.social_links.bind("<Button-1>", self.handle_social_click)

    def handle_social_click(self, _: Any) -> None:
        """Handle social media link click"""
        self.open_twitch()

    def search_summoner(self) -> None:
        """Search for summoner stats"""
        summoner_name = self.name_entry.get().strip()
        tag = self.tag_entry.get().strip()
        region = self.region_var.get()
        
        # Validate region
        if region not in REGION_ROUTING:
            messagebox.showerror(
                "Error",
                f"Invalid region: {region}"
            )
            return
        
        if not summoner_name or not tag:
            messagebox.showerror(
                "Error",
                "Please enter both summoner name and tag!"
            )
            return
        
        try:
            # Get summoner data
            summoner_data = get_summoner_data(summoner_name, tag, region)
            if not summoner_data:
                messagebox.showerror(
                    "Error",
                    "Could not find summoner. Please check the name and tag."
                )
                return
            
            # Get ranked stats and mastery data
            ranked_stats = get_ranked_stats(summoner_data['id'], region)
            mastery_data = get_mastery_champions(summoner_data['puuid'], region)
            
            # Get match history
            match_history = get_match_history(summoner_data['puuid'], region, count=10)
            
            # Get champion data from Data Dragon
            from ..api.data_dragon import get_champion_data, get_item_data
            champion_data = get_champion_data()
            item_data = get_item_data()
            
            # Create champion ID to name mapping
            champion_map = {}
            if champion_data:
                for champ_name, champ_info in champion_data.items():
                    champion_map[champ_info['key']] = champ_name
            
            # Show stats page with all data
            self.show_stats(
                summoner_name,
                ranked_stats,
                mastery_data,
                champion_map,
                summoner_data,
                region,
                match_history,
                item_data
            )
            
        except Exception as error:
            if "401" in str(error):
                messagebox.showerror(
                    "Error",
                    "API Key error. Please check:\n" +
                    "1. Key is valid and not expired\n" +
                    "2. Key was copied correctly\n" +
                    "Get a new key at: developer.riotgames.com"
                )
            else:
                messagebox.showerror(
                    "Error", 
                    f"Could not find summoner: {str(error)}"
                )

    def show_stats(
        self,
        summoner_name: str,
        ranked_stats: Any,
        mastery_data: Any,
        champion_map: dict,
        summoner_data: Any,
        region: str,
        match_history: Any,
        item_data: Any
    ) -> None:
        """Show stats page with data"""
        # Let the controller handle the page switch
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
