#!/usr/bin/env python3
"""
Comprehensive test suite for API schemas
"""
import os
import sys
from datetime import datetime


import pytest
from pydantic import ValidationError

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from api.schemas.articles import (
    ArticleBase,
    ArticleDetail,
    ArticleListParams,
    ArticleSearchParams,
    ArticleSummary,
    PaginatedArticles,
    PaginationInfo,
    RecentArticlesParams,
)
from api.schemas.common import ErrorResponse, HealthResponse, MessageResponse
from api.schemas.sources import SourceStats, SourcesResponse


class TestArticleSchemas:
    """Test suite for article schemas"""

    def test_article_base_valid(self):
        """Test valid ArticleBase creation"""
        data = {
            "title": "Test Article",
            "link": "https://example.com/article",
            "summary": "Test summary",
            "source": "Test Source",
            "source_type": "RSS News",
            "published_date": datetime(2024, 1, 15, 10, 30, 0),
        }

        article = ArticleBase(**data)

        assert article.title == "Test Article"
        assert article.link == "https://example.com/article"
        assert article.summary == "Test summary"
        assert article.source == "Test Source"
        assert article.source_type == "RSS News"
        assert article.published_date == datetime(2024, 1, 15, 10, 30, 0)

    def test_article_base_minimal(self):
        """Test ArticleBase with minimal required fields"""
        data = {
            "title": "Test Article",
            "link": "https://example.com/article",
            "source": "Test Source",
        }

        article = ArticleBase(**data)

        assert article.title == "Test Article"
        assert article.link == "https://example.com/article"
        assert article.source == "Test Source"
        assert article.summary is None
        assert article.source_type is None
        assert article.published_date is None

    def test_article_base_missing_required_fields(self):
        """Test ArticleBase with missing required fields"""
        # Missing title
        with pytest.raises(ValidationError) as exc_info:
            ArticleBase(link="https://example.com", source="Test Source")
        assert "title" in str(exc_info.value)

        # Missing link
        with pytest.raises(ValidationError) as exc_info:
            ArticleBase(title="Test", source="Test Source")
        assert "link" in str(exc_info.value)

        # Missing source
        with pytest.raises(ValidationError) as exc_info:
            ArticleBase(title="Test", link="https://example.com")
        assert "source" in str(exc_info.value)

    def test_article_summary_valid(self):
        """Test valid ArticleSummary creation"""
        data = {
            "id": 1,
            "title": "Test Article",
            "link": "https://example.com/article",
            "summary": "Test summary",
            "source": "Test Source",
            "source_type": "RSS News",
            "published_date": datetime(2024, 1, 15, 10, 30, 0),
            "created_at": datetime(2024, 1, 15, 10, 35, 0),
            "image_url": "https://example.com/image.jpg",
        }

        article = ArticleSummary(**data)

        assert article.id == 1
        assert article.created_at == datetime(2024, 1, 15, 10, 35, 0)
        assert article.image_url == "https://example.com/image.jpg"

    def test_article_detail_valid(self):
        """Test valid ArticleDetail creation"""
        data = {
            "id": 1,
            "title": "Test Article",
            "link": "https://example.com/article",
            "summary": "Test summary",
            "source": "Test Source",
            "source_type": "RSS News",
            "published_date": datetime(2024, 1, 15, 10, 30, 0),
            "created_at": datetime(2024, 1, 15, 10, 35, 0),
            "updated_at": datetime(2024, 1, 15, 10, 40, 0),
            "processed": True,
            "extracted_content": "Full content",
            "ai_summary": "AI summary",
            "image_url": "https://example.com/image.jpg",
        }

        article = ArticleDetail(**data)

        assert article.processed is True
        assert article.extracted_content == "Full content"
        assert article.ai_summary == "AI summary"
        assert article.updated_at == datetime(2024, 1, 15, 10, 40, 0)

    def test_pagination_info_valid(self):
        """Test valid PaginationInfo creation"""
        data = {
            "page": 2,
            "per_page": 20,
            "total_items": 47,
            "total_pages": 3,
            "has_next": True,
            "has_prev": True,
        }

        pagination = PaginationInfo(**data)

        assert pagination.page == 2
        assert pagination.per_page == 20
        assert pagination.total_items == 47
        assert pagination.total_pages == 3
        assert pagination.has_next is True
        assert pagination.has_prev is True

    def test_pagination_info_validation(self):
        """Test PaginationInfo validation"""
        # Invalid page (too low)
        with pytest.raises(ValidationError) as exc_info:
            PaginationInfo(page=0, per_page=20, total_items=100, total_pages=5, has_next=True, has_prev=False)
        assert "page" in str(exc_info.value)

        # Invalid per_page (too high)
        with pytest.raises(ValidationError) as exc_info:
            PaginationInfo(page=1, per_page=101, total_items=100, total_pages=5, has_next=True, has_prev=False)
        assert "per_page" in str(exc_info.value)

        # Invalid total_items (negative)
        with pytest.raises(ValidationError) as exc_info:
            PaginationInfo(page=1, per_page=20, total_items=-1, total_pages=0, has_next=False, has_prev=False)
        assert "total_items" in str(exc_info.value)

    def test_paginated_articles_valid(self):
        """Test valid PaginatedArticles creation"""
        article_data = {
            "id": 1,
            "title": "Test Article",
            "link": "https://example.com/article",
            "source": "Test Source",
            "created_at": datetime(2024, 1, 15, 10, 35, 0),
        }
        article = ArticleSummary(**article_data)

        pagination_data = {
            "page": 1,
            "per_page": 20,
            "total_items": 1,
            "total_pages": 1,
            "has_next": False,
            "has_prev": False,
        }
        pagination = PaginationInfo(**pagination_data)

        paginated = PaginatedArticles(articles=[article], pagination=pagination)

        assert len(paginated.articles) == 1
        assert paginated.articles[0].id == 1
        assert paginated.pagination.total_items == 1

    def test_article_search_params_valid(self):
        """Test valid ArticleSearchParams creation"""
        params = ArticleSearchParams(query="test search", page=2, per_page=10)

        assert params.query == "test search"
        assert params.page == 2
        assert params.per_page == 10

    def test_article_search_params_defaults(self):
        """Test ArticleSearchParams with defaults"""
        params = ArticleSearchParams(query="test")

        assert params.query == "test"
        assert params.page == 1
        assert params.per_page == 20

    def test_article_search_params_validation(self):
        """Test ArticleSearchParams validation"""
        # Query too short
        with pytest.raises(ValidationError) as exc_info:
            ArticleSearchParams(query="a")
        assert "query" in str(exc_info.value)

        # Invalid page
        with pytest.raises(ValidationError) as exc_info:
            ArticleSearchParams(query="test", page=0)
        assert "page" in str(exc_info.value)

        # Invalid per_page
        with pytest.raises(ValidationError) as exc_info:
            ArticleSearchParams(query="test", per_page=101)
        assert "per_page" in str(exc_info.value)

    def test_article_list_params_validation(self):
        """Test ArticleListParams validation"""
        # Valid params
        params = ArticleListParams(page=1, per_page=50, source="Test Source", processed_only=False)
        assert params.page == 1
        assert params.per_page == 50
        assert params.source == "Test Source"
        assert params.processed_only is False

        # Invalid per_page (too high)
        with pytest.raises(ValidationError) as exc_info:
            ArticleListParams(per_page=101)
        assert "per_page" in str(exc_info.value)

    def test_recent_articles_params_validation(self):
        """Test RecentArticlesParams validation"""
        # Valid params
        params = RecentArticlesParams(hours=72, limit=25)
        assert params.hours == 72
        assert params.limit == 25

        # Invalid hours (too high)
        with pytest.raises(ValidationError) as exc_info:
            RecentArticlesParams(hours=169)  # > 168 (1 week)
        assert "hours" in str(exc_info.value)

        # Invalid limit (too high)
        with pytest.raises(ValidationError) as exc_info:
            RecentArticlesParams(limit=101)
        assert "limit" in str(exc_info.value)


