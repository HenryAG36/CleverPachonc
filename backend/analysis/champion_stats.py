from typing import Dict, List, Any

def analyze_champion_stats(matches: List[Dict], puuid: str) -> Dict[str, Any]:
    """Analyze champion performance across matches"""
    champion_stats = {}
    
    for match in matches:
        player = next(p for p in match['info']['participants'] if p['puuid'] == puuid)
        champion = player['championName']
        
        # Initialize champion stats if not exists
        if champion not in champion_stats:
            champion_stats[champion] = {
                'games': 0,
                'wins': 0,
                'kills': 0,
                'deaths': 0,
                'assists': 0,
                'cs': 0,
                'gold': 0,
                'damage': 0,
                'vision': 0,
                'roles': {},
                'items': {},
                'total_time': 0
            }
        
        stats = champion_stats[champion]
        
        # Update basic stats
        stats['games'] += 1
        stats['wins'] += 1 if player['win'] else 0
        stats['kills'] += player['kills']
        stats['deaths'] += player['deaths']
        stats['assists'] += player['assists']
        stats['cs'] += player['totalMinionsKilled'] + player.get('neutralMinionsKilled', 0)
        stats['gold'] += player['goldEarned']
        stats['damage'] += player['totalDamageDealtToChampions']
        stats['vision'] += player['visionScore']
        stats['total_time'] += match['info']['gameDuration']
        
        # Track role frequency
        role = f"{player['teamPosition']}"
        stats['roles'][role] = stats['roles'].get(role, 0) + 1
        
        # Track item builds
        for i in range(0, 6):
            item = player.get(f'item{i}')
            if item and item != 0:
                stats['items'][item] = stats['items'].get(item, 0) + 1
    
    # Calculate averages and percentages
    for stats in champion_stats.values():
        games = stats['games']
        minutes = stats['total_time'] / 60
        
        stats['winrate'] = (stats['wins'] / games) * 100
        stats['kda'] = (stats['kills'] + stats['assists']) / max(1, stats['deaths'])
        stats['avg_kills'] = stats['kills'] / games
        stats['avg_deaths'] = stats['deaths'] / games
        stats['avg_assists'] = stats['assists'] / games
        stats['cs_per_min'] = stats['cs'] / minutes
        stats['gold_per_min'] = stats['gold'] / minutes
        stats['damage_per_min'] = stats['damage'] / minutes
        stats['vision_per_game'] = stats['vision'] / games
        
        stats['main_role'] = max(stats['roles'].items(), key=lambda x: x[1])[0]
        stats['core_items'] = sorted(stats['items'].items(), key=lambda x: x[1], reverse=True)[:6]
    
    return champion_stats
