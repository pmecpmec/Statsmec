from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import PMEC_FACEIT_NICKNAME, PMEC_STEAM_ID, settings
from app.db.session import get_db
from app.models.match import Match, MatchPlayer, Round, WeaponStat
from app.services.auto_sync import _resolve_player_id, _sync_once
from app.services.allstar_client import fetch_user_clips, normalize_clips
from app.services.external_clients import (
    fetch_csgo_classic_stats,
    fetch_faceit_player_by_nickname,
    fetch_premier_and_faceit_from_remote,
    fetch_steam_profile,
)


router = APIRouter()


# FACEIT level 1–10 to hex (grey → green → yellow → orange → red → gold)
FACEIT_LEVEL_COLORS: dict[int, str] = {
    1: "#8b8b8b",
    2: "#5a9b5a",
    3: "#5a9b5a",
    4: "#7cb35c",
    5: "#a0c95a",
    6: "#c5e359",
    7: "#f0e14e",
    8: "#f5a623",
    9: "#e86122",
    10: "#e64646",
}


def _premier_rating_to_hex(rating: int) -> str:
    """CS2 Premier rating to tier color (Gray <5k → Light Blue → Blue → Purple → Pink → Red → Yellow 30k+)."""
    if rating < 5000:
        return "#9ca3af"
    if rating < 10000:
        return "#7dd3fc"
    if rating < 15000:
        return "#60a5fa"
    if rating < 20000:
        return "#a78bfa"
    if rating < 25000:
        return "#f472b6"
    if rating < 30000:
        return "#f87171"
    return "#facc15"


class ProfileOverview(BaseModel):
    nickname: str
    steam_id: str
    faceit_nickname: str
    avatar_url: str
    rank: str
    elo: int
    total_matches: int
    total_wins: int
    total_losses: int
    win_rate: float
    overall_kd: float
    headshot_pct: float
    total_hours: float
    favorite_map: str | None
    favorite_weapon: str | None
    api_configured: bool
    faceit_level: int | None = None
    faceit_color_hex: str | None = None
    premier_rating: int | None = None
    premier_color_hex: str | None = None


