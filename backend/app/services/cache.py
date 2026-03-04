from __future__ import annotations

from typing import Any, Callable, Coroutine, Optional, TypeVar

import json

from redis.asyncio import Redis

from app.core.config import settings


T = TypeVar("T")


_redis_client: Optional[Redis] = None


def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def cached(
    key: str,
    ttl_seconds: int,
    compute: Callable[[], Coroutine[Any, Any, T]],
) -> T:
    """
    Simple Redis-backed cache helper.
    """
    client = get_redis_client()
    cached_value = await client.get(key)
    if cached_value is not None:
        return json.loads(cached_value)

    value = await compute()
    await client.set(key, json.dumps(value, default=str), ex=ttl_seconds)
    return value

