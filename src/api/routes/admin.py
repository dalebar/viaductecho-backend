"""
Admin API routes - protected by API key authentication
"""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status

from ...config import Config
from ...database.event_operations import EventOperations
from ...database.models import Event, Venue
from ...events_aggregator import EventsAggregator
from ...main import ViaductEcho
from ...publishers.github_publisher import GitHubPublisher
from ..schemas.admin import (
    AggregationResponse,
    EventCreate,
    EventUpdate,
    VenueCreate,
    VenueUpdate,
)
from ..schemas.events import EventDetail
from ..schemas.venues import VenueDetail

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

logger = logging.getLogger(__name__)


def verify_admin_key(x_api_key: str = Header(..., description="Admin API key")):
    """Verify admin API key from header"""
    if x_api_key != Config.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return x_api_key


# Venue Management


@router.post("/venues", response_model=VenueDetail, status_code=status.HTTP_201_CREATED)
async def create_venue(
    venue_data: VenueCreate,
    _: str = Depends(verify_admin_key),
):
    """
    Create a new venue (Admin only)
    """
    db = EventOperations()

    try:
        # Convert to dict and add source info
        venue_dict = venue_data.model_dump()
        venue_dict["source_name"] = "manual"

        # Create venue
        venue = db.get_or_create_venue(venue_dict)

        if not venue:
            raise HTTPException(
                status_code=500,
                detail="Failed to create venue",
            )

        return {
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

    except Exception as e:
        logger.error(f"Error creating venue: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create venue: {str(e)}",
        )
    finally:
        db.close()


@router.patch("/venues/{venue_id}", response_model=VenueDetail)
async def update_venue(
    venue_id: int,
    venue_data: VenueUpdate,
    _: str = Depends(verify_admin_key),
):
    """
    Update a venue (Admin only)
    """
    db = EventOperations()

    try:
        venue = db.get_venue_by_id(venue_id)

        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")

        # Update only provided fields
        update_data = venue_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(venue, field, value)

        # Regenerate slug if name changed
        if "name" in update_data:
            venue.slug = db._generate_slug(Venue, venue.name, venue.id)

        db.session.commit()
        db.session.refresh(venue)

        return {
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating venue: {e}")
        db.session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update venue: {str(e)}",
        )
    finally:
        db.close()


@router.delete("/venues/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue(
    venue_id: int,
    _: str = Depends(verify_admin_key),
):
    """
    Delete a venue (Admin only)
    Note: This will fail if there are events associated with this venue
    """
    db = EventOperations()

    try:
        venue = db.get_venue_by_id(venue_id)

        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")

        db.session.delete(venue)
        db.session.commit()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting venue: {e}")
        db.session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete venue: {str(e)}",
        )
    finally:
        db.close()


# Event Management


@router.post("/events", response_model=EventDetail, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    _: str = Depends(verify_admin_key),
):
    """
    Create a new event (Admin only)
    """
    db = EventOperations()

    try:
        # Verify venue exists
        venue = db.get_venue_by_id(event_data.venue_id)

        if not venue:
            raise HTTPException(
                status_code=400,
                detail=f"Venue with ID {event_data.venue_id} not found",
            )

        # Convert to dict and add source info
        event_dict = event_data.model_dump()
        # source_name comes from the form (Instagram, Skiddle, Other, etc)
        event_dict["source_type"] = "manual"  # All admin-created events are manual
        event_dict["source_id"] = None
        event_dict["source_url"] = None

        # Remove venue_id from dict (it's handled separately)
        event_dict.pop("venue_id", None)

        # Create event
        event = db.insert_event(event_dict, venue)

        if not event:
            raise HTTPException(
                status_code=500,
                detail="Failed to create event (possible duplicate)",
            )

        return {
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create event: {str(e)}",
        )
    finally:
        db.close()


@router.patch("/events/{event_id}", response_model=EventDetail)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    _: str = Depends(verify_admin_key),
):
    """
    Update an event (Admin only)
    """
    db = EventOperations()

    try:
        event = db.get_event_by_id(event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Update only provided fields
        update_data = event_data.model_dump(exclude_unset=True)

        # If venue_id is being changed, verify it exists
        if "venue_id" in update_data:
            venue = db.get_venue_by_id(update_data["venue_id"])
            if not venue:
                raise HTTPException(
                    status_code=400,
                    detail=f"Venue with ID {update_data['venue_id']} not found",
                )

        for field, value in update_data.items():
            setattr(event, field, value)

        # Regenerate slug if title changed
        if "title" in update_data:
            event.slug = db._generate_slug(Event, event.title, event.id)

        # Regenerate hash if key fields changed
        if any(k in update_data for k in ["venue_id", "start_datetime", "title"]):
            event.event_hash = db._create_event_hash(
                event.venue_id,
                event.start_datetime,
                event.title,
            )

        db.session.commit()
        db.session.refresh(event)

        return {
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event: {e}")
        db.session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update event: {str(e)}",
        )
    finally:
        db.close()


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    _: str = Depends(verify_admin_key),
):
    """
    Delete an event (Admin only)
    Soft delete: marks event as 'deleted' to prevent re-fetching from Skiddle
    """
    db = EventOperations()

    try:
        event = db.get_event_by_id(event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Soft delete: mark as deleted instead of removing from database
        event.status = "deleted"
        db.session.commit()

        logger.info(f"Event marked as deleted: {event.title} (ID: {event_id})")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        db.session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete event: {str(e)}",
        )
    finally:
        db.close()


