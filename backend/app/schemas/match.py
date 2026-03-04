from __future__ import annotations

from typing import List

from pydantic import BaseModel


class WeaponStatDetail(BaseModel):
    weapon_name: str
    shots: int
    hits: int
    headshots: int


class RoundDetail(BaseModel):
    id: int
    match_id: int
    round_number: int
    winning_team: str | None
    kills: int | None
    deaths: int | None
    weapon_used: str | None
    weapon_stats: List[WeaponStatDetail] = []

    class Config:
        from_attributes = True


class PlayerScore(BaseModel):
    player_name: str
    team: str
    is_self: bool
    kills: int
    deaths: int
    assists: int
    adr: float
    headshot_pct: float
    rating: float

    class Config:
        from_attributes = True


class Scoreboard(BaseModel):
    match_id: int
    map_name: str | None
    score_team: int | None
    score_opponent: int | None
    result: str | None
    ct: List[PlayerScore] = []
    t: List[PlayerScore] = []

