from typing import Optional, Dict, List, Any, Tuple
import requests
from ..utils.constants import get_api_key, REGION_ROUTING
from ..utils.debug import DEBUG
from ..utils.rate_limiter import RateLimiter
import asyncio
import aiohttp
import time
from collections import defaultdict

# Regional routing map for Riot API endpoints
region_routing = {
    'NA': 'americas',
    'BR': 'americas',
    'LAN': 'americas',
    'LAS': 'americas',
    'OCE': 'americas',
    'KR': 'asia',
    'JP': 'asia',
    'EUW': 'europe',
    'EUNE': 'europe',
    'TR': 'europe',
    'RU': 'europe',
}

# Create a rate limiter instance
rate_limiter = RateLimiter(requests_per_second=20)

async def fetch_endpoint(
    session: aiohttp.ClientSession,
    url: str,
    headers: Dict[str, str],
    rate_limiter: RateLimiter,
    endpoint_name: str,
    params: Dict[str, Any] = None
) -> Optional[Dict]:
    """Fetch data from an endpoint with rate limiting"""
    try:
        rate_limiter.wait(endpoint_name)
        if DEBUG:
            print(f"Fetching {endpoint_name} from: {url}")
        
        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        if DEBUG:
            print(f"Error fetching {endpoint_name}: {e}")
        return None

async def fetch_ranked_details(
    summoner_id: str,
    puuid: str,
    region: str,
    api_key: str,
    platform_url: str
) -> Dict[str, Any]:
    """Fetch detailed ranked stats including role distribution and streaks"""
    headers = {"X-Riot-Token": api_key}
    rate_limiter = RateLimiter()
    
    # Get routing value for match history
    routing = region_routing.get(region.lower(), "americas")
    
    # Prepare URLs
    ranked_url = f"{platform_url}/lol/league/v4/entries/by-summoner/{summoner_id}"
    matches_url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    
    async with aiohttp.ClientSession() as session:
        # Fetch basic ranked data
        ranked_data = await fetch_endpoint(session, ranked_url, headers, rate_limiter, "ranked")
        if not ranked_data:
            return {}
        
        # Fetch recent matches for analysis
        params = {"queue": 420, "count": 20}  # Ranked Solo/Duo games
        match_ids = await fetch_endpoint(session, matches_url, headers, rate_limiter, "matches", params=params)
        if not match_ids:
            return ranked_data
        
        # Fetch match details concurrently
        match_tasks = []
        for match_id in match_ids:
            match_url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/{match_id}"
            match_tasks.append(fetch_endpoint(session, match_url, headers, rate_limiter, "match_details"))
        
        match_details = await asyncio.gather(*match_tasks)
        
        # Analyze match data
        streak = 0
        current_streak = 0
        roles = defaultdict(int)
        total_kda = {"kills": 0, "deaths": 0, "assists": 0}
        games_analyzed = 0
        
        for match in match_details:
            if not match or "info" not in match:
                continue
            
            # Find player in match
            for participant in match["info"]["participants"]:
                if participant["puuid"] == puuid:
                    # Update streak
                    if games_analyzed == 0:
                        streak = 1 if participant["win"] else -1
                        current_streak = streak
                    else:
                        if (participant["win"] and streak > 0) or (not participant["win"] and streak < 0):
                            current_streak += 1 if participant["win"] else -1
                        else:
                            current_streak = 1 if participant["win"] else -1
                    streak = max(abs(streak), abs(current_streak)) * (1 if current_streak > 0 else -1)
                    
                    # Update role count
                    roles[participant["teamPosition"]] += 1
                    
                    # Update KDA
                    total_kda["kills"] += participant["kills"]
                    total_kda["deaths"] += participant["deaths"]
                    total_kda["assists"] += participant["assists"]
                    
                    games_analyzed += 1
                    break
        
        # Calculate averages and most played role
        avg_kda = {
            "kills": total_kda["kills"] / games_analyzed if games_analyzed > 0 else 0,
            "deaths": total_kda["deaths"] / games_analyzed if games_analyzed > 0 else 0,
            "assists": total_kda["assists"] / games_analyzed if games_analyzed > 0 else 0
        }
        
        most_played_role = max(roles.items(), key=lambda x: x[1])[0] if roles else "Unknown"
        
        # Add additional stats to ranked data
        for queue in ranked_data:
            queue["streak"] = streak
            queue["mostPlayedRole"] = most_played_role
            queue["avgKDA"] = avg_kda
            queue["recentGames"] = games_analyzed
        
        return ranked_data

