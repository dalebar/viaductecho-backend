import logging
from datetime import datetime
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from .base_source import BaseNewsSource

try:
    from ..config import Config
except ImportError:
    from config import Config


class TotallyStockportSource(BaseNewsSource):
    def __init__(self):
        super().__init__("Totally Stockport")
        self.base_url = "https://totallystockport.co.uk/latest-news/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def fetch_articles(self) -> List[Dict]:
        try:
            articles = []

            # Fetch first page
            logging.info("Fetching Totally Stockport news...")
            response = requests.get(
                self.base_url, headers=self.headers, timeout=Config.HTTP_TIMEOUT
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Find all article elements
            # WordPress blog layout - articles are in list items
            article_elements = soup.find_all("article", class_="post")

            if not article_elements:
                logging.warning(
                    "No articles found with 'post' class, trying alternative selectors"
                )
                # Try alternative selector
                article_elements = soup.find_all("div", class_="fusion-post-content")

            for article in article_elements:
                try:
                    # Extract title and link
                    title_elem = article.find("h2")
                    if not title_elem:
                        title_elem = article.find("h3")

                    if not title_elem:
                        continue

                    link_elem = title_elem.find("a")
                    if not link_elem:
                        continue

                    title = link_elem.get_text().strip()
                    link = link_elem.get("href", "")

                    # Extract date
                    date_elem = article.find("span", class_="updated")
                    if not date_elem:
                        date_elem = article.find("time")

                    pubdate = None
                    if date_elem:
                        date_text = date_elem.get_text().strip()
                        try:
                            # Try parsing "December 2, 2024" format
                            pubdate = datetime.strptime(date_text, "%B %d, %Y")
                        except ValueError:
                            try:
                                # Try alternative format
                                pubdate = datetime.strptime(date_text, "%d %B %Y")
                            except ValueError:
                                logging.warning(f"Could not parse date: {date_text}")

                    # Extract summary/excerpt
                    summary_elem = article.find(
                        "div", class_="fusion-post-content-container"
                    )
                    if not summary_elem:
                        summary_elem = article.find("div", class_="post-content")

                    summary = ""
                    if summary_elem:
                        # Get text from the first paragraph or the container
                        p = summary_elem.find("p")
                        if p:
                            summary = p.get_text().strip()
                        else:
                            summary = summary_elem.get_text().strip()

                        # Clean up summary
                        if "[...]" in summary:
                            summary = summary.replace("[...]", "").strip()
                        if "Read More" in summary:
                            summary = summary.split("Read More")[0].strip()

                    # Build article data
                    article_data = {
                        "original_title": title,
                        "original_link": link,
                        "original_summary": summary,
                        "original_source": self.source_name,
                        "source_type": "Web Scraping",
                        "original_pubdate": pubdate,
                    }

                    articles.append(article_data)

                except Exception as e:
                    logging.error(f"Error parsing Totally Stockport article: {e}")
                    continue

            # Filter by keywords
            filtered = self.filter_articles(articles, Config.KEYWORDS)
            logging.info(f"Totally Stockport: {len(filtered)} articles found")
            return filtered

        except Exception as e:
            logging.error(f"Totally Stockport fetch error: {e}")
            return []
