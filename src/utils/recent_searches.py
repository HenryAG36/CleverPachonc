import json
import os
from typing import List, Dict
from datetime import datetime

class RecentSearches:
    def __init__(self, max_searches: int = 5):
        self.max_searches = max_searches
        self.file_path = os.path.join("src", "cache", "recent_searches.json")
        self.searches = self._load_searches()
    
    def _load_searches(self) -> List[Dict]:
        """Load searches from file"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading recent searches: {e}")
        return []
    
    def _save_searches(self) -> None:
        """Save searches to file"""
        try:
            # Create cache directory if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w') as f:
                json.dump(self.searches, f)
        except Exception as e:
            print(f"Error saving recent searches: {e}")
    
    def add_search(self, summoner_name: str, region: str) -> None:
        """Add a new search"""
        # Remove if already exists
        self.searches = [s for s in self.searches 
                        if not (s['summoner_name'] == summoner_name and s['region'] == region)]
        
        # Add new search
        self.searches.insert(0, {
            'summoner_name': summoner_name,
            'region': region,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only max_searches
        self.searches = self.searches[:self.max_searches]
        
        # Save to file
        self._save_searches()
    
    def get_searches(self) -> List[Dict]:
        """Get recent searches"""
        return self.searches
    
    def clear_searches(self) -> None:
        """Clear all recent searches"""
        self.searches = []
        self._save_searches() 