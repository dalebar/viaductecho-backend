import logging
from datetime import datetime
from typing import Dict, List

from playwright.sync_api import sync_playwright

from .base_source import BaseNewsSource

try:
    from ..config import Config
except ImportError:
    from config import Config


class StockportCouncilSource(BaseNewsSource):
    def __init__(self):
        super().__init__("Stockport Council")
        self.base_url = "https://www.stockport.gov.uk/landing/news-media"

    def fetch_articles(self) -> List[Dict]:
        try:
            articles = []

            logging.info("Fetching Stockport Council news with Playwright...")

            with sync_playwright() as p:
                # Launch browser with realistic settings to avoid detection
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage",
                        "--no-sandbox",
                    ],
                )

                # Create context with realistic user agent and viewport
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080},
                    locale="en-GB",
                )

                page = context.new_page()

                # Navigate to news page
                try:
                    page.goto(self.base_url, wait_until="networkidle", timeout=30000)
                except Exception as e:
                    logging.error(f"Failed to load Stockport Council page: {e}")
                    browser.close()
                    return []

                # Wait for articles to load
                try:
                    page.wait_for_selector("article, .news-item, .card", timeout=10000)
                except Exception as e:
                    logging.warning(
                        f"Timeout waiting for articles on Stockport Council: {e}"
                    )

                # Try multiple selectors to find articles
                article_elements = page.query_selector_all("article")

                if not article_elements:
                    article_elements = page.query_selector_all(".news-item")

                if not article_elements:
                    article_elements = page.query_selector_all(".card")

                if not article_elements:
                    # Try finding any links in a news container
                    article_elements = page.query_selector_all("a[href*='/news/']")

                logging.info(
                    f"Found {len(article_elements)} potential articles on Stockport Council"
                )

                for article in article_elements:
                    try:
                        # Extract title
                        title_elem = article.query_selector("h2, h3, h4, .title")
                        if not title_elem:
                            # If it's a link, try to get text from it
                            if article.evaluate("el => el.tagName") == "A":
                                title_elem = article

                        if not title_elem:
                            continue

                        title = title_elem.inner_text().strip()

                        if not title or len(title) < 5:
                            continue

                        # Extract link
                        if article.evaluate("el => el.tagName") == "A":
                            link = article.get_attribute("href")
                        else:
                            link_elem = article.query_selector("a")
                            if not link_elem:
                                continue
                            link = link_elem.get_attribute("href")

                        if not link:
                            continue

                        # Make absolute URL
                        if link.startswith("/"):
                            link = f"https://www.stockport.gov.uk{link}"

                        # Extract date (if available)
                        date_elem = article.query_selector(
                            "time, .date, .published, [datetime]"
                        )
                        pubdate = None

                        if date_elem:
                            # Try to get datetime attribute
                            datetime_attr = date_elem.get_attribute("datetime")
                            if datetime_attr:
                                try:
                                    pubdate = datetime.fromisoformat(
                                        datetime_attr.replace("Z", "+00:00")
                                    )
                                except ValueError:
                                    pass

                            # Try to parse text content
                            if not pubdate:
                                date_text = date_elem.inner_text().strip()
                                try:
                                    # Try common UK date formats
                                    for fmt in [
                                        "%d %B %Y",
                                        "%d/%m/%Y",
                                        "%B %d, %Y",
                                    ]:
                                        try:
                                            pubdate = datetime.strptime(date_text, fmt)
                                            break
                                        except ValueError:
                                            continue
                                except Exception as e:
                                    logging.debug(
                                        f"Could not parse date from Stockport Council: {e}"
                                    )

                        # Extract summary/excerpt
                        summary_elem = article.query_selector("p, .excerpt, .summary")
                        summary = ""
                        if summary_elem:
                            summary = summary_elem.inner_text().strip()

                        # Build article data
                        article_data = {
                            "original_title": title,
                            "original_link": link,
                            "original_summary": summary,
                            "original_source": self.source_name,
                            "source_type": "Web Scraping (Playwright)",
                            "original_pubdate": pubdate,
                        }

                        articles.append(article_data)

                    except Exception as e:
                        logging.error(f"Error parsing Stockport Council article: {e}")
                        continue

                browser.close()

            # Filter by keywords
            filtered = self.filter_articles(articles, Config.KEYWORDS)
            logging.info(f"Stockport Council: {len(filtered)} articles found")
            return filtered

        except Exception as e:
            logging.error(f"Stockport Council fetch error: {e}")
            return []
