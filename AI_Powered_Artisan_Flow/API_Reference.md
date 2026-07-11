# ArtisanFlowAI — API Reference

## Base URL

```
http://localhost:4000   (development)
https://api.artisanflow.ai  (production)
```

All authenticated endpoints require:
```
Authorization: Bearer <jwt_access_token>
```

---

## Authentication

### Login (Email + Password)

```
POST /api/auth/login
```
```json
{ "email": "artisan@example.com", "password": "secret" }
```
Response `200`:
```json
{ "access_token": "eyJ...", "user": { "id": "...", "email": "...", "role": "artisan" } }
```

---

### Login with Google OAuth

```
GET /api/auth/google
```
- Redirects to Google consent screen
- On success, redirects to `/auth/google/callback` → sets token cookie → redirects to `/?token=...`

---

### Register

```
POST /api/auth/register
```
```json
{ "email": "artisan@example.com", "password": "secret" }
```
Response `201`:
```json
{ "message": "OTP sent to your email." }
```
- User is created but NOT logged in — email OTP verification required

---

### Verify OTP

```
POST /api/auth/verify-otp
```
```json
{ "email": "artisan@example.com", "otpCode": "483920" }
```
Response `200`:
```json
{ "access_token": "eyJ..." }
```

---

### Resend OTP

```
POST /api/auth/resend-otp
```
```json
{ "email": "artisan@example.com" }
```
Response `200`:
```json
{ "message": "OTP resent." }
```

---

### Forgot Password

```
POST /api/auth/forgot-password
```
```json
{ "email": "artisan@example.com" }
```
Response `200`:
```json
{ "message": "If that email exists, a reset link has been sent." }
```
(Always returns generic success — API hides whether email exists.)

---

### Reset Password

```
POST /api/auth/reset-password
```
```json
{ "resetToken": "abc123...", "newPassword": "newSecret" }
```
Response `200`:
```json
{ "message": "Password updated." }
```

---

### Get Current User

```
GET /api/auth/me
Authorization: Bearer <token>
```
Response `200`:
```json
{
  "id": "64a...",
  "email": "artisan@example.com",
  "full_name": "Meena Devi",
  "role": "artisan",
  "phone": "+91 9876543210",
  "region": "Manipur",
  "craft_specialization": "Pottery",
  "preferred_language": "hi"
}
```

---

### Update Current User

```
PATCH /api/auth/me
Authorization: Bearer <token>
```
```json
{
  "phone": "+91 9876543210",
  "region": "Manipur",
  "craft_specialization": "Pottery",
  "preferred_language": "hi"
}
```
Response `200`: updated user object.

---

### Logout

```
POST /api/auth/logout
Authorization: Bearer <token>
```
Response `200`:
```json
{ "message": "Logged out." }
```
Client must also delete the token from localStorage.

---

## Submissions

### List (artisan's own)

```
GET /api/submissions?sort=-createdAt&limit=50
Authorization: Bearer <token>
```
Response `200`: array of submission objects. Always scoped to the authenticated artisan.

---

### Filter

```
GET /api/submissions?status=completed&sort=-createdAt&limit=10
Authorization: Bearer <token>
```
Supported query params: `status`, `sort` (field name, prefix `-` for descending), `limit`, `page`.

---

### Get by ID

```
GET /api/submissions/:id
Authorization: Bearer <token>
```
Response `200`: single submission object. Returns `403` if artisan doesn't own it.

---

### Create

```
POST /api/submissions
Authorization: Bearer <token>
```
```json
{
  "raw_image_url": "https://s3.../image.jpg",
  "original_description": "मेरे उत्पाद...",
  "status": "pending"
}
```
Response `201`: created submission object.

---

### Update

```
PATCH /api/submissions/:id
Authorization: Bearer <token>
```
```json
{ "status": "completed", "completed_at": "2026-07-11T10:30:00.000Z" }
```
Response `200`: updated submission object.

---

### Delete

```
DELETE /api/submissions/:id
Authorization: Bearer <token>
```
Response `204` No Content.

---

### Run AI Pipeline

