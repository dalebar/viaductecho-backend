#!/usr/bin/env python3
"""
Comprehensive test suite for AISummarizer class
"""

import os
import sys
from unittest.mock import Mock, patch, ANY
import openai
import pytest

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from processors.ai_summarizer import AISummarizer


class TestAISummarizer:
    """Test suite for AISummarizer class"""

    @pytest.fixture
    def sample_content(self):
        """Fixture providing sample article content for testing"""
        return """
        Stockport Council announced today that they will be investing £2.5 million in 
        improving local parks and green spaces across the borough. The investment will 
        focus on upgrading playground equipment, improving walking paths, and creating 
        new community gardens. Council leader Sarah Johnson said: "This investment 
        represents our commitment to providing high-quality outdoor spaces for our 
        residents. We know how important parks are for community wellbeing, especially 
        after the challenges of recent years." The improvements are expected to begin 
        in March and will be completed by the end of the year. Local residents have 
        welcomed the news, with many having campaigned for better facilities for months.
        """

    @pytest.fixture
    def short_content(self):
        """Fixture providing short content that doesn't need truncation"""
        return "Stockport library will be closed for maintenance next week."

    @pytest.fixture
    def long_content(self):
        """Fixture providing long content for fallback testing"""
        return "A" * 300  # 300 characters of 'A'

    @pytest.fixture
    def mock_openai_response(self):
        """Fixture providing a mock OpenAI API response"""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Stockport Council's investing £2.5m in local parks, upgrading playgrounds and creating community gardens. Work starts in March, finishing by year-end. Residents are chuffed after campaigning for better facilities."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        return mock_response

    def test_initialization_success(self):
        """Test AISummarizer initializes correctly"""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client

            summarizer = AISummarizer()

            assert summarizer.client == mock_client
            mock_openai.assert_called_once()

    @patch("processors.ai_summarizer.Config")
    def test_initialization_with_api_key(self, mock_config):
        """Test that API key is set during initialization"""
        mock_config.OPENAI_API_KEY = "test-api-key-123"

        with patch("openai.OpenAI") as mock_openai:
            summarizer = AISummarizer()

            # Verify OpenAI client was created
            mock_openai.assert_called_once_with(api_key="test-api-key-123")

    def test_summarize_success(self, sample_content, mock_openai_response):
        """Test successful summarization with OpenAI API"""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_openai_response
            mock_openai.return_value = mock_client

            summarizer = AISummarizer()
            result = summarizer.summarize(sample_content)

            # Verify the result
            assert result == mock_openai_response.choices[0].message.content
            assert "Stockport Council" in result
            assert "£2.5m" in result

            # Verify API was called correctly
            mock_client.chat.completions.create.assert_called_once_with(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You summarise the user-provided text. Output the summary only, no preamble or follow-up questions. ≤200 words, shorter if clear. Informal, friendly, polite. Subtle Manchester UK vibe in phrasing. Professional, unbiased, UK spelling.",
                    },
                    {"role": "user", "content": sample_content},
                ],
                max_tokens=250,
            )

    def test_summarize_api_error_fallback(self, sample_content):
        """Test fallback behavior when OpenAI API fails"""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client

            summarizer = AISummarizer()

            with patch("logging.error") as mock_logging:
                result = summarizer.summarize(sample_content)

                # Verify fallback behavior (truncate to 200 chars + "...")
                expected_fallback = sample_content[:200] + "..."
                assert result == expected_fallback

                # Verify error was logged
                mock_logging.assert_called_once()
                assert "AI summarization error" in mock_logging.call_args[0][0]

    def test_summarize_short_content_fallback(self, short_content):
        """Test fallback with short content (no truncation)"""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client

            summarizer = AISummarizer()
            result = summarizer.summarize(short_content)

            # Short content should be returned as-is (no "...")
            assert result == short_content
            assert not result.endswith("...")

    def test_summarize_long_content_fallback(self, long_content):
        """Test fallback with content longer than 200 characters"""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client

            summarizer = AISummarizer()
            result = summarizer.summarize(long_content)

            # Long content should be truncated to 200 chars + "..."
            assert len(result) == 203  # 200 + "..."
            assert result == "A" * 200 + "..."
            assert result.endswith("...")

    def test_summarize_empty_content(self):
        """Test summarization with empty content"""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client

            summarizer = AISummarizer()
            result = summarizer.summarize("")

            # Empty content should return empty string
            assert result == ""

    def test_summarize_whitespace_content(self):
        """Test summarization with whitespace-only content"""
        whitespace_content = "   \n\t   "

        with patch("openai.OpenAI") as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client

            summarizer = AISummarizer()
            result = summarizer.summarize(whitespace_content)

            # Whitespace content should be returned as-is
            assert result == whitespace_content

    def test_summarize_openai_authentication_error(self, sample_content):
        """Test handling of OpenAI authentication errors"""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = Mock()
            # Create a proper mock exception with required arguments
            auth_error = Exception("Invalid API key - simulated AuthenticationError")
            mock_client.chat.completions.create.side_effect = auth_error
            mock_openai.return_value = mock_client

            summarizer = AISummarizer()

            with patch("logging.error") as mock_logging:
                result = summarizer.summarize(sample_content)

                # Should fall back to truncation
                assert result.endswith("...")

                # Should log the authentication error
                mock_logging.assert_called_once()

    def test_summarize_openai_rate_limit_error(self, sample_content):
        """Test handling of OpenAI rate limit errors"""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = Mock()
            # Create a proper mock exception with required arguments
            rate_limit_error = Exception(
                "Rate limit exceeded - simulated RateLimitError"
            )
            mock_client.chat.completions.create.side_effect = rate_limit_error
            mock_openai.return_value = mock_client

            summarizer = AISummarizer()

            with patch("logging.error") as mock_logging:
                result = summarizer.summarize(sample_content)

                # Should fall back to truncation
                assert result.endswith("...")

                # Should log the rate limit error
                mock_logging.assert_called_once()

    def test_summarize_system_prompt_content(self):
        """Test that the system prompt is correctly formatted"""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = "Test summary"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            summarizer = AISummarizer()
            summarizer.summarize("Test content")

            # Get the call arguments
            call_args = mock_client.chat.completions.create.call_args
            messages = call_args[1]["messages"]

            # Verify system message
            system_message = messages[0]
            assert system_message["role"] == "system"
            assert "Manchester UK vibe" in system_message["content"]
            assert "≤200 words" in system_message["content"]
            assert "UK spelling" in system_message["content"]

            # Verify user message
            user_message = messages[1]
            assert user_message["role"] == "user"
            assert user_message["content"] == "Test content"

    def test_summarize_model_and_parameters(self):
        """Test that correct model and parameters are used"""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = "Test summary"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            summarizer = AISummarizer()
            summarizer.summarize("Test content")

            # Verify API call parameters
            mock_client.chat.completions.create.assert_called_once_with(
                model="gpt-4o-mini", messages=ANY, max_tokens=250
            )


