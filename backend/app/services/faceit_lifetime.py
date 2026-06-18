"""
Pure parsing helpers for the FACEIT Data API lifetime/segment payloads.

Kept free of I/O so the transformation logic is unit-testable. The FACEIT
`/players/{id}/stats/{game}` payload uses human-readable string keys with string
values (e.g. "Average K/D Ratio": "1.12"), so everything here is defensive about
types and missing keys.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> Optional[int]:
    f = _to_float(value)
    if f is None:
        return None
    return int(f)


def _round_or_none(value: Optional[float], digits: int = 2) -> Optional[float]:
    if value is None:
        return None
    return round(value, digits)


def _parse_recent_results(raw: Any) -> List[str]:
    """
    FACEIT "Recent Results" is a list like ["1","0","1",...] where 1 == win.
    Ordered oldest → most recent. Return a normalized ["W", "L", ...] list.
    """
    if not isinstance(raw, list):
        return []
    out: List[str] = []
    for item in raw:
        s = str(item).strip()
        if s == "1":
            out.append("W")
        elif s == "0":
            out.append("L")
    return out


def _parse_segments(raw_segments: Any) -> List[Dict[str, Any]]:
    """Per-map breakdown. Keep only map-type segments with a usable label."""
    if not isinstance(raw_segments, list):
        return []
    maps: List[Dict[str, Any]] = []
    for seg in raw_segments:
        if not isinstance(seg, dict):
            continue
        if str(seg.get("type", "")).lower() != "map":
            continue
        label = seg.get("label")
        if not label:
            continue
        stats = seg.get("stats") or {}
        if not isinstance(stats, dict):
            stats = {}
        matches = _to_int(stats.get("Matches")) or 0
        if matches <= 0:
            continue
        maps.append(
            {
                "map": str(label),
                "image": seg.get("img_regular") or seg.get("img_small"),
                "matches": matches,
                "win_rate": _round_or_none(_to_float(stats.get("Win Rate %")), 1),
                "kd": _round_or_none(_to_float(stats.get("Average K/D Ratio")), 2),
                "hs_pct": _round_or_none(
                    _to_float(stats.get("Average Headshots %")), 1
                ),
            }
        )
    maps.sort(key=lambda m: m["matches"], reverse=True)
    return maps


def _parse_bans(raw_bans: Any) -> List[Dict[str, Any]]:
    if not isinstance(raw_bans, dict):
        return []
    items = raw_bans.get("items")
    if not isinstance(items, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "reason": item.get("reason") or item.get("type"),
                "game": item.get("game"),
                "starts_at": item.get("starts_at"),
                "ends_at": item.get("ends_at"),
            }
        )
    return out


def parse_faceit_lifetime(
    stats_payload: Optional[Dict[str, Any]],
    bans_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Transform raw FACEIT stats + bans payloads into the clean shape served by the API.

    Always returns a dict with `available` set; never raises on malformed input.
    """
    if not isinstance(stats_payload, dict):
        return {
            "available": False,
            "matches": 0,
            "wins": 0,
            "win_rate": None,
            "avg_kd": None,
            "avg_hs_pct": None,
            "current_win_streak": None,
            "longest_win_streak": None,
            "recent_results": [],
            "segments": [],
            "bans": _parse_bans(bans_payload),
        }

    lifetime = stats_payload.get("lifetime") or {}
    if not isinstance(lifetime, dict):
        lifetime = {}

    matches = _to_int(lifetime.get("Matches")) or 0
    wins = _to_int(lifetime.get("Wins")) or 0

    return {
        "available": matches > 0,
        "matches": matches,
        "wins": wins,
        "win_rate": _round_or_none(_to_float(lifetime.get("Win Rate %")), 1),
        "avg_kd": _round_or_none(_to_float(lifetime.get("Average K/D Ratio")), 2),
        "avg_hs_pct": _round_or_none(
            _to_float(lifetime.get("Average Headshots %")), 1
        ),
        "current_win_streak": _to_int(lifetime.get("Current Win Streak")),
        "longest_win_streak": _to_int(lifetime.get("Longest Win Streak")),
        "recent_results": _parse_recent_results(lifetime.get("Recent Results")),
        "segments": _parse_segments(stats_payload.get("segments")),
        "bans": _parse_bans(bans_payload),
    }
