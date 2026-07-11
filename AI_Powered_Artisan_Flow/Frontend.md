# ArtisanFlowAI — Frontend Documentation

## Pages Overview

| Route | Page | Access | Description |
|---|---|---|---|
| `/` | Landing | Public | Marketing page with hero, how-it-works, sample outputs, crafts gallery |
| `/login` | Login | Public | Email/password + Google OAuth login |
| `/register` | Register | Public | Email/password signup with OTP verification flow |
| `/forgot-password` | ForgotPassword | Public | Request password reset email |
| `/reset-password` | ResetPassword | Public | Set new password using `?token=` param |
| `/profile-setup` | ProfileSetup | Authenticated | Post-signup form: phone, region, craft, language |
| `/dashboard` | Dashboard | Authenticated | Artisan's submissions list + stats |
| `/submit` | Submit | Authenticated | Upload photo + description form |
| `/submissions/:id/processing` | Processing | Authenticated | AI pipeline progress with 4-step animation |
| `/submissions/:id/results` | Results | Authenticated | 3-tab results page (Analysis / Listing / Prompts) |
| `/admin` | Admin | Admin only | All submissions with filters + stats |

---

## API Client (`src/api/apiClient.js`)

All data fetching goes through a pre-configured Axios instance that injects the JWT token automatically:

```js
import axios from 'axios';

const apiClient = axios.create({ baseURL: import.meta.env.VITE_API_URL });

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default apiClient;
```

---

## Auth Context (`src/lib/AuthContext.jsx`)

```js
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      apiClient.get('/api/auth/me')
        .then(setUser)
        .catch(() => localStorage.removeItem('access_token'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const { access_token, user } = await apiClient.post('/api/auth/login', { email, password });
    localStorage.setItem('access_token', access_token);
    setUser(user);
    window.location.href = '/';
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    window.location.href = '/login';
  };

  return <AuthContext.Provider value={{ user, login, logout, loading }}>{children}</AuthContext.Provider>;
}
```

---

## Component Architecture

### Layout (`src/components/Layout.jsx`)
- App shell with sticky navigation bar
- Wraps all authenticated pages via `<Outlet />`
- Fetches current user on mount from `GET /api/auth/me`; redirects to `/login` if 401
- Redirects to `/profile-setup` if user has no `region` set
- Shows nav links: Dashboard, New Submission, Admin (role=admin), Logout

### ProtectedRoute (`src/components/ProtectedRoute.jsx`)
- Wraps protected routes as a layout route
- Renders `<Outlet />` when authenticated
- Renders `unauthenticatedElement` (redirects to `/login`) when not

### StatusBadge (`src/components/StatusBadge.jsx`)
- Color-coded status indicator
- `pending` → grey, `processing` → blue, `completed` → green, `failed` → red

### CopyButton (`src/components/CopyButton.jsx`)
- One-click copy to clipboard with "Copied!" feedback
- Used throughout Results page for every generated text element
- Uses `navigator.clipboard.writeText()`

---

## Page Details

### Landing Page
- Full marketing page, no auth required
- Sections: Hero, How It Works (3 steps), What You Get (3 deliverables), Supported Crafts Gallery (6 crafts), CTA, Footer
- "Get Started Free" button: navigates to dashboard if logged in, else triggers login flow
- Warm gradient hero background with terracotta/cream/teal palette

### Auth Pages
- Use shared `AuthLayout` component for consistent branding
- **Login**: Google button + email/password form, forgot password link

```js
// Login form submit
const handleLogin = async (e) => {
  e.preventDefault();
  await login(email, password); // from AuthContext
};

// Google OAuth
const handleGoogle = () => {
  window.location.href = `${import.meta.env.VITE_API_URL}/api/auth/google`;
};
```

- **Register**: Google button + email/password/confirm form → OTP verification step → redirect

```js
// Register
const { message } = await apiClient.post('/api/auth/register', { email, password });
setStep('otp'); // show OTP input

// Verify OTP
const { access_token } = await apiClient.post('/api/auth/verify-otp', { email, otpCode });
localStorage.setItem('access_token', access_token);
window.location.href = '/profile-setup';
```

- OTP uses `InputOTP` component (6-digit code), resend button included

### Profile Setup
- Shown after first login if `region` is not set
- Fields: phone (optional), state/region (dropdown of 30 Indian states), craft specialization (dropdown), preferred language (11 Indian languages with native script labels)

```js
const handleSave = async (formData) => {
  await apiClient.patch('/api/auth/me', formData);
  navigate('/dashboard');
};
```

### Dashboard
- Welcome message with user's first name
- Stats row: Total / Completed / Pending (3 cards)

