"""
Background task that polls FACEIT for new matches every SYNC_INTERVAL seconds.
Runs as an asyncio task started on app startup.
"""
from __future__ import annotations

import asyncio
import logging

from app.core.config import PMEC_FACEIT_NICKNAME, settings
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.services.external_clients import (
    fetch_faceit_match_history,
    fetch_faceit_player_by_nickname,
)
from app.services.faceit_ingestor import upsert_faceit_matches

log = logging.getLogger(__name__)

SYNC_INTERVAL = 60
_task: asyncio.Task | None = None
_faceit_player_id: str | None = None


async def _resolve_player_id() -> str | None:
    """Resolve pmec's FACEIT player_id UUID from nickname (cached after first call)."""
    global _faceit_player_id
    if _faceit_player_id:
        return _faceit_player_id
    try:
        data = await fetch_faceit_player_by_nickname(PMEC_FACEIT_NICKNAME)
        if data and data.get("player_id"):
            _faceit_player_id = data["player_id"]
            log.info("Resolved FACEIT player_id for %s: %s", PMEC_FACEIT_NICKNAME, _faceit_player_id)
            return _faceit_player_id
    except Exception as e:
        log.warning("Could not resolve FACEIT player_id: %s", e)
    return None


async def _sync_once() -> None:
    player_id = await _resolve_player_id()
    if not player_id:
        return

    try:
        history = await fetch_faceit_match_history(player_id, limit=20, game="cs2")
    except Exception as e:
        log.warning("Failed to fetch FACEIT match history: %s", e)
        return

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        user_q = await db.execute(select(User).where(User.faceit_id == player_id))
        user = user_q.scalar_one_or_none()

        if not user:
            user = User(
                steam_id="76561198245080640",
                faceit_id=player_id,
                nickname=PMEC_FACEIT_NICKNAME,
                rank="Global Sentinel",
                avatar_url="https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg",
            )
            db.add(user)
            await db.flush()

        try:
            count = await upsert_faceit_matches(db, user.id, player_id, history)
            await db.commit()
            if count > 0:
                log.info("Synced %d matches from FACEIT", count)
        except Exception as e:
            log.error("Error during match upsert: %s", e)
            await db.rollback()


async def _sync_loop() -> None:
    while True:
        if settings.FACEIT_API_KEY:
            try:
                await _sync_once()
            except Exception as e:
                log.error("Auto-sync error: %s", e)
        await asyncio.sleep(SYNC_INTERVAL)


def start_auto_sync() -> None:
    global _task
    if _task is not None:
        return
    _task = asyncio.create_task(_sync_loop())
    log.info("Auto-sync started (every %ds)", SYNC_INTERVAL)


def stop_auto_sync() -> None:
    global _task
    if _task:
        _task.cancel()
        _task = None
