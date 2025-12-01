"""
Venues API routes
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ...database.event_operations import EventOperations
from ..schemas.venues import PaginatedVenues, VenueDetail

router = APIRouter(prefix="/api/v1/venues", tags=["venues"])


@router.get("", response_model=PaginatedVenues)
async def get_venues(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    venue_type: Optional[str] = Query(None, description="Filter by venue type"),
):
    """
    Get paginated list of venues with optional filters
    """
    db = EventOperations()

    try:
        # Get venues
        venues, total_count = db.get_venues_paginated(
            page=page,
            per_page=page_size,
            venue_type=venue_type,
        )

        # Calculate pagination
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1

        # Convert to response models
        venue_summaries = [
            {
                "id": v.id,
                "name": v.name,
                "slug": v.slug,
                "town": v.town,
                "postcode": v.postcode,
                "venue_type": v.venue_type,
            }
            for v in venues
        ]

        return {
            "venues": venue_summaries,
            "pagination": {
                "page": page,
                "per_page": page_size,
                "total_items": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        db.close()


@router.get("/{venue_id}", response_model=VenueDetail)
async def get_venue(venue_id: int):
    """
    Get detailed information about a specific venue
    """
    db = EventOperations()

    try:
        venue = db.get_venue_by_id(venue_id)

        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")

        # Convert to response model
        venue_detail = {
            "id": venue.id,
            "name": venue.name,
            "slug": venue.slug,
            "address_line1": venue.address_line1,
            "address_line2": venue.address_line2,
            "town": venue.town,
            "postcode": venue.postcode,
            "latitude": float(venue.latitude) if venue.latitude else None,
            "longitude": float(venue.longitude) if venue.longitude else None,
            "description": venue.description,
            "venue_type": venue.venue_type,
            "capacity": venue.capacity,
            "website_url": venue.website_url,
            "phone": venue.phone,
            "image_url": venue.image_url,
            "source_name": venue.source_name,
            "created_at": venue.created_at,
        }

        return venue_detail

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        db.close()


@router.get("/{venue_slug}/events", response_model=dict)
async def get_venue_events(
    venue_slug: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Get events for a specific venue by slug
    """
    db = EventOperations()

    try:
        # Get venue by slug
        venue = db.get_venue_by_slug(venue_slug)

        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")

        # Get events for this venue
        events, total_count = db.get_events_paginated(
            page=page,
            per_page=page_size,
            venue_id=venue.id,
        )

        # Calculate pagination
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1

        # Convert to response models
        event_summaries = [
            {
                "id": e.id,
                "title": e.title,
                "slug": e.slug,
                "event_type": e.event_type,
                "start_datetime": e.start_datetime,
                "image_url": e.image_url,
                "price_min": float(e.price_min) if e.price_min else None,
                "price_max": float(e.price_max) if e.price_max else None,
                "is_free": e.is_free,
                "ticket_url": e.ticket_url,
            }
            for e in events
        ]

        return {
            "venue": {
                "id": venue.id,
                "name": venue.name,
                "slug": venue.slug,
                "town": venue.town,
                "postcode": venue.postcode,
            },
            "events": event_summaries,
            "pagination": {
                "page": page,
                "per_page": page_size,
                "total_items": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        db.close()
