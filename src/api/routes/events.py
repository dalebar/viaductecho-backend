"""
Events API routes
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ...database.event_operations import EventOperations
from ..schemas.events import (
    CalendarResponse,
    EventDetail,
    EventTypesResponse,
    PaginatedEvents,
)

router = APIRouter(prefix="/api/v1/events", tags=["events"])


@router.get("", response_model=PaginatedEvents)
async def get_events(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    venue_id: Optional[int] = Query(None, description="Filter by venue ID"),
    start_date: Optional[str] = Query(
        None, description="Filter events from date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        None, description="Filter events to date (YYYY-MM-DD)"
    ),
    is_free: Optional[bool] = Query(None, description="Filter free events"),
    is_featured: Optional[bool] = Query(None, description="Filter featured events"),
):
    """
    Get paginated list of events with optional filters
    """
    db = EventOperations()

    try:
        # Parse dates if provided
        from_date = None
        to_date = None

        if start_date:
            try:
                from_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid start_date format. Use YYYY-MM-DD",
                )

        if end_date:
            try:
                to_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid end_date format. Use YYYY-MM-DD",
                )

        # Get events
        events, total_count = db.get_events_paginated(
            page=page,
            per_page=page_size,
            from_date=from_date,
            to_date=to_date,
            event_type=event_type,
            venue_id=venue_id,
            is_free=is_free,
            featured_only=is_featured or False,
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
                "venue": (
                    {
                        "id": e.venue.id,
                        "name": e.venue.name,
                        "slug": e.venue.slug,
                        "town": e.venue.town,
                        "postcode": e.venue.postcode,
                        "venue_type": e.venue.venue_type,
                    }
                    if e.venue
                    else None
                ),
                "image_url": e.image_url,
                "price_min": float(e.price_min) if e.price_min else None,
                "price_max": float(e.price_max) if e.price_max else None,
                "is_free": e.is_free,
                "ticket_url": e.ticket_url,
            }
            for e in events
        ]

        return {
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


@router.get("/calendar", response_model=CalendarResponse)
async def get_calendar(
    year: int = Query(..., ge=2024, le=2030, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month"),
):
    """
    Get event counts by date for calendar view
    """
    db = EventOperations()

    try:
        calendar_data = db.get_calendar_data(year, month)

        return {
            "calendar": calendar_data,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        db.close()


@router.get("/types", response_model=EventTypesResponse)
async def get_event_types():
    """
    Get list of available event types
    """
    db = EventOperations()

    try:
        event_types = db.get_event_types()

        return {"event_types": event_types}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        db.close()


@router.get("/{event_id}", response_model=EventDetail)
async def get_event(event_id: int):
    """
    Get detailed information about a specific event
    """
    db = EventOperations()

    try:
        event = db.get_event_by_id(event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Convert to response model
        event_detail = {
            "id": event.id,
            "title": event.title,
            "slug": event.slug,
            "description": event.description,
            "short_description": event.short_description,
            "event_type": event.event_type,
            "start_datetime": event.start_datetime,
            "end_datetime": event.end_datetime,
            "doors_time": event.doors_time,
            "venue": (
                {
                    "id": event.venue.id,
                    "name": event.venue.name,
                    "slug": event.venue.slug,
                    "town": event.venue.town,
                    "postcode": event.venue.postcode,
                    "venue_type": event.venue.venue_type,
                }
                if event.venue
                else None
            ),
            "image_url": event.image_url,
            "ticket_url": event.ticket_url,
            "price_min": float(event.price_min) if event.price_min else None,
            "price_max": float(event.price_max) if event.price_max else None,
            "is_free": event.is_free,
            "source_name": event.source_name,
            "source_url": event.source_url,
            "status": event.status,
            "is_featured": event.is_featured,
            "created_at": event.created_at,
        }

        return event_detail

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        db.close()
