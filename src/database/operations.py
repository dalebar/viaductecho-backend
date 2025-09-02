import hashlib
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, InvalidRequestError

from .models import RSSArticle

try:
    from ..config import Config
except ImportError:
    from config import Config


class DatabaseOperations:
    def __init__(self):
        self.engine = create_engine(
            Config.DATABASE_URL,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,   # Recycle connections after 1 hour
            connect_args={"sslmode": "prefer"}  # Handle SSL connection issues
        )
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Database connection established")

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

    def article_exists(self, url: str) -> bool:
        """Check if article exists by URL hash"""
        self._reconnect_if_needed()
        url_hash = hashlib.md5(url.encode()).hexdigest()
        try:
            existing = self.session.query(RSSArticle).filter_by(url_hash=url_hash).first()
            return existing is not None
        except (OperationalError, InvalidRequestError):
            self._reconnect_if_needed()
            existing = self.session.query(RSSArticle).filter_by(url_hash=url_hash).first()
            return existing is not None

    def insert_article(self, article_data: dict) -> RSSArticle:
        """Insert new article"""
        self._reconnect_if_needed()
        url_hash = hashlib.md5(article_data["original_link"].encode()).hexdigest()

        article = RSSArticle(
            original_title=article_data["original_title"],
            original_link=article_data["original_link"],
            original_summary=article_data.get("original_summary", ""),
            original_source=article_data["original_source"],
            source_type=article_data.get("source_type", "RSS"),
            original_pubdate=article_data.get("original_pubdate"),
            url_hash=url_hash,
        )

        try:
            self.session.add(article)
            self.session.commit()
            self.logger.info(f"Inserted article: {article.original_title}")
            return article
        except (OperationalError, InvalidRequestError):
            self._reconnect_if_needed()
            self.session.add(article)
            self.session.commit()
            self.logger.info(f"Inserted article: {article.original_title}")
            return article

    def mark_processed(self, article_link: str):
        """Mark article as processed"""
        self._reconnect_if_needed()
        url_hash = hashlib.md5(article_link.encode()).hexdigest()
        try:
            article = self.session.query(RSSArticle).filter_by(url_hash=url_hash).first()
            if article:
                article.processed = True
                self.session.commit()
                self.logger.info(f"Marked processed: {article.original_title}")
        except (OperationalError, InvalidRequestError):
            self._reconnect_if_needed()
            article = self.session.query(RSSArticle).filter_by(url_hash=url_hash).first()
            if article:
                article.processed = True
                self.session.commit()
                self.logger.info(f"Marked processed: {article.original_title}")

    def close(self):
        if self.session:
            self.session.close()
