from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Dict, List

import asyncio

from sqlalchemy import Select, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match import Match, Round, WeaponStat
from app.schemas.analytics import (
    AnalyticsResponse,
    KDPerMap,
    KDPerWeapon,
    RankComparisonMetric,
    WeaponHeatmap,
    HeatmapCell,
    WinRatePoint,
)
from app.services.external_clients import fetch_faceit_rank_averages


async def compute_kd_per_map(db: AsyncSession, user_id: int) -> List[KDPerMap]:
    stmt: Select = (
        select(
            Match.map_name,
            func.sum(Round.kills).label("kills"),
            func.sum(Round.deaths).label("deaths"),
        )
        .join(Round, Round.match_id == Match.id)
        .where(Match.user_id == user_id)
        .group_by(Match.map_name)
    )
    rows = (await db.execute(stmt)).all()
    return [
        KDPerMap(map_name=row.map_name or "Unknown", kills=row.kills or 0, deaths=row.deaths or 0)
        for row in rows
    ]


async def compute_kd_per_weapon(db: AsyncSession, user_id: int) -> List[KDPerWeapon]:
    stmt: Select = (
        select(
            WeaponStat.weapon_name,
            func.sum(WeaponStat.hits).label("kills"),  # proxy if detailed data not available
            func.sum(Round.deaths).label("deaths"),
        )
        .join(Round, WeaponStat.round_id == Round.id)
        .join(Match, Round.match_id == Match.id)
        .where(Match.user_id == user_id)
        .group_by(WeaponStat.weapon_name)
    )
    rows = (await db.execute(stmt)).all()
    return [
        KDPerWeapon(weapon_name=row.weapon_name, kills=row.kills or 0, deaths=row.deaths or 0)
        for row in rows
    ]


async def compute_win_rate_trend(db: AsyncSession, user_id: int) -> List[WinRatePoint]:
    stmt: Select = (
        select(
            func.date(Match.started_at).label("day"),
            func.count(Match.id).label("matches"),
            func.sum(case((Match.result == "win", 1), else_=0)).label("wins"),
            func.sum(case((Match.result == "loss", 1), else_=0)).label("losses"),
        )
        .where(Match.user_id == user_id)
        .group_by(func.date(Match.started_at))
        .order_by(func.date(Match.started_at))
    )
    rows = (await db.execute(stmt)).all()
    return [
        WinRatePoint(
            date=row.day if isinstance(row.day, date) else date.fromisoformat(str(row.day)),
            matches=row.matches or 0,
            wins=row.wins or 0,
            losses=row.losses or 0,
        )
        for row in rows
    ]


async def compute_weapon_heatmaps(db: AsyncSession, user_id: int) -> Dict[str, List[WeaponHeatmap]]:
    # In a real implementation you would store spatial shot data.
    # Here we return a synthetic heatmap per weapon per match,
    # scaled by shot count.
    stmt: Select = (
        select(
            Match.id.label("match_id"),
            WeaponStat.weapon_name,
            func.sum(WeaponStat.shots).label("shots"),
        )
        .join(Round, Round.match_id == Match.id)
        .join(WeaponStat, WeaponStat.round_id == Round.id)
        .where(Match.user_id == user_id)
        .group_by(Match.id, WeaponStat.weapon_name)
    )
    rows = (await db.execute(stmt)).all()

    results: Dict[str, List[WeaponHeatmap]] = defaultdict(list)
    for row in rows:
        cells = [
            HeatmapCell(x=i, y=j, intensity=(row.shots or 0) / 100.0)
            for i in range(3)
            for j in range(3)
        ]
        results[row.weapon_name].append(
            WeaponHeatmap(match_id=row.match_id, weapon_name=row.weapon_name, cells=cells)
        )
    return results


async def compute_rank_comparison(db: AsyncSession, user_id: int, rank: str | None) -> List[RankComparisonMetric]:
    # Fetch overall averages from FACEIT (simplified / illustrative)
    external = await fetch_faceit_rank_averages()

    # Player aggregates (simplified)
    kd_map = await compute_kd_per_map(db, user_id)
    kd_weapon = await compute_kd_per_weapon(db, user_id)
    win_trend = await compute_win_rate_trend(db, user_id)

    player_overall_kd = (
        sum(m.kills for m in kd_map) / max(1, sum(m.deaths for m in kd_map)) if kd_map else 0.0
    )
    player_win_rate = (
        sum(p.wins for p in win_trend) / max(1, sum(p.matches for p in win_trend))
        if win_trend
        else 0.0
    )

    external_kd = float(external.get("avg_kd", 1.0)) if external else 1.0
    external_wr = float(external.get("avg_win_rate", 0.5)) if external else 0.5

    return [
        RankComparisonMetric(
            metric="overall_kd", player_value=player_overall_kd, average_value=external_kd
        ),
        RankComparisonMetric(
            metric="win_rate", player_value=player_win_rate, average_value=external_wr
        ),
    ]


async def compute_full_analytics(
    db: AsyncSession,
    user_id: int,
    rank: str | None,
) -> AnalyticsResponse:
    kd_map, kd_weapon, win_trend, heatmaps, rank_comp = await asyncio.gather(
        compute_kd_per_map(db, user_id),
        compute_kd_per_weapon(db, user_id),
        compute_win_rate_trend(db, user_id),
        compute_weapon_heatmaps(db, user_id),
        compute_rank_comparison(db, user_id, rank),
    )

    return AnalyticsResponse(
        kd_per_map=kd_map,
        kd_per_weapon=kd_weapon,
        win_rate_trend=win_trend,
        weapon_heatmaps=heatmaps,
        rank_comparison=rank_comp,
    )

