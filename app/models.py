from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class RunStatus(str, Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"


class SellerType(str, Enum):
    private = "private"
    agency = "agency"
    unknown = "unknown"


class Portal(SQLModel, table=True):
    """One search URL per row; global scrape/LLM options live in AppSetting (Config)."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    search_url: str
    """Listing search URL scraped when this portal is processed (runs iterate portals in id order)."""
    enabled: bool = Field(default=True)


class ScrapeRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    portal_id: Optional[int] = Field(default=None, foreign_key="portal.id")
    status: str = Field(default=RunStatus.pending.value, index=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    csv_path: Optional[str] = None
    new_listings: int = Field(default=0)
    updated_listings: int = Field(default=0)
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    llm_response_snippet: Optional[str] = Field(default=None, sa_column=Column(Text))
    """Truncated raw assistant message from the listing-extraction LLM call(s)."""


class Listing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    portal_id: int = Field(foreign_key="portal.id", index=True)
    canonical_url: str = Field(index=True, unique=True)
    title: Optional[str] = None
    price_raw: Optional[str] = None
    m2: Optional[str] = None
    phone: Optional[str] = None
    seller_type: str = Field(default=SellerType.unknown.value)
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    last_run_id: Optional[int] = Field(default=None, foreign_key="scraperun.id")
    raw_json: Optional[str] = Field(default=None, sa_column=Column(Text))


class BlacklistEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pattern: str = Field(index=True)
    """Exact canonical URL or prefix to match."""
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class AppSetting(SQLModel, table=True):
    """Key-value settings (LLM, schedule, prompts)."""
    key: str = Field(primary_key=True)
    value: str = Field(sa_column=Column(Text))
