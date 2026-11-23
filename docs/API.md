# API reference

API root: `http://localhost:8000/api/v1`. Interactive docs are at `/docs` outside production. Private routes require `Authorization: Bearer <access_token>`. Responses use JSON except lead deletion (`204 No Content`).

## Authentication

### `POST /auth/register` — 201

```json
{"name":"Asha Mehta","email":"asha@example.com","password":"LongPassword123!"}
```

Returns `access_token`, `token_type`, and public `user` fields. Passwords must be at least 12 characters.

### `POST /auth/login` — 200

```json
{"email":"asha@example.com","password":"LongPassword123!"}
```

An invalid email/password pair returns the same generic 401 response.

### `GET /auth/me` — 200

Returns the current public user profile.

## Leads

All lead routes are authenticated and owner-scoped. Allowed statuses: `New`, `Contacted`, `Qualified`, `Lost`. Allowed sources: `Website`, `Referral`, `Social Media`, `Advertisement`, `Cold Call`, `Other`.

### `POST /leads` — 201

```json
{
  "name":"Asha Mehta",
  "email":"asha@example.com",
  "phone":"+14155552671",
  "company":"Example Co",
  "source":"Website",
  "status":"New"
}
```

### `GET /leads` — 200

Query parameters: `page` (1+), `limit` (1–100, default 10), `search` (name, up to 100 chars), `status`, `sort_by` (`created_at`, `updated_at`, `name`, `company`, `status`), and `order` (`asc` or `desc`).

Returns `{ "items": [...], "page": 1, "limit": 10, "total": 0, "pages": 0 }`.

### `GET /leads/{lead_id}` — 200

Read one lead belonging to the current user.

### `PUT /leads/{lead_id}` — 200

Update any supplied lead fields. System-managed fields and ownership cannot be updated.

### `PATCH /leads/{lead_id}/status` — 200

```json
{"status":"Qualified"}
```

### `DELETE /leads/{lead_id}` — 204

Deletes an owned lead.

## Dashboard and health

- `GET /dashboard/stats` — authenticated counts for total and each status.
- `GET /health` — basic process health; does not depend on MongoDB.
- `GET /ready` — 200 when MongoDB responds to ping, otherwise generic 503.

## Errors

Errors use a JSON `detail` field. Common statuses are 400 (invalid ObjectId), 401 (missing/invalid token), 404 (not found or not owned), 409 (duplicate account), 422 (invalid request/query), and 503 (database unavailable). Framework validation responses use FastAPI's structured 422 detail format.
