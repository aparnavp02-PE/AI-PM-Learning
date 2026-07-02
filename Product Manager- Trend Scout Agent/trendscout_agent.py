#!/usr/bin/env python3
"""
PM-AG-002: TrendScout Agent - The "Market Radar" for Product Strategy
Stage: 1 - Discovery
Agent Type: Analyzer (Scans external data)
Automation Level: Semi-Autonomous (Runs on demand / daily, human acts on signals)

This agent helps Product Managers by continuously scanning news, patents, and
competitor updates so the team never misses a strategic threat or emerging opportunity.
"""

import openai
import json
import re
import sys
from datetime import datetime, date
from pathlib import Path

# ── File Paths ─────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
WATCHLIST_FILE = SCRIPT_DIR / "watchlist.json"
HISTORY_FILE = SCRIPT_DIR / "history.json"

# ── Prompts ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are TrendScout, a Strategic Product Analyst. Your job is to filter noise and find signal.

Core Directives:
1. Ignore press releases that are just 'marketing fluff'.
2. Focus on: New Features, Pricing Changes, Pivot announcements, and Patents.
3. Always answer the question: "Why should a Product Manager care about this?"

Decision Rules:
- News is about Stock Market or Hiring -> Discard entirely
- Competitor launches a new feature -> Tag priority as "High"
- Duplicate story from multiple sources -> Keep only the most authoritative source
- No relevant strategic news found -> Set null_result to true, signals to []

Output ONLY valid JSON matching this exact schema (no markdown, no extra text):
{
  "keyword": "string",
  "signals": [
    {
      "headline": "string",
      "summary": "string - one concise bullet summarizing the strategic change",
      "impact_score": <integer 1-10>,
      "priority": "High or Medium or Low",
      "pm_takeaway": "string - specific insight, NOT generic (e.g. 'Competitor X is targeting our Enterprise segment with this pricing change')",
      "source": "string - URL or publication name"
    }
  ],
  "null_result": <true or false>
}

Impact Score Guide:
  8-10 -> Major competitor launch, pricing change, platform pivot -> High Priority
  6-7  -> Meaningful product update worth tracking -> Include in digest
  1-5  -> Minor news -> Archive only (still include in signals array)

If no relevant strategic news is found, return exactly:
{"keyword": "...", "signals": [], "null_result": true}"""

SEARCH_PROMPT = """Search for the latest product news, feature releases, and strategic announcements for "{keyword}" from the last 24-48 hours.

Then analyze and filter:
1. Remove articles about stock prices, hiring news, minor HR updates, or generic opinion pieces.
2. For each strategic article that remains: summarize the key update in one bullet point.
3. Assign a Strategic Impact Score (1-10) based on how much it disrupts the market.
4. Write a specific "PM Takeaway" - NOT generic like "We should watch this".
   Good example: "OpenAI's GPT-4o price cut directly undercuts our $49/mo AI tier - revisit pricing strategy."
5. If a PM Takeaway comes out generic, rewrite it to be specific.

Return ONLY valid JSON. No markdown code fences, no extra explanation."""

# ── Watchlist ──────────────────────────────────────────────────────────────────

DEFAULT_WATCHLIST = {
    "description": "TrendScout Watch List - Edit keywords to customize what the agent monitors",
    "keywords": [
        "Generative AI features",
        "SaaS pricing changes",
        "OpenAI product updates",
        "Anthropic Claude updates",
        "Notion AI features"
    ]
}


def load_watchlist() -> list[str]:
    if not WATCHLIST_FILE.exists():
        WATCHLIST_FILE.write_text(json.dumps(DEFAULT_WATCHLIST, indent=2))
        print(f"[TrendScout] Created default watchlist: {WATCHLIST_FILE.name}")
    data = json.loads(WATCHLIST_FILE.read_text())
    return data.get("keywords", [])


# ── History ────────────────────────────────────────────────────────────────────

def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    return json.loads(HISTORY_FILE.read_text())


def append_to_history(entries: list[dict]) -> None:
    history = load_history()
    history.extend(entries)
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


# ── Core Scan Logic ────────────────────────────────────────────────────────────

def extract_json(text: str) -> dict | None:
    """Parse JSON from the model's response, stripping markdown fences if present."""
    text = text.strip()
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if match:
            text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None


