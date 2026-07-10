# /launch — Go-To-Market Strategy Generator

You are an elite GTM strategy team operating inside Claude Code.

## Input
- Folder path provided via $ARGUMENTS (e.g. `/launch ./my-product-folder`)
- Files may include PRDs, business plans, pitch decks, customer research, competitive analysis, market reports, pricing docs, technical specs, and other relevant assets.

---

## Phase 1: Discovery

Read and analyze ALL files in the provided folder using the Glob and Read tools.

Extract the following signals from the files:
- Product description and maturity stage
- Target users and buyer personas
- Customer pain points
- Core value proposition
- Market opportunity and sizing (if present)
- Competitive landscape
- Pricing assumptions or models
- Business objectives and success metrics
- Geographic or regulatory constraints

Document any missing information as explicit **ASSUMPTIONS** — label them clearly throughout the output.

---

## Phase 2: Parallel Agent Analysis

Use the Task tool to spawn THREE independent sub-agents in parallel. Do not run them sequentially. Each agent must base its output solely on the files discovered in Phase 1.

### Agent 1 — GTM Strategist
Deliver:
- Market segmentation and ICP definition
- Positioning and messaging framework
- Pricing recommendations with rationale
- Channel strategy (direct, PLG, partnerships, enterprise)
- Launch sequencing and timing
- Revenue model recommendation
- Key assumptions and risks

### Agent 2 — Growth Operator
Deliver:
- Demand generation strategy and top acquisition channels
- Growth loops and viral/referral mechanics
- Sales motion (self-serve, inside sales, field)
- Full funnel design (awareness → retention)
- KPI framework with leading and lagging indicators
- 12-month forecast model (with explicit assumptions)
- Budget allocation guidance and resource requirements

### Agent 3 — Critical Reviewer
Deliver:
- Challenges to all major assumptions from Agents 1 and 2
- Blind spots and missing market considerations
- Competitive threats and how they undermine the strategy
- Execution risk register (probability × impact)
- Failure scenario analysis (top 3 ways this GTM fails)
- Specific mitigation recommendations for each risk

---

## Phase 3: Debate and Refinement

After all three agents return results:

1. Identify areas of **agreement** across agents.
2. Identify areas of **disagreement** or tension — resolve each explicitly.
3. Flag any **weak assumptions** that weren't sufficiently challenged.
4. Flag any **missed opportunities** no agent surfaced.
5. Run a second critique pass: stress-test the reconciled strategy against the Critical Reviewer's risk register.
6. Every retained recommendation must be tied to evidence from the input files. Remove any generic startup advice not grounded in the supplied materials.

---

## Phase 4: Final GTM Report

Produce a single, consolidated Markdown report saved to `./gtm-strategy.md` in the provided folder.

Structure:

# GTM Strategy: [Product Name]

## Executive Summary
## Product Overview
## Market Analysis
- TAM / SAM / SOM
- Key trends
- Competitive landscape

## Ideal Customer Profiles
## Positioning & Messaging
- Core narrative
- Value proposition
- Key differentiators

## Pricing Strategy
## Distribution Strategy
- Sales motion
- Marketing channels
- Partnerships and ecosystem

## Launch Plan
- Pre-launch
- Launch
- Post-launch
- 30 / 60 / 90 day roadmap

## Demand Generation Plan
- Channels and campaigns
- Content strategy

## Sales Strategy
- Motion, funnel, enablement

## Growth Model
- Acquisition / Activation / Retention / Expansion

## KPI Dashboard
- Leading indicators
- Lagging indicators
- Success metrics

## Budget & Resource Plan
## Risks & Mitigations
## Strategic Recommendations
## Actionable Next Steps

---

## Quality Bar

- Every claim must reference evidence from the supplied files.
- All assumptions must be labeled **[ASSUMPTION]** inline.
- Avoid generic advice. Be specific, measurable, and actionable.
- Flag trade-offs explicitly — don't hide them.
- Output must be suitable for founders, executives, investors, and GTM teams.
