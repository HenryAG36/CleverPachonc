"""
Utility functions for handling images
"""
import os
import hashlib
from typing import Optional, List, Dict, Any, Tuple
import asyncio
import aiohttp
from PIL import Image
import customtkinter as ctk
from io import BytesIO
import time
from .debug import DEBUG

# Global cache for images
IMAGE_CACHE: Dict[str, bytes] = {}

def get_cache_path(url: str) -> str:
    """Get cache path for a URL"""
    # Create cache directory if it doesn't exist
    cache_dir = os.path.join("src", "cache", "images")
    os.makedirs(cache_dir, exist_ok=True)
    
    # Create filename from URL hash
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(cache_dir, f"{url_hash}.png")

def fetch_image(url: str, size: Tuple[int, int] = None) -> Optional[ctk.CTkImage]:
    """Fetch a single image synchronously"""
    try:
        # Check cache first
        if url in IMAGE_CACHE:
            image_data = IMAGE_CACHE[url]
        else:
            # Check file cache
            cache_path = get_cache_path(url)
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    image_data = f.read()
            else:
                # Fetch image synchronously
                import requests
                response = requests.get(url)
                if response.status_code == 200:
                    image_data = response.content
                    # Save to cache
                    with open(cache_path, 'wb') as f:
                        f.write(image_data)
                else:
                    return None
            
            # Store in memory cache
            IMAGE_CACHE[url] = image_data
        
        # Convert to PIL Image
        image = Image.open(BytesIO(image_data))
        
        # Resize if size is specified
        if size:
            image = image.resize(size, Image.Resampling.LANCZOS)
        
        # Convert to CTkImage
        return ctk.CTkImage(light_image=image, dark_image=image, size=size)
        
    except Exception as e:
        if DEBUG:
            print(f"Error fetching image from {url}: {e}")
        return None

async def fetch_multiple_images(urls: List[str]) -> Dict[str, bytes]:
    """Fetch multiple images concurrently"""
    if DEBUG:
        start_time = time.time()
        print(f"Starting to fetch {len(urls)} images...")
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_image(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    
    if DEBUG:
        end_time = time.time()
        print(f"Fetched {len(urls)} images in {end_time - start_time:.2f} seconds")
    
    return {url: data for url, data in zip(urls, results) if data is not None}

def load_images_batch(urls: List[str], size: Tuple[int, int] = None) -> Dict[str, Optional[ctk.CTkImage]]:
    """Load multiple images in batch"""
    if DEBUG:
        print(f"\nStarting image batch loading...")
        print(f"Starting to fetch {len(urls)} images...")
    
    start_time = time.time()
    loaded_images = {}
    cache_hits = 0
    cache_misses = 0
    
    # Fetch images
    for url in urls:
        try:
            loaded_images[url] = fetch_image(url, size)
            if url in IMAGE_CACHE:
                cache_hits += 1
            else:
                cache_misses += 1
        except Exception as e:
            if DEBUG:
                print(f"Error loading image from {url}: {e}")
            loaded_images[url] = None
    
    fetch_time = time.time() - start_time
    if DEBUG:
        print(f"Fetched {len(urls)} images in {fetch_time:.2f} seconds\n")
        print("Converting images to CTkImage format...")
        
        total_requests = cache_hits + cache_misses
        hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        print(f"Cache Status: {cache_hits} hits, {cache_misses} misses")
        print(f"Cache Hit Rate: {hit_rate:.1f}%")
    
    # Convert timing
    convert_start = time.time()
    convert_time = time.time() - convert_start
    total_time = time.time() - start_time
    
    if DEBUG:
        print(f"Image conversion took {convert_time:.2f} seconds")
        print(f"Total batch loading time: {total_time:.2f} seconds")
        print(f"Successfully loaded {len(loaded_images)} images\n")
    
    return loaded_images