```js
const { data: submissions } = useQuery({
  queryKey: ['submissions'],
  queryFn: () => apiClient.get('/api/submissions?sort=-created_date&limit=50')
});
const stats = {
  total: submissions?.length ?? 0,
  completed: submissions?.filter(s => s.status === 'completed').length ?? 0,
  pending: submissions?.filter(s => ['pending','processing'].includes(s.status)).length ?? 0
};
```

- Submissions list with thumbnail, date, description preview, status badge
- Action buttons per submission: View Results (completed), Processing... (pending), Retry (failed)

### Submit Page
- 3-step vertical flow:
  1. **Image Upload**: drag-and-drop or click, file validation (JPG/PNG/WEBP, 10MB max), preview
  2. **Description**: textarea with multilingual placeholder, character count
  3. **Submit**: "Generate My Listing Package" button

```js
// Upload image
const formData = new FormData();
formData.append('file', selectedFile);
const { file_url } = await apiClient.post('/api/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});

// Create submission and redirect to processing
const submission = await apiClient.post('/api/submissions', {
  raw_image_url: file_url,
  original_description: description,
  status: 'pending'
});
navigate(`/submissions/${submission.id}/processing`);
```

### Processing Page
- 4-step animated progress matching the AI pipeline:
  1. Translating your description
  2. Analyzing your product image
  3. Crafting your Amazon listing
  4. Creating lifestyle image prompts
- Each step shows: pending (grey icon) → running (spinner) → done (green check)
- Uses SSE to poll pipeline status:

```js
useEffect(() => {
  const es = new EventSource(`${import.meta.env.VITE_API_URL}/api/submissions/${id}/progress`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  });
  es.onmessage = (e) => {
    const { status, step } = JSON.parse(e.data);
    setCurrentStep(step);
    if (status === 'completed') { navigate(`/submissions/${id}/results`); es.close(); }
    if (status === 'failed') { setError(true); es.close(); }
  };
  return () => es.close();
}, [id]);
```

- Triggers `runPipeline()` via `POST /api/submissions/:id/pipeline` on mount
- "View Your Results" button appears when completed
- Error state with "Retry Pipeline" button on failure

### Results Page
- 3 tabs: Product Analysis | Amazon Listing | Image Prompts

```js
const { data } = useQuery({
  queryKey: ['results', id],
  queryFn: async () => {
    const [submission, analysis, listing, prompts] = await Promise.all([
      apiClient.get(`/api/submissions/${id}`),
      apiClient.get(`/api/submissions/${id}/analysis`),
      apiClient.get(`/api/submissions/${id}/listing`),
      apiClient.get(`/api/submissions/${id}/prompts`)
    ]);
    return { submission, analysis, listing, prompts };
  }
});
```

**Tab 1 — Product Analysis:**
- Confidence score badge + handmade status badge
- Info cards: Primary Material, Craft Technique, Art Form, Region, Secondary Materials
- Full analysis report rendered as markdown via `ReactMarkdown`
- "Download" button exports report as `.md` file

**Tab 2 — Amazon Listing:**
- Copyable title box with Copy button
- 5 bullet points, each with individual Copy button (appears on hover)
- Full description with "Copy All" button
- Backend keywords as tag cloud with "Copy Keywords" button
- Technical specs table (dimensions, weight, material, color, category)
- "Copy Entire Listing" button at top — copies formatted markdown

**Tab 3 — Image Prompts:**
- 7 prompt cards in responsive 2-column grid (1 column on mobile)
- Each card: prompt type badge, target platform tag, full prompt text, Copy button
- Info banner: "Paste these prompts into Gemini Imagen, FLUX, or Midjourney"

### Admin Page
- Access restricted to `role === 'admin'` (redirects to dashboard otherwise)
- Stats overview: Total, Completed Today, Pending, Failed

```js
const { data: allSubmissions } = useQuery({
  queryKey: ['admin-submissions'],
  queryFn: () => apiClient.get('/api/admin/submissions?sort=-created_date&limit=100')
});
```

- Filters: status dropdown, region dropdown
- Paginated table (10/page): artisan name, region, craft, date, status, action
- Clicking a completed submission navigates to its results page

---

## Responsive Design

- Mobile-first approach throughout
- Navigation: full labels on desktop, icons only on mobile
- Stats cards: 3-column on all sizes, text scales down on mobile
- Results grid: 2 columns on desktop, 1 column on mobile
- Admin table: hides region and craft columns on smaller screens
- All forms use `max-w-lg` / `max-w-2xl` for comfortable mobile typing

## Accessibility

- ARIA labels on all interactive elements
- Sufficient color contrast (terracotta on cream passes WCAG AA)
- Focus-visible states on all inputs and buttons
- Semantic HTML: proper heading hierarchy, list elements, table headers
