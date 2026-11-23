from pymongo import ASCENDING, DESCENDING


async def create_indexes(database) -> None:
    await database.users.create_index("normalized_email", unique=True)
    await database.leads.create_index([("owner_id", ASCENDING), ("status", ASCENDING)])
    await database.leads.create_index([("owner_id", ASCENDING), ("created_at", DESCENDING)])
    await database.leads.create_index([("owner_id", ASCENDING), ("name", ASCENDING)])
