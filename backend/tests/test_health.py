import pytest


@pytest.mark.asyncio
async def test_health_is_available_without_database(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert (await client.get("/docs")).status_code == 200


@pytest.mark.asyncio
async def test_readiness_is_unavailable_without_database(client):
    response = await client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
