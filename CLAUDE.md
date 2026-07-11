# ArtisanFlowAI — CLAUDE.md

## Project Overview

ArtisanFlowAI is a web app that helps Indian artisans sell their handcrafted products on Amazon. An artisan uploads a product photo and a description in their native language; the app runs a 4-step AI pipeline (translation → vision analysis → Amazon listing → image prompts) and delivers a complete, ready-to-use listing package.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18.2 + Vite, React Router DOM 6.26 |
| Language | JavaScript (ES2020+) — no TypeScript |
| Styling | Tailwind CSS + shadcn/ui (Radix UI) |
| State | @tanstack/react-query 5.84 |
| Forms | react-hook-form 7.54 |
| Icons | lucide-react 0.475 |
| Markdown | react-markdown 9.0.1 |
| Backend | Node.js + Express |
| Database | MongoDB + Mongoose ODM |
| Auth | JWT (jsonwebtoken) + bcrypt, Google OAuth |
| AI | Anthropic SDK — claude-sonnet-4-6 |
| File Storage | AWS S3 (multer-s3) |
| Realtime | Server-Sent Events (SSE) |

---

## Project Structure

```
ArtisanFlowAI/
├── src/                          # React frontend
│   ├── api/
│   │   └── apiClient.js          # Axios instance with JWT interceptor
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── Layout.jsx            # App shell with nav
│   │   ├── ProtectedRoute.jsx    # Auth gate for protected routes
│   │   ├── StatusBadge.jsx       # Color-coded status badges
│   │   ├── CopyButton.jsx        # Copy-to-clipboard with toast
│   │   ├── AuthLayout.jsx        # Shared auth page layout
│   │   ├── GoogleIcon.jsx        # Google SVG icon
│   │   └── ScrollToTop.jsx       # Scroll restoration on route change
│   ├── pages/
│   │   ├── Landing.jsx           # Marketing landing page
│   │   ├── Login.jsx             # Email/password + Google login
│   │   ├── Register.jsx          # Signup with OTP verification
│   │   ├── ForgotPassword.jsx    # Password reset request
│   │   ├── ResetPassword.jsx     # Password reset form
│   │   ├── ProfileSetup.jsx      # Post-signup artisan profile form
│   │   ├── Dashboard.jsx         # Artisan dashboard with stats + submissions
│   │   ├── Submit.jsx            # New submission (upload + describe)
│   │   ├── Processing.jsx        # AI pipeline progress page (SSE)
│   │   ├── Results.jsx           # 3-tab results (Analysis / Listing / Prompts)
│   │   └── Admin.jsx             # Admin dashboard with filters + table
│   ├── lib/
│   │   ├── aiPipeline.js         # 4-step AI pipeline orchestrator
│   │   ├── AuthContext.jsx       # Auth provider + hooks (JWT-based)
│   │   ├── query-client.js       # React Query client
│   │   └── PageNotFound.jsx      # 404 page
│   ├── App.jsx                   # Router + auth wrappers
│   ├── main.jsx                  # App entry point
│   └── index.css                 # Design tokens + Tailwind layers
├── server/                       # Express backend
│   ├── models/
│   │   ├── User.js
│   │   ├── Submission.js
│   │   ├── ProductAnalysis.js
│   │   ├── AmazonListing.js
│   │   └── ImagePrompt.js
│   ├── routes/
│   │   ├── auth.js               # /api/auth/*
│   │   ├── submissions.js        # /api/submissions/*
│   │   ├── upload.js             # /api/upload
│   │   └── admin.js              # /api/admin/*
│   ├── middleware/
│   │   └── auth.js               # requireAuth, requireAdmin
│   ├── lib/
│   │   └── aiPipeline.js         # Anthropic SDK pipeline steps
│   └── index.js                  # Express app entry point
├── .env                          # Environment variables (see below)
├── vite.config.js
├── tailwind.config.js
├── index.html
└── package.json
```

---

## Key Environment Variables

