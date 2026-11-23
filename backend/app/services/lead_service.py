import math

from app.core.exceptions import LeadNotFoundError
from app.schemas.lead import LeadStatus


class LeadService:
    def __init__(self, leads):
        self.leads = leads

    async def create(self, owner_id, data: dict):
        return await self.leads.create(owner_id, data)

    async def list(self, owner_id, page, limit, search, status_filter, sort_by, order):
        items, total = await self.leads.list(
            owner_id, page, limit, search, status_filter, sort_by, order
        )
        return {
            "items": items,
            "page": page,
            "limit": limit,
            "total": total,
            "pages": math.ceil(total / limit) if total else 0,
        }

    async def get(self, owner_id, lead_id):
        lead = await self.leads.get(owner_id, lead_id)
        if not lead:
            raise LeadNotFoundError
        return lead

    async def update(self, owner_id, lead_id, data: dict):
        lead = await self.leads.update(owner_id, lead_id, data)
        if not lead:
            raise LeadNotFoundError
        return lead

    async def set_status(self, owner_id, lead_id, status: LeadStatus):
        return await self.update(owner_id, lead_id, {"status": status.value})

    async def delete(self, owner_id, lead_id):
        if not await self.leads.delete(owner_id, lead_id):
            raise LeadNotFoundError

    async def stats(self, owner_id):
        return await self.leads.stats(owner_id)
