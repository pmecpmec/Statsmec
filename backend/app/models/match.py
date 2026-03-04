from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Match(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    external_match_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    provider: Mapped[str] = mapped_column(String(16), index=True)  # steam / faceit
    map_name: Mapped[str | None] = mapped_column(String(64), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    score_team: Mapped[int | None] = mapped_column(Integer)
    score_opponent: Mapped[int | None] = mapped_column(Integer)
    result: Mapped[str | None] = mapped_column(String(16), index=True)  # win / loss / draw

    user = relationship("User", back_populates="matches")
    rounds: Mapped[list["Round"]] = relationship(back_populates="match", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_match_user_started_at", "user_id", "started_at"),
    )


class Round(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("match.id"), index=True)
    round_number: Mapped[int] = mapped_column(Integer, index=True)
    winning_team: Mapped[str | None] = mapped_column(String(16))
    kills: Mapped[int | None] = mapped_column(Integer)
    deaths: Mapped[int | None] = mapped_column(Integer)
    weapon_used: Mapped[str | None] = mapped_column(String(64), index=True)

    match = relationship("Match", back_populates="rounds")
    weapon_stats: Mapped[list["WeaponStat"]] = relationship(
        back_populates="round", cascade="all, delete-orphan"
    )


class WeaponStat(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    round_id: Mapped[int] = mapped_column(ForeignKey("round.id"), index=True)
    weapon_name: Mapped[str] = mapped_column(String(64), index=True)
    shots: Mapped[int] = mapped_column(Integer)
    hits: Mapped[int] = mapped_column(Integer)
    headshots: Mapped[int] = mapped_column(Integer)

    round = relationship("Round", back_populates="weapon_stats")

