# Task Prompt — AccessibilityBot

> Paste this into the "User Message" field in Make.com's OpenAI module.
> The image is attached separately as a base64-encoded image_url.

---

Audit this UI screenshot for the following WCAG 2.1 Level AA issues:

**1. Color Contrast** (WCAG 1.4.3 Contrast Minimum)
- Normal text (<18pt / <14pt bold): ratio must be ≥ 4.5:1
- Large text (≥18pt / ≥14pt bold): ratio must be ≥ 3:1
- Decorative elements and disabled controls: **exempt**

**2. Touch Targets** (WCAG 2.5.5 Target Size)
- Buttons and interactive elements must appear ≥ 44×44px
- Phrase findings as "appears to be smaller than 44px" — do not claim exact measurements

**3. Missing Labels** (WCAG 1.1.1 Non-text Content, WCAG 4.1.2 Name, Role, Value)
- Icons without visible text (e.g., magnifying glass, hamburger menu, share icon)
- Interactive elements with no discernible label

**4. Text Size** (WCAG 1.4.4 Resize Text)
- Text that appears smaller than 12px

**5. Input Labels** (WCAG 1.3.1 Info and Relationships)
- Input fields, dropdowns, or checkboxes without a visible label

**For every failure:**
- Describe the issue clearly
- Cite the WCAG Success Criterion
- Suggest a specific fix with hex codes where applicable

**Output:** A bulleted list of violations grouped by issue type.
If no violations found, reply exactly: "✅ Passed WCAG AA Check — no violations detected."
