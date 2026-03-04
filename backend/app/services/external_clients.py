from __future__ import annotations

from typing import Any, Dict, Optional

import asyncio
import random

import httpx

from app.core.config import settings


class RateLimitedClient:
    """
    Tiny helper enforcing simple concurrency and retry-aware calls.
    """

    def __init__(
        self,
        base_url: str,
        max_concurrent: int = 5,
        timeout: int = 10,
        max_retries: int = 3,
    ) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._max_retries = max_retries

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        async with self._semaphore:
            last_exc: Exception | None = None
            for attempt in range(self._max_retries):
                try:
                    resp = await self._client.get(url, **kwargs)
                    # Retry on 5xx and 429
                    if resp.status_code in {429, 500, 502, 503, 504}:
                        await self._backoff(attempt)
                        continue
                    return resp
                except (httpx.ReadTimeout, httpx.ConnectError, httpx.RemoteProtocolError) as exc:
                    last_exc = exc
                    await self._backoff(attempt)
            if last_exc:
                raise last_exc
            # Fallback, though flow should never reach here
            return await self._client.get(url, **kwargs)

    async def _backoff(self, attempt: int) -> None:
        base = 0.5 * (2**attempt)
        jitter = random.random() * 0.25
        await asyncio.sleep(base + jitter)

    async def aclose(self) -> None:
        await self._client.aclose()


steam_client = RateLimitedClient("https://api.steampowered.com")
faceit_client = RateLimitedClient("https://open.faceit.com/data/v4")


async def fetch_steam_match_history(steam_id: str, limit: int = 20) -> Dict[str, Any]:
    if not settings.STEAM_API_KEY:
        raise RuntimeError("STEAM_API_KEY is not configured")

    # Example endpoint; adjust parameters as needed for CS.
    params = {
        "key": settings.STEAM_API_KEY,
        "steamid": steam_id,
        "count": limit,
    }
    resp = await steam_client.get("/ISteamUserStats/GetUserStatsForGame/v2/", params=params)
    resp.raise_for_status()
    return resp.json()


async def fetch_faceit_player_by_nickname(nickname: str) -> Optional[Dict[str, Any]]:
    """Resolve a FACEIT nickname to full player object (includes player_id, elo, etc)."""
    if not settings.FACEIT_API_KEY:
        return None
    headers = {"Authorization": f"Bearer {settings.FACEIT_API_KEY}"}
    resp = await faceit_client.get(f"/players?nickname={nickname}", headers=headers)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


async def fetch_faceit_match_history(faceit_id: str, limit: int = 20, game: str = "cs2") -> Dict[str, Any]:
    """Player match history. faceit_id must be the player_id UUID."""
    if not settings.FACEIT_API_KEY:
        raise RuntimeError("FACEIT_API_KEY is not configured")

    headers = {"Authorization": f"Bearer {settings.FACEIT_API_KEY}"}
    params = {"offset": 0, "limit": min(limit, 100), "game": game}
    resp = await faceit_client.get(f"/players/{faceit_id}/history", headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()


async def fetch_faceit_match_details(match_id: str) -> Optional[Dict[str, Any]]:
    """Single match details: map, results, started_at, finished_at, etc."""
    if not settings.FACEIT_API_KEY:
        return None
    headers = {"Authorization": f"Bearer {settings.FACEIT_API_KEY}"}
    resp = await faceit_client.get(f"/matches/{match_id}", headers=headers)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


async def fetch_faceit_match_stats(match_id: str) -> Optional[Dict[str, Any]]:
    """Per-round, per-player stats (rounds[].teams[].players[].player_stats)."""
    if not settings.FACEIT_API_KEY:
        return None
    headers = {"Authorization": f"Bearer {settings.FACEIT_API_KEY}"}
    resp = await faceit_client.get(f"/matches/{match_id}/stats", headers=headers)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


async def fetch_faceit_rank_averages(game: str = "cs2") -> Optional[Dict[str, Any]]:
    if not settings.FACEIT_API_KEY:
        return None

    headers = {"Authorization": f"Bearer {settings.FACEIT_API_KEY}"}
    # This is illustrative; you may need a different endpoint for real rank statistics.
    resp = await faceit_client.get("/stats/ranks", headers=headers, params={"game": game})
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()