async def fetch_all_data(
    puuid: str,
    summoner_id: str,
    region: str,
    api_key: str,
    platform_url: str
) -> Tuple[List, List, List]:
    """Fetch all data concurrently"""
    headers = {"X-Riot-Token": api_key}
    rate_limiter = RateLimiter()
    
    if DEBUG:
        start_time = time.time()
        print("\nStarting concurrent data fetch...")
    
    async with aiohttp.ClientSession() as session:
        # Fetch all data concurrently
        ranked_task = fetch_ranked_details(summoner_id, puuid, region, api_key, platform_url)
        mastery_task = fetch_endpoint(session, f"{platform_url}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}", headers, rate_limiter, "mastery")
        matches_task = fetch_endpoint(session, f"https://{region_routing.get(region.lower(), 'americas')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids", headers, rate_limiter, "matches")
        
        ranked_data, mastery_data, match_ids = await asyncio.gather(
            ranked_task, mastery_task, matches_task
        )
    
    if DEBUG:
        end_time = time.time()
        print(f"Concurrent fetch completed in {end_time - start_time:.2f} seconds")
    
    return ranked_data or [], mastery_data or [], match_ids or []

async def fetch_match_details_batch(
    match_ids: List[str],
    region: str,
    api_key: str
) -> List[Dict]:
    """Fetch match details concurrently in batches"""
    headers = {"X-Riot-Token": api_key}
    rate_limiter = RateLimiter()
    routing = region_routing.get(region.lower(), "americas")
    
    if DEBUG:
        start_time = time.time()
        print(f"\nFetching details for {len(match_ids)} matches...")
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for match_id in match_ids[:10]:  # Limit to 10 most recent matches
            url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/{match_id}"
            tasks.append(fetch_endpoint(session, url, headers, rate_limiter, "match_details"))
        
        match_details = await asyncio.gather(*tasks)
    
    if DEBUG:
        end_time = time.time()
        print(f"Match details fetched in {end_time - start_time:.2f} seconds")
    
    return [match for match in match_details if match is not None]

async def fetch_mastery_details(
    puuid: str,
    region: str,
    api_key: str,
    platform_url: str
) -> Dict[str, Any]:
    """Fetch detailed mastery statistics"""
    headers = {"X-Riot-Token": api_key}
    rate_limiter = RateLimiter()
    
    mastery_url = f"{platform_url}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
    total_url = f"{platform_url}/lol/champion-mastery/v4/scores/by-puuid/{puuid}"
    
    async with aiohttp.ClientSession() as session:
        # Fetch mastery data and total score concurrently
        mastery_data, total_score = await asyncio.gather(
            fetch_endpoint(session, mastery_url, headers, rate_limiter, "mastery"),
            fetch_endpoint(session, total_url, headers, rate_limiter, "mastery_score")
        )
        
        if not mastery_data:
            return {}
        
        # Calculate mastery statistics
        mastery_levels = defaultdict(int)
        total_points = 0
        recent_progress = []
        
        for champ in mastery_data:
            mastery_levels[champ['championLevel']] += 1
            total_points += champ['championPoints']
            
            # Track recent progress (champions close to next level)
            if champ['championLevel'] < 7:  # Only for non-M7 champions
                points_to_next = champ.get('championPointsUntilNextLevel', 0)
                if points_to_next < 10000:  # Only show champions close to next level
                    recent_progress.append({
                        'championId': champ['championId'],
                        'level': champ['championLevel'],
                        'points': champ['championPoints'],
                        'pointsToNext': points_to_next
                    })
        
        # Sort recent progress by points needed
        recent_progress.sort(key=lambda x: x['pointsToNext'])
        
        return {
            'totalScore': total_score,
            'totalPoints': total_points,
            'masteryLevels': dict(mastery_levels),
            'recentProgress': recent_progress[:3],  # Top 3 closest to next level
            'topChampions': mastery_data[:3]  # Keep existing top 3
        }

def get_summoner_data(summoner_name: str, region: str) -> Tuple[Dict, List, List, List]:
    """Get all summoner data concurrently"""
    try:
        api_key = get_api_key()
        if not api_key:
            raise ValueError("No API key set")
        
        # Get account data first
        account_data = get_summoner_by_name(summoner_name, region)
        if not account_data:
            raise ValueError("Could not find summoner")
        
        # Get platform URL
        platform_url = REGION_ROUTING.get(region.upper())
        if not platform_url:
            raise ValueError(f"Invalid region: {region}")
        
        # Run async fetches in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Fetch basic data
        ranked_data, mastery_data, match_ids = loop.run_until_complete(
            fetch_all_data(
                account_data['puuid'],
                account_data['id'],
                region,
                api_key,
                platform_url
            )
        )
        
        # Fetch match details
        match_details = loop.run_until_complete(
            fetch_match_details_batch(match_ids, region, api_key)
        )
        
        loop.close()
        
        return account_data, ranked_data, mastery_data, match_details
        
    except Exception as e:
        if DEBUG:
            print(f"Error getting summoner data: {e}")
        raise

