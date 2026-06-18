import logging
from datetime import datetime, timezone
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.match import Match, MatchPlayer, Round, WeaponStat
from app.models.user import User
from app.schemas.match import PlayerScore, RoundDetail, Scoreboard, WeaponStatDetail
from app.schemas.user import MatchSummary, User as UserSchema, UserCreate
from app.services.cache import cached
from app.services.external_clients import fetch_faceit_match_history
from app.services.faceit_ingestor import upsert_faceit_matches


log = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=UserSchema)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserSchema:
    user = User(
        steam_id=user_in.steam_id,
        faceit_id=user_in.faceit_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserSchema.model_validate(user)


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> UserSchema:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserSchema.model_validate(user)


@router.get("/{user_id}/matches", response_model=List[MatchSummary])
async def get_user_matches(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[MatchSummary]:
    """
    Return combined match history for a user from the local DB.
    To refresh from Steam/FACEIT, call the sync endpoint.
    """
    stmt = (
        select(Match)
        .where(Match.user_id == user_id)
        .order_by(Match.started_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    matches = result.scalars().all()
    return [MatchSummary.model_validate(m) for m in matches]


@router.get("/{user_id}/matches/{match_id}/rounds", response_model=List[RoundDetail])
async def get_match_rounds(
    user_id: int,
    match_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[RoundDetail]:
    """
    Detailed round‑by‑round breakdown for a given match.
    """
    match = await db.get(Match, match_id)
    if not match or match.user_id != user_id:
        raise HTTPException(status_code=404, detail="Match not found for user")

    stmt_rounds = (
        select(Round)
        .where(Round.match_id == match_id)
        .order_by(Round.round_number.asc())
    )
    result_rounds = await db.execute(stmt_rounds)
    rounds = result_rounds.scalars().all()

    # Eager load weapon stats for all rounds in a single query
    if not rounds:
        return []

    round_ids = [r.id for r in rounds]
    stmt_ws = select(WeaponStat).where(WeaponStat.round_id.in_(round_ids))
    result_ws = await db.execute(stmt_ws)
    weapon_stats = result_ws.scalars().all()

    stats_by_round: dict[int, list[WeaponStatDetail]] = {}
    for ws in weapon_stats:
        stats_by_round.setdefault(ws.round_id, []).append(
            WeaponStatDetail(
                weapon_name=ws.weapon_name,
                shots=ws.shots,
                hits=ws.hits,
                headshots=ws.headshots,
            )
        )

    payload: list[RoundDetail] = []
    for r in rounds:
        payload.append(
            RoundDetail(
                id=r.id,
                match_id=r.match_id,
                round_number=r.round_number,
                winning_team=r.winning_team,
                kills=r.kills,
                deaths=r.deaths,
                weapon_used=r.weapon_used,
                weapon_stats=stats_by_round.get(r.id, []),
            )
        )

    return payload


@router.get("/{user_id}/matches/{match_id}/scoreboard", response_model=Scoreboard)
async def get_match_scoreboard(
    user_id: int,
    match_id: int,
    db: AsyncSession = Depends(get_db),
) -> Scoreboard:
    match = await db.get(Match, match_id)
    if not match or match.user_id != user_id:
        raise HTTPException(status_code=404, detail="Match not found for user")

    stmt = (
        select(MatchPlayer)
        .where(MatchPlayer.match_id == match_id)
        .order_by(MatchPlayer.team, MatchPlayer.rating.desc())
    )
    result = await db.execute(stmt)
    players = result.scalars().all()

    ct = [PlayerScore.model_validate(p) for p in players if p.team == "CT"]
    t = [PlayerScore.model_validate(p) for p in players if p.team == "T"]

    return Scoreboard(
        match_id=match.id,
        map_name=match.map_name,
        score_team=match.score_team,
        score_opponent=match.score_opponent,
        result=match.result,
        ct=ct,
        t=t,
    )


@router.post("/{user_id}/sync", response_model=dict)
async def sync_user_matches(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Fetch latest match history from Steam and FACEIT for this user and persist it.
    Parsing is intentionally robust and uses only a small subset of common fields
    so that the endpoint keeps working even if providers add new data.
    """
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    async def _sync() -> dict:
        faceit_data = None

        if user.steam_id:
            # Steam's public Web API does NOT expose CS2 match history — that
            # requires Game Coordinator / authenticated access we don't have.
            # We therefore skip Steam match ingestion entirely instead of
            # writing fabricated rows. Lifetime CS2 stats (a different concern)
            # are served separately via fetch_csgo_classic_stats.
            log.info(
                "Skipping Steam match sync for user %s: Steam Web API does not "
                "provide CS2 match history.",
                user.id,
            )
            await _upsert_matches_from_steam(db, user.id, None)

        if user.faceit_id:
            faceit_data = await fetch_faceit_match_history(user.faceit_id, game="cs2")
            await upsert_faceit_matches(db, user.id, user.faceit_id, faceit_data)

        await db.commit()

        return {
            "steam_synced": False,
            "faceit_synced": faceit_data is not None,
        }

    result = await cached(f"user:{user_id}:sync", 300, _sync)
    return result


def _parse_steam_ts(value: Any) -> Optional[datetime]:
    """
    Best-effort parse of a Steam-style timestamp into an aware datetime.
    Accepts unix epoch seconds/milliseconds (int/str) or ISO-8601 strings.
    Returns None when the value can't be interpreted as a real timestamp.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    # Numeric epoch (seconds or milliseconds).
    try:
        ts = int(value)
    except (TypeError, ValueError):
        ts = None
    if ts is not None:
        if ts >= 1e12:  # milliseconds
            ts = ts / 1000.0
        try:
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    # ISO-8601 string fallback.
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return None


async def _upsert_matches_from_steam(
    db: AsyncSession, user_id: int, payload: Optional[dict]
) -> int:
    """
    Map a Steam match-history-like payload into Match rows.

    Steam's public Web API does not currently provide CS2 match history, so
    callers pass ``None`` and this becomes a safe no-op. The defensive parsing
    below is kept so that a real Steam match source (e.g. a future GC-backed
    ingestor) can be wired in without re-deriving the schema. It never writes
    rows with a missing/invalid ``started_at`` (the column is non-nullable).

    Returns the number of new matches inserted.
    """
    if not payload:
        return 0

    matches = (
        payload.get("matches")
        or (payload.get("result") or {}).get("matches")
        or []
    )

    inserted = 0
    for item in matches:
        if not isinstance(item, dict):
            continue

        external_id = str(item.get("match_id") or item.get("id") or "")
        if not external_id:
            continue

        started_at = _parse_steam_ts(
            item.get("start_time") or item.get("created_at")
        )
        if started_at is None:
            # started_at is required (non-nullable); skip unusable rows.
            continue

        existing = await db.execute(
            select(Match).where(Match.external_match_id == external_id)
        )
        match = existing.scalar_one_or_none()

        if match is None:
            duration = item.get("duration")
            match = Match(
                external_match_id=external_id,
                user_id=user_id,
                provider="steam",
                map_name=item.get("map") or item.get("map_name"),
                started_at=started_at,
                duration_seconds=int(duration) if duration is not None else None,
                score_team=None,
                score_opponent=None,
                result=None,
            )
            db.add(match)
            inserted += 1

    return inserted

