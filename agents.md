# ArtisanFlowAI — AI Agents

Two purpose-built agents extend the core 4-step pipeline. Both use the Anthropic SDK with `claude-sonnet-4-6`.

---

## Agent 1: Artisan Assistant

### What it does

A multilingual conversational agent that sits alongside the Results page and acts as a personal guide for the artisan. It explains AI-generated outputs in plain language (in the artisan's native language), answers follow-up questions, and offers actionable coaching on photography, pricing, and shipping — things the pipeline doesn't cover.

### Why this agent

The core pipeline outputs English text. Most artisans using this app are not English-fluent. The assistant bridges that gap: it reads the artisan's own submission data and answers questions like _"Why did the AI say my product is from Manipur?"_ or _"What price should I set?"_ in Hindi, Tamil, or any of the 11 supported languages — without the artisan needing to translate anything themselves.

### Behaviour

- Responds in the same language the artisan used in their original description (`detected_language`)
- Has full context of the submission: the product photo URL, original description, craft analysis, and generated listing
- Stays in scope: only answers questions related to the artisan's product, listing, image prompts, and selling on Amazon
- Does not regenerate the listing — it explains and coaches

### System Prompt

```
You are a warm, patient assistant for Indian artisans selling on Amazon.
You speak in the artisan's native language: {{detected_language}}.
If the language is English, respond in English.

You have full context of this artisan's submission:
- Product photo: {{raw_image_url}}
- Their description (original): {{original_description}}
- Craft identified: {{craft_technique}}, {{state_of_origin}}
- Amazon listing title: {{product_title}}
- Analysis report: {{full_report}}

Your role:
1. Explain any part of the AI-generated results in simple terms.
2. Answer questions about Amazon listings, pricing, photography, and packaging.
3. Give encouragement and practical next steps.

Rules:
- Always respond in {{detected_language}} unless the artisan switches language.
- Never make up product details not in the submission data above.
- If asked to regenerate the listing, politely say that is done separately via the main pipeline.
- Keep responses concise — artisans are often on mobile with slow connections.
```

### API Call

```js
// server/agents/artisanAssistant.js
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

export async function runArtisanAssistant({ submission, analysis, listing, conversationHistory, userMessage }) {
  const systemPrompt = `
You are a warm, patient assistant for Indian artisans selling on Amazon.
You speak in the artisan's native language: ${submission.detected_language || 'en'}.

Submission context:
- Product photo: ${submission.raw_image_url}
- Original description: ${submission.original_description}
- Craft: ${analysis.craft_technique}, ${analysis.state_of_origin}
- Amazon title: ${listing.product_title}
- Analysis report: ${analysis.full_report}

Rules:
- Always respond in ${submission.detected_language || 'English'}.
- Keep responses concise (artisans are often on mobile).
- Do not regenerate the listing — explain and coach only.
- Never invent product details not present in the context above.
`.trim();

  const response = await client.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 1024,
    system: systemPrompt,
    messages: [
      ...conversationHistory,   // [{ role: 'user'|'assistant', content: '...' }]
      { role: 'user', content: userMessage }
    ]
  });

  return response.content[0].text;
}
```

### REST Endpoint

```
POST /api/submissions/:id/assistant
Authorization: Bearer <token>
```
```json
{
  "message": "इस listing में price कितना रखूं?",
  "history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```
Response `200`:
```json
{ "reply": "आपके Longpi pottery bowl के लिए ₹1,200–₹1,800 सही रहेगा क्योंकि..." }
```

### Frontend Integration

Add a collapsible chat panel to `src/pages/Results.jsx`:

```jsx
// src/components/ArtisanChat.jsx
import { useState } from 'react';
import apiClient from '@/api/apiClient';

export function ArtisanChat({ submissionId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!input.trim()) return;
    const history = messages.map(m => ({ role: m.role, content: m.content }));
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setLoading(true);
    const { reply } = await apiClient.post(`/api/submissions/${submissionId}/assistant`, {
      message: input,
      history
    });
    setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
    setLoading(false);
  };

  return (
    <div className="border rounded-xl p-4 flex flex-col gap-3">
      <h3 className="font-semibold text-sm">Ask your Artisan Assistant</h3>
      <div className="flex flex-col gap-2 max-h-64 overflow-y-auto text-sm">
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'text-right' : 'text-left text-muted-foreground'}>
            {m.content}
          </div>
        ))}
        {loading && <div className="text-muted-foreground italic">Thinking...</div>}
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded px-2 py-1 text-sm"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Ask anything about your listing..."
        />
        <button onClick={send} className="px-3 py-1 bg-primary text-white rounded text-sm">Send</button>
      </div>
    </div>
  );
}
```

---

## Agent 2: Listing Optimizer

### What it does

A post-generation auditor that reviews the AI-generated Amazon listing and returns a structured quality report with a score, flagged issues, and rewritten versions of any weak sections. It can optionally auto-apply the suggested improvements and save them back to the `AmazonListing` record.

### Why this agent

The pipeline's Step 3 generates listings fast but not always perfectly. Titles can be too long, bullet points can be vague, and keyword density can be low. The Listing Optimizer runs a separate, focused review pass — prompted specifically to think like an Amazon SEO expert — and produces concrete, actionable fixes. This is triggered manually by the artisan (or admin) from the Results page, not on every submission.

### Behaviour

- Audits against Amazon's current listing guidelines: title ≤200 chars, bullets start with a capital, description avoids prohibited claims
- Scores each section: Title, Bullets, Description, Keywords (0–10)
- Returns rewritten versions only for sections scoring below 7
- Explains every change in plain English
- Does not change factual product details — only improves language, structure, and SEO

### System Prompt

```
You are an Amazon listing SEO expert specialising in Indian artisan and handicraft products.

Review the listing below and return a JSON object with this exact structure:
{
  "overall_score": <0-10>,
  "sections": {
    "title":       { "score": <0-10>, "issues": [...], "rewrite": "<string or null>" },
    "bullets":     { "score": <0-10>, "issues": [...], "rewrite": ["bullet1", ..., "bullet5"] or null },
    "description": { "score": <0-10>, "issues": [...], "rewrite": "<string or null>" },
    "keywords":    { "score": <0-10>, "issues": [...], "rewrite": "<string or null>" }
  },
  "summary": "<2-3 sentence plain-English summary of the main improvements>"
}

Rules:
- Only rewrite a section if its score is below 7. Otherwise set rewrite to null.
- Never invent product attributes not present in the input data.
- Title must be ≤200 characters.
- Each bullet must start with a capital letter and lead with a customer benefit.
- Flag any prohibited Amazon claims (e.g., "best", "guaranteed", "#1").
- Optimise for Indian handicraft search terms (include region, craft name, material, and use case).
```

### API Call

```js
// server/agents/listingOptimizer.js
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

const OPTIMIZER_SCHEMA = {
  type: 'object',
  required: ['overall_score', 'sections', 'summary'],
  properties: {
    overall_score: { type: 'number' },
    sections: {
      type: 'object',
      properties: {
        title:       { type: 'object', properties: { score: { type: 'number' }, issues: { type: 'array', items: { type: 'string' } }, rewrite: { type: ['string', 'null'] } } },
        bullets:     { type: 'object', properties: { score: { type: 'number' }, issues: { type: 'array', items: { type: 'string' } }, rewrite: { type: ['array', 'null'], items: { type: 'string' } } } },
        description: { type: 'object', properties: { score: { type: 'number' }, issues: { type: 'array', items: { type: 'string' } }, rewrite: { type: ['string', 'null'] } } },
        keywords:    { type: 'object', properties: { score: { type: 'number' }, issues: { type: 'array', items: { type: 'string' } }, rewrite: { type: ['string', 'null'] } } }
      }
    },
    summary: { type: 'string' }
  }
};

export async function runListingOptimizer({ listing, analysis }) {
  const listingText = `
Product Title: ${listing.product_title}

Bullet 1: ${listing.bullet_point_1}
Bullet 2: ${listing.bullet_point_2}
Bullet 3: ${listing.bullet_point_3}
Bullet 4: ${listing.bullet_point_4}
Bullet 5: ${listing.bullet_point_5}

Description:
${listing.product_description}

Backend Keywords:
${listing.backend_keywords}

Product context:
- Craft: ${analysis.craft_technique}
- Material: ${analysis.primary_material}
- Region: ${analysis.state_of_origin}
- Category: ${listing.product_category}
`.trim();

  const response = await client.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 2048,
    system: `You are an Amazon listing SEO expert specialising in Indian artisan products.
Review the listing and return a JSON object matching this schema:
${JSON.stringify(OPTIMIZER_SCHEMA, null, 2)}

Rules:
- Only rewrite a section if its score < 7. Otherwise rewrite = null.
- Never invent product attributes not in the input.
- Title must be ≤200 characters.
- Bullets must lead with a customer benefit.
- Flag prohibited Amazon claims ("best", "guaranteed", "#1").`,
    messages: [{ role: 'user', content: listingText }]
  });

  return JSON.parse(response.content[0].text);
}
```

### REST Endpoint

```
POST /api/submissions/:id/optimize
Authorization: Bearer <token>
```

Optional body:
```json
{ "apply": true }
```
If `apply: true`, approved rewrites are written back to the `AmazonListing` record automatically.

Response `200`:
```json
{
  "overall_score": 6.5,
  "sections": {
    "title": {
      "score": 5,
      "issues": ["Exceeds 200 characters", "Missing primary material in title"],
      "rewrite": "Handcrafted Longpi Pottery Bowl | Black Stone & Iron | Manipur Folk Art | Authentic Indian Handicraft"
    },
    "bullets": {
      "score": 8,
      "issues": [],
      "rewrite": null
    },
    "description": {
      "score": 6,
      "issues": ["Uses prohibited claim 'best quality'", "Missing care instructions"],
      "rewrite": "Crafted by master potters in the hills of Manipur..."
    },
    "keywords": {
      "score": 7,
      "issues": [],
      "rewrite": null
    }
  },
  "summary": "The title is too long and the description contains a prohibited claim. Rewriting both will bring the listing to a strong 8.5/10 SEO score."
}
```

### Frontend Integration

Add an "Optimize Listing" button to the Amazon Listing tab in `src/pages/Results.jsx`:

```jsx
// Inside Results.jsx — Amazon Listing tab
import { useState } from 'react';
import apiClient from '@/api/apiClient';

function OptimizeButton({ submissionId, onApplied }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const optimize = async () => {
    setLoading(true);
    const result = await apiClient.post(`/api/submissions/${submissionId}/optimize`);
    setReport(result);
    setLoading(false);
  };

  const apply = async () => {
    await apiClient.post(`/api/submissions/${submissionId}/optimize`, { apply: true });
    onApplied(); // refetch listing data
    setReport(null);
  };

  return (
    <div className="flex flex-col gap-3">
      <button onClick={optimize} disabled={loading} className="px-4 py-2 border rounded text-sm">
        {loading ? 'Analysing...' : 'Optimize Listing'}
      </button>
      {report && (
        <div className="border rounded-xl p-4 text-sm flex flex-col gap-2">
          <div className="font-semibold">Score: {report.overall_score}/10</div>
          <p className="text-muted-foreground">{report.summary}</p>
          {Object.entries(report.sections).map(([section, data]) =>
            data.rewrite ? (
              <div key={section} className="bg-muted rounded p-3">
                <div className="font-medium capitalize">{section} — {data.score}/10</div>
                <ul className="list-disc list-inside text-xs mt-1 mb-2">
                  {data.issues.map((issue, i) => <li key={i}>{issue}</li>)}
                </ul>
                <div className="text-xs italic">Suggested: {Array.isArray(data.rewrite) ? data.rewrite.join(' | ') : data.rewrite}</div>
              </div>
            ) : null
          )}
          <button onClick={apply} className="px-4 py-2 bg-primary text-white rounded text-sm self-start">
            Apply All Improvements
          </button>
        </div>
      )}
    </div>
  );
}
```

---

## Agent Comparison

| | Artisan Assistant | Listing Optimizer |
|---|---|---|
| **Trigger** | Manual (artisan asks a question) | Manual (button click on Results page) |
| **Input** | Free-form chat message + submission context | Full Amazon listing + product analysis |
| **Output** | Conversational reply in native language | Structured JSON audit report + rewrites |
| **Writes to DB** | No | Optional (`apply: true`) |
| **Primary user** | Artisan | Artisan or Admin |
| **Model** | claude-sonnet-4-6 | claude-sonnet-4-6 |
| **Max tokens** | 1024 | 2048 |
| **Multi-turn** | Yes (conversation history) | No (single-shot audit) |

---

## Adding a New Agent

1. Create `server/agents/<agent-name>.js` — export an async function that calls the Anthropic SDK
2. Add a route in `server/routes/submissions.js` or a new route file
3. Add the frontend trigger (button, chat panel, etc.) to the relevant page
4. Document it in this file

All agents share the same Anthropic client instance — import from `server/lib/anthropicClient.js`:

```js
// server/lib/anthropicClient.js
import Anthropic from '@anthropic-ai/sdk';
export const anthropic = new Anthropic(); // reads ANTHROPIC_API_KEY from env
```
