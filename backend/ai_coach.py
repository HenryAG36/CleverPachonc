import os
import json
import re
import logging

from openai import OpenAI
from backend.analysis.coach_analysis import analyze_for_coaching

logger = logging.getLogger(__name__)

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
        "You are a League of Legends coach. Analyze the pre-computed findings below and write "
        "clear, specific coaching advice in plain English. "
        "Translate all metric codes: cs_low=farm/CS, dmg_low=damage output, kda_low=deaths/survival, "
        "vision_low=vision control, role_wr_low=role performance. "
        "Always include specific numbers and actionable targets. "
        "Reference champion names and current patch meta where provided. "
        "Respond with valid JSON only, no markdown."
    )

    user_prompt = (
        f"{findings_text}\n\n"
        'Return JSON: {"assessment":"2-3 sentences","weaknesses":[{"title":"","detail":"","action":""}x3],'
        '"champion_pool":{"keep":[],"drop":[],"reasoning":""},'
        '"role_recommendation":{"recommended":"","reasoning":""},'
        '"strength":"","weekly_focus":""}'
    )

    response = client.chat.completions.create(
        model="ministral-3:3b-cloud",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=700,
    )

    content = response.choices[0].message.content.strip()
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        # Truncated or malformed LLM response — structured fallback from pre-computed findings
        p = findings["player"]
        w = findings.get("weaknesses", [])
        result = {
            "assessment": (
                f"{p['name']} is {p['tier']} {p['rank']} with {findings['recent']['wr']}% WR "
                f"over {findings['recent']['games']} recent games."
            ),
            "weaknesses": [
                {
                    "title": x["type"].replace("_", " ").title(),
                    "detail": f"{x['champion']}: {x['value']} vs {x['benchmark']} benchmark",
                    "action": "Focus on improving this metric.",
                }
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

    # Always attach meta so the frontend can render tier badges / pre-session card
    result["meta"] = meta
    return result
