# ArtisanFlowAI — Backend Documentation

## Architecture

ArtisanFlowAI uses a Node.js/Express REST API backed by MongoDB. All AI calls go directly to the Anthropic SDK. File uploads use Multer + AWS S3 (or compatible storage).

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (React)                   │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │   Pages     │  │  Components  │  │   Lib      │  │
│  │  (11 pages) │  │  (8 files)   │  │(aiPipeline)│  │
│  └──────┬──────┘  └──────┬───────┘  └─────┬──────┘  │
│         └────────────────┴─────────────────┘         │
│                    apiClient (axios)                  │
└────────────────────────┬────────────────────────────┘
                         │ REST / HTTP
              ┌──────────▼──────────┐
              │   Express Server    │
              │  ┌───────────────┐  │
              │  │  Auth (JWT)   │  │
              │  ├───────────────┤  │
              │  │  Routes/API   │  │
              │  ├───────────────┤  │
              │  │  AI Pipeline  │  │
              │  │  (Anthropic)  │  │
              │  ├───────────────┤  │
              │  │  File Upload  │  │
              │  │   (S3/Multer) │  │
              │  └───────────────┘  │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │      MongoDB        │
              │   (Mongoose ODM)    │
              └─────────────────────┘
```

---

## Authentication

| Method | Route | Notes |
|---|---|---|
| Email + Password Login | `POST /api/auth/login` | Returns `{ access_token, user }` |
| Google OAuth | `GET /api/auth/google` | Redirects to Google consent |
| Register | `POST /api/auth/register` | Creates unverified user — triggers OTP email |
| OTP Verification | `POST /api/auth/verify-otp` | Returns `{ access_token }` on success |
| Resend OTP | `POST /api/auth/resend-otp` | Sends new code to email |
| Password Reset Request | `POST /api/auth/forgot-password` | Generic success always returned |
| Password Reset | `POST /api/auth/reset-password` | Accepts `resetToken` + `newPassword` |
| Get Current User | `GET /api/auth/me` | Requires `Authorization: Bearer <token>` |
| Update Current User | `PATCH /api/auth/me` | Updates phone, region, craft, language |
| Logout | `POST /api/auth/logout` | Clears server-side session if needed |

### JWT Middleware

```js
// src/middleware/auth.js
import jwt from 'jsonwebtoken';

export function requireAuth(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Unauthorized' });
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
}

export function requireAdmin(req, res, next) {
  if (req.user?.role !== 'admin') return res.status(403).json({ error: 'Forbidden' });
  next();
}
```

### Role-Based Access Control
- **Artisan** (default): Can only access their own submissions and related records
- **Admin**: Can access all submissions across all artisans, access `/admin` dashboard
- Ownership scoping is applied in every query: `{ created_by_id: req.user.id }`

---

## AI Pipeline (`src/lib/aiPipeline.js`)

The core logic is a 4-step AI pipeline triggered when an artisan submits a product photo + description.

### Pipeline Entry Point

```js
import { runPipeline } from '@/lib/aiPipeline';

const result = await runPipeline(submission, onProgress);
// onProgress: ({ step: 1-4, status: 'running'|'done' }) => void
// Returns: { success: boolean, error?: string }
```

### Step 1 — Language Detection & Translation

```js
import Anthropic from '@anthropic-ai/sdk';
const client = new Anthropic();

const response = await client.messages.create({
  model: 'claude-sonnet-4-6',
  max_tokens: 1024,
  messages: [{
    role: 'user',
    content: `Detect the language of this text and translate it to English. 
              Return JSON with detected_language (ISO code) and english_translation.
              Text: "${submission.original_description}"`
  }]
});

const { detected_language, english_translation } = JSON.parse(response.content[0].text);
```
- Updates `Submission` with `detected_language` and `translated_description`

### Step 2 — Product Vision Analysis

```js
const imageResponse = await fetch(submission.raw_image_url);
const imageData = await imageResponse.arrayBuffer();
const base64Image = Buffer.from(imageData).toString('base64');
const mediaType = 'image/jpeg';

