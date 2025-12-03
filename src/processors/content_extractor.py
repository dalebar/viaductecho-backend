import json
import logging
import re
import time
from typing import Dict

import requests

try:
    from ..config import Config
except ImportError:
    from config import Config
from bs4 import BeautifulSoup


class ContentExtractor:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def extract_content(self, url: str, source: str) -> Dict:
        """Extract content based on source"""
        try:
            if Config.HTTP_TIMEOUT is not None:
                response = requests.get(
                    url, headers=self.headers, timeout=Config.HTTP_TIMEOUT
                )
            else:
                response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            if "bbc.com" in url:
                return self._extract_bbc_content(soup)
            elif "manchestereveningnews.co.uk" in url:
                return self._extract_men_content(soup)
            elif "stockport.nub.news" in url:
                return self._extract_nub_content(soup)
            elif "totallystockport.co.uk" in url:
                return self._extract_totallystockport_content(soup)
            else:
                return self._extract_generic_content(soup)

        except Exception as e:
            logging.error(f"Content extraction error for {url}: {e}")
            return {"content": "", "image_url": ""}
        finally:
            time.sleep(1)

    def _extract_bbc_content(self, soup: BeautifulSoup) -> Dict:
        content_divs = soup.find_all("div", {"data-component": "text-block"})
        paragraphs = []
        for div in content_divs:
            p = div.find("p")
            if p:
                paragraphs.append(p.get_text().strip())

        content = "\n\n".join(paragraphs)

        og_image = soup.find("meta", property="og:image")
        image_url = og_image.get("content") if og_image else ""

        return {"content": content, "image_url": image_url}

    def _extract_men_content(self, soup: BeautifulSoup) -> Dict:
        content = ""

        # Try JSON-LD first (most reliable when present)
        script_tag = soup.find("script", type="application/ld+json")
        if script_tag:
            try:
                data = json.loads(script_tag.string)
                if isinstance(data, list):
                    data = data[0]
                content = data.get("articleBody", "")
                if content:
                    content = content.replace('\\"', '"').replace("\\n", "\n")
                    content = re.sub(r"<[^>]+>", "", content)
            except (json.JSONDecodeError, KeyError, TypeError):
                content = ""

        # Fallback: Scrape article content from HTML
        if not content or len(content.strip()) < 100:
            logging.info(
                "MEN JSON-LD extraction failed or too short, trying HTML fallback"
            )
            paragraphs = []

            # Try to find main article content div
            article_body = soup.find(
                "div", class_=re.compile(r"article-body|article__body")
            )
            if article_body:
                # Extract paragraphs
                for p in article_body.find_all("p"):
                    text = p.get_text().strip()
                    if text and len(text) > 20:  # Skip very short paragraphs
                        paragraphs.append(text)

                # Extract bullet points/lists
                for ul in article_body.find_all(["ul", "ol"]):
                    for li in ul.find_all("li"):
                        text = li.get_text().strip()
                        if text and len(text) > 10:
                            paragraphs.append(f"• {text}")

            # If no article body found, try generic paragraph search
            if not paragraphs:
                for p in soup.find_all("p"):
                    text = p.get_text().strip()
                    if text and len(text) > 20:
                        paragraphs.append(text)

            if paragraphs:
                content = "\n\n".join(paragraphs)
                logging.info(
                    f"MEN HTML fallback extracted {len(paragraphs)} paragraphs"
                )

        og_image = soup.find("meta", property="og:image")
        image_url = og_image.get("content") if og_image else ""

        return {"content": content, "image_url": image_url}

    def _extract_nub_content(self, soup: BeautifulSoup) -> Dict:
        content_div = soup.find("div", class_="prose max-w-none leading-snug")
        content = content_div.get_text().strip() if content_div else ""

        img_div = soup.find("div", class_="w-full overflow-hidden")
        image_url = ""
        if img_div:
            img = img_div.find("img")
            if img:
                image_url = img.get("src", "")

        return {"content": content, "image_url": image_url}

    def _extract_totallystockport_content(self, soup: BeautifulSoup) -> Dict:
        """Extract content from Totally Stockport WordPress articles"""
        paragraphs = []

        # Try to find main article content (WordPress post content)
        article_content = soup.find("div", class_="post-content")
        if not article_content:
            article_content = soup.find("div", class_="fusion-post-content")
        if not article_content:
            article_content = soup.find("article")

        if article_content:
            # Extract all paragraphs
            for p in article_content.find_all("p"):
                text = p.get_text().strip()
                if text and len(text) > 20:  # Skip very short paragraphs
                    paragraphs.append(text)

            # Extract bullet points/lists
            for ul in article_content.find_all(["ul", "ol"]):
                for li in ul.find_all("li"):
                    text = li.get_text().strip()
                    if text and len(text) > 10:
                        paragraphs.append(f"• {text}")

        # Fallback: generic paragraph search
        if not paragraphs:
            for p in soup.find_all("p"):
                text = p.get_text().strip()
                if text and len(text) > 20:
                    paragraphs.append(text)

        content = "\n\n".join(paragraphs) if paragraphs else ""

        # Extract image
        og_image = soup.find("meta", property="og:image")
        image_url = og_image.get("content") if og_image else ""

        return {"content": content, "image_url": image_url}

    def _extract_generic_content(self, soup: BeautifulSoup) -> Dict:
        content = ""
        paragraphs = soup.find_all("p")
        content = "\n\n".join([p.get_text().strip() for p in paragraphs[:5]])

        og_image = soup.find("meta", property="og:image")
        image_url = og_image.get("content") if og_image else ""

        return {"content": content, "image_url": image_url}
