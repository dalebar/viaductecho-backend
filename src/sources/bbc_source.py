import feedparser
from datetime import datetime
from typing import List, Dict
from .base_source import BaseNewsSource
from config import Config
import logging

class BBCSource(BaseNewsSource):
    def __init__(self):
        super().__init__("BBC News")
        self.feed_url = "http://feeds.bbci.co.uk/news/england/manchester/rss.xml"
    
    def fetch_articles(self) -> List[Dict]:
        try:
            feed = feedparser.parse(self.feed_url)
            articles = []
            
            for entry in feed.entries:
                article = {
                    'original_title': entry.title,
                    'original_link': entry.link,
                    'original_summary': entry.get('summary', ''),
                    'original_source': self.source_name,
                    'source_type': 'RSS News',
                    'original_pubdate': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else None
                }
                articles.append(article)
            
            filtered = self.filter_articles(articles, Config.KEYWORDS)
            logging.info(f"BBC: {len(filtered)} articles found")
            return filtered
            
        except Exception as e:
            logging.error(f"BBC fetch error: {e}")
            return []