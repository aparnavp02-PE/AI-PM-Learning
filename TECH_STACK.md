# ArtisanFlowAI — Tech Stack

## Platform

| Layer | Technology | Notes |
|---|---|---|
| **Backend-as-a-Service** | Base44 | Auth, database, file storage, AI integrations, hosting, realtime subscriptions |
| **Framework** | React 18.2 | SPA with Vite bundler |
| **Language** | JavaScript (ES2020+) | No TypeScript |
| **Routing** | React Router DOM 6.26 | Client-side routing with protected routes |
| **Styling** | Tailwind CSS + shadcn/ui | Token-based design system, dark mode support |

## Frontend

| Category | Package | Purpose |
|---|---|---|
| **UI Components** | shadcn/ui (Radix UI) | Buttons, cards, tabs, selects, dialogs, badges, inputs, labels, toasts |
| **Icons** | lucide-react 0.475 | All app icons |
| **Markdown** | react-markdown 9.0.1 | Rendering AI-generated analysis reports |
| **Data Fetching** | @tanstack/react-query 5.84 | Server state management |
| **Forms** | react-hook-form 7.54 | Form handling |
| **Date Utils** | date-fns 3.6 | Date formatting and comparison |
| **Utilities** | lodash 4.17 | General utilities |
| **Charts** | recharts 2.15 | (Available for future analytics) |
| **Animations** | framer-motion 11.16 | (Available for future use) |

## Backend & Database

| Feature | Implementation |
|---|---|
| **Database** | Base44 managed MongoDB (entities as JSON schemas) |
| **Authentication** | Base44 Auth — email/password + Google OAuth, JWT tokens, OTP verification, password reset |
| **File Storage** | Base44 built-in — `UploadFile` for public, `UploadPrivateFile` + `CreateFileSignedUrl` for private |
| **AI Integration** | Base44 Core package — `InvokeLLM` with multiple model options |
| **Realtime** | Base44 entity subscriptions — `entity.subscribe(callback)` |
| **Server Logic** | Client-side pipeline in `src/lib/aiPipeline.js` (no separate backend functions needed) |

## AI Models (Free Tier)

| Model | Used For | Capabilities |
|---|---|---|
| `automatic` (default) | Translation, Listing Generation, Image Prompts | Text generation, structured JSON output |
| `gemini_3_flash` | Product Vision Analysis (Step 2) | Vision + web search context |

> **Note:** The original prompt specified `claude-sonnet-4-6` (Anthropic). Per the user's request, all AI calls use Base44's built-in free-tier models instead. The `gemini_3_flash` model is used for the vision analysis step because it supports both image input and web search context (`add_context_from_internet: true`), which enriches craft identification accuracy.

## Design System

| Token | Light Value | Dark Value | Usage |
|---|---|---|---|
| `--primary` | Terracotta `hsl(16 87% 41%)` | — | CTAs, active states, accents |
| `--accent` | Deep Teal `hsl(180 61% 26%)` | — | Secondary accents, admin elements |
| `--background` | Cream `hsl(42 72% 93%)` | Dark slate | Page background |
| `--card` | Light Cream `hsl(42 60% 97%)` | — | Card surfaces |
| `--font-heading` | Plus Jakarta Sans | — | Headings, titles |
| `--font-body` | Plus Jakarta Sans | — | Body text |

## Project Structure

```
ArtisanFlowAI/
├── src/
│   ├── api/
│   │   └── base44Client.js          # Pre-initialized Base44 SDK
│   ├── components/
│   │   ├── ui/                      # shadcn/ui components
│   │   ├── Layout.jsx               # App shell with nav + motif divider
│   │   ├── ProtectedRoute.jsx       # Auth gate for protected routes
│   │   ├── StatusBadge.jsx          # Color-coded status badges
│   │   ├── CopyButton.jsx           # Copy-to-clipboard with toast
│   │   ├── AuthLayout.jsx           # Shared auth page layout
│   │   ├── GoogleIcon.jsx           # Google SVG icon
│   │   ├── ScrollToTop.jsx          # Scroll restoration on route change
│   │   └── UserNotRegisteredError.jsx
│   ├── pages/
│   │   ├── Landing.jsx              # Marketing landing page
│   │   ├── Login.jsx                # Email/password + Google login
│   │   ├── Register.jsx             # Signup with OTP verification
│   │   ├── ForgotPassword.jsx       # Password reset request
│   │   ├── ResetPassword.jsx        # Password reset form
│   │   ├── ProfileSetup.jsx         # Post-signup artisan profile form
│   │   ├── Dashboard.jsx            # Artisan dashboard with stats + submissions
│   │   ├── Submit.jsx               # New submission (upload + describe)
│   │   ├── Processing.jsx           # AI pipeline progress page
│   │   ├── Results.jsx              # 3-tab results (Analysis / Listing / Prompts)
│   │   └── Admin.jsx                # Admin dashboard with filters + table
│   ├── lib/
│   │   ├── aiPipeline.js            # 4-step AI pipeline orchestrator
│   │   ├── AuthContext.jsx          # Auth provider + hooks
│   │   ├── app-params.js            # App configuration
│   │   ├── query-client.js          # React Query client
│   │   └── PageNotFound.jsx         # 404 page
│   ├── App.jsx                     # Router + auth wrappers
│   ├── main.jsx                    # App entry point
│   └── index.css                   # Design tokens + Tailwind layers
├── base44/
│   ├── entities/
│   │   ├── User.jsonc
│   │   ├── Submission.jsonc
│   │   ├── ProductAnalysis.jsonc
│   │   ├── AmazonListing.jsonc
│   │   └── ImagePrompt.jsonc
│   └── agents/                     # (empty — no agents configured)
├── tailwind.config.js
├── index.html
└── package.json
```

## Deployment

The app is hosted on Base44's managed infrastructure. No manual deployment steps — changes render instantly in the live preview. The app publishes to iOS/Android from the same React codebase.