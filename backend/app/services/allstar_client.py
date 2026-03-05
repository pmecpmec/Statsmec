from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from app.core.config import PMEC_STEAM_ID, settings

BASE_URL = "https://prt.allstar.gg"


async def _get_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=BASE_URL, timeout=10.0)


async def fetch_user_clips(
    steam_id: str = PMEC_STEAM_ID,
    limit: int = 12,
) -> Dict[str, Any]:
    """
    Fetch recent clips for a given user from Allstar.
    Uses the partner API key via X-API-Key header.
    """
    if not settings.ALLSTAR_SERVER_API_KEY and not settings.ALLSTAR_PUBLIC_API_KEY:
        return {"message": "Allstar API key not configured", "data": {"clips": [], "count": 0, "limit": limit}}

    headers = {
        "X-API-Key": settings.ALLSTAR_SERVER_API_KEY or settings.ALLSTAR_PUBLIC_API_KEY  # fallback to public if needed
    }

    # We filter by steamId and game=cs2, sort by date, newest first.
    params: Dict[str, Any] = {
        "steamId": steam_id,
        "limit": limit,
        "page": 1,
        "sort": ["date"],
        "game": ["cs2"],
        "onDemand": 1,  # include on-demand clips as well
    }

    async with await _get_client() as client:
        resp = await client.get("/user/clips", headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()


def _extract_meta_value(meta: List[Dict[str, Any]], key: str) -> Optional[str]:
    for item in meta or []:
        if str(item.get("key")) == key and item.get("value") is not None:
            return str(item["value"])
    return None


def normalize_clips(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Map Allstar's clip objects into a compact structure for the frontend.
    Safely handles missing fields.
    """
    data = payload.get("data") or {}
    clips = data.get("clips") or []
    normalized: List[Dict[str, Any]] = []

    for c in clips:
        meta = c.get("metadata") or []
        map_name = _extract_meta_value(meta, "CS_Map")
        kills = _extract_meta_value(meta, "CS_Kill Count")
        heads = _extract_meta_value(meta, "CS_Headshots")
        weapon = _extract_meta_value(meta, "CS_Weapons")

        normalized.append(
            {
                "clip_id": c.get("_id"),
                "title": c.get("clipTitle") or c.get("clipTitle") or "Highlight",
                "url": c.get("clipUrl"),
                "thumbnail": c.get("clipImageThumbURL") or c.get("clipSnapshotURL"),
                "created_at": c.get("createdDate"),
                "status": c.get("status"),
                "steam_id": c.get("steamid"),
                "map": map_name,
                "kills": int(kills) if kills and kills.isdigit() else None,
                "headshots": int(heads) if heads and heads.isdigit() else None,
                "weapon": weapon,
            }
        )

    return normalized

