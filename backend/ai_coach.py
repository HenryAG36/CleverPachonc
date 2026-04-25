import os
import json
import re

from openai import OpenAI


def _build_prompt(summoner, ranked, champion_stats, match_analysis):
    name = summoner.get("gameName", "")
    tag = summoner.get("tagLine", "")
    lines = [f"Summoner: {name}#{tag}"]

    solo = next((q for q in ranked if q.get("queueType") == "RANKED_SOLO_5x5"), None)
    if solo:
        tier = solo.get("tier", "Unranked")
        rank_div = solo.get("rank", "")
        lp = solo.get("leaguePoints", 0)
        wins = solo.get("wins", 0)
        losses = solo.get("losses", 0)
        total = wins + losses
        wr = (wins / total * 100) if total > 0 else 0
        streak = solo.get("streak", 0)
        role = solo.get("mostPlayedRole", "Unknown")

        lines.append(f"Rank: {tier} {rank_div} — {lp} LP")
        lines.append(f"Season: {wins}W {losses}L ({wr:.1f}% WR)")
        if streak:
            lines.append(f"Streak: {abs(streak)}{'W' if streak > 0 else 'L'}")
        lines.append(f"Main role: {role}")

    if match_analysis:
        total_g = match_analysis.get("total_games", 0)
        w = match_analysis.get("wins", 0)
        wr_r = match_analysis.get("winrate", 0)
        dur = match_analysis.get("avg_game_duration", 0)
        lines.append(
            f"\nRecent {total_g} games: {w}W {total_g - w}L "
            f"({wr_r:.1f}% WR), avg {dur / 60:.0f} min/game"
        )

        for role, stats in match_analysis.get("performance_by_role", {}).items():
            if role:
                lines.append(
                    f"  {role}: {stats['games']}g  "
                    f"{stats.get('winrate', 0):.0f}% WR  "
                    f"{stats.get('avg_kda', 0):.2f} KDA"
                )

    if champion_stats:
        lines.append("\nChampion pool:")
        sorted_champs = sorted(
            champion_stats.items(), key=lambda x: x[1].get("games", 0), reverse=True
        )
        for champ_name, s in sorted_champs[:8]:
            lines.append(
                f"  {champ_name} ({s.get('main_role', '')}): "
                f"{s.get('games')}g  {s.get('winrate', 0):.0f}% WR  "
                f"{s.get('kda', 0):.2f} KDA  "
                f"{s.get('cs_per_min', 0):.1f} CS/min  "
                f"{s.get('damage_per_min', 0):.0f} dmg/min  "
                f"{s.get('vision_per_game', 0):.1f} vision/g"
            )

    return "\n".join(lines)


def generate_coaching(payload: dict) -> dict:
    api_key = os.environ.get("OLLAMA_API_KEY", "")
    if not api_key:
        raise ValueError("OLLAMA_API_KEY is not configured on the server.")

    summoner = payload.get("summoner", {})
    ranked = payload.get("ranked", [])
    champion_stats = payload.get("champion_stats", {})
    match_analysis = payload.get("match_analysis", {})

    player_data = _build_prompt(summoner, ranked, champion_stats, match_analysis)

    client = OpenAI(base_url="https://ollama.com/v1", api_key=api_key)

    system_prompt = (
        "You are an expert League of Legends coach. "
        "Analyze player performance data and respond ONLY with valid JSON — "
        "no markdown, no code fences, no extra text before or after the JSON object."
    )

    user_prompt = f"""{player_data}

Return a coaching analysis as a JSON object with this exact structure:
{{
  "assessment": "2-3 sentence overview of the player's current performance trajectory",
  "weaknesses": [
    {{"title": "short title", "detail": "specific detail citing actual numbers", "action": "one concrete action to take"}},
    {{"title": "...", "detail": "...", "action": "..."}},
    {{"title": "...", "detail": "...", "action": "..."}}
  ],
  "champion_pool": {{
    "keep": ["Champion1", "Champion2"],
    "drop": ["Champion3"],
    "reasoning": "brief explanation citing winrates"
  }},
  "role_recommendation": {{
    "recommended": "ROLE",
    "reasoning": "explanation with numbers from the data"
  }},
  "strength": "one specific thing this player does well, citing data",
  "weekly_focus": "single most impactful thing to work on this week"
}}

Rules: cite actual numbers, give exactly 3 weaknesses, be direct not generic, only include champions that appear in the data."""

    response = client.chat.completions.create(
        model="gemini-3-flash-preview:cloud",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )

    content = response.choices[0].message.content.strip()
    # Strip markdown code fences if the model wraps the JSON anyway
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    return json.loads(content)
