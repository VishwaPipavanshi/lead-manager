# Security notes

## Implemented controls

- Configuration comes from backend environment variables. `.env` files are ignored by Git; examples contain placeholders only.
- JWTs are signed with HS256, require a subject and expiry, and have a configurable 5–60 minute lifetime (30 minutes by default). Never reuse the example secret.
- Passwords are hashed with Argon2 via `pwdlib`. Login failures do not reveal whether the email exists.
- Authenticated user identity is derived from the verified JWT. MongoDB filters include both lead ID and owner ID.
- MongoDB indexes enforce normalized user-email uniqueness. Lead status/source values, request fields, pagination, sorting, ObjectIds, and phone numbers are validated.
- Search terms are escaped before use in MongoDB regex queries; sorting uses a fixed allowlist.
- Write request bodies are capped at 1 MiB, including chunked requests.
- CORS is restricted to configured origins. Production rejects localhost and wildcard origins. Security response headers are set, and interactive API docs are disabled in production.
- Logs intentionally omit request bodies, passwords, bearer tokens, connection strings, and database exceptions.
- Lead and account endpoints return safe errors; database failures return a generic 503 response.
- Frontend stores the access token in `localStorage` for this small screening app. This is convenient but exposed to JavaScript running through an XSS vulnerability and is **not equivalent to an HttpOnly cookie**. Keep the UI free of unsafe HTML, use HTTPS in deployment, and consider moving to short-lived access tokens with Secure/HttpOnly/SameSite cookies plus CSRF protection for a production deployment.

## Limitations and production actions

- Stateless logout clears the browser's token only. It does not revoke a still-valid issued token. Immediate revocation needs a denylist or another server-side session mechanism.
- There is no application-level login/register rate limiter. Configure a real edge/API gateway rate limit before public deployment; this app does not send pretend 429s.
- Restrict Atlas network access to deployment egress addresses; do not casually allow `0.0.0.0/0`. Use an application database user with database-scoped `readWrite` access, not an Atlas administrator.
- Set a randomly generated secret of at least 32 characters, production-only explicit CORS origins, and a private MongoDB URL through the host's secret manager. Never place secrets in `VITE_*` variables.
- Configure TLS, proxy request timeouts, monitoring, backups, and dependency/security update procedures at deployment. The app does not trust forwarded headers; retain a body-size limit at the hosting proxy as well.
- CI runs dependency audit and static security checks, but does not demonstrate a clean deployed environment or replace a security review. Check scan output for the exact run; update vulnerable dependencies before release.

Generate a secret locally, without placing it in source control:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Do not paste credentials into issue trackers or logs. If a secret ever enters Git history, rotate it immediately; deleting it from the latest revision does not remove historical exposure.