```
POST /api/submissions/:id/pipeline
Authorization: Bearer <token>
```
Response `202 Accepted`:
```json
{ "message": "Pipeline started." }
```
- Pipeline runs asynchronously. Poll status via SSE endpoint below.
- On retry, clears `translated_description` and re-runs all steps.

---

### Pipeline Progress (SSE)

```
GET /api/submissions/:id/progress
Authorization: Bearer <token>
```
- Response is a `text/event-stream` (Server-Sent Events)
- Each event:
```
data: {"step": 2, "status": "running"}

data: {"step": 2, "status": "done"}

data: {"status": "completed"}
```
- Stream closes when status is `completed` or `failed`

---

## Results

### Get Product Analysis

```
GET /api/submissions/:id/analysis
Authorization: Bearer <token>
```
Response `200`:
```json
{
  "id": "64b...",
  "submission_id": "64a...",
  "primary_material": "Black Stone and Iron",
  "secondary_materials": ["Natural dye"],
  "craft_technique": "Longpi Pottery",
  "art_form_category": "Folk Art",
  "is_handmade": true,
  "state_of_origin": "Manipur",
  "confidence_score": 0.92,
  "full_report": "## Longpi Pottery Analysis\n..."
}
```

---

### Get Amazon Listing

```
GET /api/submissions/:id/listing
Authorization: Bearer <token>
```
Response `200`:
```json
{
  "id": "64c...",
  "submission_id": "64a...",
  "product_title": "Handcrafted Longpi Pottery Bowl...",
  "bullet_point_1": "Authentic Manipuri black stone pottery...",
  "bullet_point_2": "...",
  "bullet_point_3": "...",
  "bullet_point_4": "...",
  "bullet_point_5": "...",
  "product_description": "...",
  "backend_keywords": "longpi pottery, manipur handicrafts, ...",
  "item_dimensions": "10 x 8 x 5 inches",
  "item_weight": "1.2 kg",
  "material_type": "Black Stone, Iron",
  "color": "Black",
  "product_category": "Home & Kitchen > Décor"
}
```

---

### Get Image Prompts

```
GET /api/submissions/:id/prompts
Authorization: Bearer <token>
```
Response `200`: array of 7 prompt objects:
```json
[
  {
    "id": "64d...",
    "submission_id": "64a...",
    "prompt_index": 1,
    "prompt_type": "hero_shot",
    "scene_description": "A handcrafted Longpi pottery bowl centered on a white marble surface...",
    "target_platform": "Amazon Main Image"
  },
  ...
]
```

---

## File Upload

### Upload Public File

```
POST /api/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data
```
Body: `file` field with File/Blob (JPEG, PNG, WEBP — max 10MB)

Response `200`:
```json
{ "file_url": "https://s3.amazonaws.com/bucket/uploads/uuid-filename.jpg" }
```

---

## Admin Endpoints

All admin endpoints require `role === 'admin'`.

### List All Submissions

```
GET /api/admin/submissions?sort=-createdAt&limit=100&status=completed&region=Manipur
Authorization: Bearer <admin_token>
```
Response `200`: paginated array of submissions with populated artisan data.

### Admin Stats

```
GET /api/admin/stats
Authorization: Bearer <admin_token>
```
Response `200`:
```json
{
  "total": 142,
  "completed": 118,
  "completedToday": 7,
  "pending": 12,
  "failed": 12
}
```

---

## Error Responses

| Status | Meaning |
|---|---|
| `400 Bad Request` | Validation error — check request body |
| `401 Unauthorized` | Missing or invalid JWT token |
| `403 Forbidden` | Authenticated but insufficient role or not owner |
| `404 Not Found` | Resource does not exist |
| `409 Conflict` | Duplicate resource (e.g., email already registered) |
| `500 Internal Server Error` | Unexpected server error |

Error body:
```json
{ "error": "Human-readable message describing the problem." }
```

---

## Rate Limits & Constraints

- Image upload: max 10MB (JPG, PNG, WEBP)
- AI pipeline: 90-second timeout per submission
- Bulk operations: up to 500 records per query
- Pagination default: 10 submissions per page (dashboard and admin)
- Anthropic API: responses capped at ~2048 tokens per step
