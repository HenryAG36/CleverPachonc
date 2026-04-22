from typing import Dict, List, Any

def analyze_runes(matches: List[Dict], puuid: str) -> Dict[str, Any]:
    """Analyze rune choices and performance"""
    rune_stats = {
        'keystone_usage': {},
        'primary_paths': {},
        'secondary_paths': {},
        'rune_combinations': {},
        'performance_by_keystone': {}
    }
    
    for match in matches:
        player = next(p for p in match['info']['participants'] if p['puuid'] == puuid)
        
        if 'perks' in player:
            perks = player['perks']
            primary_style = perks['styles'][0]
            secondary_style = perks['styles'][1]
            
            # Track keystone usage
            keystone = primary_style['selections'][0]['perk']
            rune_stats['keystone_usage'][keystone] = \
                rune_stats['keystone_usage'].get(keystone, 0) + 1
            
            # Track path usage
            primary_path = primary_style['style']
            secondary_path = secondary_style['style']
            
            rune_stats['primary_paths'][primary_path] = \
                rune_stats['primary_paths'].get(primary_path, 0) + 1
            rune_stats['secondary_paths'][secondary_path] = \
                rune_stats['secondary_paths'].get(secondary_path, 0) + 1
            
            # Track combination performance
            combo_key = f"{primary_path}_{secondary_path}"
            if combo_key not in rune_stats['rune_combinations']:
                rune_stats['rune_combinations'][combo_key] = {
                    'games': 0,
                    'wins': 0,
                    'kills': 0,
                    'deaths': 0,
                    'assists': 0
                }
            
            combo = rune_stats['rune_combinations'][combo_key]
            combo['games'] += 1
            combo['wins'] += 1 if player['win'] else 0
            combo['kills'] += player['kills']
            combo['deaths'] += player['deaths']
            combo['assists'] += player['assists']
            
            # Track keystone performance
            if keystone not in rune_stats['performance_by_keystone']:
                rune_stats['performance_by_keystone'][keystone] = {
                    'games': 0,
                    'wins': 0,
                    'damage': 0,
                    'healing': player.get('totalHealsOnTeammates', 0),
                    'shielding': player.get('totalDamageShieldedOnTeammates', 0)
                }
            
            keystone_stats = rune_stats['performance_by_keystone'][keystone]
            keystone_stats['games'] += 1
            keystone_stats['wins'] += 1 if player['win'] else 0
            keystone_stats['damage'] += player['totalDamageDealtToChampions']
    
    # Calculate statistics
    for combo_key, stats in rune_stats['rune_combinations'].items():
        if stats['games'] > 0:
            stats['winrate'] = (stats['wins'] / stats['games']) * 100
            stats['kda'] = (stats['kills'] + stats['assists']) / max(1, stats['deaths'])
    
    for keystone, stats in rune_stats['performance_by_keystone'].items():
        if stats['games'] > 0:
            stats['winrate'] = (stats['wins'] / stats['games']) * 100
            stats['avg_damage'] = stats['damage'] / stats['games']
    
    return rune_stats
