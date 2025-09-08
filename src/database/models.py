from typing import Any, Dict

from sqlalchemy import (Boolean, Column, DateTime, Index, Integer, String,
                        Text, func)
from sqlalchemy.orm import declarative_base

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
        }
