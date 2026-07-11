# ArtisanFlowAI — Database Schema

## Overview

ArtisanFlowAI uses MongoDB with Mongoose ODM. Schema files live in `server/models/`. Every document includes built-in Mongoose fields automatically managed:

| Built-in Field | Type | Description |
|---|---|---|
| `_id` | ObjectId | Auto-generated primary key (alias: `id`) |
| `createdAt` | Date | Auto-set on creation (`timestamps: true`) |
| `updatedAt` | Date | Auto-updated on modification (`timestamps: true`) |
| `created_by_id` | ObjectId ref User | ID of the user who created the record (used for RLS) |

---

## Entity: User

**File:** `server/models/User.js`

```js
import mongoose from 'mongoose';

const UserSchema = new mongoose.Schema({
  email:                { type: String, required: true, unique: true, lowercase: true },
  password_hash:        { type: String },                    // null for OAuth users
  full_name:            { type: String, default: '' },
  role:                 { type: String, enum: ['artisan', 'admin'], default: 'artisan' },
  phone:                { type: String },
  preferred_language:   { type: String, default: 'en',
                          enum: ['en','hi','te','ta','kn','ml','bn','mr','gu','or','pa'] },
  region:               { type: String },                    // Indian state/region
  craft_specialization: { type: String },                    // e.g., "Pottery"
  otp_code:             { type: String },
  otp_expires_at:       { type: Date },
  reset_token:          { type: String },
  reset_token_expires:  { type: Date },
  google_id:            { type: String },
  is_verified:          { type: Boolean, default: false }
}, { timestamps: true });

export default mongoose.model('User', UserSchema);
```

**Security:**
- Only admins can list/update/delete other users
- Regular users can only read/update their own profile via `GET /api/auth/me` / `PATCH /api/auth/me`
- `password_hash` is never returned in API responses

---

## Entity: Submission

**File:** `server/models/Submission.js`

Represents an artisan's product submission — the core entity that triggers the AI pipeline.

```js
import mongoose from 'mongoose';

const SubmissionSchema = new mongoose.Schema({
  raw_image_url:          { type: String, required: true },
  original_description:   { type: String, required: true },
  translated_description: { type: String },
  detected_language:      { type: String },
  status: {
    type: String,
    enum: ['pending', 'processing', 'completed', 'failed'],
    default: 'pending'
  },
  completed_at:           { type: Date },
  created_by_id:          { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true }
}, { timestamps: true });

export default mongoose.model('Submission', SubmissionSchema);
```

**Corresponding fields:**

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `raw_image_url` | String | Yes | — | URL to uploaded product photo |
| `original_description` | String | Yes | — | Artisan's description in their native language |
| `translated_description` | String | No | — | English translation (AI Step 1) |
| `detected_language` | String | No | — | ISO language code from original_description |
| `status` | String (enum) | No | `"pending"` | `pending`, `processing`, `completed`, `failed` |
| `completed_at` | Date | No | — | Timestamp when pipeline completed |

**Relationships:**
- `created_by_id` → User (artisan who submitted)
- Has one `ProductAnalysis` (via `submission_id`)
- Has one `AmazonListing` (via `submission_id`)
- Has many `ImagePrompt` (via `submission_id`)

**Row-Level Security:**
- Artisans: all queries scoped with `{ created_by_id: req.user.id }`
- Admins: no `created_by_id` filter — full access

---

## Entity: ProductAnalysis

**File:** `server/models/ProductAnalysis.js`

AI-generated product analysis from Step 2 of the pipeline.

```js
import mongoose from 'mongoose';

const ProductAnalysisSchema = new mongoose.Schema({
  submission_id:       { type: mongoose.Schema.Types.ObjectId, ref: 'Submission', required: true },
  created_by_id:       { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  primary_material:    { type: String },
  secondary_materials: [{ type: String }],
  craft_technique:     { type: String },
  art_form_category:   { type: String },
  is_handmade:         { type: Boolean },
  state_of_origin:     { type: String },
  confidence_score:    { type: Number, min: 0, max: 1 },
  full_report:         { type: String }
}, { timestamps: true });

export default mongoose.model('ProductAnalysis', ProductAnalysisSchema);
```

**Field reference:**

| Field | Type | Notes |
|---|---|---|
| `submission_id` | ObjectId | FK → Submission |
| `primary_material` | String | e.g., "Black Stone and Iron" |
| `secondary_materials` | String[] | Additional material tags |
| `craft_technique` | String | e.g., "Longpi Pottery", "Dhokra Casting" |
| `art_form_category` | String | e.g., "Folk Art", "Textile", "Metalwork" |
| `is_handmade` | Boolean | Handmade vs machine-made classification |
| `state_of_origin` | String | e.g., "Manipur" |
| `confidence_score` | Number | 0.0–1.0 confidence in analysis |
| `full_report` | String | Complete AI-generated analysis in markdown |

---

## Entity: AmazonListing

**File:** `server/models/AmazonListing.js`

AI-generated Amazon marketplace listing from Step 3 of the pipeline.

