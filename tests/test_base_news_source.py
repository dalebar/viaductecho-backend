#!/usr/bin/env python3
"""
Comprehensive test suite for BaseNewsSource class
"""

import os
import sys
from abc import ABC
from typing import List, Dict
import pytest

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))  # noqa

from sources.base_source import BaseNewsSource  # noqa


class TestBaseNewsSource:
    """Test suite for BaseNewsSource abstract class"""

    def test_cannot_instantiate_abstract_class(self):
        """Test that BaseNewsSource cannot be instantiated directly"""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseNewsSource("Test Source")

    def test_is_abstract_base_class(self):
        """Test that BaseNewsSource is properly defined as ABC"""
        assert issubclass(BaseNewsSource, ABC)
        assert hasattr(BaseNewsSource, "__abstractmethods__")
        assert "fetch_articles" in BaseNewsSource.__abstractmethods__

    def test_concrete_implementation_can_be_instantiated(self):
        """Test that concrete implementations can be instantiated"""

        class ConcreteNewsSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return [
                    {
                        "original_title": "Test Article",
                        "original_summary": "Test summary",
                    }
                ]

        source = ConcreteNewsSource("Concrete Test Source")
        assert source.source_name == "Concrete Test Source"
        assert isinstance(source, BaseNewsSource)

    def test_concrete_implementation_must_implement_fetch_articles(self):
        """Test that concrete implementations must implement fetch_articles"""

        class IncompleteNewsSource(BaseNewsSource):
            pass  # Missing fetch_articles implementation

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteNewsSource("Incomplete Source")

    def test_source_name_initialization(self):
        """Test that source_name is properly set during initialization"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("My Test Source")
        assert source.source_name == "My Test Source"

    def test_filter_articles_basic_filtering(self):
        """Test basic article filtering functionality"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("Test Source")

        articles = [
            {
                "original_title": "Stockport Council Meeting",
                "original_summary": "Local government news",
            },
            {
                "original_title": "Manchester United News",
                "original_summary": "Football update",
            },
            {
                "original_title": "Weather Update",
                "original_summary": "Rain expected in Stockport",
            },
            {
                "original_title": "London News",
                "original_summary": "Capital city updates",
            },
        ]

        keywords = ["stockport", "manchester"]
        filtered = source.filter_articles(articles, keywords)

        assert len(filtered) == 3
        assert filtered[0]["original_title"] == "Stockport Council Meeting"
        assert filtered[1]["original_title"] == "Manchester United News"
        assert filtered[2]["original_title"] == "Weather Update"

    def test_filter_articles_case_insensitive(self):
        """Test that filtering is case insensitive"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("Test Source")

        articles = [
            {
                "original_title": "STOCKPORT NEWS",
                "original_summary": "Capital case title",
            },
            {
                "original_title": "local news",
                "original_summary": "News about MACCLESFIELD",
            },
            {"original_title": "Mixed Case", "original_summary": "Story about Buxton"},
        ]

        keywords = ["stockport", "macclesfield", "buxton"]
        filtered = source.filter_articles(articles, keywords)

        assert len(filtered) == 3

    def test_filter_articles_title_and_summary_matching(self):
        """Test that filtering works on both title and summary"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("Test Source")

        articles = [
            {
                "original_title": "Local Council News",
                "original_summary": "Meeting in Stockport today",
            },
            {
                "original_title": "Stockport Events",
                "original_summary": "Various local activities",
            },
            {
                "original_title": "National News",
                "original_summary": "Nothing local here",
            },
            {
                "original_title": "Weather",
                "original_summary": "Macclesfield will see rain",
            },
        ]

        keywords = ["stockport", "macclesfield"]
        filtered = source.filter_articles(articles, keywords)

        assert len(filtered) == 3
        # First matches in summary, second in title, fourth in summary
        assert "Local Council News" in [a["original_title"] for a in filtered]
        assert "Stockport Events" in [a["original_title"] for a in filtered]
        assert "Weather" in [a["original_title"] for a in filtered]

    def test_filter_articles_empty_articles_list(self):
        """Test filtering with empty articles list"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("Test Source")

        filtered = source.filter_articles([], ["stockport", "manchester"])
        assert filtered == []

    def test_filter_articles_empty_keywords_list(self):
        """Test filtering with empty keywords list"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("Test Source")

        articles = [
            {"original_title": "Stockport News", "original_summary": "Local update"},
            {"original_title": "Manchester News", "original_summary": "City update"},
        ]

        filtered = source.filter_articles(articles, [])
        assert filtered == []

    def test_filter_articles_no_matching_keywords(self):
        """Test filtering when no articles match keywords"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("Test Source")

        articles = [
            {"original_title": "London News", "original_summary": "Capital updates"},
            {
                "original_title": "Birmingham News",
                "original_summary": "Midlands update",
            },
        ]

        keywords = ["stockport", "manchester"]
        filtered = source.filter_articles(articles, keywords)
        assert filtered == []

    def test_filter_articles_missing_title_field(self):
        """Test filtering with articles missing original_title field"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("Test Source")

        articles = [
            {"original_summary": "Article about Stockport"},  # Missing title
            {"original_title": "Manchester News", "original_summary": "City update"},
            {},  # Missing both title and summary
        ]

        keywords = ["stockport", "manchester"]
        filtered = source.filter_articles(articles, keywords)

        # Should match first article by summary and second by title
        assert len(filtered) == 2

    def test_filter_articles_missing_summary_field(self):
        """Test filtering with articles missing original_summary field"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("Test Source")

        articles = [
            {"original_title": "Stockport Council Meeting"},  # Missing summary
            {"original_title": "London News", "original_summary": "Capital updates"},
            {"original_title": "Weather News"},  # Missing summary
        ]

        keywords = ["stockport"]
        filtered = source.filter_articles(articles, keywords)

        # Should match first article by title only
        assert len(filtered) == 1
        assert filtered[0]["original_title"] == "Stockport Council Meeting"

    def test_filter_articles_partial_keyword_matching(self):
        """Test that partial keyword matching works"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("Test Source")

        articles = [
            {
                "original_title": "Greater Manchester News",
                "original_summary": "Regional update",
            },
            {
                "original_title": "Stockport-based Company",
                "original_summary": "Business news",
            },
            {
                "original_title": "Local News",
                "original_summary": "About New Macclesfield development",
            },
        ]

        keywords = ["manchester", "stockport", "macclesfield"]
        filtered = source.filter_articles(articles, keywords)

        # All should match due to partial string matching
        assert len(filtered) == 3

    def test_filter_articles_special_characters_in_content(self):
        """Test filtering with special characters in titles and summaries"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("Test Source")

        articles = [
            {
                "original_title": "Stockport's New Initiative",
                "original_summary": "Local program",
            },
            {
                "original_title": "Manchester United F.C.",
                "original_summary": "Football club news",
            },
            {
                "original_title": "High Peak & District",
                "original_summary": "Regional coverage",
            },
        ]

        keywords = ["stockport", "manchester", "high peak"]
        filtered = source.filter_articles(articles, keywords)

        assert len(filtered) == 3

    def test_filter_articles_unicode_characters(self):
        """Test filtering with unicode characters"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("Test Source")

        articles = [
            {
                "original_title": "Stockport café opens",
                "original_summary": "New business",
            },
            {
                "original_title": "Manchester événement",
                "original_summary": "Cultural event",
            },
            {"original_title": "Regular news", "original_summary": "Nothing special"},
        ]

        keywords = ["stockport", "manchester"]
        filtered = source.filter_articles(articles, keywords)

        assert len(filtered) == 2

    def test_filter_articles_preserves_original_data(self):
        """Test that filtering preserves all original article data"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("Test Source")

        articles = [
            {
                "original_title": "Stockport Council Meeting",
                "original_summary": "Local government news",
                "original_link": "https://example.com/stockport-news",
                "original_source": "Test News",
                "extra_field": "should be preserved",
            }
        ]

        keywords = ["stockport"]
        filtered = source.filter_articles(articles, keywords)

        assert len(filtered) == 1
        assert filtered[0]["original_link"] == "https://example.com/stockport-news"
        assert filtered[0]["original_source"] == "Test News"
        assert filtered[0]["extra_field"] == "should be preserved"

    def test_filter_articles_performance_with_large_dataset(self):
        """Test filtering performance with a large number of articles"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("Test Source")

        # Create a large dataset
        articles = []
        for i in range(1000):
            if i % 10 == 0:  # Every 10th article contains keyword
                articles.append(
                    {
                        "original_title": f"Article {i} about Stockport",
                        "original_summary": f"Content {i}",
                    }
                )
            else:
                articles.append(
                    {
                        "original_title": f"Article {i}",
                        "original_summary": f"Content {i} without keywords",
                    }
                )

        keywords = ["stockport"]
        filtered = source.filter_articles(articles, keywords)

        # Should find 100 articles (every 10th from 1000)
        assert len(filtered) == 100


