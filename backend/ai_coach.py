import os
import json
import re

from openai import OpenAI
from backend.analysis.coach_analysis import analyze_for_coaching


def _build_findings_text(findings: dict) -> str:
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
    return "\n".join(lines)


def generate_coaching(payload: dict) -> dict:
    api_key = os.environ.get("OLLAMA_API_KEY", "")
    if not api_key:
        raise ValueError("OLLAMA_API_KEY is not configured on the server.")

    summoner = payload.get("summoner", {})
    ranked = payload.get("ranked", [])
    champion_stats = payload.get("champion_stats", {})
    match_analysis = payload.get("match_analysis", {})

    findings = analyze_for_coaching(summoner, ranked, champion_stats, match_analysis)
    findings_text = _build_findings_text(findings)

    client = OpenAI(base_url="https://ollama.com/v1", api_key=api_key)

    system_prompt = (
        "You are a League of Legends coach. "
        "Write coaching advice using the pre-analyzed findings below. "
        "Respond with valid JSON only."
    )

    user_prompt = (
        f"{findings_text}\n\n"
        'Return JSON: {"assessment":"2-3 sentences","weaknesses":[{"title":"","detail":"","action":""}x3],'
        '"champion_pool":{"keep":[],"drop":[],"reasoning":""},'
        '"role_recommendation":{"recommended":"","reasoning":""},'
        '"strength":"","weekly_focus":""}'
    )

    response = client.chat.completions.create(
        model="gemini-3-flash-preview:cloud",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=700,
    )

    content = response.choices[0].message.content.strip()
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Truncated or malformed LLM response — return structured fallback from pre-computed findings
        p = findings["player"]
        w = findings.get("weaknesses", [])
        return {
            "assessment": f"{p['name']} is {p['tier']} {p['rank']} with {findings['recent']['wr']}% WR over {findings['recent']['games']} recent games.",
            "weaknesses": [
                {"title": x["type"].replace("_", " ").title(), "detail": f"{x['champion']}: {x['value']} vs {x['benchmark']} benchmark", "action": "Focus on improving this metric."}
                for x in w
            ],
            "champion_pool": {
                "keep": [c["name"] for c in findings["champion_pool"]["keep"]],
                "drop": [c["name"] for c in findings["champion_pool"]["drop"]],
                "reasoning": "Based on win rate and game count.",
            },
            "role_recommendation": {
                "recommended": (findings.get("best_role") or {}).get("role", ""),
                "reasoning": "Highest performance score across recent games.",
            },
            "strength": (findings.get("strength") or {}).get("type", ""),
            "weekly_focus": findings.get("weekly_focus", "maintain_consistency"),
        }
