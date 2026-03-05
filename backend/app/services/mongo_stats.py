from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

_client: AsyncIOMotorClient | None = None


def _get_client() -> Optional[AsyncIOMotorClient]:
    """Return a cached Motor client if MONGODB_URI is configured."""
    global _client
    if not settings.MONGODB_URI:
        return None
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URI)
    return _client


def _get_db() -> Optional[AsyncIOMotorDatabase]:
    client = _get_client()
    if client is None:
        return None
    db_name = settings.MONGODB_DB_NAME or "statsmec"
    return client[db_name]


async def upsert_match_summary(
    user_id: int,
    match: Any,
    players: List[dict[str, Any]],
    keep: int = 300,
) -> None:
    """
    Store a compact per-match document in MongoDB and prune to a rolling window.

    This keeps MongoDB as a cache: FACEIT and the relational DB remain the
    source of truth, and Mongo only stores the last `keep` matches with
    scoreboard data for fast reads.
    """
    db = _get_db()
    if db is None:
        return

    doc = {
        "_id": match.external_match_id,
        "user_id": user_id,
        "map_name": match.map_name,
        "started_at": _ensure_datetime(match.started_at),
        "duration_seconds": match.duration_seconds,
        "score_team": match.score_team,
        "score_opponent": match.score_opponent,
        "result": match.result,
        "players": players,
    }

    await db.matches.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)

    # Ensure useful indexes exist (safe to call repeatedly).
    await db.matches.create_index([("user_id", 1), ("started_at", -1)])

    # Prune oldest matches beyond the rolling window.
    await _prune_old_matches(db, user_id=user_id, keep=keep)


async def _prune_old_matches(db: AsyncIOMotorDatabase, user_id: int, keep: int) -> None:
    cursor = (
        db.matches.find({"user_id": user_id}, {"_id": 1})
        .sort("started_at", -1)
        .skip(keep)
    )
    old_ids: list[Any] = [doc["_id"] async for doc in cursor]
    if old_ids:
        await db.matches.delete_many({"_id": {"$in": old_ids}})


def _ensure_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except Exception:
        return datetime.utcnow()

