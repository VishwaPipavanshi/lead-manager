import pytest


@pytest.mark.asyncio
async def test_lead_crud_and_status_update(authenticated_client, lead_payload):
    client = authenticated_client
    created = await client.post("/api/v1/leads", json=lead_payload)
    assert created.status_code == 201
    lead = created.json()
    assert lead["name"] == "Asha Mehta"
    assert lead["email"] == lead_payload["email"].lower()

    fetched = await client.get(f"/api/v1/leads/{lead['id']}")
    assert fetched.status_code == 200

    changed = await client.put(f"/api/v1/leads/{lead['id']}", json={"company": "Updated Company"})
    assert changed.status_code == 200
    assert changed.json()["company"] == "Updated Company"

    status_result = await client.patch(
        f"/api/v1/leads/{lead['id']}/status", json={"status": "Qualified"}
    )
    assert status_result.status_code == 200
    assert status_result.json()["status"] == "Qualified"

    deleted = await client.delete(f"/api/v1/leads/{lead['id']}")
    assert deleted.status_code == 204
    assert (await client.get(f"/api/v1/leads/{lead['id']}")).status_code == 404


@pytest.mark.asyncio
async def test_lead_validation_and_invalid_object_id(authenticated_client, lead_payload):
    client = authenticated_client
    missing = await client.post("/api/v1/leads", json={"name": "Missing"})
    assert missing.status_code == 422
    for field, value in (
        ("email", "bad-email"),
        ("phone", "12"),
        ("source", "Unknown"),
        ("status", "Pending"),
    ):
        invalid = await client.post("/api/v1/leads", json={**lead_payload, field: value})
        assert invalid.status_code == 422
    assert (await client.get("/api/v1/leads/not-an-object-id")).status_code == 400


@pytest.mark.asyncio
async def test_search_filter_pagination_and_sorting(authenticated_client, lead_payload):
    client = authenticated_client
    await client.post("/api/v1/leads", json=lead_payload)
    await client.post(
        "/api/v1/leads", json={**lead_payload, "name": "Ravi Shah", "status": "Contacted"}
    )
    response = await client.get(
        "/api/v1/leads",
        params={"search": "ravi", "status": "Contacted", "page": 1, "limit": 1, "sort_by": "name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Ravi Shah"
    assert data["pages"] == 1


@pytest.mark.asyncio
async def test_pagination_order_and_sort_allowlist(authenticated_client, lead_payload):
    client = authenticated_client
    await client.post("/api/v1/leads", json=lead_payload)
    await client.post(
        "/api/v1/leads", json={**lead_payload, "name": "Ravi Shah", "email": "ravi@example.com"}
    )
    first = await client.get(
        "/api/v1/leads", params={"page": 1, "limit": 1, "sort_by": "name", "order": "asc"}
    )
    second = await client.get(
        "/api/v1/leads", params={"page": 2, "limit": 1, "sort_by": "name", "order": "asc"}
    )
    assert first.json()["items"][0]["name"] == "Asha Mehta"
    assert second.json()["items"][0]["name"] == "Ravi Shah"
    assert first.json()["pages"] == 2
    invalid_sort = await client.get("/api/v1/leads", params={"sort_by": "$where"})
    assert invalid_sort.status_code == 422


@pytest.mark.asyncio
async def test_cross_user_cannot_access_update_or_delete_lead(
    authenticated_client, client, lead_payload
):
    created = await authenticated_client.post("/api/v1/leads", json=lead_payload)
    lead_id = created.json()["id"]
    second_account = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Second User",
            "email": f"second-{lead_payload['email']}",
            "password": "AnotherLongPassword123!",
        },
    )
    client.headers["Authorization"] = f"Bearer {second_account.json()['access_token']}"
    assert (await client.get(f"/api/v1/leads/{lead_id}")).status_code == 404
    assert (
        await client.put(f"/api/v1/leads/{lead_id}", json={"name": "Intruder"})
    ).status_code == 404
    assert (await client.delete(f"/api/v1/leads/{lead_id}")).status_code == 404


@pytest.mark.asyncio
async def test_lead_endpoints_require_authentication(client, lead_payload):
    assert (await client.post("/api/v1/leads", json=lead_payload)).status_code == 401
