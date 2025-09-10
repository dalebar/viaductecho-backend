import json
import logging
import re
import time
from datetime import datetime
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from .base_source import BaseNewsSource

try:
    from ..config import Config
except ImportError:
    from config import Config


class NubSource(BaseNewsSource):
    def __init__(self):
        super().__init__("Stockport Nub News")
        self.base_url = "https://stockport.nub.news/news"
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; ViaductBot/1.0)"}

    def fetch_articles(self) -> List[Dict]:
        try:
            if Config.HTTP_TIMEOUT is not None:
                response = requests.get(
                    self.base_url, headers=self.headers, timeout=Config.HTTP_TIMEOUT
                )
            else:
                response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            script_tag = soup.find("script", type="application/ld+json")

            if not script_tag:
                return []

            json_content = re.sub(r"[\x00-\x1F\x7F]", " ", script_tag.string)
            articles_data = json.loads(json_content)

            articles = []
            for article in articles_data:
                try:
                    date_str = article["datePublished"]
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

                    article_data = {
                        "original_title": article["headline"],
                        "original_link": article["url"],
                        "original_summary": article["headline"],
                        "original_source": self.source_name,
                        "source_type": "Web scraping",
                        "original_pubdate": date_obj,
                    }
                    articles.append(article_data)

                except Exception as e:
                    logging.error(f"Error parsing Nub article: {e}")
                    continue

            time.sleep(2)
            logging.info(f"Nub News: {len(articles)} articles found")
            return articles

        except Exception as e:
            logging.error(f"Nub News fetch error: {e}")
            return []
