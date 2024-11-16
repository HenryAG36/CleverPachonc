import os
import time
from datetime import datetime, timedelta
from typing import Optional
import json
from ..utils.debug import DEBUG

class CacheManager:
    def __init__(self, max_age_days: int = 7):
        self.cache_dir = os.path.join("src", "cache")
        self.images_dir = os.path.join(self.cache_dir, "images")
        self.data_dir = os.path.join(self.cache_dir, "data")
        self.max_age = timedelta(days=max_age_days)
        
        # Create cache directories if they don't exist
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Cache stats
        self.stats = {
            'last_cleanup': None,
            'files_removed': 0,
            'space_cleared': 0
        }
        
        # Load stats
        self._load_stats()
    
    def _load_stats(self) -> None:
        """Load cache statistics"""
        stats_file = os.path.join(self.cache_dir, "cache_stats.json")
        try:
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    self.stats = json.load(f)
        except Exception as e:
            if DEBUG:
                print(f"Error loading cache stats: {e}")
    
    def _save_stats(self) -> None:
        """Save cache statistics"""
        stats_file = os.path.join(self.cache_dir, "cache_stats.json")
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f)
        except Exception as e:
            if DEBUG:
                print(f"Error saving cache stats: {e}")
    
    def clear_old_files(self) -> tuple[int, float]:
        """Clear files older than max_age"""
        files_removed = 0
        space_cleared = 0
        
        # Current time
        now = datetime.now()
        
        # Clear images
        for filename in os.listdir(self.images_dir):
            filepath = os.path.join(self.images_dir, filename)
            if self._should_remove_file(filepath, now):
                size = os.path.getsize(filepath)
                os.remove(filepath)
                files_removed += 1
                space_cleared += size
        
        # Clear data files
        for filename in os.listdir(self.data_dir):
            filepath = os.path.join(self.data_dir, filename)
            if self._should_remove_file(filepath, now):
                size = os.path.getsize(filepath)
                os.remove(filepath)
                files_removed += 1
                space_cleared += size
        
        # Update stats
        self.stats['last_cleanup'] = now.isoformat()
        self.stats['files_removed'] = files_removed
        self.stats['space_cleared'] = space_cleared
        self._save_stats()
        
        if DEBUG:
            print(f"Cache cleanup: removed {files_removed} files ({space_cleared / 1024 / 1024:.2f} MB)")
        
        return files_removed, space_cleared
    
    def _should_remove_file(self, filepath: str, now: datetime) -> bool:
        """Check if a file should be removed based on age"""
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            return (now - mtime) > self.max_age
        except Exception:
            return False
    
    def get_cache_size(self) -> float:
        """Get total cache size in MB"""
        total_size = 0
        
        # Get size of images
        for filename in os.listdir(self.images_dir):
            filepath = os.path.join(self.images_dir, filename)
            total_size += os.path.getsize(filepath)
        
        # Get size of data files
        for filename in os.listdir(self.data_dir):
            filepath = os.path.join(self.data_dir, filename)
            total_size += os.path.getsize(filepath)
        
        return total_size / 1024 / 1024  # Convert to MB
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        return {
            'size_mb': self.get_cache_size(),
            'last_cleanup': self.stats['last_cleanup'],
            'files_removed': self.stats['files_removed'],
            'space_cleared_mb': self.stats['space_cleared'] / 1024 / 1024 if self.stats['space_cleared'] else 0
        } 