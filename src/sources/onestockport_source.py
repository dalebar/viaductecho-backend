import logging
from datetime import datetime
from typing import Dict, List

from playwright.sync_api import sync_playwright

from .base_source import BaseNewsSource

try:
    from ..config import Config
except ImportError:
    from config import Config


class OneStockportSource(BaseNewsSource):
    def __init__(self):
        super().__init__("One Stockport")
        self.base_url = "https://www.onestockport.co.uk/news/"

    def fetch_articles(self) -> List[Dict]:
        try:
            articles = []

            logging.info("Fetching One Stockport news with Playwright...")

            with sync_playwright() as p:
                # Launch browser (headless mode)
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Navigate to news page
                page.goto(self.base_url, wait_until="networkidle")

                # Wait for articles to load (FacetWP AJAX)
                page.wait_for_selector(".news-post_wrapper", timeout=10000)

                # Extract all article elements
                article_elements = page.query_selector_all(".news-post_wrapper")

                logging.info(f"Found {len(article_elements)} articles on One Stockport")

                for article in article_elements:
                    try:
                        # Extract title
                        title_elem = article.query_selector("h3")
                        if not title_elem:
                            continue

                        title = title_elem.inner_text().strip()

                        # Extract link
                        link_elem = article.query_selector("a")
                        if not link_elem:
                            continue

                        link = link_elem.get_attribute("href")
                        if not link:
                            continue

                        # Make absolute URL
                        if link.startswith("/"):
                            link = f"https://www.onestockport.co.uk{link}"

                        # Extract date (format: "02 12 25" = DD MM YY)
                        date_elem = article.query_selector(".news_date_categ")
                        pubdate = None

                        if date_elem:
                            date_text = date_elem.inner_text().strip()
                            # Extract just the date part (first line)
                            date_parts = date_text.split("\n")[0].strip().split()

                            if len(date_parts) >= 3:
                                try:
                                    # Parse "02 12 25" format
                                    day, month, year = date_parts[:3]
                                    # Convert 2-digit year to 4-digit (25 -> 2025)
                                    full_year = f"20{year}"
                                    date_string = f"{day} {month} {full_year}"
                                    pubdate = datetime.strptime(date_string, "%d %m %Y")
                                except ValueError as e:
                                    logging.warning(
                                        f"Could not parse date from One Stockport: {date_text} - {e}"
                                    )

                        # Extract category (if available)
                        category = ""
                        if date_elem:
                            lines = date_elem.inner_text().strip().split("\n")
                            if len(lines) > 1:
                                category = lines[1].strip()

                        # Build article data
                        # Note: One Stockport doesn't show summaries on list page
                        article_data = {
                            "original_title": title,
                            "original_link": link,
                            "original_summary": (
                                f"Category: {category}" if category else ""
                            ),
                            "original_source": self.source_name,
                            "source_type": "Web Scraping (Playwright)",
                            "original_pubdate": pubdate,
                        }

                        articles.append(article_data)

                    except Exception as e:
                        logging.error(f"Error parsing One Stockport article: {e}")
                        continue

                browser.close()

            # Filter by keywords
            filtered = self.filter_articles(articles, Config.KEYWORDS)
            logging.info(f"One Stockport: {len(filtered)} articles found")
            return filtered

        except Exception as e:
            logging.error(f"One Stockport fetch error: {e}")
            return []