```env
# Frontend (prefix with VITE_)
VITE_API_URL=http://localhost:4000

# Backend
PORT=4000
MONGODB_URI=mongodb://localhost:27017/artisanflow
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=7d

# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_CALLBACK_URL=http://localhost:4000/api/auth/google/callback

# AWS S3
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET=artisanflow-uploads

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Common Commands

```bash
# Install dependencies
npm install

# Start frontend dev server (port 5173)
npm run dev

# Start backend dev server (port 4000)
npm run server

# Run both concurrently
npm run dev:all

# Build frontend for production
npm run build

# Lint
npm run lint
```

---

## AI Pipeline (`src/lib/aiPipeline.js`)

The pipeline runs client-side after the Processing page triggers `POST /api/submissions/:id/pipeline`. Progress is streamed back via SSE.

| Step | Model | Input | Output Entity |
|---|---|---|---|
| 1. Language Detection & Translation | claude-sonnet-4-6 | `original_description` | Updates `Submission.translated_description` |
| 2. Vision Analysis | claude-sonnet-4-6 (vision) | Image URL + translated text | Creates `ProductAnalysis` |
| 3. Amazon Listing | claude-sonnet-4-6 | Analysis data + translated text | Creates `AmazonListing` |
| 4. Image Prompts | claude-sonnet-4-6 | Product title + craft + region | Bulk creates 7 `ImagePrompt` records |

Each step is idempotent: if the output record already exists, the step is skipped (supports retry on failure).

---

## Database Entities

| Entity | Key Fields |
|---|---|
| `User` | email, password_hash, role (artisan/admin), phone, region, craft_specialization, preferred_language |
| `Submission` | raw_image_url, original_description, translated_description, status, created_by_id |
| `ProductAnalysis` | submission_id, primary_material, craft_technique, state_of_origin, confidence_score, full_report |
| `AmazonListing` | submission_id, product_title, bullet_point_1–5, product_description, backend_keywords |
| `ImagePrompt` | submission_id, prompt_index, prompt_type, scene_description, target_platform |

All entities include `createdAt`, `updatedAt` (Mongoose timestamps), and `created_by_id` for row-level security.

---

## Auth Flow

1. Register → POST `/api/auth/register` → email OTP sent
2. Verify OTP → POST `/api/auth/verify-otp` → receive `access_token`
3. Store token in `localStorage`; Axios interceptor adds `Authorization: Bearer <token>` to every request
4. On 401 response, interceptor clears token and redirects to `/login`
5. After first login, if `region` is not set, Layout redirects to `/profile-setup`

---

## Design System

| Token | Value | Usage |
|---|---|---|
| `--primary` | Terracotta `hsl(16 87% 41%)` | CTAs, active states |
| `--accent` | Deep Teal `hsl(180 61% 26%)` | Secondary accents, admin |
| `--background` | Cream `hsl(42 72% 93%)` | Page background |
| `--card` | Light Cream `hsl(42 60% 97%)` | Card surfaces |
| `--font-heading` | Plus Jakarta Sans | Headings |
| `--font-body` | Plus Jakarta Sans | Body text |

Dark mode tokens are defined in `index.css`.

---

## Row-Level Security Pattern

Every Mongoose query for artisans must include `created_by_id: req.user.id`. Admin routes omit this filter. This is enforced in `server/routes/submissions.js`:

```js
// Artisan: own records only
const filter = req.user.role === 'admin' ? {} : { created_by_id: req.user.id };
const submissions = await Submission.find(filter).sort({ createdAt: -1 });
```

---

## Supported Languages

Artisans can describe products in: English (en), Hindi (hi), Telugu (te), Tamil (ta), Kannada (kn), Malayalam (ml), Bengali (bn), Marathi (mr), Gujarati (gu), Odia (or), Punjabi (pa). The AI pipeline detects the language automatically and translates to English before analysis.

---

## Documentation Files

| File | Contents |
|---|---|
| `Frontend.md` | Pages, components, API call patterns, auth flow |
| `Backend.md` | Express server, auth middleware, AI pipeline steps, file upload |
| `Database.md` | Mongoose schemas, RLS patterns, query examples |
| `API_Reference.md` | Full REST API endpoint reference |
| `TECH_STACK.md` | Dependency versions, design tokens, project structure |
