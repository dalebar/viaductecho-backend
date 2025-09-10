from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List


class BaseNewsSource(ABC):
    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    def fetch_articles(self) -> List[Dict]:
        """Fetch and filter articles"""
        pass

    def filter_articles(self, articles: List[Dict], keywords: List[str]) -> List[Dict]:
        """Filter articles by keywords"""
        filtered = []
        for article in articles:
            title = article.get("original_title", "").lower()
            summary = article.get("original_summary", "").lower()

            if any(keyword in title or keyword in summary for keyword in keywords):
                filtered.append(article)

        return filtered


def build_article_from_feed_entry(
    entry, source_name: str, source_type: str = "RSS News"
) -> Dict:
    """Build a standardized article dict from a feedparser entry.

    Keeps identical behavior to existing sources regarding fields and defaults.
    """
    # Handle optional summary safely via entry.get("summary", "")
    summary = None
    try:
        summary = entry.get("summary", "")
    except Exception:
        summary = ""

    # published_parsed may be absent; mimic prior hasattr check
    if hasattr(entry, "published_parsed") and entry.published_parsed is not None:
        pubdate = datetime(*entry.published_parsed[:6])
    else:
        pubdate = None

    return {
        "original_title": entry.title,
        "original_link": entry.link,
        "original_summary": summary,
        "original_source": source_name,
        "source_type": source_type,
        "original_pubdate": pubdate,
    }
