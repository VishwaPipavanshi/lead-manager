from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from pymongo.errors import PyMongoError

from app.core.config import get_settings


@pytest.mark.asyncio
async def test_expired_token_is_rejected(client):
    settings = get_settings()
    token = jwt.encode(
        {"sub": str(uuid4()), "exp": datetime.now(UTC) - timedelta(minutes=1)},
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_database_errors_do_not_expose_internal_details(authenticated_client, services):
    class BrokenLeadService:
        async def list(self, *_args, **_kwargs):
            raise PyMongoError("sensitive database connection detail")

    services[2].state.lead_service = BrokenLeadService()
    response = await authenticated_client.get("/api/v1/leads")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database service is unavailable."}
    assert "sensitive" not in response.text


@pytest.mark.asyncio
async def test_request_body_size_is_limited(client):
    response = await client.post(
        "/api/v1/auth/register",
        content=b"x" * (1_048_577),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413
    assert response.json() == {"detail": "Request body exceeds the allowed size."}