@router.get("/", response_model=ProfileOverview)
async def get_profile(db: AsyncSession = Depends(get_db)) -> ProfileOverview:
    total_q = await db.execute(select(func.count(Match.id)).where(Match.user_id == 1))
    total_matches = total_q.scalar() or 0

    wins_q = await db.execute(
        select(func.count(Match.id)).where(Match.user_id == 1, Match.result == "win")
    )
    total_wins = wins_q.scalar() or 0
    total_losses = total_matches - total_wins

    kills_q = await db.execute(
        select(func.sum(Round.kills), func.sum(Round.deaths))
        .join(Match, Round.match_id == Match.id)
        .where(Match.user_id == 1)
    )
    row = kills_q.one_or_none()
    total_kills = (row[0] or 0) if row else 0
    total_deaths = (row[1] or 0) if row else 0
    overall_kd = total_kills / max(1, total_deaths)

    hs_q = await db.execute(
        select(func.sum(WeaponStat.headshots), func.sum(WeaponStat.hits))
        .join(Round, WeaponStat.round_id == Round.id)
        .join(Match, Round.match_id == Match.id)
        .where(Match.user_id == 1)
    )
    hs_row = hs_q.one_or_none()
    total_hs = (hs_row[0] or 0) if hs_row else 0
    total_hits = (hs_row[1] or 0) if hs_row else 0
    headshot_pct = (total_hs / max(1, total_hits)) * 100

    fav_map_q = await db.execute(
        select(Match.map_name, func.count(Match.id).label("cnt"))
        .where(Match.user_id == 1)
        .group_by(Match.map_name)
        .order_by(func.count(Match.id).desc())
        .limit(1)
    )
    fav_map_row = fav_map_q.one_or_none()
    favorite_map = fav_map_row[0] if fav_map_row else None

    fav_weapon_q = await db.execute(
        select(Round.weapon_used, func.count(Round.id).label("cnt"))
        .join(Match, Round.match_id == Match.id)
        .where(Match.user_id == 1, Round.weapon_used.isnot(None))
        .group_by(Round.weapon_used)
        .order_by(func.count(Round.id).desc())
        .limit(1)
    )
    fav_weapon_row = fav_weapon_q.one_or_none()
    favorite_weapon = fav_weapon_row[0] if fav_weapon_row else None

    # Default to the known avatar URL, but try to refresh from Steam if an API key is configured.
    avatar_url = "https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg"
    try:
        steam_profile = await fetch_steam_profile(PMEC_STEAM_ID)
        if steam_profile and steam_profile.get("avatarfull"):
            avatar_url = str(steam_profile["avatarfull"])
    except Exception:
        pass

    # FACEIT level and color from API
    faceit_level: int | None = None
    faceit_color_hex: str | None = None
    elo = 2616
    has_faceit_elo = False
    try:
        faceit_player = await fetch_faceit_player_by_nickname(PMEC_FACEIT_NICKNAME)
        if faceit_player:
            games = faceit_player.get("games") or {}
            cs2 = games.get("cs2") or {}
            if isinstance(cs2, dict):
                lvl = cs2.get("skill_level")
                if lvl is not None:
                    faceit_level = int(lvl) if int(lvl) in range(1, 11) else None
                    if faceit_level is not None:
                        faceit_color_hex = FACEIT_LEVEL_COLORS.get(faceit_level)
                raw_elo = cs2.get("faceit_elo")
                if raw_elo is not None:
                    elo = int(raw_elo)
                    has_faceit_elo = True
    except Exception:
        pass

    # Optional third‑party hook (e.g. api.jakobkristensen.com) for Premier + Faceit elo
    remote_premier_rating: int | None = None
    remote_faceit_elo: int | None = None
    if settings.PMEC_PREMIER_REMOTE_URL:
        try:
            remote = await fetch_premier_and_faceit_from_remote(settings.PMEC_PREMIER_REMOTE_URL)
            if remote:
                remote_premier_rating = remote.get("premier_rating")
                remote_faceit_elo = remote.get("faceit_elo")
        except Exception:
            # Completely optional; ignore failures and fall back to other sources.
            remote_premier_rating = None
            remote_faceit_elo = None

    # If FACEIT API isn't configured or didn't give us an elo, fall back to remote Faceit elo
    if remote_faceit_elo is not None and not has_faceit_elo:
        elo = remote_faceit_elo

    # Premier from remote first, then config (no public API)
    premier_rating = remote_premier_rating if remote_premier_rating is not None else settings.PMEC_PREMIER_RATING
    premier_color_hex = settings.PMEC_PREMIER_COLOR
    if premier_rating is not None and premier_color_hex is None:
        premier_color_hex = _premier_rating_to_hex(premier_rating)

    return ProfileOverview(
        nickname="pmec",
        steam_id=PMEC_STEAM_ID,
        faceit_nickname=PMEC_FACEIT_NICKNAME,
        avatar_url=avatar_url,
        rank="Global Sentinel",
        elo=elo,
        total_matches=total_matches,
        total_wins=total_wins,
        total_losses=total_losses,
        win_rate=round((total_wins / max(1, total_matches)) * 100, 1),
        overall_kd=round(overall_kd, 2),
        headshot_pct=round(headshot_pct, 1),
        total_hours=9620,
        favorite_map=favorite_map,
        favorite_weapon=favorite_weapon,
        api_configured=bool(settings.FACEIT_API_KEY),
        faceit_level=faceit_level,
        faceit_color_hex=faceit_color_hex,
        premier_rating=premier_rating,
        premier_color_hex=premier_color_hex,
    )


class LiveStatus(BaseModel):
    status: str  # "offline" | "online" | "in_game"
    current_match_id: int | None = None
    last_match_id: int | None = None
    last_match_ago: str | None = None
    total_matches: int = 0


@router.get("/status", response_model=LiveStatus)
async def get_live_status(db: AsyncSession = Depends(get_db)) -> LiveStatus:
    """
    Returns pmec's current status. Checks if there's a very recent match
    (within last 60 min) to infer "in_game", otherwise "online" or "offline".
    With real FACEIT API keys, this would check ongoing matches directly.
    """
    latest_q = await db.execute(
        select(Match)
        .where(Match.user_id == 1)
        .order_by(Match.started_at.desc())
        .limit(1)
    )
    latest = latest_q.scalar_one_or_none()

    count_q = await db.execute(select(func.count(Match.id)).where(Match.user_id == 1))
    total = count_q.scalar() or 0

    if not latest:
        return LiveStatus(status="offline", total_matches=total)

    now = datetime.now(tz=timezone.utc)
    started = latest.started_at
    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)
    match_end = started + timedelta(seconds=latest.duration_seconds or 2400)
    diff = now - started

    if diff < timedelta(minutes=60) and now < match_end:
        status = "in_game"
        current_match_id = latest.id
    else:
        status = "online"
        current_match_id = None

    if diff < timedelta(hours=1):
        ago = f"{int(diff.total_seconds() // 60)}m ago"
    elif diff < timedelta(days=1):
        ago = f"{int(diff.total_seconds() // 3600)}h ago"
    else:
        ago = f"{diff.days}d ago"

    return LiveStatus(
        status=status,
        current_match_id=current_match_id,
        last_match_id=latest.id,
        last_match_ago=ago,
        total_matches=total,
    )


