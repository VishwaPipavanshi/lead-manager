# Lead Manager API

FastAPI backend for the Lead Manager. See the [root README](../README.md) for setup and run instructions and [API documentation](../docs/API.md) for routes.

A local `.env` containing safe placeholders is included; edit it without overwriting any configured credentials. Set the Atlas connection URI and a random 32+ character JWT secret, then run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run checks from this directory with `python -m pytest -q`, `ruff check app tests`, and `ruff format --check app tests`.