const response = await client.messages.create({
  model: 'claude-sonnet-4-6',
  max_tokens: 2048,
  messages: [{
    role: 'user',
    content: [
      {
        type: 'image',
        source: { type: 'base64', media_type: mediaType, data: base64Image }
      },
      {
        type: 'text',
        text: `Analyze this Indian artisan product. Return JSON with fields:
               primary_material, secondary_materials (array), craft_technique,
               art_form_category, is_handmade (bool), state_of_origin,
               confidence_score (0-1), full_report (markdown string).
               Context: ${english_translation}`
      }
    ]
  }]
});
```
- Creates `ProductAnalysis` record linked to submission

### Step 3 — Amazon Listing Generation

```js
const response = await client.messages.create({
  model: 'claude-sonnet-4-6',
  max_tokens: 2048,
  messages: [{
    role: 'user',
    content: `Create a complete Amazon listing. Return JSON with:
              product_title (max 200 chars), bullet_point_1 through bullet_point_5,
              product_description (200-400 words), backend_keywords (comma-separated, ~250 terms),
              item_dimensions, item_weight, material_type, color, product_category.
              Product data: ${JSON.stringify(analysisData)}`
  }]
});
```
- Creates `AmazonListing` record linked to submission

### Step 4 — Lifestyle Image Prompt Generation

```js
const response = await client.messages.create({
  model: 'claude-sonnet-4-6',
  max_tokens: 2048,
  messages: [{
    role: 'user',
    content: `Generate 7 detailed image generation prompts for this product.
              Return JSON: { prompts: [{ prompt_index, prompt_type, scene_description, target_platform }] }
              Types: 2x hero_shot, 3x lifestyle, 1x detail_closeup, 1x gifting.
              Product: ${productTitle}, Craft: ${craftTechnique}, Region: ${stateOfOrigin}`
  }]
});
```
- Bulk inserts 7 `ImagePrompt` records linked to submission
- Validates: if fewer than 5 prompts returned, pipeline fails

### Step 5 — Status Update

```js
// Success:
await Submission.findByIdAndUpdate(id, { status: 'completed', completed_at: new Date() });

// Failure (any step):
await Submission.findByIdAndUpdate(id, { status: 'failed' });
```

### Idempotency
The pipeline checks for existing records at each step. If a user retries a failed submission, completed steps are skipped:
- Step 1: Skipped if `translated_description` already set on Submission
- Step 2: Skipped if `ProductAnalysis` record exists for this `submission_id`
- Step 3: Skipped if `AmazonListing` record exists for this `submission_id`
- Step 4: Skipped if `ImagePrompt` records exist for this `submission_id`

### Helper: `formatEntireListing(listing)`
Returns a formatted text string of the complete Amazon listing for the "Copy Entire Listing" button.

---

## File Upload

```js
// server/routes/upload.js
import multer from 'multer';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { v4 as uuidv4 } from 'uuid';

const s3 = new S3Client({ region: process.env.AWS_REGION });
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 10 * 1024 * 1024 } });

router.post('/upload', requireAuth, upload.single('file'), async (req, res) => {
  const key = `uploads/${uuidv4()}-${req.file.originalname}`;
  await s3.send(new PutObjectCommand({
    Bucket: process.env.S3_BUCKET,
    Key: key,
    Body: req.file.buffer,
    ContentType: req.file.mimetype,
    ACL: 'public-read'
  }));
  const file_url = `https://${process.env.S3_BUCKET}.s3.${process.env.AWS_REGION}.amazonaws.com/${key}`;
  res.json({ file_url });
});
```

### Validation
- Accepted types: JPEG, PNG, WEBP
- Max size: 10MB
- Validated server-side by Multer before upload

---

## Realtime Status Updates

Use Server-Sent Events (SSE) to push pipeline progress to the Processing page:

```js
// server/routes/submissions.js
router.get('/:id/progress', requireAuth, (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  const interval = setInterval(async () => {
    const sub = await Submission.findById(req.params.id);
    res.write(`data: ${JSON.stringify({ status: sub.status })}\n\n`);
    if (['completed', 'failed'].includes(sub.status)) {
      clearInterval(interval);
      res.end();
    }
  }, 2000);

  req.on('close', () => clearInterval(interval));
});
```

---

## Error Handling

- Pipeline errors set submission status to `failed` and return `{ success: false, error }`
- The status update to `failed` is wrapped in `.catch(() => {})` to prevent double-failure
- Processing page displays the error with a "Retry Pipeline" button
- Retry clears `translated_description` on the Submission and re-runs the full pipeline

---

## Business Rules Enforced

1. **Image required**: Submission creation requires `raw_image_url`
2. **No reprocessing**: Once completed, a submission cannot be reprocessed — artisan must create a new submission
3. **Artisan isolation**: All queries are scoped to `{ created_by_id: req.user.id }` for artisans
4. **Admin access**: Admins can list all submissions across all users (no `created_by_id` filter)
5. **Title length**: AI prompt instructs ≤200 characters; frontend displays as-is
6. **Complete prompt set**: All 7 image prompts must be generated together; <5 triggers failure
7. **Ownership**: Generated content is owned by the artisan who submitted (`created_by_id`)
