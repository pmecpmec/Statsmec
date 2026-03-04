"""
Ingest FACEIT Data API responses into our Match / Round / WeaponStat / MatchPlayer models.
Pulls ALL 10 players per match for full scoreboard data.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match import Match, MatchPlayer, Round, WeaponStat
from app.services.external_clients import (
    fetch_faceit_match_details,
    fetch_faceit_match_stats,
)

log = logging.getLogger(__name__)


def _parse_ts(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    try:
        ts = int(value)
    except (TypeError, ValueError):
        return None
    if ts >= 1e12:
        ts = ts / 1000.0
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _find_pmec_team(details: Dict[str, Any], faceit_player_id: str) -> Optional[str]:
    """Figure out which FACEIT team (faction1/faction2) pmec is on."""
    for faction in ("faction1", "faction2"):
        team = (details.get("teams") or {}).get(faction) or {}
        roster = team.get("roster") or team.get("roster_v1") or []
        for player in roster:
            if isinstance(player, dict) and str(player.get("player_id", "")) == faceit_player_id:
                return faction
    return None


def _determine_result(details: Dict[str, Any], pmec_faction: Optional[str]) -> tuple[Optional[int], Optional[int], Optional[str]]:
    """Return (score_team, score_opponent, result) from pmec's perspective."""
    results = details.get("results") or {}
    winner_faction = (results.get("winner") or "").strip() or None
    scores = results.get("score") or {}

    if not pmec_faction:
        s = list(scores.values())
        return (_int(s[0]) if len(s) > 0 else None, _int(s[1]) if len(s) > 1 else None, None)

    other_faction = "faction2" if pmec_faction == "faction1" else "faction1"
    score_team = _int(scores.get(pmec_faction))
    score_opponent = _int(scores.get(other_faction))

    if winner_faction == pmec_faction:
        result = "win"
    elif winner_faction:
        result = "loss"
    else:
        result = None

    return score_team, score_opponent, result


def _extract_map(details: Dict[str, Any]) -> Optional[str]:
    voting = details.get("voting") or {}
    if isinstance(voting.get("map"), dict):
        return voting["map"].get("pick") or voting["map"].get("map")
    if isinstance(voting.get("map"), str):
        return voting["map"]
    return None


def _extract_all_players_from_stats(
    stats_payload: Dict[str, Any],
    faceit_player_id: str,
) -> List[Dict[str, Any]]:
    """
    Extract per-player aggregated stats from the FACEIT match stats response.
    The FACEIT stats response has rounds[].teams[].players[].player_stats.
    We aggregate across all rounds to get totals per player.
    """
    player_map: Dict[str, Dict[str, Any]] = {}

    rounds_data = stats_payload.get("rounds") or []
    for rnd in rounds_data:
        round_stats = rnd.get("round_stats") or {}
        teams = rnd.get("teams") or []

        for team in teams:
            if not isinstance(team, dict):
                continue
            team_id = team.get("team_id", "")
            team_stats = team.get("team_stats") or {}
            team_name = team_stats.get("Team") or team.get("team_id", "")

            for player in team.get("players") or []:
                if not isinstance(player, dict):
                    continue
                pid = str(player.get("player_id", ""))
                ps = player.get("player_stats") or {}

                if pid not in player_map:
                    player_map[pid] = {
                        "player_id": pid,
                        "nickname": player.get("nickname", "Unknown"),
                        "team_id": team_id,
                        "team_name": team_name,
                        "is_self": pid == faceit_player_id,
                        "kills": 0,
                        "deaths": 0,
                        "assists": 0,
                        "headshots": 0,
                        "adr": 0.0,
                        "kr": 0.0,
                        "rounds_counted": 0,
                    }

                p = player_map[pid]
                p["kills"] += _int(ps.get("Kills"))
                p["deaths"] += _int(ps.get("Deaths"))
                p["assists"] += _int(ps.get("Assists"))
                p["headshots"] += _int(ps.get("Headshots"))
                p["rounds_counted"] += 1

                adr_val = _float(ps.get("ADR") or ps.get("Average Damage per Round"))
                if adr_val > 0:
                    p["adr"] = adr_val

                kr_val = _float(ps.get("K/R Ratio") or ps.get("KR"))
                if kr_val > 0:
                    p["kr"] = kr_val

    return list(player_map.values())


