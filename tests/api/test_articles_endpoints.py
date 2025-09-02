#!/usr/bin/env python3
"""
Comprehensive test suite for Articles API endpoints
"""
import os
import sys

from fastapi import status

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestArticlesEndpoints:
    """Test suite for Articles API endpoints"""

    def test_get_articles_success(self, client, mock_api_operations, sample_articles):
        """Test successful articles retrieval"""
        # Setup mock
        mock_api_operations.get_articles_paginated.return_value = (sample_articles[:2], 10)

        # Make request
        response = client.get("/api/v1/articles?page=1&per_page=2")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "articles" in data
        assert "pagination" in data
        assert len(data["articles"]) == 2
        assert data["pagination"]["total_items"] == 10
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["per_page"] == 2
        assert data["pagination"]["has_next"] is True
        assert data["pagination"]["has_prev"] is False

        # Verify article structure
        article = data["articles"][0]
        assert article["id"] == 1
        assert article["title"] == "Test Article 1"
        assert article["link"] == "https://example.com/test-article-1"
        assert article["source"] == "Test Source 2"  # i=1: 1%3+1=2

    def test_get_articles_with_source_filter(self, client, mock_api_operations, sample_articles):
        """Test articles retrieval with source filter"""
        # Setup mock
        mock_api_operations.get_articles_paginated.return_value = (sample_articles[:1], 5)

        # Make request
        response = client.get("/api/v1/articles?source=Test Source 1")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["articles"]) == 1

        # Verify the correct parameters were passed
        mock_api_operations.get_articles_paginated.assert_called_once_with(
            page=1, per_page=20, source="Test Source 1", processed_only=True
        )

    def test_get_articles_validation(self, client, mock_api_operations):
        """Test articles endpoint parameter validation"""
        # Setup mock
        mock_api_operations.get_articles_paginated.return_value = ([], 0)

        # Test invalid page number
        response = client.get("/api/v1/articles?page=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test invalid per_page (too high)
        response = client.get("/api/v1/articles?per_page=101")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test valid edge cases
        response = client.get("/api/v1/articles?page=1&per_page=100")
        assert response.status_code == status.HTTP_200_OK

    def test_get_articles_database_error(self, client, mock_api_operations):
        """Test articles endpoint with database error"""
        # Setup mock to raise exception
        mock_api_operations.get_articles_paginated.side_effect = Exception("Database connection failed")

        # Make request
        response = client.get("/api/v1/articles")

        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "error" in data
        assert "Failed to retrieve articles" in data["error"]

    def test_get_article_by_id_success(self, client, mock_api_operations, sample_article):
        """Test successful single article retrieval"""
        # Setup mock
        mock_api_operations.get_article_by_id.return_value = sample_article

        # Make request
        response = client.get("/api/v1/articles/1")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == 1
        assert data["title"] == "Test Article Title"
        assert data["link"] == "https://example.com/test-article"
        assert data["summary"] == "This is a test article summary"
        assert data["source"] == "Test Source"
        assert data["extracted_content"] == "Full article content here"
        assert data["ai_summary"] == "AI generated summary"
        assert data["processed"] is True

    def test_get_article_by_id_not_found(self, client, mock_api_operations):
        """Test single article retrieval when not found"""
        # Setup mock
        mock_api_operations.get_article_by_id.return_value = None

        # Make request
        response = client.get("/api/v1/articles/999")

        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
        assert "Article with ID 999 not found" in data["error"]

    def test_get_article_by_id_database_error(self, client, mock_api_operations):
        """Test single article retrieval with database error"""
        # Setup mock to raise exception
        mock_api_operations.get_article_by_id.side_effect = Exception("Database error")

        # Make request
        response = client.get("/api/v1/articles/1")

        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "error" in data
        assert "Failed to retrieve article" in data["error"]

    def test_get_recent_articles_success(self, client, mock_api_operations, sample_recent_articles):
        """Test successful recent articles retrieval"""
        # Setup mock
        mock_api_operations.get_recent_articles.return_value = sample_recent_articles

        # Make request
        response = client.get("/api/v1/articles/recent?hours=12&limit=10")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 3
        assert data[0]["title"] == "Recent Article 1"
        assert data[1]["title"] == "Recent Article 2"
        assert data[2]["title"] == "Recent Article 3"

        # Verify correct parameters were passed
        mock_api_operations.get_recent_articles.assert_called_once_with(hours=12, limit=10)

    def test_get_recent_articles_defaults(self, client, mock_api_operations):
        """Test recent articles with default parameters"""
        # Setup mock
        mock_api_operations.get_recent_articles.return_value = []

        # Make request without parameters
        response = client.get("/api/v1/articles/recent")

        # Assertions
        assert response.status_code == status.HTTP_200_OK

        # Verify default parameters were used
        mock_api_operations.get_recent_articles.assert_called_once_with(hours=24, limit=50)

    def test_get_recent_articles_validation(self, client, mock_api_operations):
        """Test recent articles parameter validation"""
        # Test invalid hours (too high)
        response = client.get("/api/v1/articles/recent?hours=200")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test invalid limit (too high)
        response = client.get("/api/v1/articles/recent?limit=150")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test valid edge cases
        mock_api_operations.get_recent_articles.return_value = []

        response = client.get("/api/v1/articles/recent?hours=168&limit=100")
        assert response.status_code == status.HTTP_200_OK

    def test_search_articles_success(self, client, mock_api_operations, sample_articles):
        """Test successful article search"""
        # Setup mock
        mock_api_operations.search_articles.return_value = (sample_articles[:2], 5)

        # Make request
        response = client.get("/api/v1/articles/search?query=test&page=1&per_page=2")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "articles" in data
        assert "pagination" in data
        assert len(data["articles"]) == 2
        assert data["pagination"]["total_items"] == 5

        # Verify correct parameters were passed
        mock_api_operations.search_articles.assert_called_once_with(query="test", page=1, per_page=2)

    def test_search_articles_empty_query(self, client, mock_api_operations):
        """Test search with empty query"""
        # Test missing query
        response = client.get("/api/v1/articles/search")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test query too short
        response = client.get("/api/v1/articles/search?query=a")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_search_articles_no_results(self, client, mock_api_operations):
        """Test search with no results"""
        # Setup mock
        mock_api_operations.search_articles.return_value = ([], 0)

        # Make request
        response = client.get("/api/v1/articles/search?query=nonexistent")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["articles"]) == 0
        assert data["pagination"]["total_items"] == 0
        assert data["pagination"]["total_pages"] == 0

    def test_search_articles_database_error(self, client, mock_api_operations):
        """Test search with database error"""
        # Setup mock to raise exception
        mock_api_operations.search_articles.side_effect = Exception("Search index error")

        # Make request
        response = client.get("/api/v1/articles/search?query=test")

        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "error" in data
        assert "Search failed" in data["error"]

    def test_pagination_info_calculation(self, client, mock_api_operations, sample_articles):
        """Test pagination information calculation"""
        # Setup mock - 47 total items, page 3, 10 per page
        mock_api_operations.get_articles_paginated.return_value = (sample_articles[:3], 47)

        # Make request
        response = client.get("/api/v1/articles?page=3&per_page=10")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        pagination = data["pagination"]
        assert pagination["page"] == 3
        assert pagination["per_page"] == 10
        assert pagination["total_items"] == 47
        assert pagination["total_pages"] == 5  # ceil(47/10)
        assert pagination["has_next"] is True  # page 3 of 5
        assert pagination["has_prev"] is True  # page 3

    def test_pagination_edge_cases(self, client, mock_api_operations):
        """Test pagination edge cases"""

        # Test last page
        mock_api_operations.get_articles_paginated.return_value = ([], 25)
        response = client.get("/api/v1/articles?page=3&per_page=10")

        assert response.status_code == status.HTTP_200_OK
        pagination = response.json()["pagination"]
        assert pagination["page"] == 3
        assert pagination["total_pages"] == 3  # ceil(25/10)
        assert pagination["has_next"] is False
        assert pagination["has_prev"] is True

        # Test first page
        mock_api_operations.get_articles_paginated.return_value = ([], 25)
        response = client.get("/api/v1/articles?page=1&per_page=10")

        assert response.status_code == status.HTTP_200_OK
        pagination = response.json()["pagination"]
        assert pagination["has_next"] is True
        assert pagination["has_prev"] is False

        # Test empty results
        mock_api_operations.get_articles_paginated.return_value = ([], 0)
        response = client.get("/api/v1/articles?page=1&per_page=10")

        assert response.status_code == status.HTTP_200_OK
        pagination = response.json()["pagination"]
        assert pagination["total_pages"] == 0
        assert pagination["has_next"] is False
        assert pagination["has_prev"] is False
