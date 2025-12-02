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

    def publish_json_file(
        self, file_path: str, content: str, commit_message: str
    ) -> bool:
        """
        Publish or update a JSON file to GitHub Pages repo

        Args:
            file_path: Path within repo (e.g., "api/events.json")
            content: JSON content as string
            commit_message: Commit message

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # First, check if file exists to get its SHA (needed for updates)
            url = f"https://api.github.com/repos/{self.repo}/contents/{file_path}"
            params = {"ref": self.branch}

            get_response = requests.get(
                url, headers=self.headers, params=params, timeout=Config.HTTP_TIMEOUT
            )

            # Prepare the content
            encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

            data = {
                "message": commit_message,
                "content": encoded_content,
                "branch": self.branch,
            }

            # If file exists, include its SHA for update
            if get_response.status_code == 200:
                file_sha = get_response.json().get("sha")
                data["sha"] = file_sha
                logging.info(f"Updating existing file: {file_path}")
            else:
                logging.info(f"Creating new file: {file_path}")

            # Create or update the file
            put_response = requests.put(
                url, json=data, headers=self.headers, timeout=Config.HTTP_TIMEOUT
            )

            if put_response.status_code in (200, 201):
                logging.info(f"Successfully published: {file_path}")
                return True
            else:
                logging.error(
                    f"GitHub publish failed: {put_response.status_code} - {put_response.text}"
                )
                return False

        except Exception as e:
            logging.error(f"Error publishing {file_path}: {e}")
            return False

    def publish_static_json_files(self, static_data_dir: str = "static_data") -> dict:
        """
        Publish all static JSON files from static_data/ to GitHub Pages api/ directory

        Args:
            static_data_dir: Local directory containing JSON files

        Returns:
            dict: Results with success status and details
        """
        from pathlib import Path

        results = {"success": True, "published": [], "failed": []}

        try:
            static_path = Path(static_data_dir)

            if not static_path.exists():
                results["success"] = False
                results["error"] = f"Directory {static_data_dir} not found"
                return results

            # Find all JSON files
            json_files = list(static_path.glob("*.json"))

            if not json_files:
                results["success"] = False
                results["error"] = "No JSON files found in static_data/"
                return results

            # Publish each file
            for json_file in json_files:
                with open(json_file, "r") as f:
                    content = f.read()

                # Publish to api/ directory in Jekyll repo
                remote_path = f"api/{json_file.name}"
                commit_msg = f"Update {json_file.name} via admin dashboard"

                if self.publish_json_file(remote_path, content, commit_msg):
                    results["published"].append(json_file.name)
                else:
                    results["failed"].append(json_file.name)
                    results["success"] = False

            logging.info(
                f"Published {len(results['published'])} files, {len(results['failed'])} failed"
            )
            return results

        except Exception as e:
            logging.error(f"Error publishing static files: {e}")
            results["success"] = False
            results["error"] = str(e)
            return results
