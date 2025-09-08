#!/usr/bin/env python3
"""
Comprehensive test suite for GitHubPublisher class
"""

import os
import sys
import base64
from datetime import datetime
from unittest.mock import Mock, patch
import requests
import pytest

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from publishers.github_publisher import GitHubPublisher


class TestGitHubPublisher:
    """Test suite for GitHubPublisher class"""

    @pytest.fixture
    def sample_article_data(self):
        """Fixture providing sample article data"""
        return {
            "original_title": "Stockport Council Announces New Park Investment",
            "original_link": "https://example.com/stockport-park-investment",
            "original_source": "BBC Manchester",
            "original_summary": "Council announces major investment in local parks",
        }

    @pytest.fixture
    def sample_summary(self):
        """Fixture providing AI-generated summary"""
        return "Stockport Council's investing £2.5m in local parks, upgrading playgrounds and creating community gardens. Work starts in March, finishing by year-end. Residents are chuffed after campaigning for better facilities."

    @pytest.fixture
    def sample_image_url(self):
        """Fixture providing sample image URL"""
        return "https://example.com/images/stockport-park.jpg"

    @pytest.fixture
    def mock_config(self):
        """Fixture providing mock configuration"""
        config_mock = Mock()
        config_mock.GITHUB_TOKEN = "ghp_test_token_123"
        config_mock.GITHUB_REPO = "testuser/testrepo"
        config_mock.GITHUB_BRANCH = "main"
        return config_mock

    @pytest.fixture
    def mock_successful_response(self):
        """Fixture providing successful GitHub API response"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = '{"message": "File created successfully"}'
        return mock_response

    @pytest.fixture
    def mock_failed_response(self):
        """Fixture providing failed GitHub API response"""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.text = '{"message": "Validation Failed"}'
        return mock_response

    @patch("publishers.github_publisher.Config")
    def test_initialization(self, mock_config):
        """Test GitHubPublisher initializes correctly"""
        mock_config.GITHUB_TOKEN = "test_token"
        mock_config.GITHUB_REPO = "owner/repo"
        mock_config.GITHUB_BRANCH = "main"

        publisher = GitHubPublisher()

        assert publisher.token == "test_token"
        assert publisher.repo == "owner/repo"
        assert publisher.branch == "main"
        assert publisher.headers["Authorization"] == "token test_token"
        assert publisher.headers["Accept"] == "application/vnd.github.v3+json"

    @patch("publishers.github_publisher.Config")
    def test_create_slug_basic(self, mock_config):
        """Test basic slug creation"""
        mock_config.GITHUB_TOKEN = "test_token"
        mock_config.GITHUB_REPO = "owner/repo"
        mock_config.GITHUB_BRANCH = "main"

        publisher = GitHubPublisher()

        # Test basic title
        slug = publisher._create_slug("Stockport Council Meeting Today")
        assert slug == "stockport-council-meeting-today"

        # Test title with special characters
        slug = publisher._create_slug("New £2.5m Investment: Great News!")
        assert slug == "new-25m-investment-great-news"

        # Test title with multiple spaces and dashes
        slug = publisher._create_slug("   Multiple   Spaces   ---   Dashes   ")
        assert slug == "multiple-spaces-dashes"

    @patch("publishers.github_publisher.Config")
    def test_create_slug_length_limit(self, mock_config):
        """Test slug creation with length limitation"""
        mock_config.GITHUB_TOKEN = "test_token"
        mock_config.GITHUB_REPO = "owner/repo"
        mock_config.GITHUB_BRANCH = "main"

        publisher = GitHubPublisher()

        # Test very long title (should be truncated to 100 chars)
        long_title = "This is a very long article title that should be truncated because it exceeds the hundred character limit for slugs"
        slug = publisher._create_slug(long_title)
        assert len(slug) <= 100
        assert (
            slug
            == "this-is-a-very-long-article-title-that-should-be-truncated-because-it-exceeds-the-hundred-character-"[
                :100
            ]
        )

    @patch("publishers.github_publisher.Config")
    def test_create_slug_edge_cases(self, mock_config):
        """Test slug creation with edge cases"""
        mock_config.GITHUB_TOKEN = "test_token"
        mock_config.GITHUB_REPO = "owner/repo"
        mock_config.GITHUB_BRANCH = "main"

        publisher = GitHubPublisher()

        # Test empty string
        slug = publisher._create_slug("")
        assert slug == ""

        # Test only special characters
        slug = publisher._create_slug("!@#$%^&*()")
        assert slug == ""

        # Test only spaces and dashes
        slug = publisher._create_slug("   ---   ")
        assert slug == ""

    @patch("publishers.github_publisher.Config")
    def test_create_jekyll_content(
        self, mock_config, sample_article_data, sample_summary, sample_image_url
    ):
        """Test Jekyll content generation"""
        mock_config.GITHUB_TOKEN = "test_token"
        mock_config.GITHUB_REPO = "owner/repo"
        mock_config.GITHUB_BRANCH = "main"

        publisher = GitHubPublisher()

        content = publisher._create_jekyll_content(
            sample_article_data, sample_summary, sample_image_url
        )

        # Verify Jekyll front matter
        assert content.startswith("---\n")
        assert "layout: post" in content
        assert "author: archie" in content
        assert "categories: news" in content
        assert f"image: {sample_image_url}" in content

        # Verify content body
        assert sample_summary in content
        assert f"![Article Image]({sample_image_url})" in content
        assert (
            f"[Read the full article at {sample_article_data['original_source']}]({sample_article_data['original_link']})"
            in content
        )
        assert content.endswith("---\n")

    @patch("publishers.github_publisher.datetime")
    @patch("publishers.github_publisher.requests.put")
    @patch("publishers.github_publisher.Config")
    def test_publish_article_success(
        self,
        mock_config,
        mock_put,
        mock_datetime,
        sample_article_data,
        sample_summary,
        sample_image_url,
        mock_successful_response,
    ):
        """Test successful article publishing"""
        # Setup mocks
        mock_config.GITHUB_TOKEN = "test_token"
        mock_config.GITHUB_REPO = "owner/repo"
        mock_config.GITHUB_BRANCH = "main"

        fixed_datetime = datetime(2024, 3, 15, 10, 30, 0)
        mock_datetime.now.return_value = fixed_datetime

        mock_put.return_value = mock_successful_response

        publisher = GitHubPublisher()

        with patch("logging.info") as mock_log_info:
            result = publisher.publish_article(
                sample_article_data, sample_summary, sample_image_url
            )

            # Verify result
            assert result is True

            # Verify API call
            mock_put.assert_called_once()
            args, kwargs = mock_put.call_args

            # Check URL
            expected_url = "https://api.github.com/repos/owner/repo/contents/_posts/2024-03-15-stockport-council-announces-new-park-investment.md"
            assert args[0] == expected_url

            # Check headers
            assert kwargs["headers"]["Authorization"] == "token test_token"
            assert kwargs["headers"]["Accept"] == "application/vnd.github.v3+json"

            # Check payload
            payload = kwargs["json"]
            assert (
                payload["message"]
                == f"Auto-post: {sample_article_data['original_title']}"
            )
            assert payload["branch"] == "main"
            assert "content" in payload

            # Verify content is base64 encoded
            decoded_content = base64.b64decode(payload["content"]).decode("utf-8")
            assert sample_summary in decoded_content
            assert "layout: post" in decoded_content

            # Verify logging
            mock_log_info.assert_called_once_with(
                f"Published: {sample_article_data['original_title']}"
            )

    @patch("publishers.github_publisher.datetime")
    @patch("publishers.github_publisher.requests.put")
    @patch("publishers.github_publisher.Config")
    def test_publish_article_api_failure(
        self,
        mock_config,
        mock_put,
        mock_datetime,
        sample_article_data,
        sample_summary,
        sample_image_url,
        mock_failed_response,
    ):
        """Test article publishing with API failure"""
        # Setup mocks
        mock_config.GITHUB_TOKEN = "test_token"
        mock_config.GITHUB_REPO = "owner/repo"
        mock_config.GITHUB_BRANCH = "main"

        fixed_datetime = datetime(2024, 3, 15, 10, 30, 0)
        mock_datetime.now.return_value = fixed_datetime

        mock_put.return_value = mock_failed_response

        publisher = GitHubPublisher()

        with patch("logging.error") as mock_log_error:
            result = publisher.publish_article(
                sample_article_data, sample_summary, sample_image_url
            )

            # Verify result
            assert result is False

            # Verify error logging
            mock_log_error.assert_called_once()
            error_message = mock_log_error.call_args[0][0]
            assert "GitHub publish failed" in error_message
            assert "422" in error_message

    @patch("publishers.github_publisher.requests.put")
    @patch("publishers.github_publisher.Config")
    def test_publish_article_exception(
        self,
        mock_config,
        mock_put,
        sample_article_data,
        sample_summary,
        sample_image_url,
    ):
        """Test article publishing with exception handling"""
        # Setup mocks
        mock_config.GITHUB_TOKEN = "test_token"
        mock_config.GITHUB_REPO = "owner/repo"
        mock_config.GITHUB_BRANCH = "main"

        mock_put.side_effect = requests.exceptions.ConnectionError("Network error")

        publisher = GitHubPublisher()

        with patch("logging.error") as mock_log_error:
            result = publisher.publish_article(
                sample_article_data, sample_summary, sample_image_url
            )

            # Verify result
            assert result is False

            # Verify error logging
            mock_log_error.assert_called_once()
            error_message = mock_log_error.call_args[0][0]
            assert "Publishing error" in error_message

    @patch("publishers.github_publisher.datetime")
    @patch("publishers.github_publisher.requests.put")
    @patch("publishers.github_publisher.Config")
    def test_publish_article_different_status_codes(
        self,
        mock_config,
        mock_put,
        mock_datetime,
        sample_article_data,
        sample_summary,
        sample_image_url,
    ):
        """Test publishing with different HTTP status codes"""
        mock_config.GITHUB_TOKEN = "test_token"
        mock_config.GITHUB_REPO = "owner/repo"
        mock_config.GITHUB_BRANCH = "main"

        fixed_datetime = datetime(2024, 3, 15, 10, 30, 0)
        mock_datetime.now.return_value = fixed_datetime

        publisher = GitHubPublisher()

        # Test various error status codes
        error_codes = [400, 401, 403, 404, 500, 502, 503]

        for status_code in error_codes:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_response.text = f"Error {status_code}"
            mock_put.return_value = mock_response

            with patch("logging.error") as mock_log_error:
                result = publisher.publish_article(
                    sample_article_data, sample_summary, sample_image_url
                )

                assert result is False
                mock_log_error.assert_called_once()

    @patch("publishers.github_publisher.Config")
    def test_filename_generation(self, mock_config, sample_article_data):
        """Test filename generation logic"""
        mock_config.GITHUB_TOKEN = "test_token"
        mock_config.GITHUB_REPO = "owner/repo"
        mock_config.GITHUB_BRANCH = "main"

        publisher = GitHubPublisher()

        with patch("publishers.github_publisher.datetime") as mock_datetime:
            fixed_datetime = datetime(2024, 12, 25, 14, 30, 45)
            mock_datetime.now.return_value = fixed_datetime

            with patch("publishers.github_publisher.requests.put") as mock_put:
                mock_response = Mock()
                mock_response.status_code = 201
                mock_put.return_value = mock_response

                publisher.publish_article(
                    sample_article_data, "test summary", "test.jpg"
                )

                # Check the filename in the URL
                call_args = mock_put.call_args[0][0]
                assert (
                    "2024-12-25-stockport-council-announces-new-park-investment.md"
                    in call_args
                )

    @patch("publishers.github_publisher.Config")
    def test_base64_encoding(self, mock_config, sample_article_data):
        """Test that content is properly base64 encoded"""
        mock_config.GITHUB_TOKEN = "test_token"
        mock_config.GITHUB_REPO = "owner/repo"
        mock_config.GITHUB_BRANCH = "main"

        publisher = GitHubPublisher()

        test_summary = "Test summary content"
        test_image = "test.jpg"

        with patch("publishers.github_publisher.requests.put") as mock_put:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_put.return_value = mock_response

            publisher.publish_article(sample_article_data, test_summary, test_image)

            # Get the payload
            payload = mock_put.call_args[1]["json"]
            encoded_content = payload["content"]

            # Verify it's valid base64
            try:
                decoded = base64.b64decode(encoded_content).decode("utf-8")
                assert test_summary in decoded
                assert "layout: post" in decoded
            except Exception as e:
                pytest.fail(f"Content is not valid base64: {e}")

    @patch("publishers.github_publisher.Config")
    def test_jekyll_content_structure(self, mock_config):
        """Test Jekyll content structure in detail"""
        mock_config.GITHUB_TOKEN = "test_token"
        mock_config.GITHUB_REPO = "owner/repo"
        mock_config.GITHUB_BRANCH = "main"

        publisher = GitHubPublisher()

        article_data = {
            "original_title": "Test Article",
            "original_link": "https://example.com/test",
            "original_source": "Test Source",
        }

        summary = "This is a test summary."
        image_url = "https://example.com/image.jpg"

        content = publisher._create_jekyll_content(article_data, summary, image_url)

        lines = content.split("\n")

        # Check front matter boundaries
        assert lines[0] == "---"
        front_matter_end = lines.index("---", 1)
        assert front_matter_end > 0

        # Check front matter content
        front_matter = lines[1:front_matter_end]
        front_matter_dict = {}
        for line in front_matter:
            if ":" in line:
                key, value = line.split(":", 1)
                front_matter_dict[key.strip()] = value.strip()

        assert front_matter_dict["layout"] == "post"
        assert front_matter_dict["author"] == "archie"
        assert front_matter_dict["categories"] == "news"
        assert front_matter_dict["image"] == image_url

        # Check content after front matter
        content_body = "\n".join(lines[front_matter_end + 1 :])
        assert summary in content_body
        assert f"![Article Image]({image_url})" in content_body
        assert (
            f"[Read the full article at {article_data['original_source']}]({article_data['original_link']})"
            in content_body
        )


class TestGitHubPublisherIntegration:
    """Integration tests for GitHubPublisher"""

    @patch("publishers.github_publisher.Config")
    def test_complete_publishing_workflow(self, mock_config):
        """Test complete publishing workflow"""
        mock_config.GITHUB_TOKEN = "test_token"
        mock_config.GITHUB_REPO = "owner/repo"
        mock_config.GITHUB_BRANCH = "main"

        publisher = GitHubPublisher()

        article_data = {
            "original_title": "Integration Test Article",
            "original_link": "https://example.com/integration-test",
            "original_source": "Integration Test Source",
        }

        with patch("publishers.github_publisher.requests.put") as mock_put:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_put.return_value = mock_response

            with patch("logging.info") as mock_log_info:
                result = publisher.publish_article(
                    article_data,
                    "Integration test summary",
                    "https://example.com/integration-test.jpg",
                )

                # Verify end-to-end success
                assert result is True
                mock_put.assert_called_once()
                mock_log_info.assert_called_once()

                # Verify the complete API call
                args, kwargs = mock_put.call_args
                assert "api.github.com" in args[0]
                assert "_posts" in args[0]
                assert ".md" in args[0]

                # Verify payload structure
                payload = kwargs["json"]
                assert all(key in payload for key in ["message", "content", "branch"])
                assert payload["branch"] == "main"
                assert "Auto-post:" in payload["message"]

    @patch("publishers.github_publisher.Config")
    def test_error_recovery_scenarios(self, mock_config):
        """Test various error recovery scenarios"""
        mock_config.GITHUB_TOKEN = "test_token"
        mock_config.GITHUB_REPO = "owner/repo"
        mock_config.GITHUB_BRANCH = "main"

        publisher = GitHubPublisher()

        article_data = {
            "original_title": "Error Test Article",
            "original_link": "https://example.com/error-test",
            "original_source": "Error Test Source",
        }

        error_scenarios = [
            requests.exceptions.ConnectionError("Connection failed"),
            requests.exceptions.Timeout("Request timeout"),
            requests.exceptions.HTTPError("HTTP error"),
            Exception("Generic error"),
        ]

        for error in error_scenarios:
            with patch("publishers.github_publisher.requests.put") as mock_put:
                mock_put.side_effect = error

                with patch("logging.error") as mock_log_error:
                    result = publisher.publish_article(
                        article_data, "Error test", "error.jpg"
                    )

                    # Should always return False on error
                    assert result is False
                    # Should always log the error
                    mock_log_error.assert_called_once()
