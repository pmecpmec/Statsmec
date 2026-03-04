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