class TestSourceSchemas:
    """Test suite for source schemas"""

    def test_source_stats_valid(self):
        """Test valid SourceStats creation"""
        data = {
            "name": "BBC News",
            "article_count": 25,
            "processed_count": 23,
            "latest_article": datetime(2024, 1, 20, 15, 30, 0),
        }

        source = SourceStats(**data)

        assert source.name == "BBC News"
        assert source.article_count == 25
        assert source.processed_count == 23
        assert source.latest_article == datetime(2024, 1, 20, 15, 30, 0)

    def test_source_stats_no_latest_article(self):
        """Test SourceStats with no latest article"""
        data = {
            "name": "New Source",
            "article_count": 0,
            "processed_count": 0,
            "latest_article": None,
        }

        source = SourceStats(**data)

        assert source.latest_article is None

    def test_source_stats_validation(self):
        """Test SourceStats validation"""
        # Negative article count
        with pytest.raises(ValidationError) as exc_info:
            SourceStats(name="Test", article_count=-1, processed_count=0)
        assert "article_count" in str(exc_info.value)

        # Negative processed count
        with pytest.raises(ValidationError) as exc_info:
            SourceStats(name="Test", article_count=10, processed_count=-1)
        assert "processed_count" in str(exc_info.value)

    def test_sources_response_valid(self):
        """Test valid SourcesResponse creation"""
        source_data = {
            "name": "Test Source",
            "article_count": 5,
            "processed_count": 4,
            "latest_article": datetime(2024, 1, 20, 12, 0, 0),
        }
        source = SourceStats(**source_data)

        response = SourcesResponse(sources=[source], total_sources=1)

        assert len(response.sources) == 1
        assert response.total_sources == 1
        assert response.sources[0].name == "Test Source"

    def test_sources_response_validation(self):
        """Test SourcesResponse validation"""
        # Negative total_sources
        with pytest.raises(ValidationError) as exc_info:
            SourcesResponse(sources=[], total_sources=-1)
        assert "total_sources" in str(exc_info.value)


