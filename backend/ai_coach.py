import os
import json
import re
import logging

from openai import OpenAI
from backend.analysis.coach_analysis import analyze_for_coaching

logger = logging.getLogger(__name__)

_METRIC_TITLES = {
    "cs_low": "Low CS / Poor Farming",
    "dmg_low": "Below-Average Damage Output",
    "kda_low": "Too Many Deaths",
    "vision_low": "Weak Vision Control",
    "role_wr_low": "Underperforming in Role",
    "sample_size": "Limited Game Sample",
    "cs_good_dmg_low": "Farm Good — Damage Not Converting",
    "wr_low_kda_ok": "Win Rate Below Your KDA",
}

_METRIC_ACTIONS = {
    "cs_low": "Practice last-hitting under tower in a custom game — target 7+ CS/min before pulling ahead.",
    "dmg_low": "Identify the highest-value target before each fight and commit to dealing damage to them.",
    "kda_low": "Play one step further back than feels natural — one fewer death per game saves ~30 LP over 100 games.",
    "vision_low": "Buy a control ward every back and use your trinket before every objective setup.",
    "role_wr_low": "Watch replays of your 3 worst losses in this role and identify the exact moment you fell behind.",
    "sample_size": "Play 20+ games before drawing firm conclusions — variance is high on small samples.",
    "cs_good_dmg_low": "Your farm is solid but you're not converting it into fighting impact — prioritize skirmishes when ahead.",
    "wr_low_kda_ok": "Your individual play is strong but you're not closing out games — practice pressing leads after kills.",
}

_STRENGTH_PHRASES = {
    "cs_high": "Your farming mechanics are significantly above the benchmark",
    "vision_high": "You're placing more wards than most players at your tier",
    "dmg_high": "You consistently deal above-average damage for your role",
    "kda_high": "You're dying much less than the typical player at this rank",
}


def _fallback_weakness(x: dict) -> dict:
    t = x.get("type", "")
    champion = x.get("champion", "overall")
    value = x.get("value")
    bench = x.get("benchmark")

    title = _METRIC_TITLES.get(t, t.replace("_", " ").title())

    if t == "role_wr_low":
        detail = (
            f"Your {champion} role win rate is {value}% vs your overall {bench}% — "
            f"a gap that's actively costing you LP. Identifying why you struggle specifically in this role is the fastest path to climbing."
        )
    elif t == "sample_size":
        detail = (
            f"Only {value} ranked games analyzed so far. "
            f"Stats are unreliable at this sample size — keep playing and the picture will sharpen."
        )
    elif value is not None and bench is not None:
        detail = (
            f"{champion}: {value} vs the {bench} benchmark for your tier. "
            f"This gap compounds over time — small improvements here have outsized impact on win rate."
        )
    else:
        detail = f"Performance on {champion} is below the expected benchmark for your rank."

    action = _METRIC_ACTIONS.get(t, "Dedicate your next 10 games to consciously tracking this metric.")
    return {"title": title, "detail": detail, "action": action}


def _humanize_strength(s: dict | None) -> str:
    if not s:
        return ""
    t = s.get("type", "")
    champ = s.get("champion", "")
    val = s.get("value")
    bench = s.get("benchmark")
    delta = s.get("delta_pct", 0)

    description = _STRENGTH_PHRASES.get(t, "Your performance here is above average")
    if val is not None and bench is not None:
        return (
            f"{description} on {champ} ({val} vs {bench} benchmark, {delta:+.1f}%). "
            f"This is a real competitive edge — lean into it when choosing matchups."
        )
    return f"{description} on {champ}. This is a genuine strength you can build your playstyle around."


def _humanize_weekly_focus(weekly_focus: str) -> str:
    if not weekly_focus or weekly_focus == "maintain_consistency":
        return (
            "Your fundamentals look solid this week. "
            "Focus on playing your strongest champions in favorable matchups and avoid unnecessary variance."
        )
    parts = weekly_focus.split(":", 1)
    metric = parts[0]
    champion = parts[1] if len(parts) > 1 else ""
    action = _METRIC_ACTIONS.get(
        metric, f"Improve {metric.replace('_', ' ')} over your next 10 games."
    )
    if champion and champion not in ("overall", ""):
        return f"{champion} is your biggest lever this week: {action}"
    return action

