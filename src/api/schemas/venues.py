"""
Pydantic schemas for Venues API
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class VenueBase(BaseModel):
    """Base venue schema"""

    name: str = Field(..., description="Venue name")
    slug: str = Field(..., description="URL-friendly slug")


class VenueSummary(VenueBase):
    """Venue summary for event listings"""

    id: int = Field(..., description="Venue ID")
    town: Optional[str] = Field(None, description="Town/city")
    postcode: Optional[str] = Field(None, description="Postcode")
    venue_type: Optional[str] = Field(None, description="Venue type")

    model_config = ConfigDict(from_attributes=True)


class VenueDetail(VenueBase):
    """Full venue details"""

    id: int = Field(..., description="Venue ID")
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
    source_name: Optional[str] = Field(None, description="Data source")
    created_at: datetime = Field(..., description="Record creation time")

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return value.isoformat()


class PaginatedVenues(BaseModel):
    """Paginated venues response"""

    venues: List[VenueSummary] = Field(..., description="List of venues")
    pagination: "PaginationInfo" = Field(..., description="Pagination info")


# Import here to avoid circular imports
from .articles import PaginationInfo  # noqa: E402

PaginatedVenues.model_rebuild()