```js
import mongoose from 'mongoose';

const AmazonListingSchema = new mongoose.Schema({
  submission_id:       { type: mongoose.Schema.Types.ObjectId, ref: 'Submission', required: true },
  created_by_id:       { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  product_title:       { type: String, maxlength: 200 },
  bullet_point_1:      { type: String },
  bullet_point_2:      { type: String },
  bullet_point_3:      { type: String },
  bullet_point_4:      { type: String },
  bullet_point_5:      { type: String },
  product_description: { type: String },
  backend_keywords:    { type: String },
  item_dimensions:     { type: String },
  item_weight:         { type: String },
  material_type:       { type: String },
  color:               { type: String },
  product_category:    { type: String }
}, { timestamps: true });

export default mongoose.model('AmazonListing', AmazonListingSchema);
```

**Field reference:**

| Field | Type | Notes |
|---|---|---|
| `submission_id` | ObjectId | FK → Submission |
| `product_title` | String | Max 200 chars, Amazon-compliant, SEO-optimized |
| `bullet_point_1`–`5` | String | Benefit-driven highlights |
| `product_description` | String | Full description (200–400 words) |
| `backend_keywords` | String | Comma-separated search terms (~250 keywords) |
| `item_dimensions` | String | e.g., "10 x 8 x 5 inches" |
| `item_weight` | String | e.g., "1.2 kg" |
| `material_type` | String | e.g., "Black Stone, Iron" |
| `color` | String | Primary product color |
| `product_category` | String | e.g., "Home & Kitchen > Décor" |

---

## Entity: ImagePrompt

**File:** `server/models/ImagePrompt.js`

AI-generated lifestyle image prompts from Step 4 of the pipeline. 7 records per submission.

```js
import mongoose from 'mongoose';

const ImagePromptSchema = new mongoose.Schema({
  submission_id:     { type: mongoose.Schema.Types.ObjectId, ref: 'Submission', required: true },
  created_by_id:     { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  prompt_index:      { type: Number },
  prompt_type: {
    type: String,
    enum: ['hero_shot', 'lifestyle', 'detail_closeup', 'gifting']
  },
  scene_description: { type: String, required: true },
  target_platform:   { type: String }
}, { timestamps: true });

export default mongoose.model('ImagePrompt', ImagePromptSchema);
```

**Field reference:**

| Field | Type | Notes |
|---|---|---|
| `submission_id` | ObjectId | FK → Submission |
| `prompt_index` | Number | 1–7 ordering |
| `prompt_type` | String (enum) | `hero_shot`, `lifestyle`, `detail_closeup`, `gifting` |
| `scene_description` | String | Full image generation prompt (80–120 words) |
| `target_platform` | String | e.g., "Amazon Main Image", "Instagram", "Lifestyle Scene" |

**Distribution per submission:**
- 2 × `hero_shot` (Amazon Main Image)
- 3 × `lifestyle` (Lifestyle Scene)
- 1 × `detail_closeup` (Amazon Main Image / Detail)
- 1 × `gifting` (Gifting context)

---

## Entity Relationship Diagram

```
┌──────────┐       ┌──────────────┐       ┌──────────────────┐
│   User   │──1:N──│  Submission  │──1:1──│ ProductAnalysis  │
│          │       │              │       └──────────────────┘
│ • _id    │       │ • _id        │       ┌──────────────────┐
│ • email  │       │ • user_id    │──1:1──│ AmazonListing    │
│ • role   │       │ • image_url  │       └──────────────────┘
│ • region │       │ • description│       ┌──────────────────┐
│ • craft  │       │ • status     │──1:N──│ ImagePrompt      │
└──────────┘       └──────────────┘       │ (7 per submission)│
                                          └──────────────────┘
```

---

## Row-Level Security (RLS) Summary

| Entity | Artisan | Admin |
|---|---|---|
| User | Read/update own profile only | Read all users, update role |
| Submission | CRUD own submissions only | Read all submissions |
| ProductAnalysis | Read own (via submission ownership) | Read all |
| AmazonListing | Read own (via submission ownership) | Read all |
| ImagePrompt | Read own (via submission ownership) | Read all |

---

## Query Examples

### Get all submissions for current artisan
```js
const subs = await Submission.find({ created_by_id: req.user.id })
  .sort({ createdAt: -1 })
  .limit(10);
```

### Get results for a submission
```js
const [analysis, listing, prompts] = await Promise.all([
  ProductAnalysis.findOne({ submission_id: id }),
  AmazonListing.findOne({ submission_id: id }),
  ImagePrompt.find({ submission_id: id }).sort({ prompt_index: 1 })
]);
```

### Admin: get all submissions
```js
const allSubs = await Submission.find()
  .populate('created_by_id', 'full_name email region craft_specialization')
  .sort({ createdAt: -1 })
  .limit(100);
```

### Admin: stats query
```js
const subs = await Submission.find().select('status createdAt');
const today = new Date(); today.setHours(0, 0, 0, 0);
const stats = {
  total: subs.length,
  completed: subs.filter(s => s.status === 'completed').length,
  completedToday: subs.filter(s => s.status === 'completed' && s.createdAt >= today).length,
  pending: subs.filter(s => ['pending','processing'].includes(s.status)).length,
  failed: subs.filter(s => s.status === 'failed').length
};
```

### Idempotency check (pipeline retry)
```js
const existingAnalysis = await ProductAnalysis.findOne({ submission_id: id });
if (existingAnalysis) {
  // Skip Step 2 — analysis already exists
}
```
