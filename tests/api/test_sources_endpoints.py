#!/usr/bin/env python3
"""
Comprehensive test suite for Sources API endpoints
"""
import os
import sys

from unittest.mock import patch


from fastapi import status

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestSourcesEndpoints:
    """Test suite for Sources API endpoints"""

    @patch("api.routes.sources.get_db")
    def test_get_sources_success(self, mock_get_db, client, mock_api_operations, sample_sources_stats):
        """Test successful sources retrieval"""
        # Setup mock
        mock_get_db.return_value = mock_api_operations
        mock_api_operations.get_sources_with_stats.return_value = sample_sources_stats

        # Make request
        response = client.get("/api/v1/sources")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "sources" in data
        assert "total_sources" in data
        assert len(data["sources"]) == 3
        assert data["total_sources"] == 3

        # Verify source structure
        source = data["sources"][0]
        assert source["name"] == "BBC News"
        assert source["article_count"] == 25
        assert source["processed_count"] == 23
        assert source["latest_article"] == "2024-01-20T15:30:00"

    @patch("api.routes.sources.get_db")
    def test_get_sources_empty(self, mock_get_db, client, mock_api_operations):
        """Test sources retrieval with no sources"""
        # Setup mock
        mock_get_db.return_value = mock_api_operations
        mock_api_operations.get_sources_with_stats.return_value = []

        # Make request
        response = client.get("/api/v1/sources")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["sources"] == []
        assert data["total_sources"] == 0

    @patch("api.routes.sources.get_db")
    def test_get_sources_database_error(self, mock_get_db, client, mock_api_operations):
        """Test sources retrieval with database error"""
        # Setup mock to raise exception
        mock_get_db.return_value = mock_api_operations
        mock_api_operations.get_sources_with_stats.side_effect = Exception("Database connection failed")

        # Make request
        response = client.get("/api/v1/sources")

        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "error" in data
        assert "Failed to retrieve sources" in data["error"]

    @patch("api.routes.sources.get_db")
    def test_get_articles_by_source_success(
        self, mock_get_db, client, mock_api_operations, sample_sources_stats, sample_articles
    ):
        """Test successful articles by source retrieval"""
        # Setup mock
        mock_get_db.return_value = mock_api_operations
        mock_api_operations.get_sources_with_stats.return_value = sample_sources_stats
        mock_api_operations.get_articles_by_source.return_value = (sample_articles[:3], 15)

        # Make request
        response = client.get("/api/v1/sources/BBC News/articles?page=1&per_page=3")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "articles" in data
        assert "pagination" in data
        assert len(data["articles"]) == 3
        assert data["pagination"]["total_items"] == 15
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["per_page"] == 3

        # Verify correct parameters were passed
        mock_api_operations.get_articles_by_source.assert_called_once_with(source="BBC News", page=1, per_page=3)

    @patch("api.routes.sources.get_db")
    def test_get_articles_by_source_not_found(self, mock_get_db, client, mock_api_operations, sample_sources_stats):
        """Test articles by source when source doesn't exist"""
        # Setup mock
        mock_get_db.return_value = mock_api_operations
        mock_api_operations.get_sources_with_stats.return_value = sample_sources_stats

        # Make request with non-existent source
        response = client.get("/api/v1/sources/Nonexistent Source/articles")

        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
        assert "Source 'Nonexistent Source' not found" in data["error"]

    @patch("api.routes.sources.get_db")
    def test_get_articles_by_source_empty_results(self, mock_get_db, client, mock_api_operations, sample_sources_stats):
        """Test articles by source with no articles"""
        # Setup mock
        mock_get_db.return_value = mock_api_operations
        mock_api_operations.get_sources_with_stats.return_value = sample_sources_stats
        mock_api_operations.get_articles_by_source.return_value = ([], 0)

        # Make request
        response = client.get("/api/v1/sources/BBC News/articles")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["articles"]) == 0
        assert data["pagination"]["total_items"] == 0
        assert data["pagination"]["total_pages"] == 0

    @patch("api.routes.sources.get_db")
    def test_get_articles_by_source_validation(self, mock_get_db, client, mock_api_operations, sample_sources_stats):
        """Test articles by source parameter validation"""
        # Setup mock
        mock_get_db.return_value = mock_api_operations
        mock_api_operations.get_sources_with_stats.return_value = sample_sources_stats
        mock_api_operations.get_articles_by_source.return_value = ([], 0)

        # Test invalid page number
        response = client.get("/api/v1/sources/BBC News/articles?page=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test invalid per_page (too high)
        response = client.get("/api/v1/sources/BBC News/articles?per_page=101")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test valid edge cases
        response = client.get("/api/v1/sources/BBC News/articles?page=1&per_page=100")
        assert response.status_code == status.HTTP_200_OK

    @patch("api.routes.sources.get_db")
    def test_get_articles_by_source_database_error(
        self, mock_get_db, client, mock_api_operations, sample_sources_stats
    ):
        """Test articles by source with database error"""
        # Setup mock
        mock_get_db.return_value = mock_api_operations
        mock_api_operations.get_sources_with_stats.return_value = sample_sources_stats
        mock_api_operations.get_articles_by_source.side_effect = Exception("Database query failed")

        # Make request
        response = client.get("/api/v1/sources/BBC News/articles")

        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "error" in data
        assert "Failed to retrieve articles from source 'BBC News'" in data["error"]

    @patch("api.routes.sources.get_db")
    def test_get_articles_by_source_special_characters(
        self, mock_get_db, client, mock_api_operations, sample_sources_stats
    ):
        """Test articles by source with special characters in source name"""
        # Add source with special characters
        special_source_stats = sample_sources_stats + [
            {
                "name": "Source & News (UK)",
                "article_count": 5,
                "processed_count": 4,
                "latest_article": "2024-01-20T12:00:00",
            }
        ]

        # Setup mock
        mock_get_db.return_value = mock_api_operations
        mock_api_operations.get_sources_with_stats.return_value = special_source_stats
        mock_api_operations.get_articles_by_source.return_value = ([], 5)

        # Make request with URL-encoded source name
        response = client.get("/api/v1/sources/Source%20%26%20News%20%28UK%29/articles")

        # Assertions
        assert response.status_code == status.HTTP_200_OK

        # Verify correct parameters were passed (FastAPI handles URL decoding)
        mock_api_operations.get_articles_by_source.assert_called_once_with(
            source="Source & News (UK)", page=1, per_page=20
        )

    @patch("api.routes.sources.get_db")
    def test_sources_response_format(self, mock_get_db, client, mock_api_operations, sample_sources_stats):
        """Test sources response format matches schema"""
        # Setup mock
        mock_get_db.return_value = mock_api_operations
        mock_api_operations.get_sources_with_stats.return_value = sample_sources_stats

        # Make request
        response = client.get("/api/v1/sources")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert isinstance(data["sources"], list)
        assert isinstance(data["total_sources"], int)

        # Verify each source has required fields
        for source in data["sources"]:
            assert "name" in source
            assert "article_count" in source
            assert "processed_count" in source
            assert "latest_article" in source

            assert isinstance(source["name"], str)
            assert isinstance(source["article_count"], int)
            assert isinstance(source["processed_count"], int)
            assert source["article_count"] >= 0
            assert source["processed_count"] >= 0
            assert source["processed_count"] <= source["article_count"]

    @patch("api.routes.sources.get_db")
    def test_articles_by_source_pagination(
        self, mock_get_db, client, mock_api_operations, sample_sources_stats, sample_articles
    ):
        """Test pagination for articles by source"""
        # Setup mock
        mock_get_db.return_value = mock_api_operations
        mock_api_operations.get_sources_with_stats.return_value = sample_sources_stats
        mock_api_operations.get_articles_by_source.return_value = (sample_articles[:2], 23)

        # Make request
        response = client.get("/api/v1/sources/BBC News/articles?page=2&per_page=10")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        pagination = data["pagination"]
        assert pagination["page"] == 2
        assert pagination["per_page"] == 10
        assert pagination["total_items"] == 23
        assert pagination["total_pages"] == 3  # ceil(23/10)
        assert pagination["has_next"] is True  # page 2 of 3
        assert pagination["has_prev"] is True  # page 2
