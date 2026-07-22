# AccessibilityBot (PM-AG-014)
### The "WCAG Compliance" Validator

A semi-autonomous AI agent that scans UI screenshots/mockups for **WCAG 2.1 Level AA** violations before code is written — catching contrast failures, missing labels, and undersized tap targets in seconds.

---

## What It Does

| Check | WCAG Criterion | Pass Threshold |
|---|---|---|
| Color Contrast (normal text) | 1.4.3 Contrast Minimum | ≥ 4.5:1 |
| Color Contrast (large text >18pt) | 1.4.3 Contrast Minimum | ≥ 3:1 |
| Touch Target Size | 2.5.5 Target Size | ≥ 44×44 px |
| Missing Icon Labels | 1.1.1 Non-text Content | Label required |
| Input Field Labels | 1.3.1 Info and Relationships | Visible label |
| Text Size | 1.4.4 Resize Text | ≥ 12 px |

**What it will NOT do:** fix designs, simulate screen readers, or certify legal compliance.

---

## Architecture

```
Designer uploads screenshot
        │
        ▼
  Slack #a11y-check
        │
        ▼
  Make.com Scenario
   ┌────┴────┐
   │ Download │
   │  Image   │
   └────┬────┘
        │
        ▼
  OpenAI GPT-4o
  (Vision Model)
  System Prompt +
  Task Prompt +
  Image (base64)
        │
        ▼
  Audit Report
        │
        ▼
  Slack Thread Reply
```

---

## Project Structure

```
accessibility-bot/
├── README.md                          ← You are here
├── CLAUDE.md                          ← AI coding assistant context
├── .env.example                       ← Secrets template (copy to .env)
├── .gitignore
├── requirements.txt                   ← Python dependencies
│
├── src/                               ← Python / Flask implementation (Option B)
│   ├── __init__.py
│   ├── app.py                         ← Flask webhook server (Slack event handler)
│   ├── auditor.py                     ← Core GPT-4o vision audit logic + prompts
│   └── slack_handler.py               ← File download + thread reply helpers
│
├── prompts/                           ← All prompts — edit here, not in code
│   ├── system_prompt.md               ← Bot persona, scope, and guardrails
│   ├── task_prompt.md                 ← WCAG checklist injected with each image
│   └── refinement_prompt.md           ← Appended to force WCAG criterion citation
│
├── make_blueprint/
│   └── scenario.json                  ← Importable Make.com 4-module blueprint (Option A)
│
├── slack/
│   └── app_manifest.json              ← Slack app setup — import at api.slack.com/apps
│
├── knowledge/                         ← RAG context files — upload to GPT-4o call
│   ├── wcag_2_1_criteria.json         ← Structured WCAG 2.1 AA rules with examples
│   └── brand_colors_template.json     ← Brand palette with pre-calculated contrast ratios
│
├── docs/
│   ├── MAKE_SETUP.md                  ← Step-by-step no-code deployment guide
│   ├── DECISION_RULES.md              ← Full IF/THEN logic and exemption reference
│   └── HITL_GUIDELINES.md            ← False positives, vision limits, escalation path
│
└── tests/
    ├── __init__.py
    └── test_auditor.py                ← Unit tests for auditor + Slack handler
```

---

## Two Ways to Deploy

### Option A — No-Code (Make.com) ← Recommended for non-developers

Best for teams without a server or deployment pipeline.

1. Follow [`docs/MAKE_SETUP.md`](docs/MAKE_SETUP.md) step by step
2. Import [`make_blueprint/scenario.json`](make_blueprint/scenario.json) into Make.com
3. Connect your Slack and OpenAI accounts
4. Done — no code to write or host

### Option B — Self-Hosted Python / Flask

Best for teams that want version control over the bot logic, custom middleware, or CI/CD integration.

---

## Option A: Make.com Quickstart

