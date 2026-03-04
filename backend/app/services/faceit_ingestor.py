"""
Ingest FACEIT Data API responses into our Match / Round / WeaponStat models.
Uses official FACEIT endpoints: history, match details, match stats.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match import Match, Round, WeaponStat
from app.services.external_clients import (
    fetch_faceit_match_details,
    fetch_faceit_match_stats,
)


def _parse_ts(value: Any) -> Optional[datetime]:
    """FACEIT uses Unix seconds (or ms). Return timezone-aware UTC datetime."""
    if value is None:
        return None
    try:
        ts = int(value)
    except (TypeError, ValueError):
        return None
    if ts >= 1e12:
        ts = ts / 1000.0
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def _int_or_zero(value: Any) -> int:
    try:
        return int(value) if value is not None else 0
    except (TypeError, ValueError):
        return 0


def _score_from_results(results: Optional[Dict[str, Any]]) -> tuple[Optional[int], Optional[int]]:
    """Extract (team_score, opponent_score) from FACEIT results.score (team_id -> score)."""
    if not results or not isinstance(results.get("score"), dict):
        return None, None
    scores = list((results["score"] or {}).values())
    if len(scores) >= 2:
        return int(scores[0]), int(scores[1])
    if len(scores) == 1:
        return int(scores[0]), None
    return None, None


async def upsert_faceit_matches(
    db: AsyncSession,
    user_id: int,
    faceit_id: str,
    history_payload: Dict[str, Any],
) -> int:
    """
    For each match in FACEIT history, fetch details + stats from the API and upsert
    Match, Round, WeaponStat. Returns number of matches processed.
    Uses official FACEIT Data API only (quick and accurate).
    """
    items = history_payload.get("items") or []
    count = 0
    for item in items:
        external_id = str(item.get("match_id") or "")
        if not external_id:
            continue

        details = await fetch_faceit_match_details(external_id)
        if not details:
            continue

        started_at = _parse_ts(details.get("started_at") or details.get("finished_at"))
        if not started_at:
            continue

        finished_at = _parse_ts(details.get("finished_at"))
        duration_seconds = None
        if started_at and finished_at:
            duration_seconds = int((finished_at - started_at).total_seconds())

        results = details.get("results") or {}
        score_team, score_opponent = _score_from_results(results)
        winner = (results.get("winner") or "").strip() or None

        # Map name: FACEIT match details may have voting.map or game map in instances
        map_name = None
        voting = details.get("voting") or {}
        if isinstance(voting.get("map"), dict):
            map_name = voting["map"].get("pick") or voting["map"].get("map")
        if not map_name and isinstance(voting.get("map"), str):
            map_name = voting["map"]
        if not map_name:
            map_name = (details.get("competition_name") or "").strip() or None

        existing = await db.execute(select(Match).where(Match.external_match_id == external_id))
        match = existing.scalar_one_or_none()

        if match is None:
            match = Match(
                external_match_id=external_id,
                user_id=user_id,
                provider="faceit",
                map_name=map_name,
                started_at=started_at,
                duration_seconds=duration_seconds,
                score_team=score_team,
                score_opponent=score_opponent,
                result=winner,
            )
            db.add(match)
            await db.flush()
        else:
            match.map_name = map_name
            match.started_at = started_at
            match.duration_seconds = duration_seconds
            match.score_team = score_team
            match.score_opponent = score_opponent
            match.result = winner
            # Replace round data: delete existing (cascade deletes weapon_stats)
            for r in list(match.rounds):
                await db.delete(r)
            await db.flush()

        stats_payload = await fetch_faceit_match_stats(external_id)
        if stats_payload and isinstance(stats_payload.get("rounds"), list):
            for r in stats_payload["rounds"]:
                round_number = _int_or_zero(r.get("match_round"))
                if round_number < 1:
                    continue
                teams = r.get("teams") or []
                # Find our player in this round (any team)
                our_kills, our_deaths, our_weapon = None, None, None
                our_player_stats: Dict[str, Any] = {}
                for team in teams:
                    if not isinstance(team, dict):
                        continue
                    for player in team.get("players") or []:
                        if not isinstance(player, dict):
                            continue
                        if str(player.get("player_id") or "") == str(faceit_id):
                            our_player_stats = player.get("player_stats") or {}
                            our_kills = _int_or_zero(our_player_stats.get("Kills")) or None
                            our_deaths = _int_or_zero(our_player_stats.get("Deaths")) or None
                            our_weapon = (our_player_stats.get("Weapon") or our_player_stats.get("Most used weapon") or "").strip() or None
                            break
                    if our_player_stats:
                        break

                round_row = Round(
                    match_id=match.id,
                    round_number=round_number,
                    winning_team=(r.get("round_stats") or {}).get("Winner") if isinstance(r.get("round_stats"), dict) else None,
                    kills=our_kills,
                    deaths=our_deaths,
                    weapon_used=our_weapon,
                )
                db.add(round_row)
                await db.flush()

                # One WeaponStat per round when we have our player's stats (FACEIT uses Kills/Headshots etc.)
                if our_player_stats:
                    weapon_name = our_weapon or "Unknown"
                    shots = _int_or_zero(our_player_stats.get("Shots") or our_player_stats.get("Rounds with kills") or 1)
                    hits = _int_or_zero(our_player_stats.get("Kills") or our_player_stats.get("Hits"))
                    headshots = _int_or_zero(our_player_stats.get("Headshots"))
                    if shots < hits:
                        shots = max(shots, hits)
                    db.add(WeaponStat(round_id=round_row.id, weapon_name=weapon_name, shots=shots, hits=hits, headshots=headshots))

        count += 1

    return count
