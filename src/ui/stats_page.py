"""
Stats page module for displaying summoner statistics
"""
from typing import Any, Dict, List, Optional
import customtkinter as ctk
from PIL import Image
import requests
from io import BytesIO
from . import BaseFrame
from ..utils.constants import QUEUE_NAMES
from ..utils.image_utils import load_images_batch
from .components import LoadingIndicator
from ..utils.debug import DEBUG
import time
from base64 import b64decode

class StatsPage(BaseFrame):
    """Stats page for displaying summoner information"""
    def __init__(self, parent: Any, controller: Any):
        super().__init__(parent, controller)
        self.image_cache = {}
        
        # Create main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Create tabview
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Add tabs
        self.profile_tab = self.tabview.add("Profile")
        self.matches_tab = self.tabview.add("Match History")
        
        # Profile tab content frame (make it scrollable)
        self.profile_frame = ctk.CTkScrollableFrame(self.profile_tab, fg_color="transparent")
        self.profile_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create labels for profile info
        self.summoner_label = ctk.CTkLabel(
            self.profile_frame,
            text="",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.summoner_label.pack(pady=10)
        
        # Create ranked frame
        self.ranked_frame = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
        self.ranked_frame.pack(pady=10, fill="x")
        
        self.ranked_label = ctk.CTkLabel(
            self.ranked_frame,
            text="",
            font=ctk.CTkFont(size=16)
        )
        self.ranked_label.pack(pady=5)
        
        # Create mastery frame
        self.mastery_frame = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
        self.mastery_frame.pack(pady=10, fill="x")
        
        self.mastery_label = ctk.CTkLabel(
            self.mastery_frame,
            text="",
            font=ctk.CTkFont(size=16)
        )
        self.mastery_label.pack(pady=5)
        
        # Match history tab content
        self.matches_frame = ctk.CTkScrollableFrame(
            self.matches_tab,
            fg_color="transparent"
        )
        self.matches_frame.pack(expand=True, fill="both", padx=10, pady=10)

    def load_image(self, url: str, size: tuple = (30, 30), aspect_ratio: Optional[float] = None) -> Optional[ctk.CTkImage]:
        """Load and cache an image from URL maintaining aspect ratio"""
        try:
            if url in self.image_cache:
                return self.image_cache[url]

            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            
            if aspect_ratio:
                # Use specified aspect ratio
                target_height = size[1]
                target_width = int(target_height * aspect_ratio)
                new_size = (target_width, target_height)
            else:
                # Calculate aspect ratio from original image
                aspect_ratio = image.width / image.height
                target_size = size[0]
                new_size = (target_size, int(target_size / aspect_ratio))
            
            # Resize maintaining aspect ratio
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=new_size)
            self.image_cache[url] = ctk_image
            return ctk_image
        except Exception as e:
            print(f"Error loading image from {url}: {e}")
            return None

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
        """Update all stats"""
        # Update profile info
        self.update_profile(summoner_name, ranked_stats, mastery_data, champion_map, summoner_data)
        
        # Update match history
        self.update_match_history(match_history, summoner_data['puuid'], champion_map, item_data)
        
        # Switch to profile tab by default
        self.tabview.set("Profile")

    def update_profile(
        self,
        summoner_name: str,
        ranked_stats: List[Dict[str, Any]],
        mastery_data: List[Dict[str, Any]],
        champion_map: Dict[str, str],
        summoner_data: Dict[str, Any]
    ) -> None:
        """Update profile info"""
        try:
            # Clear existing content
            for widget in self.profile_frame.winfo_children():
                widget.destroy()
            
            # Main container
            main_container = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
            main_container.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Summoner name at the top
            ctk.CTkLabel(
                main_container,
                text=summoner_name,
                font=ctk.CTkFont(size=24, weight="bold")
            ).pack(pady=(0, 20))
            
            # Create horizontal container for ranked and mastery
            content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
            content_frame.pack(expand=True, fill="both")
            
            # Left side - Ranked Stats
            ranked_frame = ctk.CTkFrame(content_frame)
            ranked_frame.pack(side="left", fill="both", expand=True, padx=10)
            
            ctk.CTkLabel(
                ranked_frame,
                text="Ranked Stats",
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(pady=10)
            
            # Format ranked stats
            for queue in ranked_stats:
                queue_frame = ctk.CTkFrame(ranked_frame)
                queue_frame.pack(pady=5, padx=10, fill="x")
                
                # Queue type
                queue_type = self.get_queue_display_name(queue['queueType'])
                ctk.CTkLabel(
                    queue_frame,
                    text=queue_type,
                    font=ctk.CTkFont(size=14, weight="bold")
                ).pack(pady=2)
                
                # Rank emblem
                rank_url = f"https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/ranked-emblem/emblem-{queue['tier'].lower()}.png"
                height = 180
                width = int(height * 1.8)  # Perfect aspect ratio we found
                rank_img = self.load_image(rank_url, size=(width, height))
                if rank_img:
                    ctk.CTkLabel(queue_frame, text="", image=rank_img).pack(pady=2)
                
                # Rank info
                rank_text = f"{queue['tier']} {queue['rank']} - {queue['leaguePoints']} LP"
                ctk.CTkLabel(
                    queue_frame,
                    text=rank_text,
                    font=ctk.CTkFont(size=12)
                ).pack(pady=2)
                
                # Win/Loss and Streak
                wins = queue['wins']
                losses = queue['losses']
                total_games = wins + losses
                winrate = (wins / total_games * 100) if total_games > 0 else 0
                
                stats_text = f"W: {wins} L: {losses} ({winrate:.1f}%)"
                if queue.get('streak', 0) != 0:
                    streak = queue.get('streak', 0)
                    streak_text = f" | {abs(streak)}L" if streak < 0 else f" | {streak}W"
                    stats_text += streak_text
                
                ctk.CTkLabel(
                    queue_frame,
                    text=stats_text,
                    font=ctk.CTkFont(size=12),
                    text_color="#FF7F7F" if winrate < 50 else "green"
                ).pack(pady=2)
                
                # Most played role
                if 'mostPlayedRole' in queue:
                    role_text = f"Most played: {queue['mostPlayedRole'].title()}"
                    ctk.CTkLabel(
                        queue_frame,
                        text=role_text,
                        font=ctk.CTkFont(size=12)
                    ).pack(pady=2)
                
                # Average KDA
                if 'avgKDA' in queue:
                    kda = queue['avgKDA']
                    kda_text = f"Average KDA: {kda['kills']:.1f}/{kda['deaths']:.1f}/{kda['assists']:.1f}"
                    ctk.CTkLabel(
                        queue_frame,
                        text=kda_text,
                        font=ctk.CTkFont(size=12)
                    ).pack(pady=2)
            
            # Right side - Champion Mastery
            mastery_frame = ctk.CTkFrame(content_frame)
            mastery_frame.pack(side="right", fill="both", expand=True, padx=10)
            
            ctk.CTkLabel(
                mastery_frame,
                text="Champion Mastery",
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(pady=10)
            
            # Format mastery data
            for champion in mastery_data[:3]:
                champ_frame = ctk.CTkFrame(mastery_frame)
                champ_frame.pack(pady=5, padx=10, fill="x")
                
                champion_id = str(champion['championId'])
                if champion_id in champion_map:
                    champion_name = champion_map[champion_id]
                    # Keep only champion URL, remove mastery URL
                    champion_url = f"https://ddragon.leagueoflegends.com/cdn/14.22.1/img/champion/{champion_name}.png"
                    
                    # Create horizontal layout
                    info_frame = ctk.CTkFrame(champ_frame, fg_color="transparent")
                    info_frame.pack(fill="x", padx=5, pady=5)
                    
                    # Champion icon
                    champ_img = self.load_image(champion_url, size=(50, 50))
                    if champ_img:
                        ctk.CTkLabel(info_frame, text="", image=champ_img).pack(side="left", padx=5)
                    
                    # Champion details without mastery icon for now
                    details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
                    details_frame.pack(side="left", padx=5, fill="x", expand=True)
                    
                    # Champion name
                    ctk.CTkLabel(
                        details_frame,
                        text=champion_name,
                        font=ctk.CTkFont(size=12, weight="bold")
                    ).pack(anchor="w")
                    
                    # Mastery points and level
                    points_text = f"Mastery {champion['championLevel']} - {champion['championPoints']:,} points"
                    if 'lastPlayTime' in champion:
                        from datetime import datetime, timezone
                        last_played = datetime.fromtimestamp(champion['lastPlayTime'] / 1000, timezone.utc)
                        points_text += f"\nLast played: {last_played.strftime('%Y-%m-%d')}"
                    
                    ctk.CTkLabel(
                        details_frame,
                        text=points_text,
                        font=ctk.CTkFont(size=10)
                    ).pack(anchor="w")
            
            if DEBUG:
                print("DEBUG - Profile update complete")
            
        except Exception as e:
            if DEBUG:
                import traceback
                print(f"Error updating profile: {e}")
                print(traceback.format_exc())

    def format_ranked_stats(self, ranked_stats: List[Dict[str, Any]], rank_images: Dict[str, Optional[ctk.CTkImage]]) -> None:
        """Format ranked stats display"""
        # Define lane icon URLs
        lane_icons = {
            "TOP": "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-game-data/global/default/assets/ranked/positions/position-0.png",
            "JUNGLE": "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-game-data/global/default/assets/ranked/positions/position-1.png",
            "MIDDLE": "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-game-data/global/default/assets/ranked/positions/position-2.png",
            "BOTTOM": "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-game-data/global/default/assets/ranked/positions/position-3.png",
            "UTILITY": "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-game-data/global/default/assets/ranked/positions/position-4.png",
            "UNKNOWN": "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-game-data/global/default/assets/ranked/positions/position-5.png"
        }
        
        # Load lane icons
        lane_images = load_images_batch(list(lane_icons.values()), size=(25, 25))
        
        # Clear existing ranked info except title
        for widget in self.ranked_frame.winfo_children():
            if not isinstance(widget, ctk.CTkLabel) or widget != self.ranked_label:
                widget.destroy()
        
        if not ranked_stats:
            no_ranked_label = ctk.CTkLabel(
                self.ranked_frame,
                text="No ranked data available",
                font=ctk.CTkFont(size=16)
            )
            no_ranked_label.pack(pady=20)
            return
        
        # Show ranked stats for each queue vertically
        for queue in ranked_stats:
            queue_frame = ctk.CTkFrame(self.ranked_frame)
            queue_frame.pack(pady=10, padx=20, fill="x")
            
            # Queue type
            queue_type = get_queue_display_name(queue['queueType'])
            queue_label = ctk.CTkLabel(
                queue_frame,
                text=queue_type,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            queue_label.pack(pady=5)
            
            # Create a frame for role and emblem side by side
            role_emblem_frame = ctk.CTkFrame(queue_frame, fg_color="transparent")
            role_emblem_frame.pack(pady=5)
            
            # Most played role icon
            most_played_role = queue.get('mostPlayedRole', 'UNKNOWN')
            role_url = lane_icons.get(most_played_role, lane_icons['UNKNOWN'])
            if role_url in lane_images and lane_images[role_url]:
                role_label = ctk.CTkLabel(
                    role_emblem_frame,
                    text="",
                    image=lane_images[role_url]
                )
                role_label.pack(side="left", padx=10)
            
            # Rank emblem
            tier = queue['tier'].lower()
            rank_url = f"https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/ranked-emblem/emblem-{tier}.png"
            if rank_url in rank_images and rank_images[rank_url]:
                emblem_label = ctk.CTkLabel(
                    role_emblem_frame,
                    text="",
                    image=rank_images[rank_url]
                )
                emblem_label.pack(side="left", padx=10)
            
            # Stats
            stats_frame = ctk.CTkFrame(queue_frame, fg_color="transparent")
            stats_frame.pack(pady=5)
            
            # Rank info
            rank_text = f"{queue['tier']} {queue['rank']} - {queue['leaguePoints']} LP"
            rank_info = ctk.CTkLabel(
                stats_frame,
                text=rank_text,
                font=ctk.CTkFont(size=14)
            )
            rank_info.pack(pady=2)
            
            # Win/Loss
            wins = queue['wins']
            losses = queue['losses']
            winrate = (wins / (wins + losses)) * 100 if wins + losses > 0 else 0
            
            stats_text = f"W: {wins} L: {losses} ({winrate:.1f}%)"
            stats_label = ctk.CTkLabel(
                stats_frame,
                text=stats_text,
                font=ctk.CTkFont(size=14),
                text_color="#FF7F7F" if winrate < 50 else "green"
            )
            stats_label.pack(pady=2)
            
            # KDA
            if 'avgKDA' in queue:
                kda = queue['avgKDA']
                kda_ratio = (kda['kills'] + kda['assists']) / max(kda['deaths'], 1)
                kda_text = f"KDA: {kda['kills']:.1f}/{kda['deaths']:.1f}/{kda['assists']:.1f} ({kda_ratio:.2f})"
                kda_label = ctk.CTkLabel(
                    stats_frame,
                    text=kda_text,
                    font=ctk.CTkFont(size=14)
                )
                kda_label.pack(pady=2)

    def format_mastery_data(
        self,
        mastery_data: List[Dict[str, Any]],
        champion_map: Dict[str, str],
        champion_images: Dict[str, Optional[ctk.CTkImage]]
    ) -> None:
        """Format mastery data display"""
        # Clear existing mastery info
        for widget in self.mastery_frame.winfo_children():
            widget.destroy()
        
        if not mastery_data:
            no_mastery_label = ctk.CTkLabel(
                self.mastery_frame,
                text="No mastery data available",
                font=ctk.CTkFont(size=16)
            )
            no_mastery_label.pack(pady=20)
            return
        
        # Title
        title_label = ctk.CTkLabel(
            self.mastery_frame,
            text="Top Champions",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Show top 3 champions
        for champion in mastery_data[:3]:
            champion_id = str(champion['championId'])
            if champion_id in champion_map:
                champion_name = champion_map[champion_id]
                mastery_points = champion['championPoints']
                mastery_level = champion['championLevel']
                
                # Create frame for this champion
                champ_frame = ctk.CTkFrame(self.mastery_frame)
                champ_frame.pack(pady=5, padx=10, fill="x")
                
                # Add champion icon
                champion_url = f"https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/{champion_name}.png"
                if champion_url in champion_images and champion_images[champion_url]:
                    icon_label = ctk.CTkLabel(
                        champ_frame,
                        text="",
                        image=champion_images[champion_url]
                    )
                    icon_label.pack(side="left", padx=5, pady=5)
                
                # Add champion info
                info_frame = ctk.CTkFrame(champ_frame, fg_color="transparent")
                info_frame.pack(side="left", padx=10, fill="x", expand=True)
                
                name_label = ctk.CTkLabel(
                    info_frame,
                    text=champion_name,
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                name_label.pack(anchor="w")
                
                mastery_label = ctk.CTkLabel(
                    info_frame,
                    text=f"Mastery {mastery_level} - {mastery_points:,} points",
                    font=ctk.CTkFont(size=12)
                )
                mastery_label.pack(anchor="w")

    def update_match_history(
        self,
        match_history: List[Dict[str, Any]],
        puuid: str,
        champion_map: Dict[str, str],
        item_data: Dict[str, Any]
    ) -> None:
        """Update match history tab"""
        if DEBUG:
            total_start = time.time()
        
        # Show loading indicator
        loading = LoadingIndicator(self.matches_frame, "Loading match data...")
        
        try:
            # Collect all URLs
            item_urls = set()
            champion_urls = set()
            
            for match in match_history:
                try:
                    player_data = next(
                        p for p in match['info']['participants']
                        if p['puuid'] == puuid
                    )
                    
                    # Add champion icon URL
                    champion_id = str(player_data['championId'])
                    if champion_id in champion_map:
                        champion_name = champion_map[champion_id]
                        champion_url = f"https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/{champion_name}.png"
                        champion_urls.add(champion_url)
                    
                    # Add item URLs
                    for item_slot in range(0, 7):
                        item_id = str(player_data.get(f'item{item_slot}', 0))
                        if item_id != "0" and item_id in item_data['data']:
                            item_url = f"https://ddragon.leagueoflegends.com/cdn/13.24.1/img/item/{item_id}.png"
                            item_urls.add(item_url)
                except Exception as e:
                    if DEBUG:
                        print(f"Error collecting URLs from match: {e}")
                    continue
            
            if DEBUG:
                print(f"\nCollected {len(champion_urls)} champion URLs and {len(item_urls)} item URLs")
            
            loading.update_text("Loading champion icons...")
            champion_images = load_images_batch(list(champion_urls), size=(30, 30))
            
            loading.update_text("Loading item icons...")
            item_images = load_images_batch(list(item_urls), size=(25, 25))
            
            loading.update_text("Creating match history...")
            # Now create the match history UI with preloaded images
            for match in match_history:
                try:
                    # Create frame for this match
                    match_frame = ctk.CTkFrame(self.matches_frame)
                    match_frame.pack(pady=5, padx=10, fill="x")
                    
                    # Find player data
                    player_data = next(
                        p for p in match['info']['participants']
                        if p['puuid'] == puuid
                    )
                    
                    # Format match info
                    champion_id = str(player_data['championId'])
                    champion_name = champion_map.get(champion_id, 'Unknown')
                    kda = f"{player_data['kills']}/{player_data['deaths']}/{player_data['assists']}"
                    cs = player_data['totalMinionsKilled']
                    duration = match['info']['gameDuration'] // 60
                    result = "Victory" if player_data['win'] else "Defeat"
                    
                    # Add champion icon
                    champion_url = f"https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/{champion_name}.png"
                    if champion_url in champion_images and champion_images[champion_url]:
                        champion_icon = ctk.CTkLabel(
                            match_frame,
                            text="",
                            image=champion_images[champion_url]
                        )
                        champion_icon.pack(side="left", padx=5)
                    
                    # Create result label
                    result_label = ctk.CTkLabel(
                        match_frame,
                        text=result,
                        text_color="green" if player_data['win'] else "red"
                    )
                    result_label.pack(side="left", padx=10)
                    
                    # Create champion label
                    champion_label = ctk.CTkLabel(
                        match_frame,
                        text=f"Champion: {champion_name}"
                    )
                    champion_label.pack(side="left", padx=10)
                    
                    # Create KDA label
                    kda_label = ctk.CTkLabel(
                        match_frame,
                        text=f"KDA: {kda}"
                    )
                    kda_label.pack(side="left", padx=10)
                    
                    # Create CS label
                    cs_label = ctk.CTkLabel(
                        match_frame,
                        text=f"CS: {cs}"
                    )
                    cs_label.pack(side="left", padx=10)
                    
                    # Create duration label
                    duration_label = ctk.CTkLabel(
                        match_frame,
                        text=f"Duration: {duration}m"
                    )
                    duration_label.pack(side="left", padx=10)
                    
                    # Create items frame
                    items_frame = ctk.CTkFrame(match_frame, fg_color="transparent")
                    items_frame.pack(side="right", padx=10)
                    
                    # Add item icons
                    for item_slot in range(0, 7):
                        item_id = str(player_data.get(f'item{item_slot}', 0))
                        if item_id != "0" and item_id in item_data['data']:
                            item_url = f"https://ddragon.leagueoflegends.com/cdn/13.24.1/img/item/{item_id}.png"
                            if item_url in item_images and item_images[item_url]:
                                item_label = ctk.CTkLabel(
                                    items_frame,
                                    text="",
                                    image=item_images[item_url]
                                )
                                item_label.pack(side="left", padx=2)
                
                except Exception as e:
                    if DEBUG:
                        print(f"Error formatting match: {e}")
                    continue
            
            if DEBUG:
                total_end = time.time()
                print(f"\nTotal match history update time: {total_end - total_start:.2f} seconds")
            
            # Remove loading indicator
            loading.destroy()
            
        except Exception as e:
            if DEBUG:
                print(f"Error updating match history: {e}")
            loading.update_text(f"Error: {str(e)}")
            self.after(2000, loading.destroy)

    def get_queue_display_name(self, queue_type: str) -> str:
        """Convert queue type to display name"""
        queue_names = {
            'RANKED_SOLO_5x5': 'Solo/Duo',
            'RANKED_FLEX_SR': 'Flex 5v5',
            'RANKED_TFT': 'TFT',
            'RANKED_TFT_DOUBLE_UP': 'TFT Double Up',
            'RANKED_TFT_TURBO': 'Hyper Roll'
        }
        return queue_names.get(queue_type, queue_type.replace('_', ' ').title())

def get_queue_display_name(queue_type: str) -> str:
    """Convert queue type to display name"""
    queue_names = {
        'RANKED_SOLO_5x5': 'Solo/Duo',
        'RANKED_FLEX_SR': 'Flex 5v5',
        'RANKED_TFT': 'TFT',
        'RANKED_TFT_DOUBLE_UP': 'TFT Double Up',
        'RANKED_TFT_TURBO': 'Hyper Roll'
    }
    return queue_names.get(queue_type, queue_type.replace('_', ' ').title())