# Meta analysis is optional — app works without it
try:
    from backend.analysis.meta_analysis import analyze_meta_gaps
    _META_AVAILABLE = True
except Exception:
    _META_AVAILABLE = False


def _build_findings_text(findings: dict, meta: dict | None) -> str:
    p = findings["player"]
    r = findings["recent"]
    pool = findings["champion_pool"]
    br = findings.get("best_role")

    keep_str = ",".join(
        f"{c['name']}({c['games']}g,{c['wr']}%WR,{c['kda']}KDA)"
        for c in pool["keep"]
    ) or "none"

    drop_str = ",".join(
        f"{c['name']}({c['games']}g,{c['wr']}%WR,{c['reason']})"
        for c in pool["drop"]
    ) or "none"

    lines = [
        f"player={p['name']}|rank={p['tier']} {p['rank']} {p['lp']}LP"
        f"|season={p['season_wr']}%WR|streak={p['streak']:+d}",
        f"recent={r['games']}g {r['wr']}%WR",
    ]

    if br:
        lines.append(
            f"best_role={br['role']}({br['wr']}%WR,{br['kda']}KDA,{br['delta_pp']:+.1f}pp)"
        )

    lines += [f"keep={keep_str}", f"drop={drop_str}"]

    s = findings.get("strength")
    if s:
        lines.append(
            f"strength={s['type']}:{s['champion']} {s['value']} vs {s['benchmark']} bench (+{s['delta_pct']}%)"
        )
    else:
        lines.append("strength=none")

    for i, w in enumerate(findings.get("weaknesses", []), 1):
        lines.append(
            f"weak{i}={w['type']}:{w['champion']} {w['value']} vs {w['benchmark']} bench [{w['severity'].upper()}]"
        )

    for cf in findings.get("cross_flags", []):
        lines.append(f"cross={cf['type']}:{cf['champion']}({cf['note']})")

    lines.append(f"focus={findings.get('weekly_focus', 'maintain_consistency')}")

    # Meta context lines (~40 extra tokens when available)
    if meta:
        per_champ = meta.get("per_champ_meta", {})
        for champ, cm in list(per_champ.items())[:3]:
            tier_label = cm.get("tier", "?")
            meta_wr = cm.get("meta_wr", 0)
            build_gaps = cm.get("build_gaps", [])
            gap_str = f"|build_gap={len(build_gaps)}_items" if build_gaps else "|build=ok"
            lines.append(f"meta_{champ.lower()}: wr={meta_wr}%({tier_label}){gap_str}")

        for mi in meta.get("matchup_insights", [])[:2]:
            enemy = mi["enemy"]
            losses = mi["losses"]
            m_wr = mi.get("meta_wr")
            wr_str = f"|meta_wr={m_wr}%(unfavorable)" if m_wr and m_wr < 50 else ""
            lines.append(f"matchup_{enemy.lower()}: record=0-{losses}{wr_str}")

        if meta.get("tilt_flag"):
            lines.append(f"tilt: consecutive_losses={meta['consecutive_losses']}")

        picks = meta.get("meta_picks", [])
        if picks:
            picks_str = ",".join(f"{p['name']}({p['wr']}%{p['tier']})" for p in picks[:3])
            lines.append(f"meta_top_pool: {picks_str}")

    return "\n".join(lines)


