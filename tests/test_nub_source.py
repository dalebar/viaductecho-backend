#!/usr/bin/env python3
"""
Comprehensive test suite for NubSource class
"""

import os
import sys
import json
from datetime import datetime
from unittest.mock import Mock, patch

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sources.nub_source import NubSource  # noqa: E402
from sources.base_source import BaseNewsSource  # noqa: E402


def create_mock_nub_article(headline, url, date_published):
    """Helper function to create mock Nub News article JSON data"""
    return {"headline": headline, "url": url, "datePublished": date_published}


def create_mock_response(articles_data, status_code=200):
    """Helper function to create mock HTTP response"""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.raise_for_status.return_value = (
        None if status_code < 400 else Exception(f"HTTP {status_code}")
    )

    # Create mock HTML content with JSON-LD script tag
    json_content = json.dumps(articles_data)
    html_content = f"""
    <html>
        <head>
            <script type="application/ld+json">{json_content}</script>
        </head>
        <body>
            <div>Mock Nub News content</div>
        </body>
    </html>
    """

    mock_response.content = html_content.encode("utf-8")
    return mock_response


class TestNubSource:
    """Test suite for NubSource class"""

    def test_initialization(self):
        """Test NubSource initializes correctly"""
        source = NubSource()

        assert isinstance(source, BaseNewsSource)
        assert source.source_name == "Stockport Nub News"
        assert source.base_url == "https://stockport.nub.news/news"
        assert "User-Agent" in source.headers
        assert "ViaductBot" in source.headers["User-Agent"]

    def test_inherits_from_base_news_source(self):
        """Test that NubSource properly inherits from BaseNewsSource"""
        source = NubSource()

        assert isinstance(source, BaseNewsSource)
        assert hasattr(source, "filter_articles")
        assert callable(source.fetch_articles)

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_fetch_articles_success(self, mock_get, mock_sleep):
        """Test successful article fetching"""
        # Setup mock response data
        articles_data = [
            create_mock_nub_article(
                "Stockport town centre gets new public art installation",
                "https://stockport.nub.news/news/stockport-art-installation",
                "2024-03-15 10:30:00",
            ),
            create_mock_nub_article(
                "Local community group organizes charity event",
                "https://stockport.nub.news/news/charity-event",
                "2024-03-15 14:45:00",
            ),
            create_mock_nub_article(
                "New bus route connects Stockport neighborhoods",
                "https://stockport.nub.news/news/bus-route",
                "2024-03-15 16:20:00",
            ),
        ]

        mock_response = create_mock_response(articles_data)
        mock_get.return_value = mock_response

        source = NubSource()

        with patch("logging.info") as mock_log_info:
            articles = source.fetch_articles()

            assert len(articles) == 3

            # Check first article
            assert (
                articles[0]["original_title"]
                == "Stockport town centre gets new public art installation"
            )
            assert (
                articles[0]["original_link"]
                == "https://stockport.nub.news/news/stockport-art-installation"
            )
            assert (
                articles[0]["original_summary"]
                == "Stockport town centre gets new public art installation"
            )
            assert articles[0]["original_source"] == "Stockport Nub News"
            assert articles[0]["source_type"] == "Web scraping"
            assert articles[0]["original_pubdate"] == datetime(2024, 3, 15, 10, 30, 0)

            # Check second article
            assert (
                articles[1]["original_title"]
                == "Local community group organizes charity event"
            )
            assert (
                articles[1]["original_link"]
                == "https://stockport.nub.news/news/charity-event"
            )
            assert (
                articles[1]["original_summary"]
                == "Local community group organizes charity event"
            )
            assert articles[1]["original_source"] == "Stockport Nub News"
            assert articles[1]["source_type"] == "Web scraping"
            assert articles[1]["original_pubdate"] == datetime(2024, 3, 15, 14, 45, 0)

            # Check third article
            assert (
                articles[2]["original_title"]
                == "New bus route connects Stockport neighborhoods"
            )
            assert (
                articles[2]["original_link"]
                == "https://stockport.nub.news/news/bus-route"
            )
            assert (
                articles[2]["original_summary"]
                == "New bus route connects Stockport neighborhoods"
            )
            assert articles[2]["original_source"] == "Stockport Nub News"
            assert articles[2]["source_type"] == "Web scraping"
            assert articles[2]["original_pubdate"] == datetime(2024, 3, 15, 16, 20, 0)

            # Verify logging and sleep
            mock_log_info.assert_called_once_with("Nub News: 3 articles found")
            mock_sleep.assert_called_once_with(2)

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_fetch_articles_empty_response(self, mock_get, mock_sleep):
        """Test handling of empty article response"""
        articles_data = []
        mock_response = create_mock_response(articles_data)
        mock_get.return_value = mock_response

        source = NubSource()

        with patch("logging.info") as mock_log_info:
            articles = source.fetch_articles()

            assert articles == []
            mock_log_info.assert_called_once_with("Nub News: 0 articles found")
            mock_sleep.assert_called_once_with(2)

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_fetch_articles_no_json_script_tag(self, mock_get, mock_sleep):
        """Test handling when no JSON-LD script tag is found"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        # HTML without JSON-LD script tag
        html_content = """
        <html>
            <head>
                <title>Stockport Nub News</title>
            </head>
            <body>
                <div>No JSON-LD script here</div>
            </body>
        </html>
        """
        mock_response.content = html_content.encode("utf-8")
        mock_get.return_value = mock_response

        source = NubSource()
        articles = source.fetch_articles()

        assert articles == []
        # Should not call sleep or log when no script tag found
        mock_sleep.assert_not_called()

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_fetch_articles_malformed_json(self, mock_get, mock_sleep):
        """Test handling of malformed JSON in script tag"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        # HTML with malformed JSON
        html_content = """
        <html>
            <head>
                <script type="application/ld+json">{"invalid": json content}</script>
            </head>
            <body>
                <div>Content</div>
            </body>
        </html>
        """
        mock_response.content = html_content.encode("utf-8")
        mock_get.return_value = mock_response

        source = NubSource()

        with patch("logging.error") as mock_log_error:
            articles = source.fetch_articles()

            assert articles == []
            mock_log_error.assert_called_once()
            assert "Nub News fetch error:" in mock_log_error.call_args[0][0]

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_fetch_articles_http_error(self, mock_get, mock_sleep):
        """Test handling of HTTP errors"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("HTTP 404 Not Found")
        mock_get.return_value = mock_response

        source = NubSource()

        with patch("logging.error") as mock_log_error:
            articles = source.fetch_articles()

            assert articles == []
            mock_log_error.assert_called_once()
            assert "Nub News fetch error:" in mock_log_error.call_args[0][0]

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_fetch_articles_connection_error(self, mock_get, mock_sleep):
        """Test handling of connection errors"""
        mock_get.side_effect = Exception("Connection refused")

        source = NubSource()

        with patch("logging.error") as mock_log_error:
            articles = source.fetch_articles()

            assert articles == []
            mock_log_error.assert_called_once()
            assert "Connection refused" in mock_log_error.call_args[0][0]

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_fetch_articles_malformed_date(self, mock_get, mock_sleep):
        """Test handling of articles with malformed dates"""
        articles_data = [
            create_mock_nub_article(
                "Valid article",
                "https://stockport.nub.news/news/valid",
                "2024-03-15 10:30:00",
            ),
            {
                "headline": "Article with bad date",
                "url": "https://stockport.nub.news/news/bad-date",
                "datePublished": "invalid-date-format",
            },
            create_mock_nub_article(
                "Another valid article",
                "https://stockport.nub.news/news/valid2",
                "2024-03-15 14:45:00",
            ),
        ]

        mock_response = create_mock_response(articles_data)
        mock_get.return_value = mock_response

        source = NubSource()

        with (
            patch("logging.error") as mock_log_error,
            patch("logging.info") as mock_log_info,
        ):
            articles = source.fetch_articles()

            # Should return only the 2 valid articles
            assert len(articles) == 2
            assert articles[0]["original_title"] == "Valid article"
            assert articles[1]["original_title"] == "Another valid article"

            # Should log error for the bad article
            mock_log_error.assert_called_once()
            assert "Error parsing Nub article:" in mock_log_error.call_args[0][0]

            # Should log final count
            mock_log_info.assert_called_once_with("Nub News: 2 articles found")

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_fetch_articles_missing_required_fields(self, mock_get, mock_sleep):
        """Test handling of articles with missing required fields"""
        articles_data = [
            create_mock_nub_article(
                "Complete article",
                "https://stockport.nub.news/news/complete",
                "2024-03-15 10:30:00",
            ),
            {
                "headline": "Missing URL",
                "datePublished": "2024-03-15 11:30:00",
                # Missing 'url' field
            },
            {
                "url": "https://stockport.nub.news/news/missing-headline",
                "datePublished": "2024-03-15 12:30:00",
                # Missing 'headline' field
            },
            create_mock_nub_article(
                "Another complete article",
                "https://stockport.nub.news/news/complete2",
                "2024-03-15 13:30:00",
            ),
        ]

        mock_response = create_mock_response(articles_data)
        mock_get.return_value = mock_response

        source = NubSource()

        with (
            patch("logging.error") as mock_log_error,
            patch("logging.info") as mock_log_info,
        ):
            articles = source.fetch_articles()

            # Should return only the 2 complete articles
            assert len(articles) == 2
            assert articles[0]["original_title"] == "Complete article"
            assert articles[1]["original_title"] == "Another complete article"

            # Should log errors for the incomplete articles
            assert mock_log_error.call_count == 2

            # Should log final count
            mock_log_info.assert_called_once_with("Nub News: 2 articles found")

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_fetch_articles_control_characters_in_json(self, mock_get, mock_sleep):
        """Test handling of control characters in JSON content"""
        # Create JSON with control characters that need to be cleaned
        articles_data = [
            create_mock_nub_article(
                "Article with clean data",
                "https://stockport.nub.news/news/clean",
                "2024-03-15 10:30:00",
            )
        ]

        # Add control characters to the JSON
        json_content = json.dumps(articles_data)
        json_with_control_chars = json_content[:50] + "\x00\x1f" + json_content[50:]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        html_content = f"""
        <html>
            <head>
                <script type="application/ld+json">{json_with_control_chars}</script>
            </head>
            <body>
                <div>Content</div>
            </body>
        </html>
        """
        mock_response.content = html_content.encode("utf-8")
        mock_get.return_value = mock_response

        source = NubSource()

        with patch("logging.info") as mock_log_info:
            articles = source.fetch_articles()

            # Should successfully parse after cleaning control characters
            assert len(articles) == 1
            assert articles[0]["original_title"] == "Article with clean data"
            mock_log_info.assert_called_once_with("Nub News: 1 articles found")

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_fetch_articles_preserves_all_fields(self, mock_get, mock_sleep):
        """Test that all article fields are properly preserved"""
        articles_data = [
            create_mock_nub_article(
                "Stockport community center opens new facilities",
                "https://stockport.nub.news/news/community-center-facilities",
                "2024-03-15 10:30:00",
            )
        ]

        mock_response = create_mock_response(articles_data)
        mock_get.return_value = mock_response

        source = NubSource()
        articles = source.fetch_articles()

        assert len(articles) == 1
        article = articles[0]

        # Check all expected fields are present and correct
        assert (
            article["original_title"]
            == "Stockport community center opens new facilities"
        )
        assert (
            article["original_link"]
            == "https://stockport.nub.news/news/community-center-facilities"
        )
        assert (
            article["original_summary"]
            == "Stockport community center opens new facilities"
        )  # Same as title for Nub
        assert article["original_source"] == "Stockport Nub News"
        assert article["source_type"] == "Web scraping"
        assert article["original_pubdate"] == datetime(2024, 3, 15, 10, 30, 0)

        # Ensure no extra fields are added
        expected_keys = {
            "original_title",
            "original_link",
            "original_summary",
            "original_source",
            "source_type",
            "original_pubdate",
        }
        assert set(article.keys()) == expected_keys

    def test_base_url_and_headers(self):
        """Test that the base URL and headers are correctly set"""
        source = NubSource()

        assert source.base_url == "https://stockport.nub.news/news"
        assert "User-Agent" in source.headers
        assert "Mozilla/5.0" in source.headers["User-Agent"]
        assert "ViaductBot/1.0" in source.headers["User-Agent"]

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_requests_called_with_correct_parameters(self, mock_get, mock_sleep):
        """Test that requests.get is called with correct parameters"""
        articles_data = [
            create_mock_nub_article(
                "Test article",
                "https://stockport.nub.news/news/test",
                "2024-03-15 10:30:00",
            )
        ]

        mock_response = create_mock_response(articles_data)
        mock_get.return_value = mock_response

        # Trigger the request
        source = NubSource()
        _ = source.fetch_articles()

        # Verify requests.get was called with correct parameters
        mock_get.assert_called_once_with(
            "https://stockport.nub.news/news",
            headers={"User-Agent": "Mozilla/5.0 (compatible; ViaductBot/1.0)"},
        )

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_logging_behavior(self, mock_get, mock_sleep):
        """Test that logging works correctly for both success and error cases"""
        # Test successful logging
        articles_data = [
            create_mock_nub_article(
                "Test article",
                "https://stockport.nub.news/news/test",
                "2024-03-15 10:30:00",
            )
        ]

        mock_response = create_mock_response(articles_data)
        mock_get.return_value = mock_response

        with patch("logging.info") as mock_log_info:
            source = NubSource()
            _ = source.fetch_articles()
            mock_log_info.assert_called_once_with("Nub News: 1 articles found")

        # Test error logging
        mock_get.side_effect = Exception("Network error")

        with patch("logging.error") as mock_log_error:
            source = NubSource()
            _ = source.fetch_articles()
            mock_log_error.assert_called_once_with(
                "Nub News fetch error: Network error"
            )


class TestNubSourceIntegration:
    """Integration tests for NubSource"""

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_complete_workflow(self, mock_get, mock_sleep):
        """Test complete article fetching workflow"""
        # Create a realistic set of Nub News articles
        articles_data = [
            create_mock_nub_article(
                "Stockport Market receives major investment for renovation",
                "https://stockport.nub.news/news/market-investment-renovation-2024",
                "2024-03-15 09:00:00",
            ),
            create_mock_nub_article(
                "New cycle path connects Stockport town centre to railway station",
                "https://stockport.nub.news/news/cycle-path-town-centre-railway-2024",
                "2024-03-15 11:30:00",
            ),
            create_mock_nub_article(
                "Local school wins national environmental award",
                "https://stockport.nub.news/news/school-environmental-award-2024",
                "2024-03-15 13:45:00",
            ),
            create_mock_nub_article(
                "Community garden project brings neighbors together",
                "https://stockport.nub.news/news/community-garden-neighbors-2024",
                "2024-03-15 15:20:00",
            ),
            create_mock_nub_article(
                "Stockport business district sees new shop openings",
                "https://stockport.nub.news/news/business-district-shop-openings-2024",
                "2024-03-15 17:10:00",
            ),
        ]

        mock_response = create_mock_response(articles_data)
        mock_get.return_value = mock_response

        source = NubSource()

        with patch("logging.info") as mock_log_info:
            articles = source.fetch_articles()

            # Should return all 5 articles (Nub News is local to Stockport, no filtering needed)
            assert len(articles) == 5

            # Verify all articles are included with correct data
            expected_titles = [
                "Stockport Market receives major investment for renovation",
                "New cycle path connects Stockport town centre to railway station",
                "Local school wins national environmental award",
                "Community garden project brings neighbors together",
                "Stockport business district sees new shop openings",
            ]

            actual_titles = [article["original_title"] for article in articles]
            for title in expected_titles:
                assert title in actual_titles

            # Verify all articles have correct source and type
            for article in articles:
                assert article["original_source"] == "Stockport Nub News"
                assert article["source_type"] == "Web scraping"
                assert (
                    article["original_summary"] == article["original_title"]
                )  # Nub uses title as summary

            # Verify logging and sleep behavior
            mock_log_info.assert_called_once_with("Nub News: 5 articles found")
            mock_sleep.assert_called_once_with(2)

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_error_recovery_scenarios(self, mock_get, mock_sleep):
        """Test that NubSource recovers gracefully from various errors"""
        source = NubSource()

        # Test various error scenarios
        error_scenarios = [
            Exception("Network timeout"),
            ConnectionError("Unable to connect"),
            ValueError("Invalid response format"),
            KeyError("Missing JSON field"),
        ]

        for error in error_scenarios:
            mock_get.side_effect = error

            with patch("logging.error") as mock_log_error:
                articles = source.fetch_articles()

                # Should always return empty list on error
                assert articles == []

                # Should always log the error
                mock_log_error.assert_called_once()
                assert str(error) in mock_log_error.call_args[0][0]

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_mixed_valid_invalid_articles(self, mock_get, mock_sleep):
        """Test handling of a mix of valid and invalid articles"""
        # Mix of valid articles and articles with various issues
        articles_data = [
            # Valid article
            create_mock_nub_article(
                "Valid Stockport community news",
                "https://stockport.nub.news/news/valid-community-news",
                "2024-03-15 10:00:00",
            ),
            # Article with missing headline
            {
                "url": "https://stockport.nub.news/news/missing-headline",
                "datePublished": "2024-03-15 11:00:00",
            },
            # Article with invalid date
            {
                "headline": "Article with bad date",
                "url": "https://stockport.nub.news/news/bad-date",
                "datePublished": "not-a-date",
            },
            # Another valid article
            create_mock_nub_article(
                "Another valid Stockport update",
                "https://stockport.nub.news/news/valid-update",
                "2024-03-15 12:00:00",
            ),
            # Article with missing URL
            {"headline": "Missing URL article", "datePublished": "2024-03-15 13:00:00"},
            # Final valid article
            create_mock_nub_article(
                "Final valid news item",
                "https://stockport.nub.news/news/final-valid",
                "2024-03-15 14:00:00",
            ),
        ]

        mock_response = create_mock_response(articles_data)
        mock_get.return_value = mock_response

        source = NubSource()

        with (
            patch("logging.error") as mock_log_error,
            patch("logging.info") as mock_log_info,
        ):
            articles = source.fetch_articles()

            # Should return only the 3 valid articles
            assert len(articles) == 3

            valid_titles = [article["original_title"] for article in articles]
            assert "Valid Stockport community news" in valid_titles
            assert "Another valid Stockport update" in valid_titles
            assert "Final valid news item" in valid_titles

            # Should log errors for each invalid article
            assert mock_log_error.call_count == 3

            # Should log final count
            mock_log_info.assert_called_once_with("Nub News: 3 articles found")

    @patch("sources.nub_source.time.sleep")
    @patch("sources.nub_source.requests.get")
    def test_rate_limiting_behavior(self, mock_get, mock_sleep):
        """Test that rate limiting (sleep) is properly implemented"""
        articles_data = [
            create_mock_nub_article(
                "Test rate limiting",
                "https://stockport.nub.news/news/rate-limit-test",
                "2024-03-15 10:30:00",
            )
        ]

        mock_response = create_mock_response(articles_data)
        mock_get.return_value = mock_response

        source = NubSource()
        articles = source.fetch_articles()

        # Verify that sleep was called with correct duration
        mock_sleep.assert_called_once_with(2)

        # Verify articles were still fetched correctly
        assert len(articles) == 1
        assert articles[0]["original_title"] == "Test rate limiting"
