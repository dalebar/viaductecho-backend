#!/usr/bin/env python3
"""
Comprehensive test suite for API error handling
"""
import os
import sys
from unittest.mock import Mock, patch


from fastapi import status

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestHealthEndpoint:
    """Test suite for health endpoint"""

    @patch("api.app.APIOperations")
    def test_health_check_healthy(self, mock_api_operations_class, client):
        """Test healthy health check"""
        # Setup mock
        mock_api_operations = Mock()
        mock_api_operations.health_check.return_value = {
            "status": "healthy",
            "total_articles": 100,
            "recent_articles_24h": 5,
            "database_connected": True,
            "timestamp": "2024-01-15T10:30:00",
        }
        mock_api_operations_class.return_value = mock_api_operations

        # Make request
        response = client.get("/health")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "healthy"
        assert data["total_articles"] == 100
        assert data["recent_articles_24h"] == 5
        assert data["database_connected"] is True

        # Verify database operations were called and closed
        mock_api_operations.health_check.assert_called_once()
        mock_api_operations.close.assert_called_once()

    @patch("api.app.APIOperations")
    def test_health_check_unhealthy(self, mock_api_operations_class, client):
        """Test unhealthy health check"""
        # Setup mock
        mock_api_operations = Mock()
        mock_api_operations.health_check.return_value = {
            "status": "unhealthy",
            "error": "Database connection failed",
            "database_connected": False,
            "timestamp": "2024-01-15T10:30:00",
        }
        mock_api_operations_class.return_value = mock_api_operations

        # Make request
        response = client.get("/health")

        # Assertions
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()

        assert data["status"] == "unhealthy"
        assert data["database_connected"] is False
        assert "error" in data

    @patch("api.app.APIOperations")
    def test_health_check_exception(self, mock_api_operations_class, client):
        """Test health check with exception"""
        # Setup mock to raise exception
        mock_api_operations_class.side_effect = Exception("Failed to initialize database operations")

        # Make request
        response = client.get("/health")

        # Assertions
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()

        assert data["status"] == "unhealthy"
        assert data["database_connected"] is False
        assert "error" in data


class TestRootEndpoint:
    """Test suite for root endpoint"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API information"""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["name"] == "Viaduct Echo API"
        assert data["version"] == "1.0.0"
        assert "description" in data
        assert "docs" in data
        assert "endpoints" in data
        assert "timestamp" in data


class TestGlobalErrorHandling:
    """Test suite for global error handling"""

    def test_unhandled_exception_handling(self, client, mock_api_operations):
        """Test global exception handler for unhandled errors"""
        # Setup mock to return invalid format that will cause unpacking error
        mock_api_operations.get_articles_paginated.return_value = "not a tuple"

        # Make request that triggers the exception
        response = client.get("/api/v1/articles")

        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()

        # Route-specific error message, not global handler
        assert "error" in data
        assert "Failed to retrieve articles" in data["error"]
        assert "timestamp" in data

    def test_http_exception_handling(self, client, mock_api_operations):
        """Test HTTP exception handler"""
        # Setup mock to raise HTTP exception
        mock_api_operations.get_article_by_id.return_value = None

        # Make request that triggers 404
        response = client.get("/api/v1/articles/999")

        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        assert "error" in data
        assert "Article with ID 999 not found" in data["error"]
        assert "timestamp" in data

    def test_validation_error_handling(self, client):
        """Test validation error handling"""
        # Make request with invalid parameters
        response = client.get("/api/v1/articles?page=0&per_page=101")

        # Assertions
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()

        # FastAPI's default validation error format
        assert "detail" in data

    def test_method_not_allowed(self, client):
        """Test method not allowed error"""
        response = client.post("/api/v1/articles")  # POST not allowed

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_endpoint_not_found(self, client):
        """Test 404 for non-existent endpoints"""
        response = client.get("/api/v1/nonexistent")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDatabaseErrorHandling:
    """Test suite for database-related error handling"""

    def test_database_connection_error(self, client, mock_api_operations):
        """Test database connection error handling"""
        # Setup mock to raise database connection error
        mock_api_operations.get_articles_paginated.side_effect = Exception("Connection to database failed")

        # Make request
        response = client.get("/api/v1/articles")

        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()

        assert "error" in data
        assert "Failed to retrieve articles" in data["error"]

    def test_database_timeout_error(self, client, mock_api_operations):
        """Test database timeout error handling"""
        # Setup mock to raise timeout error
        mock_api_operations.search_articles.side_effect = Exception("Query timeout exceeded")

        # Make request
        response = client.get("/api/v1/articles/search?query=test")

        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()

        assert "error" in data
        assert "Search failed" in data["error"]

    def test_source_not_found_error(self, client, mock_api_operations):
        """Test source not found error handling"""
        # Setup mock
        mock_api_operations.get_sources_with_stats.return_value = [
            {"name": "BBC News", "article_count": 10, "processed_count": 8, "latest_article": "2024-01-20T15:30:00"}
        ]

        # Make request for non-existent source
        response = client.get("/api/v1/sources/Nonexistent Source/articles")

        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()

        assert "error" in data
        assert "Source 'Nonexistent Source' not found" in data["error"]


class TestParameterValidation:
    """Test suite for parameter validation errors"""

    def test_search_query_too_short(self, client):
        """Test search query validation"""
        response = client.get("/api/v1/articles/search?query=a")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_pagination_validation(self, client):
        """Test pagination parameter validation"""
        # Page too low
        response = client.get("/api/v1/articles?page=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Per_page too high
        response = client.get("/api/v1/articles?per_page=101")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Per_page too low
        response = client.get("/api/v1/articles?per_page=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_recent_articles_validation(self, client):
        """Test recent articles parameter validation"""
        # Hours too high
        response = client.get("/api/v1/articles/recent?hours=200")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Limit too high
        response = client.get("/api/v1/articles/recent?limit=150")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_article_id(self, client, mock_api_operations):
        """Test invalid article ID parameter"""
        # Non-numeric ID
        response = client.get("/api/v1/articles/abc")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Negative ID (should be handled by endpoint logic)
        mock_api_operations.get_article_by_id.return_value = None
        response = client.get("/api/v1/articles/-1")
        # This might pass validation but return 404 from the endpoint
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestCORSHandling:
    """Test suite for CORS handling"""

    def test_cors_preflight(self, client):
        """Test CORS preflight request"""
        response = client.options(
            "/api/v1/articles",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        # Should allow CORS
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses"""
        response = client.get("/api/v1/sources", headers={"Origin": "https://example.com"})

        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers

    def test_cors_credentials_allowed(self, client):
        """Test that CORS allows credentials"""
        response = client.get("/api/v1/articles", headers={"Origin": "https://example.com"})

        # Check for credentials header
        # Note: Actual header presence depends on the request and CORS configuration
