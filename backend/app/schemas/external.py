from __future__ import annotations

from pydantic import BaseModel, Field


class ScrapeSource(BaseModel):
    """
    A single best-effort scraped source. `available` is the honesty flag: when
    False the UI must show a "couldn't fetch" state instead of any numbers.
    """

    available: bool = False
    source: str
    url: str | None = None
    method: str | None = None
    status: str | None = None
    stats: dict[str, str | float | int | None] = Field(default_factory=dict)


class ExternalStatsResponse(BaseModel):
    csstats: ScrapeSource
    esea: ScrapeSource
