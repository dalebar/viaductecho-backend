#!/usr/bin/env python3
"""
Comprehensive test suite for APIOperations class
"""
import os
import sys

from unittest.mock import Mock, patch
from datetime import datetime

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from database.api_operations import APIOperations


class TestAPIOperations:
    """Test suite for APIOperations class"""

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_initialization(self, mock_init):
        """Test APIOperations initializes correctly"""
        mock_init.return_value = None

        api_ops = APIOperations()

        assert isinstance(api_ops, APIOperations)
        mock_init.assert_called_once()

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_get_articles_paginated_success(self, mock_init, sample_articles):
        """Test successful paginated article retrieval"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()

        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 25
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = sample_articles[:3]
        api_ops.session.query.return_value = mock_query

        articles, total_count = api_ops.get_articles_paginated(page=1, per_page=3)

        assert len(articles) == 3
        assert total_count == 25
        assert articles[0].original_title == "Test Article 1"

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_get_articles_paginated_with_source_filter(
        self, mock_init, sample_articles
    ):
        """Test paginated articles with source filter"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()

        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 8
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_articles[0], sample_articles[3]]
        api_ops.session.query.return_value = mock_query

        articles, total_count = api_ops.get_articles_paginated(
            page=1, per_page=20, source="Test Source 1"
        )

        assert len(articles) == 2
        assert total_count == 8
        # Verify source filter was applied
        api_ops.session.query.return_value.filter.assert_called()

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_get_articles_paginated_validation(self, mock_init):
        """Test pagination parameter validation"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        api_ops.session.query.return_value = mock_query

        # Test parameter validation
        articles, total_count = api_ops.get_articles_paginated(page=-1, per_page=150)

        # Check that offset is calculated correctly (page should be normalized to 1)
        mock_query.offset.assert_called_with(0)  # (1-1) * per_page
        # Check that per_page is capped at 100
        mock_query.limit.assert_called_with(100)

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_get_recent_articles_success(self, mock_init, sample_recent_articles):
        """Test successful recent articles retrieval"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()

        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = sample_recent_articles
        api_ops.session.query.return_value = mock_query

        articles = api_ops.get_recent_articles(hours=24, limit=10)

        assert len(articles) == 3
        assert articles[0].original_title == "Recent Article 1"
        # Verify limit was applied
        mock_query.limit.assert_called_with(10)

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_get_recent_articles_validation(self, mock_init):
        """Test recent articles parameter validation"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        api_ops.session.query.return_value = mock_query

        # Test limit validation (should cap at 100)
        api_ops.get_recent_articles(hours=24, limit=150)

        mock_query.limit.assert_called_with(100)

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_search_articles_success(self, mock_init, sample_articles):
        """Test successful article search"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()

        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = sample_articles[:2]
        api_ops.session.query.return_value = mock_query

        articles, total_count = api_ops.search_articles("test", page=1, per_page=2)

        assert len(articles) == 2
        assert total_count == 5
        # Verify search filter was applied
        mock_query.filter.assert_called()

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_search_articles_empty_query(self, mock_init):
        """Test search with empty query"""
        mock_init.return_value = None

        api_ops = APIOperations()

        # Test with empty string
        articles, total_count = api_ops.search_articles("", page=1, per_page=20)
        assert articles == []
        assert total_count == 0

        # Test with whitespace only
        articles, total_count = api_ops.search_articles("  ", page=1, per_page=20)
        assert articles == []
        assert total_count == 0

        # Test with single character
        articles, total_count = api_ops.search_articles("a", page=1, per_page=20)
        assert articles == []
        assert total_count == 0

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_get_articles_by_source(self, mock_init, sample_articles):
        """Test getting articles by source"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()

        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 10
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = sample_articles[:3]
        api_ops.session.query.return_value = mock_query

        articles, total_count = api_ops.get_articles_by_source(
            "Test Source", page=1, per_page=3
        )

        assert len(articles) == 3
        assert total_count == 10

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_get_article_by_id_success(self, mock_init, sample_article):
        """Test successful single article retrieval"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()
        api_ops.logger = Mock()

        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_article
        api_ops.session.query.return_value = mock_query

        article = api_ops.get_article_by_id(1)

        assert article is not None
        assert article.id == 1
        assert article.original_title == "Test Article Title"

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_get_article_by_id_not_found(self, mock_init):
        """Test article not found"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()
        api_ops.logger = Mock()

        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        api_ops.session.query.return_value = mock_query

        article = api_ops.get_article_by_id(999)

        assert article is None

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_get_article_by_id_exception(self, mock_init):
        """Test article retrieval with exception"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()
        api_ops.logger = Mock()

        # Mock exception
        api_ops.session.query.side_effect = Exception("Database error")

        article = api_ops.get_article_by_id(1)

        assert article is None
        api_ops.logger.error.assert_called_once()

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_get_sources_with_stats_success(self, mock_init, sample_sources_stats):
        """Test successful source statistics retrieval"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()
        api_ops.logger = Mock()

        # Mock query results
        mock_results = []
        for source in sample_sources_stats:
            mock_result = Mock()
            mock_result.original_source = source["name"]
            mock_result.article_count = source["article_count"]
            mock_result.processed_count = source["processed_count"]
            mock_result.latest_article = datetime.fromisoformat(
                source["latest_article"]
            )
            mock_results.append(mock_result)

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_results
        api_ops.session.query.return_value = mock_query

        sources = api_ops.get_sources_with_stats()

        assert len(sources) == 3
        assert sources[0]["name"] == "BBC News"
        assert sources[0]["article_count"] == 25
        assert sources[0]["processed_count"] == 23

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_get_sources_with_stats_exception(self, mock_init):
        """Test source statistics retrieval with exception"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()
        api_ops.logger = Mock()

        # Mock exception
        api_ops.session.query.side_effect = Exception("Database error")

        sources = api_ops.get_sources_with_stats()

        assert sources == []
        api_ops.logger.error.assert_called_once()

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_get_article_count_success(self, mock_init):
        """Test successful article count"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()
        api_ops.logger = Mock()

        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 42
        api_ops.session.query.return_value = mock_query

        count = api_ops.get_article_count(processed_only=True)

        assert count == 42
        mock_query.filter.assert_called_once()

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_get_article_count_all_articles(self, mock_init):
        """Test article count including unprocessed"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()
        api_ops.logger = Mock()

        # Mock query chain
        mock_query = Mock()
        mock_query.count.return_value = 55
        api_ops.session.query.return_value = mock_query

        count = api_ops.get_article_count(processed_only=False)

        assert count == 55
        # Should not call filter when processed_only=False
        mock_query.filter.assert_not_called()

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_get_article_count_exception(self, mock_init):
        """Test article count with exception"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()
        api_ops.logger = Mock()

        # Mock exception
        api_ops.session.query.side_effect = Exception("Database error")

        count = api_ops.get_article_count()

        assert count == 0
        api_ops.logger.error.assert_called_once()

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_health_check_healthy(self, mock_init):
        """Test healthy system health check"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()
        api_ops.logger = Mock()

        # Mock successful operations
        api_ops.get_article_count = Mock(return_value=100)
        api_ops.get_recent_articles = Mock(return_value=[Mock(), Mock()])
        api_ops.session.execute = Mock()

        health = api_ops.health_check()

        assert health["status"] == "healthy"
        assert health["total_articles"] == 100
        assert health["recent_articles_24h"] == 2
        assert health["database_connected"] is True
        assert "timestamp" in health

    @patch("database.api_operations.DatabaseOperations.__init__")
    def test_health_check_unhealthy(self, mock_init):
        """Test unhealthy system health check"""
        mock_init.return_value = None

        api_ops = APIOperations()
        api_ops.session = Mock()
        api_ops.logger = Mock()

        # Mock database failure
        api_ops.get_article_count = Mock(
            side_effect=Exception("Database connection failed")
        )

        health = api_ops.health_check()

        assert health["status"] == "unhealthy"
        assert health["database_connected"] is False
        assert "error" in health
        assert "timestamp" in health
        api_ops.logger.error.assert_called_once()