class TestCommonSchemas:
    """Test suite for common schemas"""

    def test_error_response_valid(self):
        """Test valid ErrorResponse creation"""
        error = ErrorResponse(
            error="Test error",
            detail="Detailed error message",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
        )

        assert error.error == "Test error"
        assert error.detail == "Detailed error message"
        assert error.timestamp == datetime(2024, 1, 15, 10, 30, 0)

    def test_error_response_minimal(self):
        """Test ErrorResponse with minimal fields"""
        error = ErrorResponse(error="Test error")

        assert error.error == "Test error"
        assert error.detail is None
        assert isinstance(error.timestamp, datetime)

    def test_health_response_healthy(self):
        """Test healthy HealthResponse"""
        health = HealthResponse(
            status="healthy",
            total_articles=100,
            recent_articles_24h=5,
            database_connected=True,
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
        )

        assert health.status == "healthy"
        assert health.total_articles == 100
        assert health.recent_articles_24h == 5
        assert health.database_connected is True
        assert health.error is None

    def test_health_response_unhealthy(self):
        """Test unhealthy HealthResponse"""
        health = HealthResponse(
            status="unhealthy",
            database_connected=False,
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            error="Database connection failed",
        )

        assert health.status == "unhealthy"
        assert health.database_connected is False
        assert health.error == "Database connection failed"
        assert health.total_articles is None

    def test_message_response_valid(self):
        """Test valid MessageResponse creation"""
        message = MessageResponse(
            message="Operation completed successfully",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
        )

        assert message.message == "Operation completed successfully"
        assert message.timestamp == datetime(2024, 1, 15, 10, 30, 0)

    def test_message_response_with_default_timestamp(self):
        """Test MessageResponse with default timestamp"""
        message = MessageResponse(message="Test message")

        assert message.message == "Test message"
        assert isinstance(message.timestamp, datetime)


class TestSchemaIntegration:
    """Integration tests for schemas working together"""

    def test_complete_article_workflow(self):
        """Test complete article data workflow through schemas"""
        # Create article detail
        article_data = {
            "id": 1,
            "title": "Complete Test Article",
            "link": "https://example.com/complete-article",
            "summary": "Complete test summary",
            "source": "Complete Test Source",
            "source_type": "RSS News",
            "published_date": datetime(2024, 1, 15, 10, 30, 0),
            "created_at": datetime(2024, 1, 15, 10, 35, 0),
            "updated_at": datetime(2024, 1, 15, 10, 40, 0),
            "processed": True,
            "extracted_content": "Full article content here",
            "ai_summary": "AI-generated summary",
            "image_url": "https://example.com/image.jpg",
        }

        # Test ArticleDetail creation
        detail = ArticleDetail(**article_data)
        assert detail.id == 1
        assert detail.processed is True

        # Test conversion to ArticleSummary (subset of fields)
        summary_data = {
            k: v
            for k, v in article_data.items()
            if k
            in [
                "id",
                "title",
                "link",
                "summary",
                "source",
                "source_type",
                "published_date",
                "created_at",
                "image_url",
            ]
        }
        summary = ArticleSummary(**summary_data)
        assert summary.id == 1
        assert summary.title == "Complete Test Article"

        # Test in paginated response
        pagination = PaginationInfo(page=1, per_page=20, total_items=1, total_pages=1, has_next=False, has_prev=False)
        paginated = PaginatedArticles(articles=[summary], pagination=pagination)

        assert len(paginated.articles) == 1
        assert paginated.pagination.total_items == 1
