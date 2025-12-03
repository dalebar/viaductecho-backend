from typing import Dict, List

import feedparser

from .base_source import BaseNewsSource, build_article_from_feed_entry

try:
    from ..config import Config
except ImportError:
    from config import Config

import logging


class MENSource(BaseNewsSource):
    def __init__(self):
        super().__init__("Manchester Evening News")
        self.feed_url = "https://www.manchestereveningnews.co.uk/news/greater-manchester-news/?service=rss"

    def fetch_articles(self) -> List[Dict]:
        try:
            feed = feedparser.parse(self.feed_url)
            articles = []

            for entry in feed.entries:
                article = build_article_from_feed_entry(
                    entry, self.source_name, "RSS News"
                )

                # Filter out aggregator-style "Top stories" articles
                title_lower = article["original_title"].lower()
                if (
                    "top" in title_lower
                    and "stories" in title_lower
                    and ("missed" in title_lower or "week" in title_lower)
                ):
                    logging.info(
                        f"Skipping aggregator article: {article['original_title']}"
                    )
                    continue

                articles.append(article)

            filtered = self.filter_articles(articles, Config.KEYWORDS)
            logging.info(f"MEN: {len(filtered)} articles found")
            return filtered

        except Exception as e:
            logging.error(f"MEN fetch error: {e}")
            return []