def get_summoner_by_name(summoner_name: str, region: str) -> Dict[str, Any]:
    """Get summoner data by name"""
    # Split name and tag
    name_parts = summoner_name.split('#')
    game_name = name_parts[0]
    tag_line = name_parts[1] if len(name_parts) > 1 else None
    
    if not tag_line:
        raise ValueError("Riot ID tag is required (e.g., Name#TAG)")
    
    # Get the regional routing based on platform
    region_routing = {
        'NA': 'americas',
        'BR': 'americas',
        'LAN': 'americas',
        'LAS': 'americas',
        'OCE': 'americas',
        'KR': 'asia',
        'JP': 'asia',
        'EUW': 'europe',
        'EUNE': 'europe',
        'TR': 'europe',
        'RU': 'europe',
    }
    
    region_upper = region.upper()
    regional_routing = region_routing.get(region_upper, 'americas')
    platform = REGION_ROUTING.get(region_upper)
    
    if not platform:
        raise ValueError(f"Invalid region: {region}")
    
    # Build the URL for Riot ID endpoint using regional routing
    url = f"https://{regional_routing}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    
    if DEBUG:
        print(f"Getting account data from: {url}")
    
    # Wait for rate limit before account request
    rate_limiter.wait("account")
    response = requests.get(
        url,
        headers={"X-Riot-Token": get_api_key()}
    )
    
    # Check for errors
    response.raise_for_status()
    
    account_data = response.json()
    
    # Now get summoner data using PUUID from the platform URL
    summoner_url = f"{platform}/lol/summoner/v4/summoners/by-puuid/{account_data['puuid']}"
    
    if DEBUG:
        print(f"Getting summoner data from: {summoner_url}")
    
    # Wait for rate limit before summoner request
    rate_limiter.wait("summoner")
    summoner_response = requests.get(
        summoner_url,
        headers={"X-Riot-Token": get_api_key()}
    )
    
    # Check for errors
    summoner_response.raise_for_status()
    
    return summoner_response.json()

def get_ranked_stats(summoner_id: str, region: str = "na1") -> Optional[List[Dict[str, Any]]]:
    """Get ranked stats for a summoner"""
    try:
        api_key = get_api_key()
        if not api_key:
            raise ValueError("No API key set")
        
        # Convert region code
        platform = region.lower()
        if platform == "lan":
            platform = "la1"
        elif platform == "las":
            platform = "la2"
        elif not platform.endswith('1'):
            platform = f"{platform}1"
        
        url = f"https://{platform}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
        headers = {"X-Riot-Token": api_key}
        
        print(f"Getting ranked stats from: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting ranked stats: {e}")
        return None

def get_mastery_champions(puuid: str, region: str = "na1") -> Optional[List[Dict[str, Any]]]:
    """Get champion mastery data"""
    try:
        api_key = get_api_key()
        if not api_key:
            raise ValueError("No API key set")
        
        # Convert region code
        platform = region.lower()
        if platform == "lan":
            platform = "la1"
        elif platform == "las":
            platform = "la2"
        elif not platform.endswith('1'):
            platform = f"{platform}1"
        
        url = f"https://{platform}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
        headers = {"X-Riot-Token": api_key}
        
        # Wait for rate limit
        rate_limiter.wait("mastery")
        
        if DEBUG:
            print(f"Getting mastery data from: {url}")
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting mastery data: {e}")
        return None

def get_match_history(puuid: str, region: str = "na1", count: int = 10) -> Optional[List[str]]:
    """Get match history for a summoner"""
    try:
        api_key = get_api_key()
        if not api_key:
            raise ValueError("No API key set")
        
        # Get routing value
        routing = REGION_ROUTING.get(region.lower(), "americas")
        
        url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        headers = {"X-Riot-Token": api_key}
        params = {"count": count}
        
        print(f"Getting match history from: {url}")
        # Wait for rate limit
        rate_limiter.wait("match_history")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting match history: {e}")
        return None

def get_match_details(match_id: str, region: str = "na1") -> Optional[Dict[str, Any]]:
    """Get details for a specific match"""
    try:
        api_key = get_api_key()
        if not api_key:
            raise ValueError("No API key set")
        
        # Get routing value
        routing = REGION_ROUTING.get(region.lower(), "americas")
        
        url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        headers = {"X-Riot-Token": api_key}
        
        print(f"Getting match details from: {url}")
        # Wait for rate limit
        rate_limiter.wait("match_details")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting match details: {e}")
        return None
