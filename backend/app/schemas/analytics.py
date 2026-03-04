from datetime import date
from typing import Dict, List

from pydantic import BaseModel


class KDPerMap(BaseModel):
    map_name: str
    kills: int
    deaths: int

    @property
    def kd_ratio(self) -> float:
        return self.kills / self.deaths if self.deaths else float(self.kills)


class KDPerWeapon(BaseModel):
    weapon_name: str
    kills: int
    deaths: int

    @property
    def kd_ratio(self) -> float:
        return self.kills / self.deaths if self.deaths else float(self.kills)


class WinRatePoint(BaseModel):
    date: date
    matches: int
    wins: int
    losses: int

    @property
    def win_rate(self) -> float:
        return self.wins / self.matches if self.matches else 0.0


class HeatmapCell(BaseModel):
    x: int
    y: int
    intensity: float


class WeaponHeatmap(BaseModel):
    match_id: int
    weapon_name: str
    cells: List[HeatmapCell]


class RankComparisonMetric(BaseModel):
    metric: str
    player_value: float
    average_value: float


class AnalyticsResponse(BaseModel):
    kd_per_map: List[KDPerMap]
    kd_per_weapon: List[KDPerWeapon]
    win_rate_trend: List[WinRatePoint]
    weapon_heatmaps: Dict[str, List[WeaponHeatmap]]
    rank_comparison: List[RankComparisonMetric]

