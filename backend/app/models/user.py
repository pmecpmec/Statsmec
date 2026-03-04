from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    steam_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    faceit_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    nickname: Mapped[str | None] = mapped_column(String(128))
    rank: Mapped[str | None] = mapped_column(String(64), index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(256))

    matches: Mapped[list["Match"]] = relationship(back_populates="user")

