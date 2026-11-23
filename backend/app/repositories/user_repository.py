from datetime import UTC, datetime

from pymongo.errors import DuplicateKeyError

from app.core.exceptions import DuplicateUserError


class UserRepository:
    def __init__(self, collection):
        self.collection = collection

    async def find_by_email(self, email: str) -> dict | None:
        return await self.collection.find_one({"normalized_email": email})

    async def find_by_id(self, user_id) -> dict | None:
        return await self.collection.find_one({"_id": user_id})

    async def create(self, name: str, email: str, password_hash: str) -> dict:
        now = datetime.now(UTC)
        document = {
            "name": name,
            "email": email,
            "normalized_email": email,
            "password_hash": password_hash,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        try:
            result = await self.collection.insert_one(document)
        except DuplicateKeyError as exc:
            raise DuplicateUserError from exc
        document["_id"] = result.inserted_id
        return document
