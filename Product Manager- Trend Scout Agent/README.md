# PM-AG-002: TrendScout Agent
**The "Market Radar" for Product Strategy** | Stage 1: Discovery

TrendScout is a semi-autonomous AI agent that scans news, competitor updates, and product announcements daily — filtering noise and surfacing only the signals that matter to Product Managers.

---

## What It Does

| Step | Action |
|------|--------|
| 1. Fetch | Searches the web for recent news on your keyword watch list |
| 2. Filter | Removes stock news, hiring updates, and marketing fluff |
| 3. Score | Assigns a Strategic Impact Score (1–10) to each signal |
| 4. Digest | Outputs a Daily Market Pulse report (markdown file) |
| 5. Alert | Prints Slack-style DMs for high-impact signals (score > 6) |

**What it will NOT do:** predict stock movements, auto-update your roadmap, scrape paywalled content, or spam you with every mention.

---

## Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys)

---

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Set your API key**

On Windows:
```bash
set OPENAI_API_KEY=sk-your-key-here
```

On macOS / Linux:
```bash
export OPENAI_API_KEY=sk-your-key-here
```

**3. Customize your watch list**

Edit `watchlist.json` to add the keywords, competitor names, or topics you want to monitor:
```json
{
  "keywords": [
    "OpenAI product updates",
    "Figma AI features",
    "SaaS pricing changes",
    "Your Competitor name"
  ]
}
```

---

## Running the Agent

**Option A — Claude slash command (recommended)**

Open this project folder in Claude Code, then run:
```
/trendscout
```

Pass specific keywords directly:
```
/trendscout "Notion AI" "Linear updates" "Intercom pricing"
```

**Option B — Python directly**

Run with keywords from `watchlist.json`:
```bash
python trendscout_agent.py
```

Run with specific keywords:
```bash
python trendscout_agent.py "OpenAI updates" "Figma AI" "SaaS pricing"
```

---

## Output

Every run produces:

| Output | Location | Description |
|--------|----------|-------------|
| Daily Digest | `digest_YYYY-MM-DD.md` | Full market pulse report (markdown) |
| Signal History | `history.json` | Cumulative log of all signals found |
| Console alerts | stdout | Slack-style DMs for high-impact signals |

**Sample digest structure:**
```
# TrendScout Daily Market Pulse
Date: July 02, 2025  |  Agent: PM-AG-002

## HIGH PRIORITY SIGNALS
### [OpenAI product updates] GPT-4o gets real-time voice API
- Summary: OpenAI opened its real-time voice API to all developers at $0.06/min
- Impact Score: 9/10
- PM Takeaway: Our voice assistant feature is now directly commoditized — reprice or differentiate within 60 days.
- Source: techcrunch.com

## MARKET SIGNALS (Score 6-7)
...

## ARCHIVED (Score 1-5)
...
```

---

## Impact Score Guide

| Score | Meaning | Action |
|-------|---------|--------|
| 8–10 | Major launch, pricing change, platform pivot | High Priority — act now |
| 6–7 | Meaningful update worth tracking | Include in weekly digest |
| 1–5 | Minor news | Archive only |

---

## Decision Rules

| Condition | Action |
|-----------|--------|
| News is about Stock Market or Hiring | Discard |
| Competitor launches a new feature | Tag High Priority |
| Duplicate story from multiple sources | Keep most authoritative source |
| No relevant news found | Silent — no digest entry |

---

## File Structure

```
PM-AG-002 - TrendScout Agent - Stage1 Discovery/
├── trendscout_agent.py       # Main agent
├── watchlist.json            # Keywords to monitor (edit this)
├── requirements.txt          # Python dependencies
├── history.json              # Created on first run — signal log
├── digest_YYYY-MM-DD.md      # Created each run — daily report
└── .claude/
    └── commands/
        └── trendscout.md     # /trendscout Claude slash command
```

---

## Success Metrics

- **Target:** 3–5 high-quality signals per week
- **Key question:** Did we miss any major competitor launch? (Blindspot Rate)

---

## Human-in-the-Loop Checkpoints

- **Relevance check:** If the agent posts too much, tighten the `SYSTEM_PROMPT` in `trendscout_agent.py` (raise the filter threshold).
- **Hallucination check:** Click the source link in each signal to verify the news is real before acting on it.
