import os
from datetime import UTC, datetime
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from bson import ObjectId


def pytest_configure():
    os.environ.update(
        {
            "APP_ENV": "test",
            "MONGODB_URL": "mongodb://localhost:27017",
            "DATABASE_NAME": "lead_manager_test",
            "JWT_SECRET_KEY": "local-test-secret-that-is-never-used-outside-tests",
            "ALLOWED_ORIGINS": "http://localhost:5173",
        }
    )


class MemoryUsers:
    def __init__(self):
        self.by_id = {}
        self.by_email = {}

    async def find_by_email(self, email):
        return self.by_email.get(email)

    async def find_by_id(self, user_id):
        return self.by_id.get(user_id)

    async def create(self, name, email, password_hash):
        if email in self.by_email:
            from app.core.exceptions import DuplicateUserError

            raise DuplicateUserError
        now = datetime.now(UTC)
        user = {
            "_id": ObjectId(),
            "name": name,
            "email": email,
            "normalized_email": email,
            "password_hash": password_hash,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        self.by_id[user["_id"]] = user
        self.by_email[email] = user
        return user


class MemoryLeads:
    def __init__(self):
        self.items = {}

    async def create(self, owner_id, data):
        now = datetime.now(UTC)
        lead = {
            **data,
            "_id": ObjectId(),
            "owner_id": owner_id,
            "created_at": now,
            "updated_at": now,
        }
        self.items[lead["_id"]] = lead
        return lead

    async def list(self, owner_id, page, limit, search, status_filter, sort_by, order):
        items = [
            lead
            for lead in self.items.values()
            if lead["owner_id"] == owner_id
            and (not status_filter or lead["status"] == status_filter.value)
            and (not search or search.lower() in lead["name"].lower())
        ]
        items.sort(key=lambda item: item[sort_by], reverse=order == "desc")
        offset = (page - 1) * limit
        return items[offset : offset + limit], len(items)

    async def get(self, owner_id, lead_id):
        lead = self.items.get(lead_id)
        return lead if lead and lead["owner_id"] == owner_id else None

    async def update(self, owner_id, lead_id, changes):
        lead = await self.get(owner_id, lead_id)
        if lead:
            lead.update(changes)
            lead["updated_at"] = datetime.now(UTC)
        return lead

    async def delete(self, owner_id, lead_id):
        lead = await self.get(owner_id, lead_id)
        if lead:
            del self.items[lead_id]
            return True
        return False

    async def stats(self, owner_id):
        owned = [lead for lead in self.items.values() if lead["owner_id"] == owner_id]
        counts = {
            key: sum(lead["status"] == label for lead in owned)
            for key, label in [
                ("new", "New"),
                ("contacted", "Contacted"),
                ("qualified", "Qualified"),
                ("lost", "Lost"),
            ]
        }
        return {"total": len(owned), **counts}


@pytest.fixture
def services():
    from app.core.config import get_settings
    from app.main import app
    from app.services.auth_service import AuthService
    from app.services.lead_service import LeadService

    users = MemoryUsers()
    leads = MemoryLeads()
    app.state.auth_service = AuthService(users, get_settings())
    app.state.lead_service = LeadService(leads)
    return users, leads, app


@pytest_asyncio.fixture
async def client(services):
    transport = httpx.ASGITransport(app=services[2])
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


@pytest.fixture
def lead_payload():
    return {
        "name": "  Asha  Mehta ",
        "email": f"asha-{uuid4().hex[:8]}@example.com",
        "phone": "+14155552671",
        "company": "Meru Systems",
        "source": "Website",
        "status": "New",
    }


@pytest_asyncio.fixture
async def authenticated_client(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": f"tester-{uuid4().hex[:8]}@example.com",
            "password": "SafeLongTestPassword123!",
        },
    )
    assert response.status_code == 201
    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"
    return client
