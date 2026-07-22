import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM_PROMPT = """You are AccessibilityBot, a Certified CPACC Accessibility Auditor.
You audit UI designs for compliance with WCAG 2.1 Level AA standards.

Core Directives:
1. Be strict. If a color looks too light, flag it.
2. Explain WHY it failed (e.g., "Low contrast makes this hard to read for visually impaired users").
3. Provide specific hex code suggestions that would pass.
4. For every failure, cite the specific WCAG Success Criterion (e.g., "WCAG 1.4.3 Contrast Minimum").

Scope — You WILL check:
- Color contrast ratios (text vs background)
- Missing labels on icons and interactive elements
- Button/tap target sizes (minimum 44x44px)
- Text size (minimum 12px)
- Input field visible labels

Scope — You will NOT:
- Fix designs or open external tools
- Simulate screen reader navigation
- Issue a legal compliance certificate
- State exact pixel measurements you cannot verify precisely"""

TASK_PROMPT = """Audit this UI screenshot for the following WCAG 2.1 Level AA issues:

1. **Color Contrast** (WCAG 1.4.3 Contrast Minimum)
   - Normal text (<18pt / <14pt bold): ratio must be ≥ 4.5:1
   - Large text (≥18pt / ≥14pt bold): ratio must be ≥ 3:1
   - Decorative elements and disabled controls: exempt

2. **Touch Targets** (WCAG 2.5.5 Target Size)
   - Buttons and interactive elements must appear ≥ 44×44px
   - Phrase findings as "appears to be smaller than 44px" — do not claim exact measurements

3. **Missing Labels** (WCAG 1.1.1 Non-text Content, WCAG 4.1.2 Name, Role, Value)
   - Icons without visible text (e.g., magnifying glass, hamburger menu, share icon)
   - Interactive elements with no discernible label

4. **Text Size** (WCAG 1.4.4 Resize Text)
   - Text that appears smaller than 12px

5. **Input Labels** (WCAG 1.3.1 Info and Relationships)
   - Input fields, dropdowns, or checkboxes without a visible label

For every failure:
- Describe the issue clearly
- Cite the WCAG Success Criterion
- Suggest a specific fix with hex codes where applicable (e.g., "Change #CCCCCC to #767676 to achieve 4.5:1 ratio")

Output: A bulleted list of violations grouped by issue type.
If no violations are found, reply exactly: "✅ Passed WCAG AA Check — no violations detected."
"""

REFINEMENT_PROMPT = (
    "For every failure found, cite the specific WCAG Success Criterion "
    "(e.g., '1.4.3 Contrast Minimum'). Do not report a failure without a criterion."
)


def audit_image(image_data: bytes, context: str = "") -> str:
    image_b64 = base64.standard_b64encode(image_data).decode("utf-8")

    context_note = f"\n\nDesigner context: {context}" if context.strip() else ""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": TASK_PROMPT + context_note + "\n\n" + REFINEMENT_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}",
                            "detail": "high",
                        },
                    },
                ],
            },
        ],
        max_tokens=1500,
        temperature=0.1,
    )

    return response.choices[0].message.content
