from __future__ import annotations

from typing import Any, Callable, Coroutine, Optional, TypeVar

import asyncio
import json
import time

from app.core.config import settings


T = TypeVar("T")


# ---------- In-memory fallback (always works, no external dependency) ----------

_memory_store: dict[str, tuple[float, str]] = {}


class _MemoryCache:
    async def get(self, key: str) -> Optional[str]:
        entry = _memory_store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.time() > expires_at:
            _memory_store.pop(key, None)
            return None
        return value

    async def set(self, key: str, value: str, ex: int = 300) -> None:
        _memory_store[key] = (time.time() + ex, value)

    async def aclose(self) -> None:
        pass


# ---------- Client selection ----------

_cache_client: Any = None
_USE_MEMORY = False


def get_redis_client() -> Any:
    global _cache_client, _USE_MEMORY
    if _cache_client is not None:
        return _cache_client

    if _USE_MEMORY or not settings.REDIS_URL.startswith("redis://"):
        pass
    else:
        try:
            from redis.asyncio import Redis
            _cache_client = Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=1)
            return _cache_client
        except Exception:
            pass

    _USE_MEMORY = True
    _cache_client = _MemoryCache()
    return _cache_client


async def _ping_redis() -> bool:
    """Quick non-blocking ping to see if Redis is reachable."""
    client = get_redis_client()
    if isinstance(client, _MemoryCache):
        return False
    try:
        result = await asyncio.wait_for(client.ping(), timeout=1.0)
        return bool(result)
    except Exception:
        return False


async def ensure_cache_ready() -> None:
    """Called once at startup. Falls back to memory cache if Redis is unreachable."""
    global _cache_client, _USE_MEMORY
    if not await _ping_redis():
        _USE_MEMORY = True
        _cache_client = _MemoryCache()


async def cached(
    key: str,
    ttl_seconds: int,
    compute: Callable[[], Coroutine[Any, Any, T]],
) -> T:
    client = get_redis_client()
    try:
        cached_value = await asyncio.wait_for(client.get(key), timeout=1.0)
        if cached_value is not None:
            return json.loads(cached_value)
    except Exception:
        pass

    value = await compute()

    try:
        await asyncio.wait_for(
            client.set(key, json.dumps(value, default=str), ex=ttl_seconds),
            timeout=1.0,
        )
    except Exception:
        pass

    return value
