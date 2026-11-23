import re
from datetime import UTC, datetime

from pymongo import ASCENDING, DESCENDING

from app.schemas.lead import LeadStatus

SORT_FIELDS = {
    "created_at": "created_at",
    "updated_at": "updated_at",
    "name": "name",
    "company": "company",
    "status": "status",
}


class LeadRepository:
    def __init__(self, collection):
        self.collection = collection

    async def create(self, owner_id, data: dict) -> dict:
        now = datetime.now(UTC)
        document = {**data, "owner_id": owner_id, "created_at": now, "updated_at": now}
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def list(self, owner_id, page, limit, search, status_filter, sort_by, order):
        query = {"owner_id": owner_id}
        if status_filter:
            query["status"] = status_filter.value
        if search:
            query["name"] = {"$regex": re.escape(search), "$options": "i"}
        total = await self.collection.count_documents(query)
        direction = ASCENDING if order == "asc" else DESCENDING
        cursor = (
            self.collection.find(query)
            .sort(SORT_FIELDS[sort_by], direction)
            .skip((page - 1) * limit)
            .limit(limit)
        )
        return await cursor.to_list(length=limit), total

    async def get(self, owner_id, lead_id):
        return await self.collection.find_one({"_id": lead_id, "owner_id": owner_id})

    async def update(self, owner_id, lead_id, changes: dict):
        if not changes:
            return await self.get(owner_id, lead_id)
        changes["updated_at"] = datetime.now(UTC)
        return await self.collection.find_one_and_update(
            {"_id": lead_id, "owner_id": owner_id},
            {"$set": changes},
            return_document=True,
        )

    async def delete(self, owner_id, lead_id) -> bool:
        result = await self.collection.delete_one({"_id": lead_id, "owner_id": owner_id})
        return result.deleted_count == 1

    async def stats(self, owner_id) -> dict:
        pipeline = [
            {"$match": {"owner_id": owner_id}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]
        cursor = await self.collection.aggregate(pipeline)
        counts = {row["_id"]: row["count"] async for row in cursor}

        return {
            "total": sum(counts.values()),
            "new": counts.get(LeadStatus.NEW.value, 0),
            "contacted": counts.get(LeadStatus.CONTACTED.value, 0),
            "qualified": counts.get(LeadStatus.QUALIFIED.value, 0),
            "lost": counts.get(LeadStatus.LOST.value, 0),
        }