def scan_keyword(client: openai.OpenAI, keyword: str) -> dict | None:
    """
    Use GPT-4o with web search (Responses API) to scan for strategic news on a keyword.
    The web_search_preview tool is handled server-side by OpenAI.
    """
    response = client.responses.create(
        model="gpt-4o",
        instructions=SYSTEM_PROMPT,
        tools=[{"type": "web_search_preview"}],
        input=SEARCH_PROMPT.format(keyword=keyword),
    )

    text = response.output_text
    if not text:
        return None

    result = extract_json(text)
    if result:
        result.setdefault("keyword", keyword)
        result.setdefault("null_result", False)
        result.setdefault("signals", [])
        result["scanned_at"] = datetime.now().isoformat()
        return result

    return None


# ── Decision Rules ─────────────────────────────────────────────────────────────

def apply_decision_rules(result: dict) -> dict:
    """
    Enforce blueprint decision rules on Claude's output:
    - Normalize priority based on impact_score
    - Signals scoring <= 6 are archived, not alerted
    """
    if result.get("null_result"):
        return result

    for signal in result.get("signals", []):
        score = signal.get("impact_score", 0)
        if score >= 8:
            signal["priority"] = "High"
        elif score >= 6:
            signal["priority"] = "Medium"
        else:
            signal["priority"] = "Low"

    return result


# ── Output Formatting ──────────────────────────────────────────────────────────

