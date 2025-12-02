"""
Database operations for Events and Venues
"""

import hashlib
import logging
import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func

from .models import Event, Venue
from .operations import DatabaseOperations


class EventOperations(DatabaseOperations):
    """Extended database operations for events and venues"""

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    # ==========================================
    # VENUE OPERATIONS
    # ==========================================

    @staticmethod
    def _create_slug(text: str) -> str:
        """Create URL-safe slug from text"""
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        slug = re.sub(r"[-\s]+", "-", slug).strip("-")
        return slug[:200]

    def _generate_slug(
        self, model_class, text: str, exclude_id: Optional[int] = None
    ) -> str:
        """
        Generate unique slug for a model instance

        Args:
            model_class: Event or Venue model class
            text: Text to convert to slug
            exclude_id: Optional ID to exclude from uniqueness check (for updates)

        Returns:
            Unique slug
        """
        base_slug = self._create_slug(text)
        slug = base_slug
        counter = 1

        while True:
            # Check if slug exists
            query = self.session.query(model_class).filter_by(slug=slug)
            if exclude_id:
                query = query.filter(model_class.id != exclude_id)

            if not query.first():
                return slug

            # Slug exists, add counter
            slug = f"{base_slug}-{counter}"
            counter += 1

    def get_or_create_venue(self, venue_data: Dict[str, Any]) -> Venue:
        """Get existing venue or create new one"""
        # Try to find by source first
        if venue_data.get("source_name") and venue_data.get("source_id"):
            existing = (
                self.session.query(Venue)
                .filter_by(
                    source_name=venue_data["source_name"],
                    source_id=str(venue_data["source_id"]),
                )
                .first()
            )
            if existing:
                return existing

        # Try to find by name and postcode
        if venue_data.get("name") and venue_data.get("postcode"):
            existing = (
                self.session.query(Venue)
                .filter_by(
                    name=venue_data["name"],
                    postcode=venue_data.get("postcode"),
                )
                .first()
            )
            if existing:
                # Update source info if we have it
                if venue_data.get("source_name") and not existing.source_name:
                    existing.source_name = venue_data["source_name"]
                    existing.source_id = str(venue_data.get("source_id", ""))
                    self.session.commit()
                return existing

        # Create new venue
        slug = self._create_slug(venue_data["name"])

        # Ensure unique slug
        base_slug = slug
        counter = 1
        while self.session.query(Venue).filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        venue = Venue(
            name=venue_data["name"],
            slug=slug,
            address_line1=venue_data.get("address_line1"),
            address_line2=venue_data.get("address_line2"),
            town=venue_data.get("town", "Stockport"),
            postcode=venue_data.get("postcode"),
            latitude=venue_data.get("latitude"),
            longitude=venue_data.get("longitude"),
            description=venue_data.get("description"),
            venue_type=venue_data.get("venue_type"),
            capacity=venue_data.get("capacity"),
            website_url=venue_data.get("website_url"),
            phone=venue_data.get("phone"),
            image_url=venue_data.get("image_url"),
            source_name=venue_data.get("source_name"),
            source_id=(
                str(venue_data.get("source_id", ""))
                if venue_data.get("source_id")
                else None
            ),
        )

        self.session.add(venue)
        self.session.commit()
        self.logger.info(f"Created venue: {venue.name}")
        return venue

    def get_venue_by_id(self, venue_id: int) -> Optional[Venue]:
        """Get venue by ID"""
        return self.session.query(Venue).filter_by(id=venue_id).first()

    def get_venue_by_slug(self, slug: str) -> Optional[Venue]:
        """Get venue by slug"""
        return self.session.query(Venue).filter_by(slug=slug).first()

    def get_all_venues(self, venue_type: Optional[str] = None) -> List[Venue]:
        """Get all venues, optionally filtered by type"""
        query = self.session.query(Venue).order_by(Venue.name)
        if venue_type:
            query = query.filter_by(venue_type=venue_type)
        return query.all()

    def get_venues_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        venue_type: Optional[str] = None,
    ) -> Tuple[List[Venue], int]:
        """Get paginated venues"""
        page = max(1, page)
        per_page = min(100, max(1, per_page))
        offset = (page - 1) * per_page

        query = self.session.query(Venue)
        if venue_type:
            query = query.filter_by(venue_type=venue_type)

        total_count = query.count()
        venues = query.order_by(Venue.name).offset(offset).limit(per_page).all()

        return venues, total_count

    # ==========================================
    # EVENT OPERATIONS
    # ==========================================

    @staticmethod
    def _create_event_hash(venue_id: int, start_datetime: datetime, title: str) -> str:
        """Create unique hash for event deduplication"""
        # Normalize title for comparison
        normalized_title = re.sub(r"[^\w]", "", title.lower())[:50]
        date_str = start_datetime.strftime("%Y-%m-%d")

        hash_input = f"{venue_id}:{date_str}:{normalized_title}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def event_exists(self, venue_id: int, start_datetime: datetime, title: str) -> bool:
        """Check if event already exists (deduplication)"""
        event_hash = self._create_event_hash(venue_id, start_datetime, title)
        existing = self.session.query(Event).filter_by(event_hash=event_hash).first()
        return existing is not None

    def insert_event(self, event_data: Dict[str, Any], venue: Venue) -> Optional[Event]:
        """Insert new event"""
        try:
            # Create hash for deduplication
            event_hash = self._create_event_hash(
                venue.id,
                event_data["start_datetime"],
                event_data["title"],
            )

            # Check for existing
            existing = (
                self.session.query(Event).filter_by(event_hash=event_hash).first()
            )
            if existing:
                self.logger.debug(f"Event already exists: {event_data['title']}")
                return None

            # Create slug
            date_str = event_data["start_datetime"].strftime("%Y-%m-%d")
            slug = f"{self._create_slug(event_data['title'])}-{date_str}"

            # Handle price fields
            price_min = event_data.get("price_min")
            price_max = event_data.get("price_max")

            if price_min is not None:
                price_min = Decimal(str(price_min))
            if price_max is not None:
                price_max = Decimal(str(price_max))

            event = Event(
                title=event_data["title"],
                slug=slug,
                description=event_data.get("description"),
                short_description=event_data.get("short_description"),
                start_datetime=event_data["start_datetime"],
                end_datetime=event_data.get("end_datetime"),
                doors_time=event_data.get("doors_time"),
                venue_id=venue.id,
                event_type=event_data.get("event_type", "other"),
                image_url=event_data.get("image_url"),
                ticket_url=event_data.get("ticket_url"),
                price_min=price_min,
                price_max=price_max,
                is_free=event_data.get("is_free", False),
                source_name=event_data["source_name"],
                source_type=event_data["source_type"],
                source_id=(
                    str(event_data.get("source_id", ""))
                    if event_data.get("source_id")
                    else None
                ),
                source_url=event_data.get("source_url"),
                event_hash=event_hash,
                status="active",
            )

            self.session.add(event)
            self.session.commit()
            self.logger.info(f"Inserted event: {event.title}")
            return event

        except Exception as e:
            self.logger.error(f"Error inserting event: {e}")
            self.session.rollback()
            return None

    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Get event by ID"""
        return self.session.query(Event).filter_by(id=event_id, status="active").first()

    def get_event_by_slug(self, slug: str) -> Optional[Event]:
        """Get event by slug"""
        return self.session.query(Event).filter_by(slug=slug, status="active").first()

    def get_events_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        venue_id: Optional[int] = None,
        is_free: Optional[bool] = None,
        featured_only: bool = False,
    ) -> Tuple[List[Event], int]:
        """Get paginated events with filters"""
        page = max(1, page)
        per_page = min(100, max(1, per_page))
        offset = (page - 1) * per_page

        query = self.session.query(Event).filter(Event.status == "active")

        # Default to future events if no date specified
        if from_date is None and to_date is None:
            from_date = datetime.now()

        if from_date:
            query = query.filter(Event.start_datetime >= from_date)
        if to_date:
            query = query.filter(Event.start_datetime <= to_date)
        if event_type:
            query = query.filter(Event.event_type == event_type)
        if venue_id:
            query = query.filter(Event.venue_id == venue_id)
        if is_free is not None:
            query = query.filter(Event.is_free == is_free)
        if featured_only:
            query = query.filter(Event.is_featured)

        total_count = query.count()
        events = (
            query.order_by(Event.start_datetime).offset(offset).limit(per_page).all()
        )

        return events, total_count

    def get_events_for_date(self, date: datetime) -> List[Event]:
        """Get all events for a specific date"""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        return (
            self.session.query(Event)
            .filter(
                and_(
                    Event.status == "active",
                    Event.start_datetime >= start_of_day,
                    Event.start_datetime < end_of_day,
                )
            )
            .order_by(Event.start_datetime)
            .all()
        )

    def get_events_by_venue(
        self,
        venue_id: int,
        from_date: Optional[datetime] = None,
        limit: int = 20,
    ) -> List[Event]:
        """Get events for a specific venue"""
        query = self.session.query(Event).filter(
            and_(
                Event.venue_id == venue_id,
                Event.status == "active",
            )
        )

        if from_date:
            query = query.filter(Event.start_datetime >= from_date)
        else:
            query = query.filter(Event.start_datetime >= datetime.now())

        return query.order_by(Event.start_datetime).limit(limit).all()

    def get_calendar_data(
        self,
        year: int,
        month: int,
    ) -> Dict[str, int]:
        """Get event counts by date for calendar display"""
        from calendar import monthrange

        start_date = datetime(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = datetime(year, month, last_day, 23, 59, 59)

        results = (
            self.session.query(
                func.date(Event.start_datetime).label("event_date"),
                func.count(Event.id).label("count"),
            )
            .filter(
                and_(
                    Event.status == "active",
                    Event.start_datetime >= start_date,
                    Event.start_datetime <= end_date,
                )
            )
            .group_by(func.date(Event.start_datetime))
            .all()
        )

        return {str(row.event_date): row.count for row in results}

    def get_upcoming_events(self, limit: int = 50) -> List[Event]:
        """Get upcoming events for static JSON generation"""
        return (
            self.session.query(Event)
            .filter(
                and_(
                    Event.status == "active",
                    Event.start_datetime >= datetime.now(),
                )
            )
            .order_by(Event.start_datetime)
            .limit(limit)
            .all()
        )

    def mark_past_events(self) -> int:
        """Mark events in the past as 'past' status"""
        count = (
            self.session.query(Event)
            .filter(
                and_(
                    Event.status == "active",
                    Event.start_datetime < datetime.now(),
                )
            )
            .update({"status": "past"})
        )
        self.session.commit()
        self.logger.info(f"Marked {count} events as past")
        return count

    def get_event_count(self, future_only: bool = True) -> int:
        """Get total event count"""
        query = self.session.query(Event).filter(Event.status == "active")
        if future_only:
            query = query.filter(Event.start_datetime >= datetime.now())
        return query.count()

    def get_event_types(self) -> List[str]:
        """Get list of distinct event types"""
        results = (
            self.session.query(Event.event_type)
            .filter(Event.status == "active")
            .distinct()
            .all()
        )
        return [r[0] for r in results if r[0]]
