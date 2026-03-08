"""Mongo connection utilities with graceful fallback behavior."""

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
import certifi

from app.config import settings

_mongo_client: MongoClient | None = None


def get_mongo_client() -> MongoClient | None:
    """Return a cached Mongo client if connection is available."""
    global _mongo_client
    if _mongo_client is not None:
        return _mongo_client

    try:
        client = MongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=1500,
            tlsCAFile=certifi.where(),
        )
        client.admin.command("ping")
        _mongo_client = client
        return _mongo_client
    except PyMongoError as e:
        print("Mongo connection failed:", e)
        return None


def get_sessions_collection() -> Collection | None:
    """Return Mongo collection for tax sessions or None if unavailable."""
    client = get_mongo_client()
    if client is None:
        return None
    db = client[settings.mongodb_db_name]
    return db[settings.mongodb_collection_sessions]


def get_boxdata_collection() -> Collection | None:
    """Return Mongo collection for parser box-data docs or None."""
    client = get_mongo_client()
    if client is None:
        return None
    db = client[settings.mongodb_db_name]
    return db[settings.mongodb_collection_boxdata]
