"""
Pydantic schemas for Events API
"""

from datetime import datetime, time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .venues import VenueSummary


class EventBase(BaseModel):
    """Base event schema"""

    title: str = Field(..., description="Event title")
    slug: str = Field(..., description="URL-friendly slug")
    event_type: str = Field(..., description="Event category")
    start_datetime: datetime = Field(..., description="Event start date/time")

    @field_serializer("start_datetime")
    def serialize_start_datetime(self, value: datetime) -> str:
        return value.isoformat()


class EventSummary(EventBase):
    """Event summary for list views"""

    id: int = Field(..., description="Event ID")
    venue: Optional[VenueSummary] = Field(None, description="Venue summary")
    image_url: Optional[str] = Field(None, description="Event image URL")
    price_min: Optional[float] = Field(None, description="Minimum ticket price")
    price_max: Optional[float] = Field(None, description="Maximum ticket price")
    is_free: bool = Field(False, description="Whether event is free")
    ticket_url: Optional[str] = Field(None, description="Ticket purchase URL")

    model_config = ConfigDict(from_attributes=True)


class EventDetail(EventBase):
    """Full event details"""

    id: int = Field(..., description="Event ID")
    description: Optional[str] = Field(None, description="Full description")
    short_description: Optional[str] = Field(None, description="Short description")
    end_datetime: Optional[datetime] = Field(None, description="Event end date/time")
    doors_time: Optional[time] = Field(None, description="Doors open time")
    venue: Optional[VenueSummary] = Field(None, description="Venue details")
    image_url: Optional[str] = Field(None, description="Event image URL")
    ticket_url: Optional[str] = Field(None, description="Ticket purchase URL")
    price_min: Optional[float] = Field(None, description="Minimum ticket price")
    price_max: Optional[float] = Field(None, description="Maximum ticket price")
    is_free: bool = Field(False, description="Whether event is free")
    source_name: str = Field(..., description="Data source")
    source_url: Optional[str] = Field(None, description="Original listing URL")
    status: str = Field(..., description="Event status")
    is_featured: bool = Field(False, description="Whether event is featured")
    created_at: datetime = Field(..., description="Record creation time")

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("end_datetime")
    def serialize_end_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None

    @field_serializer("doors_time")
    def serialize_doors_time(self, value: Optional[time]) -> Optional[str]:
        return str(value) if value else None

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return value.isoformat()


class PaginatedEvents(BaseModel):
    """Paginated events response"""

    events: List[EventSummary] = Field(..., description="List of events")
    pagination: "PaginationInfo" = Field(..., description="Pagination info")


class CalendarResponse(BaseModel):
    """Calendar data response"""

    calendar: dict = Field(..., description="Event counts by date (YYYY-MM-DD: count)")
    generated_at: Optional[str] = Field(None, description="Data generation timestamp")


class EventTypesResponse(BaseModel):
    """Available event types"""

    event_types: List[str] = Field(..., description="List of event types")


# Import here to avoid circular imports
from .articles import PaginationInfo  # noqa: E402

PaginatedEvents.model_rebuild()
