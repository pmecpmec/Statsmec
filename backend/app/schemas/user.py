from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    steam_id: str | None = None
    faceit_id: str | None = None
    nickname: str | None = None
    rank: str | None = None
    avatar_url: str | None = None


class UserCreate(UserBase):
    steam_id: str | None = None
    faceit_id: str | None = None


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class MatchSummary(BaseModel):
    id: int
    external_match_id: str
    provider: str
    map_name: str | None
    started_at: datetime
    duration_seconds: int | None
    score_team: int | None
    score_opponent: int | None
    result: str | None

    class Config:
        from_attributes = True