@router.patch("/events/{event_id}/feature", response_model=EventDetail)
async def toggle_featured(
    event_id: int,
    is_featured: bool,
    _: str = Depends(verify_admin_key),
):
    """
    Set an event's featured status (Admin only)
    """
    db = EventOperations()

    try:
        event = db.get_event_by_id(event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        event.is_featured = is_featured
        db.session.commit()
        db.session.refresh(event)

        return {
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling featured status: {e}")
        db.session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update featured status: {str(e)}",
        )
    finally:
        db.close()


# Aggregation Job


@router.post("/aggregate", response_model=AggregationResponse)
async def trigger_aggregation(
    _: str = Depends(verify_admin_key),
):
    """
    Manually trigger events aggregation job (Admin only)
    Fetches events from Skiddle API but does NOT publish to GitHub Pages
    """
    try:
        aggregator = EventsAggregator()

        # Run aggregation
        stats = aggregator.run_aggregation()

        # Mark past events
        past_count = aggregator.db.mark_past_events()

        aggregator.close()

        message = f"Fetched {stats['total_fetched']} events from Skiddle. {stats['total_inserted']} new, {stats['total_duplicates']} duplicates."
        logger.info(message)

        return {
            "success": True,
            "message": message,
            "stats": {
                "total_fetched": stats["total_fetched"],
                "total_inserted": stats["total_inserted"],
                "total_duplicates": stats["total_duplicates"],
                "total_errors": stats["total_errors"],
                "past_events_marked": past_count,
                "github_published": 0,
                "github_failed": 0,
            },
        }

    except Exception as e:
        logger.error(f"Aggregation job failed: {e}")
        return {
            "success": False,
            "message": f"Aggregation failed: {str(e)}",
            "stats": None,
        }


@router.post("/publish", response_model=AggregationResponse)
async def publish_to_github(
    _: str = Depends(verify_admin_key),
):
    """
    Publish events to GitHub Pages (Admin only)
    Generates JSON files from current database and pushes to GitHub Pages
    Does NOT fetch new events from Skiddle
    """
    try:
        aggregator = EventsAggregator()

        # Generate static JSON files from current database
        aggregator.generate_static_json()

        aggregator.close()

        # Publish to GitHub Pages
        publisher = GitHubPublisher()
        publish_results = publisher.publish_static_json_files()

        if publish_results["success"]:
            message = f"Published {len(publish_results['published'])} files to GitHub Pages successfully."
            logger.info(message)
        else:
            message = (
                f"Publishing failed: {publish_results.get('error', 'Unknown error')}"
            )
            logger.warning(message)

        return {
            "success": publish_results["success"],
            "message": message,
            "stats": {
                "total_fetched": 0,
                "total_inserted": 0,
                "total_duplicates": 0,
                "total_errors": 0,
                "past_events_marked": 0,
                "github_published": len(publish_results.get("published", [])),
                "github_failed": len(publish_results.get("failed", [])),
            },
        }

    except Exception as e:
        logger.error(f"Publishing failed: {e}")
        return {
            "success": False,
            "message": f"Publishing failed: {str(e)}",
            "stats": None,
        }


@router.post("/aggregate-news")
async def trigger_news_aggregation(
    _: str = Depends(verify_admin_key),
):
    """
    Manually trigger news aggregation (Admin only)
    Runs the ViaductEcho aggregator once to fetch, process, and publish news articles
    """
    try:
        logger.info("Starting manual news aggregation...")

        # Run aggregation once
        echo = ViaductEcho()
        echo.run_once()

        logger.info("News aggregation completed successfully")

        return {
            "success": True,
            "message": "News aggregation completed successfully. Check logs for details.",
        }

    except Exception as e:
        logger.error(f"News aggregation failed: {e}")
        return {
            "success": False,
            "message": f"News aggregation failed: {str(e)}",
        }


# Image Upload


@router.post("/upload-image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    _: str = Depends(verify_admin_key),
):
    """
    Upload an event image (Admin only)

    Accepts: JPG, JPEG, PNG, GIF, WEBP
    Returns: URL to the uploaded image
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: JPG, PNG, GIF, WEBP. Got: {file.content_type}",
        )

    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    contents = await file.read()
    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: 5MB. Got: {len(contents) / 1024 / 1024:.2f}MB",
        )

    try:
        # Generate unique filename
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # Save to static/event_images directory
        upload_dir = Path("static/event_images")
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / unique_filename

        with open(file_path, "wb") as f:
            f.write(contents)

        # Return URL
        image_url = f"/static/event_images/{unique_filename}"

        logger.info(f"Image uploaded: {unique_filename}")

        return {
            "success": True,
            "filename": unique_filename,
            "url": image_url,
            "size": len(contents),
        }

    except Exception as e:
        logger.error(f"Image upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}",
        )