class TestBaseNewsSourceIntegration:
    """Integration tests for BaseNewsSource with real-world scenarios"""

    def test_concrete_implementation_workflow(self):
        """Test complete workflow with a concrete implementation"""

        class MockNewsSource(BaseNewsSource):
            def __init__(self, source_name: str):
                super().__init__(source_name)
                self.mock_data = [
                    {
                        "original_title": "Stockport Market Reopens",
                        "original_summary": "Local shopping venue",
                    },
                    {
                        "original_title": "Manchester Airport Expansion",
                        "original_summary": "Travel news",
                    },
                    {
                        "original_title": "London Stock Exchange",
                        "original_summary": "Financial news",
                    },
                    {
                        "original_title": "Weather Update",
                        "original_summary": "Macclesfield expects snow",
                    },
                ]

            def fetch_articles(self) -> List[Dict]:
                # Simulate fetching and filtering in one step
                keywords = ["stockport", "manchester", "macclesfield"]
                return self.filter_articles(self.mock_data, keywords)

        source = MockNewsSource("Mock Local News")
        articles = source.fetch_articles()

        # Should return 3 articles (excluding London Stock Exchange)
        assert len(articles) == 3
        assert source.source_name == "Mock Local News"

        # Verify the correct articles are returned
        titles = [article["original_title"] for article in articles]
        assert "Stockport Market Reopens" in titles
        assert "Manchester Airport Expansion" in titles
        assert "Weather Update" in titles
        assert "London Stock Exchange" not in titles

    def test_multiple_keyword_sets(self):
        """Test filtering with different keyword sets"""

        class TestSource(BaseNewsSource):
            def fetch_articles(self) -> List[Dict]:
                return []

        source = TestSource("Test Source")

        articles = [
            {
                "original_title": "Stockport Council Budget",
                "original_summary": "Financial planning",
            },
            {
                "original_title": "Manchester United Match",
                "original_summary": "Football news",
            },
            {"original_title": "Buxton Festival", "original_summary": "Cultural event"},
            {
                "original_title": "London Parliament",
                "original_summary": "National politics",
            },
        ]

        # Test with different keyword sets
        local_keywords = ["stockport", "manchester", "buxton"]
        sports_keywords = ["united", "match", "football"]
        political_keywords = ["council", "parliament", "budget"]

        local_filtered = source.filter_articles(articles, local_keywords)
        sports_filtered = source.filter_articles(articles, sports_keywords)
        political_filtered = source.filter_articles(articles, political_keywords)

        assert len(local_filtered) == 3  # First three articles
        assert len(sports_filtered) == 1  # Manchester United Match
        assert len(political_filtered) == 2  # Council Budget and Parliament

    def test_inheritance_chain(self):
        """Test that inheritance works properly through multiple levels"""

        class IntermediateSource(BaseNewsSource):
            def __init__(self, source_name: str, region: str):
                super().__init__(source_name)
                self.region = region

            def get_region_keywords(self) -> List[str]:
                return (
                    ["stockport", "manchester", "macclesfield"]
                    if self.region == "greater_manchester"
                    else []
                )

        class SpecificSource(IntermediateSource):
            def fetch_articles(self) -> List[Dict]:
                mock_articles = [
                    {
                        "original_title": "Stockport News",
                        "original_summary": "Local update",
                    }
                ]
                keywords = self.get_region_keywords()
                return self.filter_articles(mock_articles, keywords)

        source = SpecificSource("Specific Local News", "greater_manchester")

        # Test that all inheritance works
        assert isinstance(source, BaseNewsSource)
        assert isinstance(source, IntermediateSource)
        assert source.source_name == "Specific Local News"
        assert source.region == "greater_manchester"

        articles = source.fetch_articles()
        assert len(articles) == 1