def build_digest(results: list[dict], run_date: str) -> str:
    """Format all scan results as a Daily Market Pulse markdown digest."""
    high_signals, medium_signals, low_signals = [], [], []

    for result in results:
        if result.get("null_result") or not result.get("signals"):
            continue
        for signal in result["signals"]:
            enriched = {**signal, "keyword": result["keyword"]}
            score = enriched.get("impact_score", 0)
            if score >= 8:
                high_signals.append(enriched)
            elif score >= 6:
                medium_signals.append(enriched)
            else:
                low_signals.append(enriched)

    lines = [
        "# TrendScout Daily Market Pulse",
        f"**Date:** {run_date}  |  **Agent:** PM-AG-002  |  **Stage:** Discovery",
        "",
        "---",
        "",
    ]

    if high_signals:
        lines += ["## HIGH PRIORITY SIGNALS", ""]
        for s in high_signals:
            lines += [
                f"### [{s['keyword']}] {s['headline']}",
                f"- **Summary:** {s['summary']}",
                f"- **Impact Score:** {s['impact_score']}/10",
                f"- **PM Takeaway:** {s['pm_takeaway']}",
                f"- **Source:** {s.get('source', 'N/A')}",
                "",
            ]

    if medium_signals:
        lines += ["## MARKET SIGNALS (Score 6-7)", ""]
        for s in medium_signals:
            lines += [
                f"**[{s['keyword']}]** {s['headline']}",
                f"  - {s['summary']}",
                f"  - Impact: {s['impact_score']}/10  |  PM Takeaway: {s['pm_takeaway']}",
                f"  - Source: {s.get('source', 'N/A')}",
                "",
            ]

    if low_signals:
        lines += ["## ARCHIVED (Score 1-5)", ""]
        for s in low_signals:
            lines.append(
                f"- **[{s['keyword']}]** {s['headline']}  *(Score: {s['impact_score']}/10)*"
            )
        lines.append("")

    if not high_signals and not medium_signals and not low_signals:
        lines += [
            "## No Significant Signals Today",
            "",
            "No strategic threats or opportunities detected above threshold.",
            "Silence is better than noise.",
            "",
        ]

    lines += [
        "---",
        f"*Generated by TrendScout (PM-AG-002) | {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ]

    return "\n".join(lines)


def print_slack_alerts(results: list[dict]) -> None:
    """
    Print Slack-DM-style urgent alerts for signals with impact_score > 6.
    Blueprint: 'If Impact > High -> Send Slack DM'
    """
    alerts = [
        (result["keyword"], signal)
        for result in results
        for signal in result.get("signals", [])
        if signal.get("impact_score", 0) > 6
    ]

    if not alerts:
        return

    print("\n" + "=" * 60)
    print("SLACK DM: #market-intel  (High-Impact Alerts)")
    print("=" * 60)
    for keyword, s in alerts:
        print(f"\n  [TrendScout Signal: {keyword}]")
        print(f"  News:        {s['summary']}")
        print(f"  Impact:      {s['impact_score']}/10")
        print(f"  PM Takeaway: {s['pm_takeaway']}")
        print(f"  Source:      {s.get('source', 'N/A')}")
        print("  " + "-" * 50)


# ── Entry Point ────────────────────────────────────────────────────────────────

def main():
    today = date.today()
    print(f"TrendScout Agent (PM-AG-002) | {today.isoformat()}")
    print("=" * 60)

    # Keywords: CLI args override watchlist.json
    if len(sys.argv) > 1:
        keywords = sys.argv[1:]
        print(f"Keywords (CLI): {keywords}")
    else:
        keywords = load_watchlist()
        print(f"Keywords (watchlist.json): {keywords}")

    if not keywords:
        print("ERROR: No keywords to scan. Add keywords to watchlist.json or pass as CLI args.")
        sys.exit(1)

    client = openai.OpenAI()

    print(f"\nScanning {len(keywords)} keyword(s)...\n")

    results = []
    for keyword in keywords:
        print(f"  [{keyword}]", end=" ", flush=True)
        result = scan_keyword(client, keyword)
        if result is None:
            print("ERROR - could not parse response")
            continue
        result = apply_decision_rules(result)
        results.append(result)

        signals = result.get("signals", [])
        if result.get("null_result") or not signals:
            print("no relevant signals")
        else:
            max_score = max((s.get("impact_score", 0) for s in signals), default=0)
            high_count = sum(1 for s in signals if s.get("impact_score", 0) >= 7)
            print(f"{len(signals)} signal(s) | max score: {max_score}/10 | high-impact: {high_count}")

    if not results:
        print("\nNo results. Verify OPENAI_API_KEY and network access.")
        sys.exit(1)

    # Build and save digest
    digest_file = SCRIPT_DIR / f"digest_{today.isoformat()}.md"
    digest_text = build_digest(results, today.strftime("%B %d, %Y"))
    digest_file.write_text(digest_text, encoding="utf-8")

    # Archive all signals to history.json
    history_entries = [
        {
            "date": today.isoformat(),
            "keyword": result["keyword"],
            "headline": signal.get("headline"),
            "impact_score": signal.get("impact_score"),
            "priority": signal.get("priority"),
            "source": signal.get("source"),
            "pm_takeaway": signal.get("pm_takeaway"),
        }
        for result in results
        for signal in result.get("signals", [])
    ]
    if history_entries:
        append_to_history(history_entries)

    # Print digest to stdout
    print("\n" + "=" * 60)
    print(digest_text)

    # Slack-style urgent alerts for high-impact signals
    print_slack_alerts(results)

    # Run summary (Success Metric: target 3-5 high-quality signals/week)
    all_signals = [s for r in results for s in r.get("signals", [])]
    high_impact = [s for s in all_signals if s.get("impact_score", 0) >= 7]
    print(f"\nRun Summary: {len(all_signals)} total signals | {len(high_impact)} high-impact (>=7)")
    print(f"Digest saved: {digest_file.name}")
    if history_entries:
        print(f"History:      {len(history_entries)} entries logged to history.json")


if __name__ == "__main__":
    main()
