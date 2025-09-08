#!/usr/bin/env python3
"""
Comprehensive test suite for MENSource class
"""

import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sources.men_source import MENSource
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


class TestMENSource:
    """Test suite for MENSource class"""

    def test_initialization(self):
        """Test MENSource initializes correctly"""
        source = MENSource()

        assert isinstance(source, BaseNewsSource)
        assert source.source_name == "Manchester Evening News"
        assert (
            source.feed_url
            == "https://www.manchestereveningnews.co.uk/news/greater-manchester-news/?service=rss"
        )

    def test_inherits_from_base_news_source(self):
        """Test that MENSource properly inherits from BaseNewsSource"""
        source = MENSource()

        assert isinstance(source, BaseNewsSource)
        assert hasattr(source, "filter_articles")
        assert callable(source.fetch_articles)

    @patch("sources.men_source.Config")
    @patch("sources.men_source.feedparser.parse")
    def test_fetch_articles_success(self, mock_feedparser, mock_config):
        """Test successful article fetching"""
        # Setup mock config
        mock_config.KEYWORDS = ["stockport", "manchester", "macclesfield"]

        # Setup mock feed data
        mock_entry1 = create_mock_rss_entry(
            "Stockport town centre to see major redevelopment",
            "https://www.manchestereveningnews.co.uk/news/stockport-redevelopment",
            "Council approves ambitious regeneration plans",
            (2024, 3, 15, 10, 30, 0),
        )

        mock_entry2 = create_mock_rss_entry(
            "Manchester United fans react to transfer window",
            "https://www.manchestereveningnews.co.uk/sport/manchester-united-transfer",
            "Supporters share views on new signings",
            (2024, 3, 15, 14, 45, 0),
        )

        mock_entry3 = create_mock_rss_entry(
            "Birmingham traffic chaos continues",
            "https://www.manchestereveningnews.co.uk/news/birmingham-traffic",
            "Motorway closure causes delays",
            # No published_parsed to test None handling
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry1, mock_entry2, mock_entry3]
        mock_feedparser.return_value = mock_feed

        source = MENSource()

        with patch("logging.info") as mock_log_info:
            articles = source.fetch_articles()

            # Should return 2 articles (Stockport and Manchester, not Birmingham)
            assert len(articles) == 2

            # Check first article
            assert (
                articles[0]["original_title"]
                == "Stockport town centre to see major redevelopment"
            )
            assert (
                articles[0]["original_link"]
                == "https://www.manchestereveningnews.co.uk/news/stockport-redevelopment"
            )
            assert (
                articles[0]["original_summary"]
                == "Council approves ambitious regeneration plans"
            )
            assert articles[0]["original_source"] == "Manchester Evening News"
            assert articles[0]["source_type"] == "RSS News"
            assert articles[0]["original_pubdate"] == datetime(2024, 3, 15, 10, 30, 0)

            # Check second article
            assert (
                articles[1]["original_title"]
                == "Manchester United fans react to transfer window"
            )
            assert (
                articles[1]["original_link"]
                == "https://www.manchestereveningnews.co.uk/sport/manchester-united-transfer"
            )
            assert (
                articles[1]["original_summary"]
                == "Supporters share views on new signings"
            )
            assert articles[1]["original_source"] == "Manchester Evening News"
            assert articles[1]["source_type"] == "RSS News"
            assert articles[1]["original_pubdate"] == datetime(2024, 3, 15, 14, 45, 0)

            # Verify logging
            mock_log_info.assert_called_once_with("MEN: 2 articles found")

    @patch("sources.men_source.Config")
    @patch("sources.men_source.feedparser.parse")
    def test_fetch_articles_empty_feed(self, mock_feedparser, mock_config):
        """Test handling of empty RSS feed"""
        mock_config.KEYWORDS = ["stockport", "manchester"]

        mock_feed = Mock()
        mock_feed.entries = []
        mock_feedparser.return_value = mock_feed

        source = MENSource()

        with patch("logging.info") as mock_log_info:
            articles = source.fetch_articles()

            assert articles == []
            mock_log_info.assert_called_once_with("MEN: 0 articles found")

    @patch("sources.men_source.Config")
    @patch("sources.men_source.feedparser.parse")
    def test_fetch_articles_no_matching_keywords(self, mock_feedparser, mock_config):
        """Test when no articles match the keywords"""
        mock_config.KEYWORDS = ["stockport", "manchester", "macclesfield"]

        mock_entry = create_mock_rss_entry(
            "London property market update",
            "https://www.manchestereveningnews.co.uk/news/london-property",
            "Capital city real estate trends",
            (2024, 3, 15, 10, 30, 0),
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = MENSource()

        with patch("logging.info") as mock_log_info:
            articles = source.fetch_articles()

            assert articles == []
            mock_log_info.assert_called_once_with("MEN: 0 articles found")

    @patch("sources.men_source.Config")
    @patch("sources.men_source.feedparser.parse")
    def test_fetch_articles_missing_summary(self, mock_feedparser, mock_config):
        """Test handling of entries without summary field"""
        mock_config.KEYWORDS = ["stockport"]

        mock_entry = create_mock_rss_entry(
            "Stockport college announces new courses",
            "https://www.manchestereveningnews.co.uk/news/stockport-college",
            None,  # No summary
            (2024, 3, 15, 10, 30, 0),
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = MENSource()

        articles = source.fetch_articles()

        assert len(articles) == 1
        assert articles[0]["original_summary"] == ""  # Should default to empty string

    @patch("sources.men_source.Config")
    @patch("sources.men_source.feedparser.parse")
    def test_fetch_articles_missing_published_date(self, mock_feedparser, mock_config):
        """Test handling of entries without published_parsed field"""
        mock_config.KEYWORDS = ["manchester"]

        mock_entry = create_mock_rss_entry(
            "Manchester City Council budget approved",
            "https://www.manchestereveningnews.co.uk/news/manchester-council-budget",
            "Annual spending plans confirmed",
            # No published_parsed - omitted
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = MENSource()

        articles = source.fetch_articles()

        assert len(articles) == 1
        assert articles[0]["original_pubdate"] is None

    @patch("sources.men_source.Config")
    @patch("sources.men_source.feedparser.parse")
    def test_fetch_articles_feedparser_exception(self, mock_feedparser, mock_config):
        """Test handling of feedparser exceptions"""
        mock_config.KEYWORDS = ["stockport"]
        mock_feedparser.side_effect = Exception("RSS feed unavailable")

        source = MENSource()

        with patch("logging.error") as mock_log_error:
            articles = source.fetch_articles()

            assert articles == []
            mock_log_error.assert_called_once_with(
                "MEN fetch error: RSS feed unavailable"
            )

    @patch("sources.men_source.Config")
    @patch("sources.men_source.feedparser.parse")
    def test_fetch_articles_malformed_date(self, mock_feedparser, mock_config):
        """Test handling of malformed published_parsed dates"""
        mock_config.KEYWORDS = ["manchester"]

        mock_entry = create_mock_rss_entry(
            "Manchester transport improvements announced",
            "https://www.manchestereveningnews.co.uk/news/manchester-transport",
            "New bus routes planned",
            (2024, 3),  # Incomplete date tuple
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = MENSource()

        with patch("logging.error") as mock_log_error:
            articles = source.fetch_articles()

            # Should handle the error and return empty list
            assert articles == []
            mock_log_error.assert_called_once()

    @patch("sources.men_source.Config")
    @patch("sources.men_source.feedparser.parse")
    def test_fetch_articles_keyword_filtering(self, mock_feedparser, mock_config):
        """Test that keyword filtering works correctly"""
        mock_config.KEYWORDS = ["stockport", "manchester", "high peak"]

        # Create entries with different keyword matches
        mock_entries = [
            # Should match on title
            create_mock_rss_entry(
                "Stockport market traders celebrate success",
                "https://men.co.uk/1",
                "Local business community thriving",
                (2024, 1, 1, 10, 0, 0),
            ),
            # Should match on summary
            create_mock_rss_entry(
                "Local business roundup",
                "https://men.co.uk/2",
                "Manchester companies report strong growth",
                (2024, 1, 2, 11, 0, 0),
            ),
            # Should not match
            create_mock_rss_entry(
                "Liverpool docks expansion",
                "https://men.co.uk/3",
                "Merseyside port development",
                (2024, 1, 3, 12, 0, 0),
            ),
            # Should match on partial word
            create_mock_rss_entry(
                "High Peak District tourism boost",
                "https://men.co.uk/4",
                "Visitor numbers increase",
                (2024, 1, 4, 13, 0, 0),
            ),
        ]

        mock_feed = Mock()
        mock_feed.entries = mock_entries
        mock_feedparser.return_value = mock_feed

        source = MENSource()
        articles = source.fetch_articles()

        # Should return 3 articles (excluding Liverpool)
        assert len(articles) == 3

        titles = [article["original_title"] for article in articles]
        assert "Stockport market traders celebrate success" in titles
        assert "Local business roundup" in titles
        assert "High Peak District tourism boost" in titles
        assert "Liverpool docks expansion" not in titles

    @patch("sources.men_source.Config")
    @patch("sources.men_source.feedparser.parse")
    def test_fetch_articles_case_insensitive_filtering(
        self, mock_feedparser, mock_config
    ):
        """Test that keyword filtering is case insensitive"""
        mock_config.KEYWORDS = ["manchester"]  # lowercase

        mock_entry = create_mock_rss_entry(
            "MANCHESTER CITY CENTRE DEVELOPMENT",  # uppercase
            "https://www.manchestereveningnews.co.uk/news/manchester-development",
            "Urban regeneration project announced",
            (2024, 3, 15, 10, 30, 0),
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = MENSource()
        articles = source.fetch_articles()

        # Should match despite case difference
        assert len(articles) == 1
        assert articles[0]["original_title"] == "MANCHESTER CITY CENTRE DEVELOPMENT"

    @patch("sources.men_source.Config")
    @patch("sources.men_source.feedparser.parse")
    def test_fetch_articles_preserves_all_fields(self, mock_feedparser, mock_config):
        """Test that all article fields are properly preserved"""
        mock_config.KEYWORDS = ["macclesfield"]

        mock_entry = create_mock_rss_entry(
            "Macclesfield Forest trail reopens",
            "https://www.manchestereveningnews.co.uk/news/macclesfield-forest",
            "Popular walking route restored after maintenance",
            (2024, 3, 15, 10, 30, 0),
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = MENSource()
        articles = source.fetch_articles()

        assert len(articles) == 1
        article = articles[0]

        # Check all expected fields are present and correct
        assert article["original_title"] == "Macclesfield Forest trail reopens"
        assert (
            article["original_link"]
            == "https://www.manchestereveningnews.co.uk/news/macclesfield-forest"
        )
        assert (
            article["original_summary"]
            == "Popular walking route restored after maintenance"
        )
        assert article["original_source"] == "Manchester Evening News"
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
        source = MENSource()
        expected_url = "https://www.manchestereveningnews.co.uk/news/greater-manchester-news/?service=rss"
        assert source.feed_url == expected_url

    @patch("sources.men_source.Config")
    @patch("sources.men_source.feedparser.parse")
    def test_logging_behavior(self, mock_feedparser, mock_config):
        """Test that logging works correctly for both success and error cases"""
        mock_config.KEYWORDS = ["manchester"]

        # Test successful logging
        mock_entry = create_mock_rss_entry(
            "Manchester weather warning issued",
            "https://men.co.uk/weather",
            "Met office alerts residents",
            (2024, 1, 1, 10, 0, 0),
        )

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        with patch("logging.info") as mock_log_info:
            source = MENSource()
            _ = source.fetch_articles()
            mock_log_info.assert_called_once_with("MEN: 1 articles found")

        # Test error logging
        mock_feedparser.side_effect = Exception("Connection timeout")

        with patch("logging.error") as mock_log_error:
            source = MENSource()
            _ = source.fetch_articles()
            mock_log_error.assert_called_once_with(
                "MEN fetch error: Connection timeout"
            )


class TestMENSourceIntegration:
    """Integration tests for MENSource"""

    @patch("sources.men_source.Config")
    @patch("sources.men_source.feedparser.parse")
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
                "Stockport Grammar School celebrates achievements",
                "Students excel in national competitions",
            ),
            (
                "Manchester Airport welcomes new airline",
                "International route expansion continues",
            ),
            (
                "Macclesfield Silk Museum exhibition opens",
                "Local history showcased in new display",
            ),
            ("High Peak walking festival announced", "Annual outdoor event returns"),
            (
                "Buxton Opera House hosts charity gala",
                "Local performers raise funds for community",
            ),
        ]

        # Non-local news that should be excluded
        non_local_entries = [
            (
                "Leeds United transfer speculation",
                "Championship club considers new signings",
            ),
            ("Sheffield transport updates", "City tram system improvements"),
            ("Liverpool FC European campaign", "Champions League preparation begins"),
        ]

        # Add local entries
        for i, (title, summary) in enumerate(local_entries):
            entry = create_mock_rss_entry(
                title,
                f"https://www.manchestereveningnews.co.uk/news/local-{i}",
                summary,
                (2024, 3, i + 1, 10 + i, 0, 0),
            )
            entries.append(entry)

        # Add non-local entries
        for i, (title, summary) in enumerate(non_local_entries):
            entry = create_mock_rss_entry(
                title,
                f"https://www.manchestereveningnews.co.uk/news/national-{i}",
                summary,
                (2024, 3, 10 + i, 10 + i, 0, 0),
            )
            entries.append(entry)

        mock_feed = Mock()
        mock_feed.entries = entries
        mock_feedparser.return_value = mock_feed

        source = MENSource()

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
            mock_log_info.assert_called_once_with("MEN: 5 articles found")

    @patch("sources.men_source.Config")
    def test_error_recovery(self, mock_config):
        """Test that MENSource recovers gracefully from various errors"""
        mock_config.KEYWORDS = ["manchester"]
        source = MENSource()

        # Test various error scenarios
        error_scenarios = [
            Exception("Network timeout"),
            ConnectionError("Unable to reach server"),
            ValueError("Invalid RSS format"),
            KeyError("Missing entry field"),
        ]

        for error in error_scenarios:
            with (
                patch("sources.men_source.feedparser.parse") as mock_feedparser,
                patch("logging.error") as mock_log_error,
            ):

                mock_feedparser.side_effect = error

                articles = source.fetch_articles()

                # Should always return empty list on error
                assert articles == []

                # Should always log the error
                mock_log_error.assert_called_once()
                assert str(error) in mock_log_error.call_args[0][0]

    @patch("sources.men_source.Config")
    @patch("sources.men_source.feedparser.parse")
    def test_real_world_rss_structure(self, mock_feedparser, mock_config):
        """Test with realistic RSS feed structure similar to actual MEN feeds"""
        mock_config.KEYWORDS = ["stockport"]

        # Simulate realistic MEN RSS entry structure
        mock_entry = create_mock_rss_entry(
            "Stockport County FC prepare for new season with ambitious signings",
            "https://www.manchestereveningnews.co.uk/sport/football/stockport-county-fc-transfers-2024",
            "The League Two club has been busy in the transfer market as they look to build on last season's success.",
            (2024, 3, 15, 14, 30, 45, 3, 75, 0),  # Full time tuple
        )

        # Add some additional fields that might be present in real feeds
        mock_entry.id = "https://www.manchestereveningnews.co.uk/sport/football/stockport-county-fc-transfers-2024"
        mock_entry.author = "MEN Sport"
        mock_entry.tags = [{"term": "Football"}, {"term": "Stockport County"}]

        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        source = MENSource()
        articles = source.fetch_articles()

        assert len(articles) == 1
        article = articles[0]

        # Should extract the core fields correctly
        assert (
            article["original_title"]
            == "Stockport County FC prepare for new season with ambitious signings"
        )
        assert (
            article["original_link"]
            == "https://www.manchestereveningnews.co.uk/sport/football/stockport-county-fc-transfers-2024"
        )
        assert "transfer market as they look to build" in article["original_summary"]
        assert article["original_source"] == "Manchester Evening News"
        assert article["source_type"] == "RSS News"

        # Should handle the full date tuple correctly
        expected_date = datetime(2024, 3, 15, 14, 30, 45)
        assert article["original_pubdate"] == expected_date
