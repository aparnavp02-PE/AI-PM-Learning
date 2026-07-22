# CLAUDE.md — AccessibilityBot (PM-AG-014)

## What This Project Is

A semi-autonomous WCAG 2.1 Level AA compliance validator. A designer uploads a UI screenshot to Slack channel `#a11y-check`; the bot replies in-thread with a structured audit report citing specific WCAG violations, suggested hex fixes, and tap-target warnings.

Agent type: **Validator** (flags issues, does not fix them).
Automation level: **Semi-Autonomous** (audits designs, flags for human fix).

---

## Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill in secrets
cp .env.example .env

# Start the Flask webhook server
python -m src.app

# Run tests
pytest tests/ -v
```

The server listens on `http://0.0.0.0:3000` by default. Set `PORT` in `.env` to override.

Health check endpoint: `GET /health` — returns `{"status": "ok"}`.

---

## Key Files and Their Roles

| File | Role |
|---|---|
| `src/app.py` | Flask webhook server. Handles Slack URL verification and `message` events. Spawns a background thread per image so Slack's 3-second timeout is never hit. |
| `src/auditor.py` | Core logic. Encodes the image as base64, assembles the GPT-4o call with system + task + refinement prompts, returns the audit string. |
| `src/slack_handler.py` | Two helpers only: `download_file()` (authenticated GET) and `post_audit_report()` (thread reply). |
| `prompts/system_prompt.md` | Authoritative source for the bot persona and scope guardrails. The text in `auditor.py:SYSTEM_PROMPT` must stay in sync with this file. |
| `prompts/task_prompt.md` | Authoritative source for the WCAG checklist sent with each image. Synced to `auditor.py:TASK_PROMPT`. |
| `prompts/refinement_prompt.md` | Appended to the task prompt. Forces citation of a WCAG Success Criterion for every finding. |
| `make_blueprint/scenario.json` | Importable Make.com blueprint — the no-code deployment path. Prompts are duplicated inline here (keep in sync with `prompts/`). |
| `knowledge/wcag_2_1_criteria.json` | Structured WCAG rules uploaded as RAG context. Gives the model accurate criterion IDs and thresholds. |
| `knowledge/brand_colors_template.json` | Brand palette with pre-calculated contrast ratios. Replace placeholder hex values with real brand colors before deploying. |
| `slack/app_manifest.json` | Slack app configuration. Update `request_url` to your deployed server URL before importing. |
| `docs/DECISION_RULES.md` | IF/THEN logic reference. When changing audit behavior, update both the prompts and this doc. |
| `docs/HITL_GUIDELINES.md` | False positive reference and escalation path for designers. |
| `docs/MAKE_SETUP.md` | Step-by-step no-code setup guide for Make.com deployment. |

---

## Prompt Editing Convention

**Edit prompts in `prompts/*.md` first, then sync to `src/auditor.py`.**

Never put prompt text only in `auditor.py` — the `.md` files are the source of truth so non-developers can read and propose changes without touching Python.

After editing a prompt file, update the corresponding constant in `auditor.py`:
- `prompts/system_prompt.md` → `auditor.py:SYSTEM_PROMPT`
- `prompts/task_prompt.md` → `auditor.py:TASK_PROMPT`
- `prompts/refinement_prompt.md` → `auditor.py:REFINEMENT_PROMPT`

Also update the inline prompt in `make_blueprint/scenario.json` (Module 3, messages array) to keep the no-code path current.

---

## Decision Rules (Summary)

Full table in `docs/DECISION_RULES.md`. Key thresholds hardcoded into the task prompt:

| Element | Contrast Threshold |
|---|---|
| Normal text (<18pt) | 4.5:1 |
| Large text (≥18pt or ≥14pt bold) | 3:1 |
| Decorative / disabled | Exempt |
| Touch targets | ≥ 44×44px |
| Text size | ≥ 12px |

---

## Agent Scope — Hard Boundaries

The bot MUST NOT:
- Fix or modify designs (no Figma API calls)
- Test screen reader behavior
- Certify legal ADA/WCAG compliance
- State exact pixel measurements it cannot verify (phrase as "appears to be smaller than 44px")

If asked to add functionality outside this scope, decline and explain the boundary.

---

## Testing

Tests use `pytest` with `unittest.mock`. All OpenAI and Slack SDK calls are mocked — no live API calls in the test suite.

```bash
pytest tests/ -v
```

Key test cases in `tests/test_auditor.py`:
- Pass/fail report content
- Context string injection
- GPT-4o model and `detail: high` enforcement
- Temperature ≤ 0.2 enforcement
- Slack file download (200 vs 403)
- Thread reply content and footer

When adding a new audit check, add at least one test for the pass case and one for the fail case.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SLACK_BOT_TOKEN` | Yes | — | Bot OAuth token (`xoxb-...`) |
| `SLACK_SIGNING_SECRET` | Yes | — | Used to verify Slack request signatures |
| `OPENAI_API_KEY` | Yes | — | GPT-4o access required |
| `SLACK_CHANNEL_ID` | No | — | Optional; for future channel-scoped filtering |
| `PORT` | No | `3000` | Flask server port |

---

## Known Failure Modes

| Failure | Cause | Mitigation |
|---|---|---|
| Bot doesn't reply | Image MIME type not in `SUPPORTED_MIME_TYPES` | Add the type to the set in `app.py` |
| False positive on disabled button | GPT-4o can't distinguish disabled state visually | Designer checks HITL guidelines and re-uploads with context |
| Contrast flag on decorative element | GPT-4o flags background patterns | Prompt says "Decorative elements: exempt" — review HITL doc |
| Slack 403 on file download | Bot token missing `files:read` scope | Re-install Slack app with correct scopes |
| OpenAI timeout | Large image + high detail takes >30s | Increase `max_tokens` budget or compress image before upload |

---

## Dependencies

| Package | Purpose |
|---|---|
| `flask` | Webhook HTTP server |
| `openai` | GPT-4o vision API client |
| `slack-sdk` | Slack Web API client + signature verification |
| `python-dotenv` | Loads `.env` into `os.environ` |
| `requests` | Authenticated file download from Slack CDN |
| `pytest` / `pytest-mock` | Test runner and mock helpers |

---

## Deployment Checklist (Python Path)

- [ ] `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, `OPENAI_API_KEY` set in environment
- [ ] `slack/app_manifest.json` imported and app installed to workspace
- [ ] `request_url` in Slack Event Subscriptions points to live `/slack/events` endpoint
- [ ] Bot invited to `#a11y-check` channel
- [ ] `knowledge/brand_colors_template.json` updated with real brand hex values
- [ ] Pilot test passed: light-gray-on-white screenshot triggers WCAG 1.4.3 flag
- [ ] `pytest tests/ -v` passes with 0 failures
