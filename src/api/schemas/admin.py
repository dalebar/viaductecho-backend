"""
Pydantic schemas for Admin API
"""

from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel, Field


class VenueCreate(BaseModel):
    """Schema for creating a venue"""

    name: str = Field(..., description="Venue name")
    address_line1: Optional[str] = Field(None, description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    town: Optional[str] = Field(None, description="Town/city")
    postcode: Optional[str] = Field(None, description="Postcode")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    description: Optional[str] = Field(None, description="Venue description")
    venue_type: Optional[str] = Field(None, description="Venue type")
    capacity: Optional[int] = Field(None, description="Venue capacity")
    website_url: Optional[str] = Field(None, description="Website URL")
    phone: Optional[str] = Field(None, description="Phone number")
    image_url: Optional[str] = Field(None, description="Venue image URL")


class VenueUpdate(BaseModel):
    """Schema for updating a venue"""

    name: Optional[str] = Field(None, description="Venue name")
    address_line1: Optional[str] = Field(None, description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    town: Optional[str] = Field(None, description="Town/city")
    postcode: Optional[str] = Field(None, description="Postcode")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    description: Optional[str] = Field(None, description="Venue description")
    venue_type: Optional[str] = Field(None, description="Venue type")
    capacity: Optional[int] = Field(None, description="Venue capacity")
    website_url: Optional[str] = Field(None, description="Website URL")
    phone: Optional[str] = Field(None, description="Phone number")
    image_url: Optional[str] = Field(None, description="Venue image URL")


class EventCreate(BaseModel):
    """Schema for creating an event"""

    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Full description")
    short_description: Optional[str] = Field(None, description="Short description")
    event_type: str = Field(..., description="Event category")
    start_datetime: datetime = Field(..., description="Event start date/time")
    end_datetime: Optional[datetime] = Field(None, description="Event end date/time")
    doors_time: Optional[time] = Field(None, description="Doors open time")
    venue_id: int = Field(..., description="Venue ID")
    image_url: Optional[str] = Field(None, description="Event image URL")
    ticket_url: Optional[str] = Field(None, description="Ticket purchase URL")
    price_min: Optional[float] = Field(None, description="Minimum ticket price")
    price_max: Optional[float] = Field(None, description="Maximum ticket price")
    is_free: bool = Field(False, description="Whether event is free")
    is_featured: bool = Field(False, description="Whether event is featured")


class EventUpdate(BaseModel):
    """Schema for updating an event"""

    title: Optional[str] = Field(None, description="Event title")
    description: Optional[str] = Field(None, description="Full description")
    short_description: Optional[str] = Field(None, description="Short description")
    event_type: Optional[str] = Field(None, description="Event category")
    start_datetime: Optional[datetime] = Field(
        None, description="Event start date/time"
    )
    end_datetime: Optional[datetime] = Field(None, description="Event end date/time")
    doors_time: Optional[time] = Field(None, description="Doors open time")
    venue_id: Optional[int] = Field(None, description="Venue ID")
    image_url: Optional[str] = Field(None, description="Event image URL")
    ticket_url: Optional[str] = Field(None, description="Ticket purchase URL")
    price_min: Optional[float] = Field(None, description="Minimum ticket price")
    price_max: Optional[float] = Field(None, description="Maximum ticket price")
    is_free: Optional[bool] = Field(None, description="Whether event is free")
    is_featured: Optional[bool] = Field(None, description="Whether event is featured")
    status: Optional[str] = Field(None, description="Event status")


class AggregationStats(BaseModel):
    """Response from aggregation job"""

    total_fetched: int = Field(..., description="Total events fetched from sources")
    total_inserted: int = Field(..., description="Total events inserted")
    total_duplicates: int = Field(..., description="Total duplicates/skipped")
    total_errors: int = Field(..., description="Total errors")
    past_events_marked: int = Field(..., description="Past events marked")


class AggregationResponse(BaseModel):
    """Aggregation job response"""

    success: bool = Field(..., description="Whether job completed successfully")
    message: str = Field(..., description="Job status message")
    stats: Optional[AggregationStats] = Field(
        None, description="Aggregation statistics"
    )
