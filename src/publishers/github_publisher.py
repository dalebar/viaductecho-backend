import base64
import re
from datetime import datetime

import requests

try:
    from ..config import Config
except ImportError:
    from config import Config

import logging


class GitHubPublisher:
    def __init__(self):
        self.token = Config.GITHUB_TOKEN
        self.repo = Config.GITHUB_REPO
        self.branch = Config.GITHUB_BRANCH
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def publish_article(self, article_data: dict, summary: str, image_url: str) -> bool:
        """Publish article to GitHub Pages"""
        try:
            jekyll_content = self._create_jekyll_content(
                article_data, summary, image_url
            )

            slug = self._create_slug(article_data["original_title"])
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_str}-{slug}.md"

            encoded_content = base64.b64encode(jekyll_content.encode("utf-8")).decode(
                "utf-8"
            )

            url = f"https://api.github.com/repos/{self.repo}/contents/_posts/{filename}"
            data = {
                "message": f"Auto-post: {article_data['original_title']}",
                "content": encoded_content,
                "branch": self.branch,
            }

            if Config.HTTP_TIMEOUT is not None:
                response = requests.put(
                    url, json=data, headers=self.headers, timeout=Config.HTTP_TIMEOUT
                )
            else:
                response = requests.put(url, json=data, headers=self.headers)

            if response.status_code == 201:
                logging.info(f"Published: {article_data['original_title']}")
                return True
            else:
                logging.error(
                    f"GitHub publish failed: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logging.error(f"Publishing error: {e}")
            return False

    def _create_jekyll_content(
        self, article: dict, summary: str, image_url: str
    ) -> str:
        """Create Jekyll markdown content"""
        content = f"""---
layout: post
title: "{article['original_title']}"
author: archie
categories: news
image: {image_url}
---
{summary}

![Article Image]({image_url})

[Read the full article at {article['original_source']}]({article['original_link']})

---
"""
        return content

    def _create_slug(self, title: str) -> str:
        """Create URL-safe slug from title"""
        slug = re.sub(r"[^\w\s-]", "", title.lower())
        slug = re.sub(r"[-\s]+", "-", slug).strip("-")
        return slug[:100]  # Increased from 50 to 100 characters for longer titles