class SyncResult(BaseModel):
    success: bool
    message: str
    api_configured: bool


@router.post("/sync", response_model=SyncResult)
async def trigger_sync() -> SyncResult:
    """Manually trigger a FACEIT data sync."""
    if not settings.FACEIT_API_KEY:
        return SyncResult(
            success=False,
            message="FACEIT_API_KEY not configured. Add it to backend/.env",
            api_configured=False,
        )
    try:
        await _sync_once()
        return SyncResult(success=True, message="Sync complete", api_configured=True)
    except Exception as e:
        return SyncResult(success=False, message=str(e), api_configured=True)


@router.delete("/seed-data")
async def delete_seed_data(db: AsyncSession = Depends(get_db)) -> dict:
    """Remove seeded/demo matches (those without real FACEIT UUID external IDs)."""
    from sqlalchemy import and_, delete, not_, select

    seed_matches = await db.execute(
        select(Match.id).where(
            and_(
                Match.user_id == 1,
                not_(Match.external_match_id.like("1-________-____-____-____-____________%")),
            )
        )
    )
    seed_ids = [r[0] for r in seed_matches.all()]
    if not seed_ids:
        return {"deleted": 0}

    seed_round_ids = await db.execute(
        select(Round.id).where(Round.match_id.in_(seed_ids))
    )
    rids = [r[0] for r in seed_round_ids.all()]
    if rids:
        await db.execute(delete(WeaponStat).where(WeaponStat.round_id.in_(rids)))
    await db.execute(delete(Round).where(Round.match_id.in_(seed_ids)))
    await db.execute(delete(MatchPlayer).where(MatchPlayer.match_id.in_(seed_ids)))
    await db.execute(delete(Match).where(Match.id.in_(seed_ids)))
    await db.commit()
    return {"deleted": len(seed_ids)}


class HighlightClip(BaseModel):
    clip_id: str | None
    title: str
    url: str | None
    thumbnail: str | None
    created_at: str | None
    status: str | None
    steam_id: str | None
    map: str | None = None
    kills: int | None = None
    headshots: int | None = None
    weapon: str | None = None


class HighlightsResponse(BaseModel):
    total: int
    clips: list[HighlightClip]


@router.get("/highlights", response_model=HighlightsResponse)
async def get_highlights(limit: int = 12) -> HighlightsResponse:
    """
    Return recent Allstar.gg clips for pmec (CS2 only).
    """
    payload = await fetch_user_clips(steam_id=PMEC_STEAM_ID, limit=limit)
    normalized = normalize_clips(payload)
    total = (payload.get("data") or {}).get("count") or len(normalized)
    # Trim in case API returns more than requested.
    normalized = normalized[:limit]
    return HighlightsResponse(
        total=total,
        clips=[HighlightClip(**c) for c in normalized],
    )


class CSGOClassicStats(BaseModel):
    total_kills: int
    total_deaths: int
    kd: float
    total_wins: int
    total_time_hours: float


@router.get("/csgo-classic", response_model=CSGOClassicStats)
async def get_csgo_classic_stats() -> CSGOClassicStats:
    """
    Lifetime CS:GO / CS2 classic stats from Steam Web API.
    Uses appid 730 and the configured STEAM_API_KEY.
    """
    payload = await fetch_csgo_classic_stats(PMEC_STEAM_ID)
    stats_list = ((payload or {}).get("playerstats") or {}).get("stats") or []
    stats = {str(s.get("name")): int(s.get("value") or 0) for s in stats_list if "name" in s}

    total_kills = int(stats.get("total_kills", 0))
    total_deaths = int(stats.get("total_deaths", 0))
    total_wins = int(stats.get("total_wins", 0))
    # Some schemas use total_time_played, others may have variants; fall back gracefully.
    time_seconds = int(
        stats.get("total_time_played", 0)
    )
    total_time_hours = time_seconds / 3600 if time_seconds > 0 else 0.0
    kd = total_kills / max(1, total_deaths)

    return CSGOClassicStats(
        total_kills=total_kills,
        total_deaths=total_deaths,
        kd=round(kd, 2),
        total_wins=total_wins,
        total_time_hours=round(total_time_hours, 1),
    )
