# ArtisanFlowAI

**AI-powered Amazon listing generator for Indian artisans.**

ArtisanFlowAI helps traditional craftspeople — potters, weavers, metalworkers, embroiderers — sell their handmade products on Amazon without needing to know English or e-commerce copywriting. An artisan uploads a product photo and a short description in their native language. A 4-step AI pipeline handles everything else: translation, craft identification, listing generation, and lifestyle image prompts.

---

## What It Does

| Step | What happens |
|---|---|
| **1. Translate** | Detects the artisan's language (Hindi, Telugu, Tamil, and 8 more) and translates to English |
| **2. Analyse** | Identifies the craft, material, technique, region of origin, and handmade authenticity from the product photo |
| **3. List** | Generates a complete Amazon listing: SEO title, 5 benefit bullets, full description, 250 backend keywords, and technical specs |
| **4. Prompt** | Creates 7 professional image-generation prompts (hero shots, lifestyle, detail close-up, gifting) ready for Midjourney, FLUX, or Gemini Imagen |

---

## Screenshots

> _Landing page · Dashboard · Processing · Results (3 tabs)_

_(Add screenshots here after first deployment)_

---

## Tech Stack

**Frontend**
- React 18.2 + Vite
- React Router DOM 6.26
- Tailwind CSS + shadcn/ui (Radix UI)
- @tanstack/react-query 5.84
- react-markdown 9.0.1

**Backend**
- Node.js + Express
- MongoDB + Mongoose
- JWT authentication + Google OAuth
- AWS S3 for image storage
- Server-Sent Events for real-time pipeline progress

**AI**
- Anthropic SDK — `claude-sonnet-4-6` (vision + text)

---

## Getting Started

### Prerequisites

- Node.js 20+
- MongoDB (local or Atlas)
- AWS S3 bucket
- Anthropic API key
- Google OAuth credentials (optional — for Google login)

### Installation

```bash
git clone https://github.com/your-org/artisanflow-ai.git
cd artisanflow-ai
npm install
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Frontend
VITE_API_URL=http://localhost:4000

# Backend
PORT=4000
MONGODB_URI=mongodb://localhost:27017/artisanflow
JWT_SECRET=your-jwt-secret
JWT_EXPIRES_IN=7d

# Google OAuth (optional)
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

### Running Locally

```bash
# Start both frontend (port 5173) and backend (port 4000)
npm run dev:all

# Or separately:
npm run dev       # Vite dev server
npm run server    # Express server (with nodemon)
```

Open [http://localhost:5173](http://localhost:5173).

### Build for Production

```bash
npm run build     # Compiles frontend to /dist
npm start         # Serves Express + static /dist
```

---

## User Roles

| Role | Capabilities |
|---|---|
| **Artisan** (default) | Submit products, view own dashboard, access results |
| **Admin** | View all submissions across all artisans, filter by region/status/craft |

Assign admin role directly in MongoDB:
```js
db.users.updateOne({ email: "you@example.com" }, { $set: { role: "admin" } })
```

---

## Project Structure

```
ArtisanFlowAI/
├── src/              # React frontend
│   ├── api/          # Axios client with JWT interceptor
│   ├── components/   # Layout, ProtectedRoute, StatusBadge, CopyButton
│   ├── pages/        # 11 pages (Landing → Admin)
│   └── lib/          # aiPipeline.js, AuthContext, React Query client
├── server/           # Express backend
│   ├── models/       # Mongoose schemas (User, Submission, ProductAnalysis, AmazonListing, ImagePrompt)
│   ├── routes/       # auth, submissions, upload, admin
│   ├── middleware/   # requireAuth, requireAdmin
│   └── lib/          # Anthropic SDK pipeline logic
└── .env
```

---

## Supported Languages

Artisans can describe their products in:

| Language | Code |
|---|---|
| English | en |
| Hindi | hi |
| Telugu | te |
| Tamil | ta |
| Kannada | kn |
| Malayalam | ml |
| Bengali | bn |
| Marathi | mr |
| Gujarati | gu |
| Odia | or |
| Punjabi | pa |

---

## AI Agents

Two purpose-built agents extend the core pipeline:

| Agent | Purpose |
|---|---|
| **Artisan Assistant** | Multilingual conversational guide — explains results, answers questions, coaches artisans on photography and pricing |
| **Listing Optimizer** | Post-generation reviewer — audits Amazon policy compliance, boosts SEO score, and rewrites weak sections |

See [`agents.md`](./agents.md) for implementation details.

---

## Documentation

| File | Contents |
|---|---|
| [`CLAUDE.md`](./CLAUDE.md) | Full developer guide (stack, commands, patterns) |
| [`Frontend.md`](./Frontend.md) | Pages, components, API call patterns |
| [`Backend.md`](./Backend.md) | Express server, auth, AI pipeline, file upload |
| [`Database.md`](./Database.md) | Mongoose schemas, RLS, query examples |
| [`API_Reference.md`](./API_Reference.md) | Complete REST endpoint reference |
| [`agents.md`](./agents.md) | AI agent specifications and integration guide |

---

## License

MIT
