from pymongo import AsyncMongoClient

from app.core.config import Settings


def create_mongo_client(settings: Settings) -> AsyncMongoClient:
    return AsyncMongoClient(
        settings.mongodb_url.get_secret_value(),
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        tz_aware=True,
    )
