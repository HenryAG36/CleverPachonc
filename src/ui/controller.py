from typing import Protocol, Dict, List, Any

class Controller(Protocol):
    """Interface for the main controller"""
    def show_frame(self, frame_class: Any) -> None:
        """Show a frame"""
        pass

    def show_search_page(self) -> None:
        """Show search page"""
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
        """Show stats page with data"""
        pass 