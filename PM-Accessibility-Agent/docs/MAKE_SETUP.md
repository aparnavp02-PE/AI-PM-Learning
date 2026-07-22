# Make.com Setup Guide (No-Code Deployment)

Follow these steps to deploy AccessibilityBot without writing any code.

---

## Prerequisites

- A Make.com account (free tier works for low volume)
- A Slack workspace where you can install apps
- An OpenAI API key with GPT-4o access

---

## Step 1 — Create the Slack Channel

1. In Slack, click **+** next to Channels
2. Create channel: `#a11y-check`
3. Set description: "Upload UI screenshots here for automated WCAG accessibility auditing"
4. Invite the team: UX designers, frontend devs, PMs

---

## Step 2 — Connect Slack to Make.com

1. In Make.com, go to **Connections** → **Add a connection**
2. Choose **Slack**
3. Authenticate with your Slack workspace
4. Ensure the bot gets added to `#a11y-check` (Make will prompt you)

---

## Step 3 — Import the Blueprint

1. In Make.com, go to **Scenarios** → **Create a new scenario**
2. Click the **three-dot menu** → **Import blueprint**
3. Upload or paste the contents of [`make_blueprint/scenario.json`](../make_blueprint/scenario.json)
4. The four-module flow will appear:
   - Module 1: Slack (Watch Messages)
   - Module 2: Slack (Download File)
   - Module 3: OpenAI (GPT-4o Vision)
   - Module 4: Slack (Post Message)

---

## Step 4 — Configure Module 1 (Trigger)

- **Connection:** Select your Slack connection
- **Channel:** Select `#a11y-check`
- **Filter:** Conditions → `files[] exists` (only process messages with attachments)

---

## Step 5 — Configure Module 2 (Download Image)

- **URL:** Map `{{1.files[1].url_private}}` from the trigger
- **Token:** This is automatically passed via your Slack connection

---

## Step 6 — Configure Module 3 (GPT-4o)

- **Connection:** Add your OpenAI API key
- **Model:** `gpt-4o`
- **Temperature:** `0.1`
- **Max Tokens:** `1500`
- **System Message:** Copy from [`prompts/system_prompt.md`](../prompts/system_prompt.md)
- **User Message:** Copy from [`prompts/task_prompt.md`](../prompts/task_prompt.md)
- **Image Attachment:** Map `{{2.data}}` as base64 image_url with `"detail": "high"`

---

## Step 7 — Configure Module 4 (Post to Slack)

- **Channel:** Map `{{1.channel}}`
- **Thread Timestamp:** Map `{{1.event_ts}}` (replies in the same thread)
- **Message:** 
  ```
  *Accessibility Audit Report*

  {{3.choices[].message.content}}

  _Note: AI-assisted check. Use Stark or Figma's accessibility plugin for pixel-perfect verification._
  ```

---

## Step 8 — Enable and Test

1. Turn the scenario **ON** (toggle in top-left)
2. Set **Scheduling:** Instantly (trigger-based, not scheduled)
3. **Pilot test:** Upload a screenshot with light gray text on white to `#a11y-check`
4. The bot should reply within 30 seconds with a contrast violation report

---

## Optional: Add Zapier Code for Precise Contrast Math

For exact contrast ratio calculations (rather than AI estimation), add a **Code by Zapier** step between Module 2 and Module 3:

```javascript
// Contrast ratio calculator
// Input: foreground hex, background hex
// Output: contrast ratio

function relativeLuminance(hex) {
  const rgb = parseInt(hex.slice(1), 16);
  const r = ((rgb >> 16) & 255) / 255;
  const g = ((rgb >> 8) & 255) / 255;
  const b = (rgb & 255) / 255;
  const toLinear = c => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
}

const fg = inputData.foreground; // e.g. "#CCCCCC"
const bg = inputData.background; // e.g. "#FFFFFF"
const l1 = relativeLuminance(fg);
const l2 = relativeLuminance(bg);
const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
output = [{ ratio: ratio.toFixed(2), passes_normal: ratio >= 4.5, passes_large: ratio >= 3.0 }];
```
