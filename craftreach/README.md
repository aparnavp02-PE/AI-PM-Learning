# craftReach — Claude Code Agent & Command

craftReach turns a single product photo from an artisan or small craft
seller into a **ready-to-copy Amazon India listing** and **5 lifestyle image
prompts** for Google Gemini Imagen 2 — in one pass, with zero clarifying
questions.

## What's inside

```
craftreach/
├── .claude/
│   ├── commands/
│   │   └── craftreach.md      # /craftreach slash command
│   └── agents/
│       └── craft-reach.md     # craft-reach subagent (does the actual work)
└── README.md
```

- **`.claude/agents/craft-reach.md`** — a subagent definition. It contains
  the full instructions for the three-step workflow: product analysis,
  Amazon India listing generation, and lifestyle prompt generation. Claude
  Code can invoke this agent automatically whenever a product image is
  provided with selling/listing intent, or you can call it explicitly.

- **`.claude/commands/craftreach.md`** — a slash command (`/craftreach`) that
  wraps the agent so you can trigger the workflow directly from the CLI/chat
  with an image path.

## Installation

1. Copy the `.claude` folder into the root of your project (or into your
   home directory at `~/.claude` for a global install):

   ```bash
   cp -r craftreach/.claude /path/to/your/project/
   ```

2. Restart Claude Code (or start a new session) in that project so it picks
   up the new command and agent.

3. Confirm they're loaded:
   - Run `/agents` to see `craft-reach` listed.
   - Run `/craftreach` (it should show up in your slash command list).

## Usage

### Option A — Slash command
```
/craftreach path/to/product-photo.jpg
```
If you've already attached/uploaded an image in the conversation, you can
omit the path:
```
/craftreach
```

### Option B — Let Claude auto-invoke the agent
Just upload a product photo and ask something like:
> "Create an Amazon listing for this."
> "Generate lifestyle photos and a listing for this handicraft."

Claude Code will recognize the intent (per the agent's `description`) and
route the request to `craft-reach` automatically.

## What you get back

1. **📦 PRODUCT ANALYSIS** — bullet list covering product type, materials,
   colors, dimensions, craft technique, region/origin, use case, target
   audience, USPs, and packaging.

2. **📝 AMAZON INDIA LISTING** — category path, SEO-optimized title (with
   character count), 5 feature bullets (with character counts), a
   plain-text product description (with character count), backend search
   keywords (with byte count), and a suggested price range with rationale.
   Follows Amazon India's formatting rules (no promotional language, no HTML,
   no contact info/URLs/pricing in the description, Title Case bullet
   labels, sentence case description).

3. **🎨 5 LIFESTYLE IMAGE PROMPTS** — written for Google Gemini Imagen 2
   image-to-image generation using the original product photo as reference.
   Alternates realistic photography and editorial/aesthetic styles across
   home, gifting, outdoor, flat-lay, and human-interaction scenes — usable
   for both Amazon listing images and Instagram/Pinterest.

## Notes & customization

- The agent **never asks clarifying questions** — it always makes its best
  inference from the image and produces a complete output. If you want a
  more conversational/confirm-before-generating flow, remove the
  "zero back-and-forth" instructions near the top of
  `.claude/agents/craft-reach.md`.
- If you sell in a specific category repeatedly (e.g., only jewelry, or only
  textiles), you can trim the "category-specific rules" list in the agent
  file to keep the prompt shorter and more focused.
- `model: sonnet` is set in the agent's frontmatter; change it if you want a
  different model tier for this workflow.
- Backend keyword byte-count is calculated in UTF-8 bytes, per Amazon's
  actual limit — double check this if you add Hindi/regional-script terms,
  since those take more bytes per character than plain ASCII.
