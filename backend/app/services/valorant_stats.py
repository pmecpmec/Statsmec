"""
Aggregate real Valorant per-match stats for a single player (PUUID).

`val/match/v1` returns one big object per match; this module turns a batch of
those into a compact per-match list plus summary numbers (ACS, K/D, win rate,
top agents) that the frontend can render directly.

The heavy lifting (`summarize_player_matches`) is a pure function so it can be
unit-tested without hitting Riot. The async helpers wrap the network calls and a
small in-memory cache for val-content-v1 (agent / map name lookups).
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from app.services.external_clients import (
    fetch_valorant_content,
    fetch_valorant_match,
)

# How many recent matches to pull full details for. val/match/v1 is rate-limited
# tightly, so keep this small.
DEFAULT_MATCH_DETAIL_COUNT = 5

# val-content-v1 changes rarely; cache the derived name maps for a while.
_CONTENT_TTL_SECONDS = 60 * 60
_content_cache: tuple[float, dict[str, str], dict[str, str]] | None = None


def _name_maps_from_content(content: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    """
    Build (map_path_or_id -> map name, agent_id -> agent name) from a
    val-content-v1 payload. Keys are lower-cased so match-v1 ids (lowercase
    uuids / asset paths) match regardless of Riot's casing.
    """
    map_names: dict[str, str] = {}
    for m in content.get("maps") or []:
        name = m.get("name")
        if not name:
            continue
        for key in (m.get("assetPath"), m.get("id"), m.get("assetName")):
            if key:
                map_names[str(key).lower()] = str(name)

    agent_names: dict[str, str] = {}
    for c in content.get("characters") or []:
        name = c.get("name")
        cid = c.get("id")
        if name and cid:
            agent_names[str(cid).lower()] = str(name)

    return map_names, agent_names


async def get_content_name_maps() -> tuple[dict[str, str], dict[str, str]]:
    """Cached (map_names, agent_names). Returns empty maps if content is unavailable."""
    global _content_cache
    now = time.monotonic()
    if _content_cache and (now - _content_cache[0]) < _CONTENT_TTL_SECONDS:
        return _content_cache[1], _content_cache[2]

    try:
        content = await fetch_valorant_content("en-US")
    except Exception:
        # Fall back to whatever we cached before, else empty maps.
        if _content_cache:
            return _content_cache[1], _content_cache[2]
        return {}, {}

    map_names, agent_names = _name_maps_from_content(content)
    _content_cache = (now, map_names, agent_names)
    return map_names, agent_names


def _map_label(map_id: str | None, map_names: dict[str, str]) -> str:
    if not map_id:
        return "Unknown"
    key = str(map_id).lower()
    if key in map_names:
        return map_names[key]
    # mapId is usually an asset path like "/Game/Maps/Ascent/Ascent"; take the leaf.
    leaf = str(map_id).rstrip("/").rsplit("/", 1)[-1]
    return leaf or "Unknown"


def _agent_label(agent_id: str | None, agent_names: dict[str, str]) -> str:
    if not agent_id:
        return "Unknown"
    return agent_names.get(str(agent_id).lower(), "Unknown")


def summarize_player_matches(
    puuid: str,
    matches: list[dict[str, Any]],
    *,
    map_names: dict[str, str] | None = None,
    agent_names: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Reduce raw val/match/v1 match objects to one player's per-match rows + summary.

    Pure: no network. `matches` may contain None / malformed entries; they are
    skipped. Matches where the player's PUUID is absent are ignored.
    """
    map_names = map_names or {}
    agent_names = agent_names or {}

    per_match: list[dict[str, Any]] = []
    total_kills = total_deaths = total_assists = 0
    total_score = total_rounds = 0
    wins = 0
    # agent name -> running tally
    agents: dict[str, dict[str, Any]] = {}

    for match in matches:
        if not isinstance(match, dict):
            continue
        info = match.get("matchInfo") or {}
        players = match.get("players") or []
        teams = match.get("teams") or []

        me = next((p for p in players if p.get("puuid") == puuid), None)
        if not me:
            continue

        stats = me.get("stats") or {}
        kills = int(stats.get("kills") or 0)
        deaths = int(stats.get("deaths") or 0)
        assists = int(stats.get("assists") or 0)
        score = int(stats.get("score") or 0)
        rounds = int(stats.get("roundsPlayed") or 0)

        team_id = me.get("teamId")
        my_team = next((t for t in teams if t.get("teamId") == team_id), None)
        won = bool(my_team.get("won")) if my_team else False
        my_rounds = int((my_team or {}).get("roundsWon") or 0)
        opp_rounds = max(
            (int(t.get("roundsWon") or 0) for t in teams if t.get("teamId") != team_id),
            default=0,
        )

        acs = round(score / rounds) if rounds else 0
        agent = _agent_label(me.get("characterId"), agent_names)

        per_match.append(
            {
                "match_id": info.get("matchId"),
                "map": _map_label(info.get("mapId"), map_names),
                "agent": agent,
                "kills": kills,
                "deaths": deaths,
                "assists": assists,
                "acs": acs,
                "kd": round(kills / deaths, 2) if deaths else float(kills),
                "score": f"{my_rounds}-{opp_rounds}",
                "won": won,
                "queue": info.get("queueId") or None,
                "started_at": info.get("gameStartMillis"),
            }
        )

        total_kills += kills
        total_deaths += deaths
        total_assists += assists
        total_score += score
        total_rounds += rounds
        if won:
            wins += 1

        bucket = agents.setdefault(
            agent, {"name": agent, "games": 0, "wins": 0, "kills": 0, "deaths": 0}
        )
        bucket["games"] += 1
        bucket["wins"] += 1 if won else 0
        bucket["kills"] += kills
        bucket["deaths"] += deaths

    played = len(per_match)
    top_agents = sorted(agents.values(), key=lambda a: a["games"], reverse=True)
    for a in top_agents:
        a["kd"] = round(a["kills"] / a["deaths"], 2) if a["deaths"] else float(a["kills"])
        a["win_rate"] = round((a["wins"] / a["games"]) * 100, 1) if a["games"] else 0.0

    summary = {
        "matches": played,
        "wins": wins,
        "losses": played - wins,
        "win_rate": round((wins / played) * 100, 1) if played else 0.0,
        "kd": round(total_kills / total_deaths, 2) if total_deaths else float(total_kills),
        "acs": round(total_score / total_rounds) if total_rounds else 0,
        "kills": total_kills,
        "deaths": total_deaths,
        "assists": total_assists,
        "top_agents": top_agents[:3],
    }

    return {"summary": summary, "matches": per_match}


async def build_player_valorant_stats(
    puuid: str,
    match_ids: list[str],
    *,
    limit: int = DEFAULT_MATCH_DETAIL_COUNT,
) -> dict[str, Any]:
    """
    Fetch up to `limit` match details concurrently and summarize them for `puuid`.
    Network failures on individual matches are swallowed so partial data still renders.
    """
    selected = [mid for mid in match_ids if mid][:limit]
    if not selected:
        return {"summary": summarize_player_matches(puuid, [])["summary"], "matches": []}

    map_names, agent_names = await get_content_name_maps()

    async def _safe(mid: str) -> dict[str, Any] | None:
        try:
            return await fetch_valorant_match(mid)
        except Exception:
            return None

    results = await asyncio.gather(*(_safe(mid) for mid in selected))
    matches = [r for r in results if isinstance(r, dict)]
    return summarize_player_matches(
        puuid, matches, map_names=map_names, agent_names=agent_names
    )
