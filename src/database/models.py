from typing import Any, Dict

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class RSSArticle(Base):
    __tablename__ = "rss_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_title = Column(String(500), nullable=False)
    original_link = Column(Text, nullable=False, unique=True)
    original_summary = Column(Text)
    original_source = Column(String(100), nullable=False)
    source_type = Column(String(50))
    original_pubdate = Column(DateTime(timezone=True))
    url_hash = Column(String(64), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)
    extracted_content = Column(Text)
    ai_summary = Column(Text)
    image_url = Column(Text)
    status = Column(String(20), default="published")  # draft, published, deleted
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Database indexes for API performance
    __table_args__ = (
        Index("idx_articles_created_at", "created_at"),
        Index("idx_articles_source", "original_source"),
        Index("idx_articles_pubdate", "original_pubdate"),
        Index("idx_articles_processed", "processed"),
        Index("idx_articles_source_created", "original_source", "created_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary for API serialization"""
        return {
            "id": self.id,
            "title": self.original_title,
            "link": self.original_link,
            "summary": self.original_summary,
            "source": self.original_source,
            "source_type": self.source_type,
            "published_date": (
                self.original_pubdate.isoformat() if self.original_pubdate else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "processed": self.processed,
            "extracted_content": self.extracted_content,
            "ai_summary": self.ai_summary,
            "image_url": self.image_url,
            "status": self.status,
        }

    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert model instance to summary dictionary for list views"""
        return {
            "id": self.id,
            "title": self.original_title,
            "link": self.original_link,
            "summary": self.original_summary,
            "source": self.original_source,
            "source_type": self.source_type,
            "published_date": (
                self.original_pubdate.isoformat() if self.original_pubdate else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "image_url": self.image_url,
            "status": self.status,
        }


class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(300), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)

    # Address
    address_line1 = Column(String(200))
    address_line2 = Column(String(200))
    town = Column(String(100))
    postcode = Column(String(10))

    # Geo
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))

    # Details
    description = Column(Text)
    venue_type = Column(String(50))
    capacity = Column(Integer)

    # Contact
    website_url = Column(Text)
    phone = Column(String(20))

    # Media
    image_url = Column(Text)

    # Source tracking
    source_name = Column(String(100))
    source_id = Column(String(200))

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    events = relationship("Event", back_populates="venue")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "town": self.town,
            "postcode": self.postcode,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "description": self.description,
            "venue_type": self.venue_type,
            "capacity": self.capacity,
            "website_url": self.website_url,
            "phone": self.phone,
            "image_url": self.image_url,
            "source_name": self.source_name,
        }

    def to_summary_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "town": self.town,
            "postcode": self.postcode,
            "venue_type": self.venue_type,
        }


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(200), nullable=False)

    # Description
    description = Column(Text)
    short_description = Column(String(500))

    # Timing
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True))
    doors_time = Column(Time)

    # Location
    venue_id = Column(Integer, ForeignKey("venues.id"))

    # Categorisation
    event_type = Column(String(50), nullable=False)

    # Media
    image_url = Column(Text)

    # Tickets
    ticket_url = Column(Text)
    price_min = Column(Numeric(10, 2))
    price_max = Column(Numeric(10, 2))
    is_free = Column(Boolean, default=False)

    # Source tracking
    source_name = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)
    source_id = Column(String(200))
    source_url = Column(Text)

    # Deduplication
    event_hash = Column(String(64), unique=True)

    # Status
    status = Column(String(20), default="active")
    is_featured = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    venue = relationship("Venue", back_populates="events")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "description": self.description,
            "short_description": self.short_description,
            "start_datetime": (
                self.start_datetime.isoformat() if self.start_datetime else None
            ),
            "end_datetime": (
                self.end_datetime.isoformat() if self.end_datetime else None
            ),
            "doors_time": str(self.doors_time) if self.doors_time else None,
            "venue": self.venue.to_summary_dict() if self.venue else None,
            "event_type": self.event_type,
            "image_url": self.image_url,
            "ticket_url": self.ticket_url,
            "price_min": float(self.price_min) if self.price_min else None,
            "price_max": float(self.price_max) if self.price_max else None,
            "is_free": self.is_free,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "status": self.status,
            "is_featured": self.is_featured,
        }

    def to_summary_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "start_datetime": (
                self.start_datetime.isoformat() if self.start_datetime else None
            ),
            "venue": self.venue.to_summary_dict() if self.venue else None,
            "event_type": self.event_type,
            "image_url": self.image_url,
            "price_min": float(self.price_min) if self.price_min else None,
            "price_max": float(self.price_max) if self.price_max else None,
            "is_free": self.is_free,
            "ticket_url": self.ticket_url,
        }
