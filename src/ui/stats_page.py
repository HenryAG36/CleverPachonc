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
import tkinter as tk
from .controller import Controller
from ..utils.image_utils import get_champion_icon, get_rank_icon, get_item_icon

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
        self.ranked_label.pack(pady=5)
        
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
            self.format_ranked_stats(ranked_stats)
        else:
            self.ranked_label.configure(text="No ranked data available")
        
        # Update mastery data
        if mastery_data:
            self.format_mastery_data(mastery_data, champion_map)
        else:
            self.mastery_label.configure(text="No mastery data available")
        
        # Update match history
        self.format_match_history(match_history, summoner_data['puuid'], champion_map, item_data)

    def format_ranked_stats(self, ranked_stats: Dict[str, Any]) -> None:
        """Format ranked stats for display"""
        if not ranked_stats:
            return "No ranked data available"
        
        # Clear previous widgets
        for widget in self.ranked_frame.winfo_children():
            widget.destroy()
        
        self.ranked_label = ctk.CTkLabel(
            self.ranked_frame,
            text="Ranked Stats",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.ranked_label.pack(pady=5)
        
        for queue in ranked_stats:
            # Create frame for each queue
            queue_frame = ctk.CTkFrame(self.ranked_frame)
            queue_frame.pack(fill="x", pady=2)
            
            # Get queue info
            queue_type = queue['queueType'].replace('_', ' ').title()
            tier = queue['tier'].title()
            rank = queue['rank']
            lp = queue['leaguePoints']
            wins = queue['wins']
            losses = queue['losses']
            total_games = wins + losses
            winrate = (wins / total_games * 100) if total_games > 0 else 0
            
            # Get rank icon
            icon = get_rank_icon(tier)
            if icon:
                icon_label = ctk.CTkLabel(queue_frame, image=icon, text="")
                icon_label.image = icon  # Keep reference
                icon_label.pack(side="left", padx=5)
            
            # Queue info
            info_frame = ctk.CTkFrame(queue_frame)
            info_frame.pack(side="left", fill="x", expand=True)
            
            queue_label = ctk.CTkLabel(
                info_frame,
                text=f"{queue_type}",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            queue_label.pack(anchor="w")
            
            rank_label = ctk.CTkLabel(
                info_frame,
                text=f"{tier} {rank} ({lp} LP)"
            )
            rank_label.pack(anchor="w")
            
            stats_label = ctk.CTkLabel(
                info_frame,
                text=f"{wins}W {losses}L ({winrate:.1f}% WR)"
            )
            stats_label.pack(anchor="w")

    def format_mastery_data(
        self,
        mastery_data: List[Dict[str, Any]],
        champion_map: Dict[str, str]
    ) -> None:
        """Format mastery data for display"""
        if not mastery_data:
            return "No mastery data available"
        
        # Clear previous widgets
        for widget in self.mastery_frame.winfo_children():
            widget.destroy()
        
        # Sort by mastery points
        sorted_mastery = sorted(
            mastery_data,
            key=lambda x: x['championPoints'],
            reverse=True
        )[:5]  # Top 5 champions
        
        for champ in sorted_mastery:
            # Create frame for each champion
            champ_frame = ctk.CTkFrame(self.mastery_frame)
            champ_frame.pack(fill="x", pady=2)
            
            # Get champion info
            champ_id = str(champ['championId'])
            champ_name = champion_map.get(champ_id, f"Champion {champ_id}")
            points = champ['championPoints']
            level = champ['championLevel']
            
            # Get champion icon
            icon = get_champion_icon(champ_name)
            if icon:
                icon_label = ctk.CTkLabel(champ_frame, image=icon, text="")
                icon_label.image = icon  # Keep reference
                icon_label.pack(side="left", padx=5)
            
            # Champion info
            info_frame = ctk.CTkFrame(champ_frame)
            info_frame.pack(side="left", fill="x", expand=True)
            
            name_label = ctk.CTkLabel(
                info_frame,
                text=f"{champ_name}",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            name_label.pack(anchor="w")
            
            stats_label = ctk.CTkLabel(
                info_frame,
                text=f"Level {level} • {points:,} points"
            )
            stats_label.pack(anchor="w")

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
            
            # Get champion icon
            icon = get_champion_icon(champ_name, size=(40, 40))
            if icon:
                icon_label = ctk.CTkLabel(match_frame, image=icon, text="")
                icon_label.image = icon  # Keep reference
                icon_label.pack(side="left", padx=5)
            
            # Create info frame
            info_frame = ctk.CTkFrame(match_frame)
            info_frame.pack(side="left", fill="x", expand=True, padx=5)
            
            # Result and champion name
            result_label = ctk.CTkLabel(
                info_frame,
                text=f"{result} - {champ_name}",
                text_color=result_color,
                font=ctk.CTkFont(weight="bold")
            )
            result_label.pack(anchor="w")
            
            # Stats frame
            stats_frame = ctk.CTkFrame(info_frame)
            stats_frame.pack(fill="x", expand=True)
            
            # KDA and CS
            kda = f"{player['kills']}/{player['deaths']}/{player['assists']}"
            kda_ratio = (player['kills'] + player['assists']) / max(1, player['deaths'])
            cs = player['totalMinionsKilled'] + player.get('neutralMinionsKilled', 0)
            minutes = match['info']['gameDuration'] / 60
            cs_per_min = cs / minutes
            
            stats_label = ctk.CTkLabel(
                stats_frame,
                text=f"KDA: {kda} ({kda_ratio:.2f}) • CS: {cs} ({cs_per_min:.1f}/min)",
                font=ctk.CTkFont(size=12)
            )
            stats_label.pack(side="left", padx=10)
            
            # Items frame
            items_frame = ctk.CTkFrame(match_frame)
            items_frame.pack(side="right", padx=10)
            
            # Add item icons
            for i in range(6):
                item_id = str(player.get(f'item{i}', 0))
                if item_id != "0" and item_id in item_data:
                    item_icon = get_item_icon(item_id)
                    if item_icon:
                        item_label = ctk.CTkLabel(
                            items_frame,
                            image=item_icon,
                            text="",
                            cursor="hand2"
                        )
                        item_label.image = item_icon  # Keep reference
                        item_label.pack(side="left", padx=2)
                        
                        # Add tooltip with item name
                        item_name = item_data[item_id]['name']
                        tooltip_text = f"{item_name}"
                        item_label.bind("<Enter>", lambda e, text=tooltip_text: self.show_tooltip(e, text))
                        item_label.bind("<Leave>", self.hide_tooltip)

    def go_back(self) -> None:
        """Return to search page"""
        # Clear current stats
        self.summoner_name.configure(text="")
        self.ranked_label.configure(text="Ranked Stats")
        self.mastery_label.configure(text="Champion Mastery")
        
        # Let the controller handle the page switch
        self.controller.show_search_page()

    def show_tooltip(self, event, text: str) -> None:
        """Show tooltip on hover"""
        x, y, _, _ = event.widget.bbox("insert")
        x += event.widget.winfo_rootx() + 25
        y += event.widget.winfo_rooty() + 20
        
        # Create tooltip window
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Configure tooltip style
        frame = tk.Frame(
            self.tooltip,
            background="#1a1a1a",
            borderwidth=1,
            relief="solid"
        )
        frame.pack(fill="both", expand=True)
        
        label = tk.Label(
            frame,
            text=text,
            justify='left',
            background="#1a1a1a",
            foreground="#e0e0e0",
            font=("Segoe UI", 10),
            wraplength=250,
            padx=8,
            pady=4
        )
        label.pack()
        
        # Add subtle shadow effect
        self.tooltip.lift()
        self.tooltip.attributes('-alpha', 0.95)

    def hide_tooltip(self, event=None) -> None:
        """Hide tooltip"""
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
