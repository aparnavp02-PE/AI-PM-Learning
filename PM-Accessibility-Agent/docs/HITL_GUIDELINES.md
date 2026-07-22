# Human-in-the-Loop (HITL) Guidelines

When a designer receives an AccessibilityBot audit report, they should verify before acting on any flagged item. This document explains the known failure modes and how to handle them.

---

## Review Checkpoints

Before making a design change based on a bot finding, the designer must answer:

1. **Is the element disabled?** — Disabled buttons and inputs are exempt from WCAG contrast rules. If the bot flagged a disabled button, ignore the contrast warning.
2. **Is the element decorative?** — Background patterns, watermarks, and illustration fills are exempt. If the bot flagged a decorative shape, ignore it.
3. **Is the text a logotype?** — WCAG explicitly exempts logo text. Ignore contrast flags on brand logos.
4. **Could the tap target have invisible padding?** — A small icon button in code may have a large tap area via padding. Verify in the developer's implementation before requesting a redesign.

---

## Known False Positive Patterns

| Bot Finding | Likely False Positive When... | Correct Action |
|---|---|---|
| Low contrast on gray text | The element is a disabled control | Verify state → ignore if disabled |
| Missing label on icon | The icon is decorative only (not interactive) | Verify interactivity → ignore if decorative |
| Touch target too small | The icon has `padding: 12px` in CSS making actual tap area 44px+ | Verify with dev → may be fine |
| Text too small | The text is a legal disclaimer that is intentionally small | Still flag — WCAG does not make exceptions for disclaimers |
| Low contrast on placeholder | Placeholders are NOT exempt — WCAG 1.4.3 applies | Act on this finding |

---

## Vision Model Limitations

The bot uses GPT-4o's vision capability, which has inherent constraints:

| Limitation | Mitigation (how the prompt handles it) |
|---|---|
| Cannot measure exact pixels | Bot phrases: "appears to be smaller than 44px" — never states exact measurements |
| May misidentify text color on complex backgrounds | Treat contrast findings on gradient/image backgrounds as "needs manual check" |
| Cannot distinguish interactive vs decorative without context | Designer provides context string (e.g., "This is a mobile login screen") |
| Cannot simulate screen reader output | Out of scope — use VoiceOver / NVDA for screen reader testing |

---

## Escalation Path

If a flagged issue is genuinely unclear:

1. Designer adds context: re-upload the screenshot with a message like "This button is disabled — verify contrast exemption"
2. Bot re-audits with the additional context
3. If still unclear: escalate to Frontend Lead for a code-level check

---

## Tools for Pixel-Perfect Verification

The bot's findings are a **first pass**. Always verify with:

| Tool | What it verifies |
|---|---|
| **Figma Accessibility Plugin** (Stark) | Exact contrast ratios, color blindness simulation |
| **WebAIM Contrast Checker** | Manual hex-code contrast calculation |
| **axe DevTools** (browser extension) | Live DOM accessibility audit |
| **VoiceOver / NVDA** | Screen reader behavior (out of bot scope) |
