# Decision Rules (IF / THEN Logic)

Reference for how AccessibilityBot applies WCAG 2.1 thresholds. These rules are baked into the task prompt.

---

## Color Contrast Rules

| Condition (IF) | Action (THEN) |
|---|---|
| Text is "Large Scale" (≥18pt, or ≥14pt bold) | Contrast threshold = **3:1** |
| Text is "Normal Scale" (<18pt, <14pt bold) | Contrast threshold = **4.5:1** |
| Element is "Decorative" (background pattern, divider, illustration) | **Ignore contrast rules** |
| Control is "Disabled" (visually grayed out, not interactive) | **Ignore contrast rules** |
| Text is on a gradient background | Flag if **either** lightest or darkest region fails |

---

## Touch Target Rules

| Condition (IF) | Action (THEN) |
|---|---|
| Button/icon appears < 44px | Flag: "Appears to be smaller than 44×44px (WCAG 2.5.5)" |
| Button has padding that expands tap area | Note: "Visual size is small but tap area may be adequate — verify in code" |
| Element is decorative (not interactive) | Ignore tap target rule |

---

## Label / Icon Rules

| Condition (IF) | Action (THEN) |
|---|---|
| Icon has no visible text label | Flag: missing label (WCAG 1.1.1) |
| Icon has a tooltip shown on hover | Note: "Tooltip present but not visible on mobile — add persistent label" |
| Input field has only placeholder text | Flag: missing label (WCAG 1.3.1) — placeholder disappears on focus |
| Input field has a visible label above/beside it | Pass |

---

## Text Size Rules

| Condition (IF) | Action (THEN) |
|---|---|
| Text appears < 12px | Flag: text too small (WCAG 1.4.4) |
| Text appears ≥ 12px | Pass |
| Text is purely decorative (background watermark) | Ignore size rules |

---

## Exemptions Summary

The bot MUST NOT flag these:
- Disabled UI controls (contrast exempt)
- Purely decorative imagery, background patterns
- Logo text (WCAG explicitly exempts logotypes)
- Captions embedded in media (different standard)
