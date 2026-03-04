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