class TestAISummarizerIntegration:
    """Integration tests for AISummarizer (these would require real API keys in practice)"""

    @pytest.mark.skip(reason="Requires real OpenAI API key and makes actual API calls")
    def test_real_api_call(self):
        """Integration test with real OpenAI API (skipped by default)"""
        # This test would require a real API key and would make actual API calls
        # Uncomment and provide API key for integration testing

        # summarizer = AISummarizer()
        # content = "This is a test article about local news in Greater Manchester."
        # result = summarizer.summarize(content)
        #
        # assert isinstance(result, str)
        # assert len(result) > 0
        # assert len(result) <= 250  # Rough check for max_tokens limit
        pass

    def test_logging_behavior(self):
        """Test that logging works correctly for both success and error cases"""
        # Test successful logging
        with patch("openai.OpenAI") as mock_openai, patch("logging.info") as mock_info:

            mock_client = Mock()
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = "Test summary"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            sample_content = "Test content for logging behavior"
            summarizer = AISummarizer()
            summarizer.summarize(sample_content)

            # Verify success logging
            mock_info.assert_called_once_with("AI summary generated")

        # Test error logging
        with (
            patch("openai.OpenAI") as mock_openai,
            patch("logging.error") as mock_error,
        ):

            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("Test error")
            mock_openai.return_value = mock_client

            sample_content = "Test content for error logging"
            summarizer = AISummarizer()
            summarizer.summarize(sample_content)

            # Verify error logging
            mock_error.assert_called_once()
            assert "AI summarization error: Test error" in mock_error.call_args[0][0]
