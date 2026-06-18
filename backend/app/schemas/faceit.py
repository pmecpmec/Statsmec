from __future__ import annotations

from pydantic import BaseModel, Field


class FaceitMapSegment(BaseModel):
    map: str
    image: str | None = None
    matches: int = 0
    win_rate: float | None = None
    kd: float | None = None
    hs_pct: float | None = None


class FaceitBan(BaseModel):
    reason: str | None = None
    game: str | None = None
    starts_at: str | None = None
    ends_at: str | None = None


class FaceitLifetimeStats(BaseModel):
    """Clean lifetime FACEIT stats for pmec, served by /me/faceit-lifetime."""

    available: bool = False
    api_configured: bool = False
    matches: int = 0
    wins: int = 0
    win_rate: float | None = None
    avg_kd: float | None = None
    avg_hs_pct: float | None = None
    current_win_streak: int | None = None
    longest_win_streak: int | None = None
    recent_results: list[str] = Field(default_factory=list)
    segments: list[FaceitMapSegment] = Field(default_factory=list)
    bans: list[FaceitBan] = Field(default_factory=list)
    error: str | None = None