async def upsert_faceit_matches(
    db: AsyncSession,
    user_id: int,
    faceit_player_id: str,
    history_payload: Dict[str, Any],
) -> int:
    """
    For each match in FACEIT history, fetch details + stats and upsert
    Match, MatchPlayer, Round, WeaponStat. Returns matches processed.
    """
    items = history_payload.get("items") or []
    count = 0

    for item in items:
        external_id = str(item.get("match_id") or "")
        if not external_id:
            continue

        try:
            details = await fetch_faceit_match_details(external_id)
        except Exception as e:
            log.warning("Failed to fetch details for %s: %s", external_id, e)
            continue
        if not details:
            continue

        started_at = _parse_ts(details.get("started_at") or details.get("finished_at"))
        if not started_at:
            continue

        finished_at = _parse_ts(details.get("finished_at"))
        duration_seconds = None
        if started_at and finished_at:
            duration_seconds = int((finished_at - started_at).total_seconds())

        map_name = _extract_map(details)
        pmec_faction = _find_pmec_team(details, faceit_player_id)
        score_team, score_opponent, result = _determine_result(details, pmec_faction)

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
                result=result,
            )
            db.add(match)
            await db.flush()
        else:
            match.map_name = map_name
            match.started_at = started_at
            match.duration_seconds = duration_seconds
            match.score_team = score_team
            match.score_opponent = score_opponent
            match.result = result
            for r in list(match.rounds):
                await db.delete(r)
            for p in list(match.players):
                await db.delete(p)
            await db.flush()

        # Fetch match stats (all players, all rounds)
        try:
            stats_payload = await fetch_faceit_match_stats(external_id)
        except Exception as e:
            log.warning("Failed to fetch stats for %s: %s", external_id, e)
            stats_payload = None

        if stats_payload:
            all_players = _extract_all_players_from_stats(stats_payload, faceit_player_id)

            pmec_team_id = None
            for p in all_players:
                if p["is_self"]:
                    pmec_team_id = p["team_id"]
                    break

            for p in all_players:
                if pmec_team_id:
                    team_label = "CT" if p["team_id"] == pmec_team_id else "T"
                else:
                    team_label = "CT"

                kills = p["kills"]
                deaths = max(1, p["deaths"])
                hs_pct = (p["headshots"] / max(1, kills)) * 100 if kills > 0 else 0
                kd = kills / deaths
                rating = round(0.5 + kd * 0.3 + p.get("kr", 0) * 1.5, 2)
                rating = max(0.3, min(2.5, rating))

                db.add(MatchPlayer(
                    match_id=match.id,
                    player_name=p["nickname"],
                    team=team_label,
                    is_self=p["is_self"],
                    kills=kills,
                    deaths=p["deaths"],
                    assists=p["assists"],
                    adr=p["adr"],
                    headshot_pct=round(hs_pct, 1),
                    rating=rating,
                ))

            # Extract round-by-round data for pmec
            rounds_data = stats_payload.get("rounds") or []
            for rnd in rounds_data:
                round_number = _int(rnd.get("match_round"))
                if round_number < 1:
                    continue
                round_stats = rnd.get("round_stats") or {}

                our_kills, our_deaths, our_weapon = None, None, None
                our_ps: Dict[str, Any] = {}
                for team in rnd.get("teams") or []:
                    if not isinstance(team, dict):
                        continue
                    for player in team.get("players") or []:
                        if not isinstance(player, dict):
                            continue
                        if str(player.get("player_id", "")) == faceit_player_id:
                            our_ps = player.get("player_stats") or {}
                            our_kills = _int(our_ps.get("Kills")) or None
                            our_deaths = _int(our_ps.get("Deaths")) or None
                            our_weapon = (our_ps.get("Weapon") or "").strip() or None
                            break
                    if our_ps:
                        break

                round_row = Round(
                    match_id=match.id,
                    round_number=round_number,
                    winning_team=round_stats.get("Winner") if isinstance(round_stats, dict) else None,
                    kills=our_kills,
                    deaths=our_deaths,
                    weapon_used=our_weapon,
                )
                db.add(round_row)
                await db.flush()

                if our_ps:
                    weapon_name = our_weapon or "Unknown"
                    shots = _int(our_ps.get("Shots") or 1)
                    hits = _int(our_ps.get("Kills"))
                    headshots = _int(our_ps.get("Headshots"))
                    if shots < hits:
                        shots = max(shots, hits)
                    db.add(WeaponStat(
                        round_id=round_row.id,
                        weapon_name=weapon_name,
                        shots=shots,
                        hits=hits,
                        headshots=headshots,
                    ))

        count += 1

    return count
