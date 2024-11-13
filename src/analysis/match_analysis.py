from typing import Dict, List, Any

def analyze_match_history(matches: List[Dict], puuid: str) -> Dict[str, Any]:
    """Analyze match history for trends and patterns"""
    match_analysis = {
        'total_games': 0,
        'wins': 0,
        'losses': 0,
        'roles': {},
        'game_durations': [],
        'performance_by_role': {},
        'recent_performance': []  # Last 5 games
    }
    
    for match in matches:
        player = next(p for p in match['info']['participants'] if p['puuid'] == puuid)
        
        # Basic match stats
        match_analysis['total_games'] += 1
        match_analysis['wins'] += 1 if player['win'] else 0
        match_analysis['losses'] += 1 if not player['win'] else 0
        
        # Role tracking
        role = player['teamPosition']
        match_analysis['roles'][role] = match_analysis['roles'].get(role, 0) + 1
        
        # Track performance by role
        if role not in match_analysis['performance_by_role']:
            match_analysis['performance_by_role'][role] = {
                'games': 0,
                'wins': 0,
                'kills': 0,
                'deaths': 0,
                'assists': 0
            }
        
        role_stats = match_analysis['performance_by_role'][role]
        role_stats['games'] += 1
        role_stats['wins'] += 1 if player['win'] else 0
        role_stats['kills'] += player['kills']
        role_stats['deaths'] += player['deaths']
        role_stats['assists'] += player['assists']
        
        # Track game duration
        match_analysis['game_durations'].append(match['info']['gameDuration'])
        
        # Recent performance
        recent_game = {
            'champion': player['championName'],
            'result': 'Victory' if player['win'] else 'Defeat',
            'kda': f"{player['kills']}/{player['deaths']}/{player['assists']}",
            'role': role,
            'cs': player['totalMinionsKilled'] + player.get('neutralMinionsKilled', 0)
        }
        match_analysis['recent_performance'].append(recent_game)
    
    # Calculate averages and percentages
    if match_analysis['total_games'] > 0:
        match_analysis['winrate'] = (match_analysis['wins'] / match_analysis['total_games']) * 100
        match_analysis['avg_game_duration'] = sum(match_analysis['game_durations']) / len(match_analysis['game_durations'])
        
        # Calculate role preferences
        match_analysis['role_preferences'] = {
            role: (games / match_analysis['total_games'] * 100)
            for role, games in match_analysis['roles'].items()
        }
        
        # Calculate role performance
        for role, stats in match_analysis['performance_by_role'].items():
            if stats['games'] > 0:
                stats['winrate'] = (stats['wins'] / stats['games']) * 100
                stats['avg_kda'] = (stats['kills'] + stats['assists']) / max(1, stats['deaths'])
    
    return match_analysis
