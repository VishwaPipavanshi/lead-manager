import pytest


@pytest.mark.asyncio
async def test_dashboard_counts_only_authenticated_users(authenticated_client, lead_payload):
    client = authenticated_client
    own_token = client.headers["Authorization"]
    await client.post("/api/v1/leads", json=lead_payload)
    await client.post(
        "/api/v1/leads", json={**lead_payload, "name": "Contacted Person", "status": "Contacted"}
    )
    second_account = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Another User",
            "email": "another@example.com",
            "password": "AnotherLongPassword123!",
        },
    )
    client.headers["Authorization"] = f"Bearer {second_account.json()['access_token']}"
    await client.post("/api/v1/leads", json={**lead_payload, "name": "Private Lead"})
    client.headers["Authorization"] = own_token
    response = await client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    assert response.json() == {
        "total": 2,
        "new": 1,
        "contacted": 1,
        "qualified": 0,
        "lost": 0,
    }
