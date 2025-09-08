#!/usr/bin/env python3
"""
Comprehensive test suite for ContentExtractor class
"""

import os
import sys
import json
from unittest.mock import Mock, patch
import requests
import pytest


# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from processors.content_extractor import ContentExtractor


class TestContentExtractor:
    """Test suite for ContentExtractor class"""

    @pytest.fixture
    def extractor(self):
        """Fixture providing ContentExtractor instance"""
        return ContentExtractor()

    @pytest.fixture
    def sample_bbc_html(self):
        """Fixture providing sample BBC HTML structure"""
        return """
        <html>
            <head>
                <meta property="og:image" content="https://example.com/bbc-image.jpg">
            </head>
            <body>
                <div data-component="text-block">
                    <p>First paragraph of BBC article content.</p>
                </div>
                <div data-component="text-block">
                    <p>Second paragraph with more details about the story.</p>
                </div>
                <div data-component="other-component">
                    <p>This should not be included.</p>
                </div>
            </body>
        </html>
        """

    @pytest.fixture
    def sample_men_html(self):
        """Fixture providing sample MEN HTML with JSON-LD"""
        json_data = {
            "articleBody": "This is the article body from JSON-LD.\\nSecond line with <b>HTML tags</b>.",
            "headline": "Test Article Headline",
        }
        return f"""
        <html>
            <head>
                <meta property="og:image" content="https://example.com/men-image.jpg">
                <script type="application/ld+json">{json.dumps(json_data)}</script>
            </head>
            <body>
                <h1>Article Title</h1>
            </body>
        </html>
        """

    @pytest.fixture
    def sample_men_html_array(self):
        """Fixture providing sample MEN HTML with JSON-LD array"""
        json_data = [
            {
                "articleBody": "Article body from JSON-LD array.",
                "headline": "First Article",
            },
            {"articleBody": "Second article body", "headline": "Second Article"},
        ]
        return f"""
        <html>
            <head>
                <meta property="og:image" content="https://example.com/men-array-image.jpg">
                <script type="application/ld+json">{json.dumps(json_data)}</script>
            </head>
        </html>
        """

    @pytest.fixture
    def sample_nub_html(self):
        """Fixture providing sample Nub News HTML structure"""
        return """
        <html>
            <body>
                <div class="prose max-w-none leading-snug">
                    <p>Nub News article content goes here.</p>
                    <p>Multiple paragraphs of local news.</p>
                </div>
                <div class="w-full overflow-hidden">
                    <img src="https://example.com/nub-image.jpg" alt="News image">
                </div>
            </body>
        </html>
        """

    @pytest.fixture
    def sample_generic_html(self):
        """Fixture providing generic HTML structure"""
        return """
        <html>
            <head>
                <meta property="og:image" content="https://example.com/generic-image.jpg">
            </head>
            <body>
                <p>First paragraph of generic content.</p>
                <p>Second paragraph with more information.</p>
                <p>Third paragraph continues the story.</p>
                <p>Fourth paragraph adds details.</p>
                <p>Fifth paragraph wraps up.</p>
                <p>Sixth paragraph should not be included (limit is 5).</p>
            </body>
        </html>
        """

    @pytest.fixture
    def mock_response(self):
        """Fixture providing a mock HTTP response"""
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        return mock_resp

    def test_initialization(self, extractor):
        """Test ContentExtractor initializes correctly"""
        assert extractor.headers is not None
        assert "User-Agent" in extractor.headers
        assert "Mozilla/5.0" in extractor.headers["User-Agent"]

    @patch("processors.content_extractor.time.sleep")
    @patch("processors.content_extractor.requests.get")
    def test_extract_bbc_content_success(
        self, mock_get, mock_sleep, extractor, mock_response, sample_bbc_html
    ):
        """Test successful BBC content extraction"""
        mock_response.content = sample_bbc_html.encode("utf-8")
        mock_get.return_value = mock_response

        result = extractor.extract_content(
            "https://www.bbc.com/news/test-article", "BBC News"
        )

        # Verify HTTP request
        mock_get.assert_called_once_with(
            "https://www.bbc.com/news/test-article", headers=extractor.headers
        )
        mock_response.raise_for_status.assert_called_once()
        mock_sleep.assert_called_once_with(1)

        # Verify extracted content
        assert (
            result["content"]
            == "First paragraph of BBC article content.\n\nSecond paragraph with more details about the story."
        )
        assert result["image_url"] == "https://example.com/bbc-image.jpg"

    @patch("processors.content_extractor.time.sleep")
    @patch("processors.content_extractor.requests.get")
    def test_extract_men_content_success(
        self, mock_get, mock_sleep, extractor, mock_response, sample_men_html
    ):
        """Test successful MEN content extraction"""
        mock_response.content = sample_men_html.encode("utf-8")
        mock_get.return_value = mock_response

        result = extractor.extract_content(
            "https://www.manchestereveningnews.co.uk/news/test", "MEN"
        )

        # Verify extracted content
        expected_content = (
            "This is the article body from JSON-LD.\nSecond line with HTML tags."
        )
        assert result["content"] == expected_content
        assert result["image_url"] == "https://example.com/men-image.jpg"

    @patch("processors.content_extractor.time.sleep")
    @patch("processors.content_extractor.requests.get")
    def test_extract_men_content_array(
        self, mock_get, mock_sleep, extractor, mock_response, sample_men_html_array
    ):
        """Test MEN content extraction with JSON-LD array"""
        mock_response.content = sample_men_html_array.encode("utf-8")
        mock_get.return_value = mock_response

        result = extractor.extract_content(
            "https://www.manchestereveningnews.co.uk/news/array-test", "MEN"
        )

        # Should extract from first item in array
        assert result["content"] == "Article body from JSON-LD array."
        assert result["image_url"] == "https://example.com/men-array-image.jpg"

    @patch("processors.content_extractor.time.sleep")
    @patch("processors.content_extractor.requests.get")
    def test_extract_nub_content_success(
        self, mock_get, mock_sleep, extractor, mock_response, sample_nub_html
    ):
        """Test successful Nub News content extraction"""
        mock_response.content = sample_nub_html.encode("utf-8")
        mock_get.return_value = mock_response

        result = extractor.extract_content(
            "https://stockport.nub.news/news/test", "Nub News"
        )

        # Verify extracted content (BeautifulSoup strips extra whitespace)
        expected_content = (
            "Nub News article content goes here.\nMultiple paragraphs of local news."
        )
        assert result["content"] == expected_content
        assert result["image_url"] == "https://example.com/nub-image.jpg"

    @patch("processors.content_extractor.time.sleep")
    @patch("processors.content_extractor.requests.get")
    def test_extract_generic_content_success(
        self, mock_get, mock_sleep, extractor, mock_response, sample_generic_html
    ):
        """Test successful generic content extraction"""
        mock_response.content = sample_generic_html.encode("utf-8")
        mock_get.return_value = mock_response

        result = extractor.extract_content(
            "https://example.com/news/test", "Generic Source"
        )

        # Verify extracted content (should limit to first 5 paragraphs)
        expected_content = "First paragraph of generic content.\n\nSecond paragraph with more information.\n\nThird paragraph continues the story.\n\nFourth paragraph adds details.\n\nFifth paragraph wraps up."
        assert result["content"] == expected_content
        assert result["image_url"] == "https://example.com/generic-image.jpg"

    @patch("processors.content_extractor.time.sleep")
    @patch("processors.content_extractor.requests.get")
    def test_extract_content_http_error(self, mock_get, mock_sleep, extractor):
        """Test handling of HTTP errors"""
        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")

        with patch("logging.error") as mock_logging:
            result = extractor.extract_content(
                "https://example.com/not-found", "Test Source"
            )

            # Should return empty content on error
            assert result == {"content": "", "image_url": ""}

            # Should log the error
            mock_logging.assert_called_once()
            assert "Content extraction error" in mock_logging.call_args[0][0]
            assert "https://example.com/not-found" in mock_logging.call_args[0][0]

        # Should still call sleep in finally block
        mock_sleep.assert_called_once_with(1)

    @patch("processors.content_extractor.time.sleep")
    @patch("processors.content_extractor.requests.get")
    def test_extract_content_connection_error(self, mock_get, mock_sleep, extractor):
        """Test handling of connection errors"""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with patch("logging.error") as mock_logging:
            result = extractor.extract_content(
                "https://unreachable.example.com/test", "Test Source"
            )

            assert result == {"content": "", "image_url": ""}
            mock_logging.assert_called_once()

    @patch("processors.content_extractor.time.sleep")
    @patch("processors.content_extractor.requests.get")
    def test_extract_content_timeout_error(self, mock_get, mock_sleep, extractor):
        """Test handling of timeout errors"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        with patch("logging.error") as mock_logging:
            result = extractor.extract_content(
                "https://slow.example.com/test", "Test Source"
            )

            assert result == {"content": "", "image_url": ""}
            mock_logging.assert_called_once()

    @patch("processors.content_extractor.time.sleep")
    @patch("processors.content_extractor.requests.get")
    def test_extract_men_content_invalid_json(
        self, mock_get, mock_sleep, extractor, mock_response
    ):
        """Test MEN content extraction with invalid JSON-LD"""
        invalid_html = """
        <html>
            <head>
                <meta property="og:image" content="https://example.com/image.jpg">
                <script type="application/ld+json">{ invalid json }</script>
            </head>
        </html>
        """
        mock_response.content = invalid_html.encode("utf-8")
        mock_get.return_value = mock_response

        result = extractor.extract_content(
            "https://www.manchestereveningnews.co.uk/news/invalid", "MEN"
        )

        # Should fallback to empty content when JSON is invalid
        assert result["content"] == ""
        assert result["image_url"] == "https://example.com/image.jpg"

    @patch("processors.content_extractor.time.sleep")
    @patch("processors.content_extractor.requests.get")
    def test_extract_men_content_no_json_ld(
        self, mock_get, mock_sleep, extractor, mock_response
    ):
        """Test MEN content extraction without JSON-LD script"""
        no_json_html = """
        <html>
            <head>
                <meta property="og:image" content="https://example.com/image.jpg">
            </head>
            <body><p>Regular content</p></body>
        </html>
        """
        mock_response.content = no_json_html.encode("utf-8")
        mock_get.return_value = mock_response

        result = extractor.extract_content(
            "https://www.manchestereveningnews.co.uk/news/no-json", "MEN"
        )

        assert result["content"] == ""
        assert result["image_url"] == "https://example.com/image.jpg"

    @patch("processors.content_extractor.time.sleep")
    @patch("processors.content_extractor.requests.get")
    def test_extract_content_no_og_image(
        self, mock_get, mock_sleep, extractor, mock_response
    ):
        """Test content extraction without og:image meta tag"""
        no_image_html = """
        <html>
            <body>
                <p>Content without image</p>
            </body>
        </html>
        """
        mock_response.content = no_image_html.encode("utf-8")
        mock_get.return_value = mock_response

        result = extractor.extract_content("https://example.com/no-image", "Generic")

        assert result["content"] == "Content without image"
        assert result["image_url"] == ""

    @patch("processors.content_extractor.time.sleep")
    @patch("processors.content_extractor.requests.get")
    def test_extract_nub_content_missing_elements(
        self, mock_get, mock_sleep, extractor, mock_response
    ):
        """Test Nub content extraction with missing elements"""
        minimal_html = """
        <html>
            <body>
                <!-- Missing prose div and image div -->
                <p>Some content</p>
            </body>
        </html>
        """
        mock_response.content = minimal_html.encode("utf-8")
        mock_get.return_value = mock_response

        result = extractor.extract_content(
            "https://stockport.nub.news/minimal", "Nub News"
        )

        assert result["content"] == ""  # No prose div found
        assert result["image_url"] == ""  # No image div found

    @patch("processors.content_extractor.time.sleep")
    @patch("processors.content_extractor.requests.get")
    def test_extract_bbc_content_no_paragraphs(
        self, mock_get, mock_sleep, extractor, mock_response
    ):
        """Test BBC content extraction with text blocks but no paragraphs"""
        no_p_html = """
        <html>
            <body>
                <div data-component="text-block">
                    <div>Not a paragraph tag</div>
                </div>
            </body>
        </html>
        """
        mock_response.content = no_p_html.encode("utf-8")
        mock_get.return_value = mock_response

        result = extractor.extract_content("https://www.bbc.com/no-paragraphs", "BBC")

        assert result["content"] == ""  # No paragraphs found in text blocks
        assert result["image_url"] == ""

    def test_url_routing_bbc(self, extractor):
        """Test URL routing logic for BBC"""
        with patch.object(extractor, "_extract_bbc_content") as mock_bbc:
            mock_bbc.return_value = {"content": "BBC content", "image_url": "bbc.jpg"}

            with (
                patch("processors.content_extractor.requests.get") as mock_get,
                patch("processors.content_extractor.time.sleep"),
            ):

                # Setup proper mock response
                mock_response = Mock()
                mock_response.content = b"<html></html>"
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result = extractor.extract_content(
                    "https://www.bbc.com/news/test", "BBC"
                )
                mock_bbc.assert_called_once()

    def test_url_routing_men(self, extractor):
        """Test URL routing logic for MEN"""
        with patch.object(extractor, "_extract_men_content") as mock_men:
            mock_men.return_value = {"content": "MEN content", "image_url": "men.jpg"}

            with (
                patch("processors.content_extractor.requests.get") as mock_get,
                patch("processors.content_extractor.time.sleep"),
            ):

                # Setup proper mock response
                mock_response = Mock()
                mock_response.content = b"<html></html>"
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result = extractor.extract_content(
                    "https://www.manchestereveningnews.co.uk/test", "MEN"
                )
                mock_men.assert_called_once()

    def test_url_routing_nub(self, extractor):
        """Test URL routing logic for Nub News"""
        with patch.object(extractor, "_extract_nub_content") as mock_nub:
            mock_nub.return_value = {"content": "Nub content", "image_url": "nub.jpg"}

            with (
                patch("processors.content_extractor.requests.get") as mock_get,
                patch("processors.content_extractor.time.sleep"),
            ):

                # Setup proper mock response
                mock_response = Mock()
                mock_response.content = b"<html></html>"
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result = extractor.extract_content(
                    "https://stockport.nub.news/test", "Nub"
                )
                mock_nub.assert_called_once()

    def test_url_routing_generic(self, extractor):
        """Test URL routing logic for generic sites"""
        with patch.object(extractor, "_extract_generic_content") as mock_generic:
            mock_generic.return_value = {
                "content": "Generic content",
                "image_url": "generic.jpg",
            }

            with (
                patch("processors.content_extractor.requests.get") as mock_get,
                patch("processors.content_extractor.time.sleep"),
            ):

                # Setup proper mock response
                mock_response = Mock()
                mock_response.content = b"<html></html>"
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result = extractor.extract_content(
                    "https://unknown-site.com/test", "Unknown"
                )
                mock_generic.assert_called_once()


class TestContentExtractorIntegration:
    """Integration tests for ContentExtractor"""

    def test_rate_limiting_sleep(self):
        """Test that rate limiting sleep is always called"""
        extractor = ContentExtractor()

        with (
            patch("processors.content_extractor.requests.get") as mock_get,
            patch("processors.content_extractor.time.sleep") as mock_sleep,
        ):

            # Test successful case
            mock_response = Mock()
            mock_response.content = b"<html><body><p>Test</p></body></html>"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            extractor.extract_content("https://example.com/test", "Test")
            mock_sleep.assert_called_with(1)

            # Reset and test error case
            mock_sleep.reset_mock()
            mock_get.side_effect = Exception("Test error")

            with patch("logging.error"):
                extractor.extract_content("https://example.com/error", "Test")

            # Should still sleep even on error
            mock_sleep.assert_called_with(1)

    def test_user_agent_header(self):
        """Test that User-Agent header is correctly set"""
        extractor = ContentExtractor()

        with (
            patch("processors.content_extractor.requests.get") as mock_get,
            patch("processors.content_extractor.time.sleep"),
        ):

            mock_response = Mock()
            mock_response.content = b"<html><body></body></html>"
            mock_get.return_value = mock_response

            extractor.extract_content("https://example.com/test", "Test")

            # Verify headers were passed
            args, kwargs = mock_get.call_args
            assert "headers" in kwargs
            assert "User-Agent" in kwargs["headers"]
            assert "Mozilla/5.0" in kwargs["headers"]["User-Agent"]
