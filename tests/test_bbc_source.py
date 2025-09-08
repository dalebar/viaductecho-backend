#!/usr/bin/env python3
"""
Comprehensive test suite for BBCSource class
"""

import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch

# Removed SimpleNamespace import, using Mock instead

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sources.bbc_source import BBCSource
from sources.base_source import BaseNewsSource


def create_mock_rss_entry(title, link, summary=None, published_parsed=None):
    """Helper function to create properly mocked RSS entries"""
    entry = Mock()
    entry.title = title
    entry.link = link

    # Mock the .get() method for summary - this handles entry.get('summary', '')
    def get_method(key, default=""):
        if key == "summary":
            return summary if summary is not None else default
        return default

    entry.get = Mock(side_effect=get_method)

    # Set published_parsed if provided
    if published_parsed is not None:
        entry.published_parsed = published_parsed
    else:
        # Ensure hasattr returns False when no published_parsed
        del entry.published_parsed

    return entry


class TestBBCSource:
    """Test suite for BBCSource class"""

    def test_initialization(self):
        """Test BBCSource initializes correctly"""
        source = BBCSource()

        assert isinstance(source, BaseNewsSource)
        assert source.source_name == "BBC News"
        assert (
            source.feed_url == "http://feeds.bbci.co.uk/news/england/manchester/rss.xml"
        )

    def test_inherits_from_base_news_source(self):
        """Test that BBCSource properly inherits from BaseNewsSource"""
        source = BBCSource()

        assert isinstance(source, BaseNewsSource)
        assert hasattr(source, "filter_articles")
        assert callable(source.fetch_articles)

    @patch("sources.bbc_source.Config")
    @patch("sources.bbc_source.feedparser.parse")
    def test_fetch_articles_success(self, mock_feedparser, mock_config):
        """Test successful article fetching"""
        # Setup mock config
        mock_config.KEYWORDS = ["stockport", "manchester", "macclesfield"]

        # Setup mock feed data
        mock_entry1 = create_mock_rss_entry(
            "Stockport Council announces new initiative",
            "https://www.bbc.com/news/stockport-initiative",
            "Local government launches community program",
            (2024, 3, 15, 10, 30, 0),
        )

        mock_entry2 = create_mock_rss_entry(
            "Manchester United transfer news",
            "https://www.bbc.com/sport/manchester-united",
            "Football club considers new signing",
            (2024, 3, 15, 14, 45, 0),
        )

        mock_entry3 = create_mock_rss_entry(
            "London weather update",
            "https://www.bbc.com/weather/london",
            "Capital city forecast",
            # No published_parsed to test None handling
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry1, mock_entry2, mock_entry3]
        mock_feedparser.return_value = mock_feed

        source = BBCSource()

        with patch("logging.info") as mock_log_info:
            articles = source.fetch_articles()

            # Should return 2 articles (Stockport and Manchester, not London)
            assert len(articles) == 2

            # Check first article
            assert (
                articles[0]["original_title"]
                == "Stockport Council announces new initiative"
            )
            assert (
                articles[0]["original_link"]
                == "https://www.bbc.com/news/stockport-initiative"
            )
            assert (
                articles[0]["original_summary"]
                == "Local government launches community program"
            )
            assert articles[0]["original_source"] == "BBC News"
            assert articles[0]["source_type"] == "RSS News"
            assert articles[0]["original_pubdate"] == datetime(2024, 3, 15, 10, 30, 0)

            # Check second article
            assert articles[1]["original_title"] == "Manchester United transfer news"
            assert (
                articles[1]["original_link"]
                == "https://www.bbc.com/sport/manchester-united"
            )
            assert (
                articles[1]["original_summary"] == "Football club considers new signing"
            )
            assert articles[1]["original_source"] == "BBC News"
            assert articles[1]["source_type"] == "RSS News"
            assert articles[1]["original_pubdate"] == datetime(2024, 3, 15, 14, 45, 0)

            # Verify logging
            mock_log_info.assert_called_once_with("BBC: 2 articles found")

    @patch("sources.bbc_source.Config")
    @patch("sources.bbc_source.feedparser.parse")
    def test_fetch_articles_empty_feed(self, mock_feedparser, mock_config):
        """Test handling of empty RSS feed"""
        mock_config.KEYWORDS = ["stockport", "manchester"]

        mock_feed = Mock()
        mock_feed.entries = []
        mock_feedparser.return_value = mock_feed

        source = BBCSource()

        with patch("logging.info") as mock_log_info:
            articles = source.fetch_articles()

            assert articles == []
            mock_log_info.assert_called_once_with("BBC: 0 articles found")

    @patch("sources.bbc_source.Config")
    @patch("sources.bbc_source.feedparser.parse")
    def test_fetch_articles_no_matching_keywords(self, mock_feedparser, mock_config):
        """Test when no articles match the keywords"""
        mock_config.KEYWORDS = ["stockport", "manchester", "macclesfield"]

        mock_entry = create_mock_rss_entry(
            "London news update",
            "https://www.bbc.com/news/london",
            "Capital city developments",
            (2024, 3, 15, 10, 30, 0),
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = BBCSource()

        with patch("logging.info") as mock_log_info:
            articles = source.fetch_articles()

            assert articles == []
            mock_log_info.assert_called_once_with("BBC: 0 articles found")

    @patch("sources.bbc_source.Config")
    @patch("sources.bbc_source.feedparser.parse")
    def test_fetch_articles_missing_summary(self, mock_feedparser, mock_config):
        """Test handling of entries without summary field"""
        mock_config.KEYWORDS = ["stockport"]

        mock_entry = create_mock_rss_entry(
            "Stockport market reopens",
            "https://www.bbc.com/news/stockport-market",
            None,  # No summary
            (2024, 3, 15, 10, 30, 0),
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = BBCSource()

        articles = source.fetch_articles()

        assert len(articles) == 1
        assert articles[0]["original_summary"] == ""  # Should default to empty string

    @patch("sources.bbc_source.Config")
    @patch("sources.bbc_source.feedparser.parse")
    def test_fetch_articles_missing_published_date(self, mock_feedparser, mock_config):
        """Test handling of entries without published_parsed field"""
        mock_config.KEYWORDS = ["stockport"]

        mock_entry = create_mock_rss_entry(
            "Stockport festival announced",
            "https://www.bbc.com/news/stockport-festival",
            "Annual cultural event details",
            # No published_parsed - omitted
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = BBCSource()

        articles = source.fetch_articles()

        assert len(articles) == 1
        assert articles[0]["original_pubdate"] is None

    @patch("sources.bbc_source.Config")
    @patch("sources.bbc_source.feedparser.parse")
    def test_fetch_articles_feedparser_exception(self, mock_feedparser, mock_config):
        """Test handling of feedparser exceptions"""
        mock_config.KEYWORDS = ["stockport"]
        mock_feedparser.side_effect = Exception("Network error")

        source = BBCSource()

        with patch("logging.error") as mock_log_error:
            articles = source.fetch_articles()

            assert articles == []
            mock_log_error.assert_called_once_with("BBC fetch error: Network error")

    @patch("sources.bbc_source.Config")
    @patch("sources.bbc_source.feedparser.parse")
    def test_fetch_articles_malformed_date(self, mock_feedparser, mock_config):
        """Test handling of malformed published_parsed dates"""
        mock_config.KEYWORDS = ["stockport"]

        mock_entry = create_mock_rss_entry(
            "Stockport development news",
            "https://www.bbc.com/news/stockport-development",
            "New housing project",
            (2024, 3),  # Incomplete date tuple
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = BBCSource()

        with patch("logging.error") as mock_log_error:
            articles = source.fetch_articles()

            # Should handle the error and return empty list
            assert articles == []
            mock_log_error.assert_called_once()

    @patch("sources.bbc_source.Config")
    @patch("sources.bbc_source.feedparser.parse")
    def test_fetch_articles_keyword_filtering(self, mock_feedparser, mock_config):
        """Test that keyword filtering works correctly"""
        mock_config.KEYWORDS = ["stockport", "manchester", "buxton"]

        # Create entries with different keyword matches
        mock_entries = [
            # Should match on title
            create_mock_rss_entry(
                "Stockport Council budget approved",
                "https://bbc.com/1",
                "Local authority finances",
                (2024, 1, 1, 10, 0, 0),
            ),
            # Should match on summary
            create_mock_rss_entry(
                "Local government news",
                "https://bbc.com/2",
                "Manchester City Council meeting",
                (2024, 1, 2, 11, 0, 0),
            ),
            # Should not match
            create_mock_rss_entry(
                "London weather forecast",
                "https://bbc.com/3",
                "Capital city conditions",
                (2024, 1, 3, 12, 0, 0),
            ),
            # Should match on partial word
            create_mock_rss_entry(
                "Greater Manchester transport",
                "https://bbc.com/4",
                "Regional travel updates",
                (2024, 1, 4, 13, 0, 0),
            ),
        ]

        mock_feed = Mock()
        mock_feed.entries = mock_entries
        mock_feedparser.return_value = mock_feed

        source = BBCSource()
        articles = source.fetch_articles()

        # Should return 3 articles (excluding London)
        assert len(articles) == 3

        titles = [article["original_title"] for article in articles]
        assert "Stockport Council budget approved" in titles
        assert "Local government news" in titles
        assert "Greater Manchester transport" in titles
        assert "London weather forecast" not in titles

    @patch("sources.bbc_source.Config")
    @patch("sources.bbc_source.feedparser.parse")
    def test_fetch_articles_case_insensitive_filtering(
        self, mock_feedparser, mock_config
    ):
        """Test that keyword filtering is case insensitive"""
        mock_config.KEYWORDS = ["stockport"]  # lowercase

        mock_entry = create_mock_rss_entry(
            "STOCKPORT MARKET UPDATE",  # uppercase
            "https://www.bbc.com/news/stockport-market",
            "Market renovation progress",
            (2024, 3, 15, 10, 30, 0),
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = BBCSource()
        articles = source.fetch_articles()

        # Should match despite case difference
        assert len(articles) == 1
        assert articles[0]["original_title"] == "STOCKPORT MARKET UPDATE"

    @patch("sources.bbc_source.Config")
    @patch("sources.bbc_source.feedparser.parse")
    def test_fetch_articles_preserves_all_fields(self, mock_feedparser, mock_config):
        """Test that all article fields are properly preserved"""
        mock_config.KEYWORDS = ["stockport"]

        mock_entry = create_mock_rss_entry(
            "Stockport heritage project",
            "https://www.bbc.com/news/stockport-heritage",
            "Historical preservation initiative",
            (2024, 3, 15, 10, 30, 0),
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = BBCSource()
        articles = source.fetch_articles()

        assert len(articles) == 1
        article = articles[0]

        # Check all expected fields are present and correct
        assert article["original_title"] == "Stockport heritage project"
        assert article["original_link"] == "https://www.bbc.com/news/stockport-heritage"
        assert article["original_summary"] == "Historical preservation initiative"
        assert article["original_source"] == "BBC News"
        assert article["source_type"] == "RSS News"
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

    def test_feed_url_is_correct(self):
        """Test that the RSS feed URL is correct"""
        source = BBCSource()
        expected_url = "http://feeds.bbci.co.uk/news/england/manchester/rss.xml"
        assert source.feed_url == expected_url

    @patch("sources.bbc_source.Config")
    @patch("sources.bbc_source.feedparser.parse")
    def test_logging_behavior(self, mock_feedparser, mock_config):
        """Test that logging works correctly for both success and error cases"""
        mock_config.KEYWORDS = ["stockport"]

        # Test successful logging
        mock_entry = create_mock_rss_entry(
            "Stockport news item",
            "https://bbc.com/news",
            "Test summary",
            (2024, 1, 1, 10, 0, 0),
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = BBCSource()

        with patch("logging.info") as mock_log_info:
            articles = source.fetch_articles()
            mock_log_info.assert_called_once_with("BBC: 1 articles found")

        # Test error logging
        mock_feedparser.side_effect = Exception("Test error")

        with patch("logging.error") as mock_log_error:
            articles = source.fetch_articles()
            mock_log_error.assert_called_once_with("BBC fetch error: Test error")


class TestBBCSourceIntegration:
    """Integration tests for BBCSource"""

    @patch("sources.bbc_source.Config")
    @patch("sources.bbc_source.feedparser.parse")
    def test_complete_workflow(self, mock_feedparser, mock_config):
        """Test complete article fetching and filtering workflow"""
        mock_config.KEYWORDS = [
            "stockport",
            "manchester",
            "macclesfield",
            "buxton",
            "high peak",
        ]

        # Create a realistic set of RSS entries
        entries = []

        # Local news that should be included
        local_entries = [
            (
                "Stockport Market renovation begins",
                "Construction work starts on historic market",
            ),
            (
                "Manchester Airport expansion approved",
                "Runway development gets green light",
            ),
            (
                "Macclesfield festival cancelled",
                "Annual event postponed due to weather",
            ),
            (
                "High Peak hiking trails closed",
                "Safety concerns prompt temporary closure",
            ),
            (
                "Buxton Opera House reopens",
                "Venue welcomes back audiences after refurbishment",
            ),
        ]

        # Non-local news that should be excluded
        non_local_entries = [
            ("London Stock Market rises", "Financial markets show positive movement"),
            ("Birmingham traffic delays", "City center construction causes disruption"),
            ("Liverpool FC transfer news", "Football club confirms new signing"),
        ]

        # Add local entries
        for i, (title, summary) in enumerate(local_entries):
            entry = create_mock_rss_entry(
                title,
                f"https://www.bbc.com/news/local-{i}",
                summary,
                (2024, 3, i + 1, 10 + i, 0, 0),
            )
            entries.append(entry)

        # Add non-local entries
        for i, (title, summary) in enumerate(non_local_entries):
            entry = create_mock_rss_entry(
                title,
                f"https://www.bbc.com/news/national-{i}",
                summary,
                (2024, 3, 10 + i, 10 + i, 0, 0),
            )
            entries.append(entry)

        mock_feed = Mock()
        mock_feed.entries = entries
        mock_feedparser.return_value = mock_feed

        source = BBCSource()

        with patch("logging.info") as mock_log_info:
            articles = source.fetch_articles()

            # Should return only the 5 local articles
            assert len(articles) == 5

            # Verify all local articles are included
            titles = [article["original_title"] for article in articles]
            for title, _ in local_entries:
                assert title in titles

            # Verify non-local articles are excluded
            for title, _ in non_local_entries:
                assert title not in titles

            # Verify logging
            mock_log_info.assert_called_once_with("BBC: 5 articles found")

    @patch("sources.bbc_source.Config")
    def test_error_recovery(self, mock_config):
        """Test that BBCSource recovers gracefully from various errors"""
        mock_config.KEYWORDS = ["stockport"]
        source = BBCSource()

        # Test various error scenarios
        error_scenarios = [
            Exception("Network timeout"),
            ConnectionError("Unable to connect"),
            ValueError("Invalid feed format"),
            KeyError("Missing required field"),
        ]

        for error in error_scenarios:
            with (
                patch("sources.bbc_source.feedparser.parse") as mock_feedparser,
                patch("logging.error") as mock_log_error,
            ):

                mock_feedparser.side_effect = error

                articles = source.fetch_articles()

                # Should always return empty list on error
                assert articles == []

                # Should always log the error
                mock_log_error.assert_called_once()
                assert str(error) in mock_log_error.call_args[0][0]

    @patch("sources.bbc_source.Config")
    @patch("sources.bbc_source.feedparser.parse")
    def test_real_world_rss_structure(self, mock_feedparser, mock_config):
        """Test with realistic RSS feed structure similar to actual BBC feeds"""
        mock_config.KEYWORDS = ["manchester"]

        # Simulate realistic BBC RSS entry structure
        mock_entry = create_mock_rss_entry(
            "Manchester United prepare for Champions League",
            "https://www.bbc.com/sport/football/manchester-united-12345",
            "The football club continues preparations for European competition with new signings expected.",
            (2024, 3, 15, 14, 30, 45, 3, 75, 0),  # Full time tuple
        )

        # Add some additional fields that might be present in real feeds
        mock_entry.id = "https://www.bbc.com/sport/football/manchester-united-12345"
        mock_entry.author = "BBC Sport"
        mock_entry.tags = [{"term": "Football"}, {"term": "Manchester United"}]

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = BBCSource()
        articles = source.fetch_articles()

        assert len(articles) == 1
        article = articles[0]

        # Should extract the core fields correctly
        assert (
            article["original_title"]
            == "Manchester United prepare for Champions League"
        )
        assert (
            article["original_link"]
            == "https://www.bbc.com/sport/football/manchester-united-12345"
        )
        assert "competition with new signings" in article["original_summary"]
        assert article["original_source"] == "BBC News"
        assert article["source_type"] == "RSS News"

        # Should handle the full date tuple correctly
        expected_date = datetime(2024, 3, 15, 14, 30, 45)
        assert article["original_pubdate"] == expected_date
