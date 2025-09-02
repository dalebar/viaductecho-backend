from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, func, or_

from .models import RSSArticle
from .operations import DatabaseOperations


class APIOperations(DatabaseOperations):
    """Extended database operations for API endpoints"""

    def get_articles_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        source: Optional[str] = None,
        processed_only: bool = True,
    ) -> Tuple[List[RSSArticle], int]:
        """
        Get paginated articles with optional filtering

        Args:
            page: Page number (1-based)
            per_page: Items per page (max 100)
            source: Filter by source name
            processed_only: Only return processed articles

        Returns:
            Tuple of (articles, total_count)
        """
        # Validate pagination parameters
        page = max(1, page)
        per_page = min(100, max(1, per_page))
        offset = (page - 1) * per_page

        query = self.session.query(RSSArticle)

        # Apply filters
        if processed_only:
            query = query.filter(RSSArticle.processed == True)  # noqa: E712

        if source:
            query = query.filter(RSSArticle.original_source == source)

        # Get total count before pagination
        total_count = query.count()

        # Apply ordering and pagination
        articles = query.order_by(desc(RSSArticle.created_at)).offset(offset).limit(per_page).all()

        return articles, total_count

    def get_recent_articles(self, hours: int = 24, limit: int = 50) -> List[RSSArticle]:
        """
        Get articles from the last N hours

        Args:
            hours: Hours back to look
            limit: Maximum number of articles

        Returns:
            List of recent articles
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        limit = min(100, max(1, limit))

        return (
            self.session.query(RSSArticle)
            .filter(
                and_(
                    RSSArticle.created_at >= cutoff_time,
                    RSSArticle.processed == True,  # noqa: E712
                )
            )
            .order_by(desc(RSSArticle.created_at))
            .limit(limit)
            .all()
        )

    def search_articles(self, query: str, page: int = 1, per_page: int = 20) -> Tuple[List[RSSArticle], int]:
        """
        Search articles by title, summary, or content

        Args:
            query: Search query
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            Tuple of (articles, total_count)
        """
        if not query or len(query.strip()) < 2:
            return [], 0

        # Validate pagination parameters
        page = max(1, page)
        per_page = min(100, max(1, per_page))
        offset = (page - 1) * per_page

        # Create search pattern
        search_pattern = f"%{query.strip().lower()}%"

        base_query = self.session.query(RSSArticle).filter(
            and_(
                RSSArticle.processed == True,  # noqa: E712
                or_(
                    func.lower(RSSArticle.original_title).like(search_pattern),
                    func.lower(RSSArticle.original_summary).like(search_pattern),
                    func.lower(RSSArticle.extracted_content).like(search_pattern),
                ),
            )
        )

        total_count = base_query.count()

        articles = base_query.order_by(desc(RSSArticle.created_at)).offset(offset).limit(per_page).all()

        return articles, total_count

    def get_articles_by_source(self, source: str, page: int = 1, per_page: int = 20) -> Tuple[List[RSSArticle], int]:
        """
        Get articles from a specific source

        Args:
            source: Source name
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            Tuple of (articles, total_count)
        """
        return self.get_articles_paginated(page=page, per_page=per_page, source=source, processed_only=True)

    def get_article_by_id(self, article_id: int) -> Optional[RSSArticle]:
        """
        Get a single article by ID

        Args:
            article_id: Article ID

        Returns:
            Article or None if not found
        """
        try:
            return (
                self.session.query(RSSArticle)
                .filter(
                    and_(
                        RSSArticle.id == article_id,
                        RSSArticle.processed == True,  # noqa: E712
                    )
                )
                .first()
            )
        except Exception as e:
            self.logger.error(f"Error fetching article {article_id}: {e}")
            return None

    def get_sources_with_stats(self) -> List[Dict[str, any]]:
        """
        Get all sources with article counts and latest article date

        Returns:
            List of source statistics
        """
        try:
            results = (
                self.session.query(
                    RSSArticle.original_source,
                    func.count(RSSArticle.id).label("article_count"),
                    func.max(RSSArticle.created_at).label("latest_article"),
                    func.count(func.nullif(RSSArticle.processed, False)).label(
                        "processed_count"
                    ),  # Count processed articles
                )
                .filter(RSSArticle.processed == True)  # noqa: E712
                .group_by(RSSArticle.original_source)
                .order_by(desc("article_count"))
                .all()
            )

            sources = []
            for result in results:
                sources.append(
                    {
                        "name": result.original_source,
                        "article_count": result.article_count,
                        "processed_count": result.processed_count,
                        "latest_article": (result.latest_article.isoformat() if result.latest_article else None),
                    }
                )

            return sources
        except Exception as e:
            self.logger.error(f"Error fetching source statistics: {e}")
            return []

    def get_article_count(self, processed_only: bool = True) -> int:
        """
        Get total article count

        Args:
            processed_only: Count only processed articles

        Returns:
            Total article count
        """
        try:
            query = self.session.query(RSSArticle)
            if processed_only:
                query = query.filter(RSSArticle.processed == True)  # noqa: E712
            return query.count()
        except Exception as e:
            self.logger.error(f"Error counting articles: {e}")
            return 0

    def health_check(self) -> Dict[str, any]:
        """
        Perform database health check for API

        Returns:
            Health status information
        """
        try:
            # Test basic query
            article_count = self.get_article_count()
            recent_count = len(self.get_recent_articles(hours=24, limit=1))

            # Test database connection
            self.session.execute("SELECT 1")

            return {
                "status": "healthy",
                "total_articles": article_count,
                "recent_articles_24h": recent_count,
                "database_connected": True,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_connected": False,
                "timestamp": datetime.now().isoformat(),
            }
