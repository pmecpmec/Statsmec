"""
Proxies for Valorant product APIs (content, status, ranked leaderboards).

Match list + account resolution live under /me/valorant and use separate Riot products
(val/match/v1, riot/account/v1); ensure those are enabled on your key if you use them.
"""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings
from app.services.external_clients import (
    fetch_valorant_content,
    fetch_valorant_leaderboard_by_act,
    fetch_valorant_platform_status,
)

router = APIRouter()


def _riot_or_503() -> None:
    if not settings.RIOT_API_KEY or not settings.RIOT_API_KEY.strip():
        detail = (
            "RIOT_API_KEY not configured"
            if settings.dev_hints_in_api
            else "Service temporarily unavailable"
        )
        raise HTTPException(status_code=503, detail=detail)


def _map_riot_exc(exc: httpx.HTTPStatusError) -> HTTPException:
    body = (exc.response.text or "")[:500]
    return HTTPException(status_code=exc.response.status_code, detail=body or exc.response.reason_phrase)


@router.get("/content")
async def get_valorant_content(
    locale: str | None = Query(None, description="e.g. en-US; omit for all localizations"),
) -> dict[str, Any]:
    """val-content-v1 — agents, maps, acts, etc. (250 / 10s)."""
    _riot_or_503()
    try:
        return await fetch_valorant_content(locale)
    except httpx.HTTPStatusError as e:
        raise _map_riot_exc(e) from e


@router.get("/platform-status")
async def get_valorant_platform_status() -> dict[str, Any]:
    """val-status-v1 — platform / incident data (very high limits)."""
    _riot_or_503()
    try:
        return await fetch_valorant_platform_status()
    except httpx.HTTPStatusError as e:
        raise _map_riot_exc(e) from e


@router.get("/leaderboards/by-act/{act_id}")
async def get_valorant_leaderboard_by_act(act_id: str) -> dict[str, Any]:
    """val-ranked-v1 — leaderboard for a competitive act UUID (10 / 10s)."""
    _riot_or_503()
    try:
        data = await fetch_valorant_leaderboard_by_act(act_id)
    except httpx.HTTPStatusError as e:
        raise _map_riot_exc(e) from e
    if data is None:
        raise HTTPException(status_code=404, detail="Unknown act_id or empty leaderboard")
    return data
