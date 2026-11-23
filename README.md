# Lead Manager

A compact, full-stack lead-management app built for the Meru Technosoft Private Limited Full Stack Developer screening assignment. It provides account registration and login, a private sales pipeline, lead search/filtering, status counts, and CRUD workflows backed by MongoDB.

## Features

- Register and sign in with Argon2 password hashing and short-lived JWT access tokens.
- Create, list, search, filter, sort, edit, change status, and delete leads with confirmation.
- Owner-scoped records and dashboard counts.
- Validated API, pagination, safe ObjectId handling, MongoDB indexes, a 1 MiB request cap, and generic readiness/error responses.
- Responsive React UI with loading, validation, error, and empty states.
- Pytest backend tests, Ruff, Bandit and pip-audit configuration; frontend lint and production build checks.

## Technology choices

- **FastAPI** provides typed request validation, OpenAPI documentation, dependency injection, and asynchronous request handlers.
- **MongoDB Atlas with PyMongo Async** stores flexible lead and user records, with owner-scoped queries and indexes. This uses supported `AsyncMongoClient`, not deprecated Motor.
- **React + Vite** provides a small responsive JavaScript frontend and fast local development. Axios centralizes API access.

## Architecture

```text
backend/app/
  api/          HTTP routes and auth dependencies
  core/         settings, JWT/password security, logging, errors
  database/     client setup and MongoDB indexes
  repositories/ MongoDB queries
  schemas/      Pydantic request/response validation
  services/     business logic
  tests/        API behavior and authorization tests
frontend/src/
  app/          routes and protection
  context/      authentication session state
  pages/        login, registration, dashboard
  services/     Axios API and resource calls
  styles/       responsive SCSS
docs/           API, security, and Git workflow references
```

## Prerequisites and MongoDB Atlas

- Python 3.11+ and Node.js LTS/npm.
- A MongoDB Atlas cluster and a **database-scoped application user** with `readWrite` on `lead_manager`. Keep Atlas network access restricted to your actual development/deployment egress addresses; do not open access to the world as a shortcut.
- Copy `backend/.env.example` to `backend/.env` and set your private `MONGODB_URL` and a locally generated random `JWT_SECRET_KEY` (at least 32 characters). A safe placeholder `backend/.env` is present but will intentionally fail startup until replaced. Never commit that local file.
- For a production environment, set `APP_ENV=production`, `ALLOWED_ORIGINS` to exact frontend origins, and secrets in the hosting platform's secret manager. Do not put private values in `VITE_*`.

Generate a local signing secret with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Backend setup

From the repository root in PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Update the existing placeholder values for `MONGODB_URL` and `JWT_SECRET_KEY` in `backend/.env`, then start the server:

```powershell
uvicorn app.main:app --reload
```

The API is at `http://localhost:8000`, development OpenAPI UI at `/docs`, basic health at `/health`, and MongoDB readiness at `/ready`.

## Frontend setup

In another terminal:

```powershell
cd frontend
npm ci
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
npm run dev
```

Open the local Vite URL printed in the terminal. Configure `VITE_API_BASE_URL` if the backend address differs.

## API and authentication

The API is versioned under `/api/v1`. Authentication routes are `/auth/register`, `/auth/login`, and `/auth/me`. Lead CRUD and status routes are under `/leads`; dashboard counts are at `/dashboard/stats`. See [docs/API.md](docs/API.md).

Frontend access tokens are stored in browser `localStorage`, which is vulnerable to token theft via JavaScript execution and is not equivalent to an HttpOnly cookie. Logout clears local storage but cannot revoke a stateless JWT before its expiry. Details and mitigations are in [docs/SECURITY.md](docs/SECURITY.md).

## Tests and checks

From `backend/` with the virtual environment activated:

```powershell
python -m pytest -q
ruff check app tests
ruff format --check app tests
bandit -r app
pip-audit
```

From `frontend/`:

```powershell
npm ci
npm run lint
npm run build
```

Backend tests use an in-memory test adapter; they do not connect to or modify Atlas. CI uses test-only configuration and no production credentials.

## Git, CI, deployment

GitHub Actions are configured for backend and frontend checks on pull requests and pushes to `develop` and `main`. Dependabot checks pip, npm, and GitHub Actions weekly. Workflow files being present does not mean they have run: a GitHub remote and repository are needed. See [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md) to enable branch protection and required checks.

Deployment is not configured or completed. For a future deployment, configure the production environment variables, TLS, a strict CORS allowlist, Atlas network allowlisting, health checks (`/health` and `/ready`), and host-level request limits. The backend can run with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`; build the frontend with `npm run build` and serve `frontend/dist` using a static host. Do not publish resources without explicit authorization.

## Assumptions and limitations

- Every lead is private to the account that created it; the API does not expose a shared team workspace.
- Phone numbers without a country prefix are interpreted as US numbers; supply an international `+` prefix for other regions.
- No app-level abuse limiter, JWT revocation store, deployment target, or Atlas credentials are included.
- API tests exercise routes and auth with an isolated in-memory repository adapter. MongoDB connectivity, indexes, and Atlas permissions still require manual verification against a configured Atlas cluster.
- External Google Fonts are referenced for typography; a restrictive CSP/offline deployment should self-host fonts or remove that import.

## Technical challenge

The central design challenge is maintaining tenant isolation consistently: each lead operation and aggregation is constrained by the identity verified from a signed, expiring token, rather than trusting a client-supplied owner ID. The test adapter exercises cross-account read, update, and delete behavior without touching production data.

## Future improvements

Production cookie-based authentication with CSRF protection and revocation, actual edge rate limiting, audit events, team/role management, self-hosted fonts, and a configured deployment pipeline.

## License

MIT. See [LICENSE](LICENSE).