def generate_coaching(payload: dict) -> dict:
    api_key = os.environ.get("OLLAMA_API_KEY", "")
    if not api_key:
        raise ValueError("OLLAMA_API_KEY is not configured on the server.")

    summoner = payload.get("summoner", {})
    ranked = payload.get("ranked", [])
    champion_stats = payload.get("champion_stats", {})
    match_analysis = payload.get("match_analysis", {})
    matches = payload.get("matches", [])

    findings = analyze_for_coaching(summoner, ranked, champion_stats, match_analysis)

    # Best-effort meta analysis — never blocks coaching if unavailable
    meta: dict | None = None
    if _META_AVAILABLE and champion_stats:
        try:
            solo = next(
                (q for q in ranked if q.get("queueType") == "RANKED_SOLO_5x5"), None
            )
            tier = solo.get("tier", "DEFAULT") if solo else "DEFAULT"
            meta = analyze_meta_gaps(champion_stats, match_analysis, matches, tier)
        except Exception as exc:
            logger.warning("Meta analysis failed (non-fatal): %s", exc)

    findings_text = _build_findings_text(findings, meta)

    client = OpenAI(base_url="https://ollama.com/v1", api_key=api_key)

    system_prompt = (
        "You are an expert League of Legends climbing coach. Analyze the pre-computed data and write "
        "specific, actionable advice in plain English with real numbers. "
        "Metric codes to translate: cs_low=farming/CS per minute, dmg_low=damage per minute, "
        "kda_low=deaths/KDA ratio, vision_low=vision score per game, role_wr_low=win rate in a specific role. "
        "Rules: (1) weakness detail must be 2 sentences — what is happening and why it costs LP. "
        "(2) weakness action must be a concrete drill with a measurable target, not generic advice. "
        "(3) strength must name the champion and specific stat with the exact number vs benchmark. "
        "(4) weekly_focus must be one actionable drill the player can do this week, with a measurable target. "
        "(5) Never return raw metric codes like 'kda_high' or 'cs_low' as field values — always write full sentences. "
        "Respond with valid JSON only, no markdown fences."
    )

    user_prompt = (
        f"{findings_text}\n\n"
        "Return JSON exactly:\n"
        '{"assessment":"2-3 sentences: rank, recent WR, and the single most important takeaway",'
        '"weaknesses":[{"title":"short readable label","detail":"2 sentences: what is happening and why it costs LP","action":"specific drill with a measurable target"}],'
        '"champion_pool":{"keep":["ChampName"],"drop":["ChampName"],"reasoning":"1-2 sentences on pool health and what to focus on"},'
        '"role_recommendation":{"recommended":"ROLE","reasoning":"1 sentence with specific numbers"},'
        '"strength":"1 sentence naming the champion, the stat with exact numbers vs benchmark, and what edge it gives",'
        '"weekly_focus":"1 concrete drill to do this week with a measurable target — no generic advice"}'
    )

    response = client.chat.completions.create(
        model="ministral-3:3b-cloud",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=950,
    )

    content = response.choices[0].message.content.strip()
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        # Truncated or malformed LLM response — humanized fallback from pre-computed findings
        p = findings["player"]
        w = findings.get("weaknesses", [])
        rank_str = f"{p['tier']} {p['rank']}".strip() or "Unranked"
        result = {
            "assessment": (
                f"{p['name']} is {rank_str} with {findings['recent']['wr']}% WR "
                f"over {findings['recent']['games']} recent games. "
                f"The analysis below highlights the highest-impact areas for climbing."
            ),
            "weaknesses": [_fallback_weakness(x) for x in w],
            "champion_pool": {
                "keep": [c["name"] for c in findings["champion_pool"]["keep"]],
                "drop": [c["name"] for c in findings["champion_pool"]["drop"]],
                "reasoning": "Based on win rate and game count across recent matches. Drop low-WR champions and double down on what's working.",
            },
            "role_recommendation": {
                "recommended": (findings.get("best_role") or {}).get("role", ""),
                "reasoning": "Highest combined win rate and KDA score across recent games in this role.",
            },
            "strength": _humanize_strength(findings.get("strength")),
            "weekly_focus": _humanize_weekly_focus(findings.get("weekly_focus", "maintain_consistency")),
        }

    # Always attach meta so the frontend can render tier badges / pre-session card
    result["meta"] = meta
    return result
