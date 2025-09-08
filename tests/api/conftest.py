#!/usr/bin/env python3
"""
Test fixtures and configuration for API tests
"""
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))  # noqa

from api.app import app  # noqa
from api.routes.articles import get_db as get_articles_db  # noqa
from api.routes.sources import get_db as get_sources_db  # noqa
from database.models import RSSArticle  # noqa


@pytest.fixture
def client(mock_api_operations):
    """FastAPI test client with mocked database dependencies"""

    # Override the dependencies
    def override_get_db():
        yield mock_api_operations

    app.dependency_overrides[get_articles_db] = override_get_db
    app.dependency_overrides[get_sources_db] = override_get_db

    test_client = TestClient(app)

    yield test_client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def mock_api_operations():
    """Mock APIOperations instance"""
    mock_ops = Mock()
    mock_ops.close = Mock()
    return mock_ops


@pytest.fixture
def sample_article():
    """Sample article for testing"""
    return RSSArticle(
        id=1,
        original_title="Test Article Title",
        original_link="https://example.com/test-article",
        original_summary="This is a test article summary",
        original_source="Test Source",
        source_type="RSS News",
        original_pubdate=datetime(2024, 1, 15, 10, 30, 0),
        url_hash="abc123",
        created_at=datetime(2024, 1, 15, 10, 35, 0),
        processed=True,
        extracted_content="Full article content here",
        ai_summary="AI generated summary",
        image_url="https://example.com/image.jpg",
        updated_at=datetime(2024, 1, 15, 10, 40, 0),
    )


@pytest.fixture
def sample_articles():
    """List of sample articles for testing"""
    articles = []
    for i in range(1, 6):
        article = RSSArticle(
            id=i,
            original_title=f"Test Article {i}",
            original_link=f"https://example.com/test-article-{i}",
            original_summary=f"This is test article {i} summary",
            original_source=f"Test Source {i % 3 + 1}",  # Rotate through 3 sources
            source_type="RSS News",
            original_pubdate=datetime(2024, 1, 15 + i, 10, 30, 0),
            url_hash=f"abc12{i}",
            created_at=datetime(2024, 1, 15 + i, 10, 35, 0),
            processed=True,
            extracted_content=f"Full article {i} content here",
            ai_summary=f"AI generated summary {i}",
            image_url=f"https://example.com/image{i}.jpg",
            updated_at=datetime(2024, 1, 15 + i, 10, 40, 0),
        )
        articles.append(article)
    return articles


@pytest.fixture
def sample_recent_articles():
    """Recent articles for testing"""
    now = datetime.now()
    articles = []
    for i in range(3):
        article = RSSArticle(
            id=i + 10,
            original_title=f"Recent Article {i + 1}",
            original_link=f"https://example.com/recent-{i + 1}",
            original_summary=f"Recent article {i + 1} summary",
            original_source="Recent Source",
            source_type="RSS News",
            original_pubdate=now - timedelta(hours=i),
            url_hash=f"recent{i}",
            created_at=now - timedelta(hours=i),
            processed=True,
            extracted_content=f"Recent content {i + 1}",
            ai_summary=f"Recent AI summary {i + 1}",
            image_url=f"https://example.com/recent{i + 1}.jpg",
            updated_at=now - timedelta(hours=i),
        )
        articles.append(article)
    return articles


@pytest.fixture
def sample_sources_stats():
    """Sample source statistics"""
    return [
        {
            "name": "BBC News",
            "article_count": 25,
            "processed_count": 23,
            "latest_article": "2024-01-20T15:30:00",
        },
        {
            "name": "Manchester Evening News",
            "article_count": 18,
            "processed_count": 16,
            "latest_article": "2024-01-20T14:20:00",
        },
        {
            "name": "Stockport Nub News",
            "article_count": 12,
            "processed_count": 12,
            "latest_article": "2024-01-20T13:10:00",
        },
    ]
