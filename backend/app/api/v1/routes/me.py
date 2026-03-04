from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import PMEC_FACEIT_NICKNAME, PMEC_STEAM_ID
from app.db.session import get_db
from app.models.match import Match, Round, WeaponStat


router = APIRouter()


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

    return ProfileOverview(
        nickname="pmec",
        steam_id=PMEC_STEAM_ID,
        faceit_nickname=PMEC_FACEIT_NICKNAME,
        avatar_url="https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg",
        rank="Global Sentinel",
        elo=2616,
        total_matches=total_matches,
        total_wins=total_wins,
        total_losses=total_losses,
        win_rate=round((total_wins / max(1, total_matches)) * 100, 1),
        overall_kd=round(overall_kd, 2),
        headshot_pct=round(headshot_pct, 1),
        total_hours=9620,
        favorite_map=favorite_map,
        favorite_weapon=favorite_weapon,
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
