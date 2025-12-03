import hashlib
import logging
from typing import Callable, TypeVar

from sqlalchemy import create_engine, text
from sqlalchemy.exc import InvalidRequestError, OperationalError
from sqlalchemy.orm import sessionmaker

from .models import Base, RSSArticle

try:
    from ..config import Config
except ImportError:
    from config import Config


class DatabaseOperations:
    def __init__(self):
        self.engine = create_engine(
            Config.DATABASE_URL,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,  # Recycle connections after 1 hour
            connect_args={"sslmode": "prefer"},  # Handle SSL connection issues
        )
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.logger = logging.getLogger(__name__)

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        self.logger.info("Database connection established")

    @staticmethod
    def _hash_url(url: str) -> str:
        data = url.encode()
        try:
            # Prefer explicit non-security use to satisfy FIPS/Bandit where supported
            return hashlib.md5(data, usedforsecurity=False).hexdigest()
        except TypeError:
            # Fallback for Python/OpenSSL without usedforsecurity argument
            return hashlib.md5(data).hexdigest()

    def _reconnect_if_needed(self):
        """Reconnect to database if connection is lost"""
        try:
            # Test connection
            self.session.execute(text("SELECT 1"))
        except (OperationalError, InvalidRequestError) as e:
            self.logger.warning(f"Database connection lost, reconnecting: {e}")
            try:
                self.session.rollback()
                self.session.close()
                self.session = self.Session()
                self.logger.info("Database reconnection successful")
            except Exception as reconnect_error:
                self.logger.error(f"Database reconnection failed: {reconnect_error}")
                raise

    T = TypeVar("T")

    def _run_with_reconnect(self, op: Callable[[], T]) -> T:
        """Run a DB operation, retrying once after reconnect on connection errors."""
        from sqlalchemy.exc import InvalidRequestError, OperationalError

        self._reconnect_if_needed()
        try:
            return op()
        except (OperationalError, InvalidRequestError):
            self._reconnect_if_needed()
            return op()

    def article_exists(self, url: str) -> bool:
        """Check if article exists by URL hash"""
        url_hash = self._hash_url(url)

        def _op() -> bool:
            existing = (
                self.session.query(RSSArticle).filter_by(url_hash=url_hash).first()
            )
            return existing is not None

        return self._run_with_reconnect(_op)

    def insert_article(self, article_data: dict) -> RSSArticle:
        """Insert new article"""
        url_hash = self._hash_url(article_data["original_link"])

        article = RSSArticle(
            original_title=article_data["original_title"],
            original_link=article_data["original_link"],
            original_summary=article_data.get("original_summary", ""),
            original_source=article_data["original_source"],
            source_type=article_data.get("source_type", "RSS"),
            original_pubdate=article_data.get("original_pubdate"),
            url_hash=url_hash,
        )

        def _op() -> RSSArticle:
            self.session.add(article)
            self.session.commit()
            self.logger.info(f"Inserted article: {article.original_title}")
            return article

        return self._run_with_reconnect(_op)

    def update_article_content(
        self, article_link: str, extracted_content: str, image_url: str = None
    ):
        """Update article with extracted content and image URL"""
        url_hash = self._hash_url(article_link)

        def _op() -> None:
            article = (
                self.session.query(RSSArticle).filter_by(url_hash=url_hash).first()
            )
            if article:
                article.extracted_content = extracted_content
                if image_url:
                    article.image_url = image_url
                self.session.commit()
                self.logger.info(f"Updated content for: {article.original_title}")
            return None

        self._run_with_reconnect(_op)

    def update_article_ai_summary(self, article_link: str, ai_summary: str):
        """Update article with AI-generated summary"""
        url_hash = self._hash_url(article_link)

        def _op() -> None:
            article = (
                self.session.query(RSSArticle).filter_by(url_hash=url_hash).first()
            )
            if article:
                article.ai_summary = ai_summary
                self.session.commit()
                self.logger.info(f"Updated AI summary for: {article.original_title}")
            return None

        self._run_with_reconnect(_op)

    def mark_processed(self, article_link: str):
        """Mark article as processed"""
        url_hash = self._hash_url(article_link)

        def _op() -> None:
            article = (
                self.session.query(RSSArticle).filter_by(url_hash=url_hash).first()
            )
            if article:
                article.processed = True
                self.session.commit()
                self.logger.info(f"Marked processed: {article.original_title}")
            return None

        self._run_with_reconnect(_op)

    def get_article_by_id(self, article_id: int) -> RSSArticle:
        """Get article by ID"""

        def _op() -> RSSArticle:
            return self.session.query(RSSArticle).filter_by(id=article_id).first()

        return self._run_with_reconnect(_op)

    def get_all_articles(
        self, limit: int = 100, offset: int = 0, status_filter: str = None
    ):
        """Get all articles with optional filtering"""

        def _op():
            query = self.session.query(RSSArticle)

            # Filter by status if provided
            if status_filter and status_filter != "all":
                query = query.filter_by(status=status_filter)

            # Order by created_at descending (newest first)
            query = query.order_by(RSSArticle.created_at.desc())

            # Get total count
            total = query.count()

            # Apply pagination
            articles = query.limit(limit).offset(offset).all()

            return {"articles": articles, "total": total}

        return self._run_with_reconnect(_op)

    def update_article(self, article_id: int, update_data: dict) -> RSSArticle:
        """Update article fields"""

        def _op() -> RSSArticle:
            article = self.session.query(RSSArticle).filter_by(id=article_id).first()

            if not article:
                return None

            # Update provided fields
            for key, value in update_data.items():
                if hasattr(article, key):
                    setattr(article, key, value)

            # Update URL hash if link changed
            if "original_link" in update_data:
                article.url_hash = self._hash_url(update_data["original_link"])

            self.session.commit()
            self.session.refresh(article)
            self.logger.info(f"Updated article: {article.original_title}")

            return article

        return self._run_with_reconnect(_op)

    def delete_article(self, article_id: int) -> bool:
        """Soft delete article by setting status to 'deleted'"""

        def _op() -> bool:
            article = self.session.query(RSSArticle).filter_by(id=article_id).first()

            if not article:
                return False

            article.status = "deleted"
            self.session.commit()
            self.logger.info(f"Deleted article: {article.original_title}")

            return True

        return self._run_with_reconnect(_op)

    def close(self):
        if self.session:
            self.session.close()