```
make_blueprint/scenario.json  →  Make.com (Import Blueprint)
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
     Module 1: Slack           Module 3: OpenAI        Module 4: Slack
     Watch #a11y-check         GPT-4o Vision           Post to Thread
     (image filter)            (system + task prompt)
              │
     Module 2: Slack
     Download File
```

Full walkthrough: [`docs/MAKE_SETUP.md`](docs/MAKE_SETUP.md)

---

## Option B: Python / Flask Setup

### Prerequisites

- Python 3.11+
- A Slack workspace where you can install apps
- An OpenAI API key with GPT-4o access
- A public HTTPS URL for the Slack webhook (use [ngrok](https://ngrok.com) for local dev)

### 1. Clone & Install

```bash
git clone https://github.com/your-org/accessibility-bot.git
cd accessibility-bot
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Open .env and fill in your values
```

| Variable | Where to find it |
|---|---|
| `SLACK_BOT_TOKEN` | Slack App → OAuth & Permissions → Bot Token (`xoxb-...`) |
| `SLACK_SIGNING_SECRET` | Slack App → Basic Information → Signing Secret |
| `OPENAI_API_KEY` | platform.openai.com → API Keys |
| `SLACK_CHANNEL_ID` | Right-click `#a11y-check` in Slack → Copy Channel ID |
| `PORT` | Optional — defaults to `3000` |

### 3. Create the Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From manifest**
2. Paste the contents of [`slack/app_manifest.json`](slack/app_manifest.json)
3. Click **Install to workspace** and approve the OAuth scopes
4. Copy the Bot Token and Signing Secret into your `.env`
5. Invite the bot to the channel: `/invite @AccessibilityBot` in `#a11y-check`

### 4. Run the Server

```bash
python -m src.app
```

For local development, expose the server with ngrok in a second terminal:

```bash
ngrok http 3000
```

Then go to **Slack App → Event Subscriptions → Request URL** and set it to:

```
https://<your-ngrok-subdomain>.ngrok-free.app/slack/events
```

Slack will send a verification request — the app handles it automatically.

### 5. Run the Tests

```bash
pytest tests/ -v
```

### 6. Pilot Test

Upload a screenshot with **light gray text on a white background** to `#a11y-check`.
The bot should reply in the thread within 30 seconds, citing WCAG 1.4.3 Contrast Minimum.

---

## Prompts

All prompts are in the [`prompts/`](prompts/) directory and can be edited without touching code:

- [`system_prompt.md`](prompts/system_prompt.md) — Bot persona and hard constraints
- [`task_prompt.md`](prompts/task_prompt.md) — The audit checklist sent with each image
- [`refinement_prompt.md`](prompts/refinement_prompt.md) — Forces WCAG citation on every finding

---

## Knowledge Base (RAG)

Upload these two files as context in your GPT-4o call or Make.com scenario:

| File | Purpose |
|---|---|
| [`knowledge/wcag_2_1_criteria.json`](knowledge/wcag_2_1_criteria.json) | Structured WCAG rules the bot enforces |
| [`knowledge/brand_colors_template.json`](knowledge/brand_colors_template.json) | Your brand palette — bot suggests on-brand fixes |

---

## Success Metrics

| Metric | Target |
|---|---|
| Audit turnaround time | < 30 seconds |
| Accessibility tickets filed in QA | 0 |
| False positive rate | < 10% |

---

## RACI

| Role | Person |
|---|---|
| Responsible (Builder) | UX Lead / AI Engineer |
| Accountable (Owner) | Head of Design |
| Consulted | Frontend Lead |
| Informed | Legal / Compliance Team |

---

## Limitations & Known False Positives

See [`docs/HITL_GUIDELINES.md`](docs/HITL_GUIDELINES.md) for the full list. Key ones:

- **Disabled buttons** are exempt from contrast rules — verify before acting on a flag
- **Decorative elements** (background patterns, dividers) are exempt
- Pixel measurements are **estimates** — use Stark or Figma's accessibility plugin for exact values

---

## License

MIT
