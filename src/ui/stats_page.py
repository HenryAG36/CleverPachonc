"""
Stats page module for displaying summoner statistics
"""
from . import (
    ctk,
    messagebox,
    Any,
    Dict,
    List,
    BaseFrame
)
from .controller import Controller

class StatsPage(BaseFrame):
    """Stats page for displaying summoner information"""
    def __init__(self, parent: Any, controller: Controller):
        super().__init__(parent, controller)
        
        # Create main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, padx=20, pady=20)
        
        # Back button
        self.back_button = ctk.CTkButton(
            self.main_frame,
            text="Back to Search",
            command=self.go_back
        )
        self.back_button.pack(pady=10)
        
        # Stats container
        self.stats_frame = ctk.CTkFrame(self.main_frame)
        self.stats_frame.pack(pady=20, fill="both", expand=True)
        
        # Summoner info
        self.summoner_frame = ctk.CTkFrame(self.stats_frame)
        self.summoner_frame.pack(pady=10, fill="x")
        
        self.summoner_name = ctk.CTkLabel(
            self.summoner_frame,
            text="",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.summoner_name.pack()
        
        # Ranked stats
        self.ranked_frame = ctk.CTkFrame(self.stats_frame)
        self.ranked_frame.pack(pady=10, fill="x")
        
        self.ranked_label = ctk.CTkLabel(
            self.ranked_frame,
            text="Ranked Stats",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.ranked_label.pack()
        
        # Champion mastery
        self.mastery_frame = ctk.CTkFrame(self.stats_frame)
        self.mastery_frame.pack(pady=10, fill="x")
        
        self.mastery_label = ctk.CTkLabel(
            self.mastery_frame,
            text="Champion Mastery",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.mastery_label.pack()
        
        # Match history container
        self.match_history_frame = ctk.CTkFrame(self.stats_frame)
        self.match_history_frame.pack(pady=10, fill="both", expand=True)
        
        self.match_history_label = ctk.CTkLabel(
            self.match_history_frame,
            text="Recent Games",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.match_history_label.pack(pady=5)
        
        # Container for individual match entries
        self.matches_container = ctk.CTkFrame(self.match_history_frame)
        self.matches_container.pack(fill="both", expand=True)

    def update_stats(
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
        """Update the stats display with new data"""
        # Update summoner name
        self.summoner_name.configure(text=f"{summoner_name} ({region})")
        
        # Update ranked stats
        if ranked_stats:
            ranked_text = self.format_ranked_stats(ranked_stats)
            self.ranked_label.configure(text=ranked_text)
        else:
            self.ranked_label.configure(text="No ranked data available")
        
        # Update mastery data
        if mastery_data:
            mastery_text = self.format_mastery_data(mastery_data, champion_map)
            self.mastery_label.configure(text=mastery_text)
        else:
            self.mastery_label.configure(text="No mastery data available")
        
        # Update match history
        self.format_match_history(match_history, summoner_data['puuid'], champion_map, item_data)

    def format_ranked_stats(self, ranked_stats: Dict[str, Any]) -> str:
        """Format ranked stats for display"""
        if not ranked_stats:
            return "No ranked data available"
        
        formatted_text = ""
        for queue in ranked_stats:
            # Get queue type (e.g., "RANKED_SOLO_5x5", "RANKED_FLEX_SR")
            queue_type = queue['queueType'].replace('_', ' ').title()
            
            # Format the stats
            tier = queue['tier'].title()
            rank = queue['rank']
            lp = queue['leaguePoints']
            wins = queue['wins']
            losses = queue['losses']
            total_games = wins + losses
            winrate = (wins / total_games * 100) if total_games > 0 else 0
            
            formatted_text += f"{queue_type}:\n"
            formatted_text += f"• {tier} {rank} ({lp} LP)\n"
            formatted_text += f"• {wins}W {losses}L ({winrate:.1f}% WR)\n\n"
        
        return formatted_text if formatted_text else "No ranked data available"

    def format_mastery_data(
        self,
        mastery_data: List[Dict[str, Any]],
        champion_map: Dict[str, str]
    ) -> str:
        """Format mastery data for display"""
        if not mastery_data:
            return "No mastery data available"
        
        # Sort by mastery points
        sorted_mastery = sorted(
            mastery_data,
            key=lambda x: x['championPoints'],
            reverse=True
        )
        
        # Take top 5 champions
        top_champions = sorted_mastery[:5]
        
        formatted_text = "Top 5 Champions:\n"
        for champ in top_champions:
            champ_id = str(champ['championId'])
            # Get champion name from map, fallback to ID if not found
            champ_name = champion_map.get(champ_id, f"Champion {champ_id}")
            points = champ['championPoints']
            level = champ['championLevel']
            
            # Format points with commas for readability
            formatted_points = f"{points:,}"
            
            formatted_text += f"• {champ_name} (Level {level})\n"
            formatted_text += f"  {formatted_points} points\n"
        
        return formatted_text

    def format_match_history(
        self,
        matches: List[Dict[str, Any]],
        puuid: str,
        champion_map: Dict[str, str],
        item_data: Dict[str, Any]
    ) -> None:
        """Format and display match history"""
        # Clear previous matches
        for widget in self.matches_container.winfo_children():
            widget.destroy()
        
        if not matches:
            no_games = ctk.CTkLabel(
                self.matches_container,
                text="No recent games found"
            )
            no_games.pack(pady=5)
            return
        
        for match in matches:
            # Get player data from match
            player = next(p for p in match['info']['participants'] if p['puuid'] == puuid)
            
            # Create match frame
            match_frame = ctk.CTkFrame(self.matches_container)
            match_frame.pack(pady=5, padx=10, fill="x")
            
            # Result and champion
            result = "Victory" if player['win'] else "Defeat"
            result_color = "green" if player['win'] else "red"
            champ_id = str(player['championId'])
            champ_name = champion_map.get(champ_id, f"Champion {champ_id}")
            
            result_label = ctk.CTkLabel(
                match_frame,
                text=f"{result} - {champ_name}",
                text_color=result_color,
                font=ctk.CTkFont(weight="bold")
            )
            result_label.pack(side="left", padx=10)
            
            # KDA
            kda = f"{player['kills']}/{player['deaths']}/{player['assists']}"
            kda_ratio = (player['kills'] + player['assists']) / max(1, player['deaths'])
            kda_label = ctk.CTkLabel(
                match_frame,
                text=f"KDA: {kda} ({kda_ratio:.2f})"
            )
            kda_label.pack(side="left", padx=10)
            
            # CS and game duration
            cs = player['totalMinionsKilled'] + player.get('neutralMinionsKilled', 0)
            minutes = match['info']['gameDuration'] / 60
            cs_per_min = cs / minutes
            cs_label = ctk.CTkLabel(
                match_frame,
                text=f"CS: {cs} ({cs_per_min:.1f}/min)"
            )
            cs_label.pack(side="left", padx=10)
            
            # Items
            items_frame = ctk.CTkFrame(match_frame)
            items_frame.pack(side="right", padx=10)
            
            for i in range(6):
                item_id = str(player.get(f'item{i}', 0))
                if item_id != "0" and item_id in item_data:
                    item_name = item_data[item_id]['name']
                    item_label = ctk.CTkLabel(
                        items_frame,
                        text=f"•{item_name}",
                        font=ctk.CTkFont(size=10)
                    )
                    item_label.pack(side="left", padx=2)

    def go_back(self) -> None:
        """Return to search page"""
        # Clear current stats
        self.summoner_name.configure(text="")
        self.ranked_label.configure(text="Ranked Stats")
        self.mastery_label.configure(text="Champion Mastery")
        
        # Let the controller handle the page switch
        self.controller.show_search_page()
