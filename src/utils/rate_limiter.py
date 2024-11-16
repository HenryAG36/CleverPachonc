import time
from typing import Dict

class RateLimiter:
    def __init__(self, requests_per_second: int = 20):
        self.requests_per_second = requests_per_second
        self.last_request_time: Dict[str, float] = {}
        self.min_interval = 1.0 / requests_per_second
    
    def wait(self, endpoint: str) -> None:
        """Wait if necessary to respect rate limits"""
        current_time = time.time()
        if endpoint in self.last_request_time:
            elapsed = current_time - self.last_request_time[endpoint]
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
        
        self.last_request_time[endpoint] = time.time() 