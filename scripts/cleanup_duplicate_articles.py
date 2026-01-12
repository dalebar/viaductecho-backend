#!/usr/bin/env python3
"""
Script to find and delete duplicate/broken articles from the Jekyll repo.

When articles are republished, new files are created with today's date.
This script finds old versions of the same article and deletes them.

Usage:
    python -m scripts.cleanup_duplicate_articles --dry-run  # Preview what will be deleted
    python -m scripts.cleanup_duplicate_articles            # Delete old duplicates
"""

import argparse
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

import requests

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class JekyllRepoCleaner:
    def __init__(self):
        self.token = Config.GITHUB_TOKEN
        self.repo = Config.GITHUB_REPO
        self.branch = Config.GITHUB_BRANCH
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def get_all_posts(self) -> list:
        """Get all files from _posts directory."""
        url = f"https://api.github.com/repos/{self.repo}/contents/_posts"
        params = {"ref": self.branch}

        response = requests.get(url, headers=self.headers, params=params, timeout=30)

        if response.status_code != 200:
            logging.error(f"Failed to get posts: {response.status_code}")
            return []

        return response.json()

    def extract_slug(self, filename: str) -> str:
        """Extract slug from filename (remove date prefix and .md extension)."""
        # Filename format: YYYY-MM-DD-slug-here.md
        match = re.match(r"\d{4}-\d{2}-\d{2}-(.+)\.md$", filename)
        if match:
            return match.group(1)
        return filename

    def extract_date(self, filename: str) -> str:
        """Extract date from filename."""
        match = re.match(r"(\d{4}-\d{2}-\d{2})-", filename)
        if match:
            return match.group(1)
        return ""

    def find_duplicates(self, posts: list) -> dict:
        """Find posts with the same slug but different dates."""
        # Group posts by slug
        by_slug = defaultdict(list)

        for post in posts:
            filename = post["name"]
            slug = self.extract_slug(filename)
            date = self.extract_date(filename)
            by_slug[slug].append(
                {
                    "filename": filename,
                    "date": date,
                    "sha": post["sha"],
                }
            )

        # Find slugs with multiple versions
        duplicates = {
            slug: versions for slug, versions in by_slug.items() if len(versions) > 1
        }

        return duplicates

    def delete_file(self, filename: str, sha: str) -> bool:
        """Delete a file from the repo."""
        url = f"https://api.github.com/repos/{self.repo}/contents/_posts/{filename}"

        data = {
            "message": f"Cleanup: Remove duplicate article {filename}",
            "sha": sha,
            "branch": self.branch,
        }

        response = requests.delete(url, json=data, headers=self.headers, timeout=30)

        if response.status_code in (200, 204):
            logging.info(f"Deleted: {filename}")
            return True
        else:
            logging.error(f"Failed to delete {filename}: {response.status_code}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Find and delete duplicate articles from Jekyll repo"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show duplicates without deleting",
    )
    args = parser.parse_args()

    cleaner = JekyllRepoCleaner()

    # Get all posts
    logging.info("Fetching posts from Jekyll repo...")
    posts = cleaner.get_all_posts()

    if not posts:
        logging.error("No posts found or failed to fetch posts")
        return

    logging.info(f"Found {len(posts)} total posts")

    # Find duplicates
    duplicates = cleaner.find_duplicates(posts)

    if not duplicates:
        logging.info("No duplicate articles found!")
        return

    logging.info(f"\nFound {len(duplicates)} articles with duplicates:\n")

    # For each set of duplicates, keep the newest and mark others for deletion
    to_delete = []

    for slug, versions in duplicates.items():
        # Sort by date, newest first
        versions.sort(key=lambda x: x["date"], reverse=True)

        logging.info(f"Slug: {slug}")
        for i, v in enumerate(versions):
            if i == 0:
                logging.info(f"  KEEP:   {v['filename']} ({v['date']})")
            else:
                logging.info(f"  DELETE: {v['filename']} ({v['date']})")
                to_delete.append(v)

    if not to_delete:
        logging.info("\nNo files to delete.")
        return

    logging.info(f"\n{len(to_delete)} files marked for deletion.")

    if args.dry_run:
        logging.info("\nDry run - no files deleted. Run without --dry-run to delete.")
        return

    # Confirm deletion
    logging.info("\nDeleting old duplicates...")

    success = 0
    failed = 0

    for item in to_delete:
        if cleaner.delete_file(item["filename"], item["sha"]):
            success += 1
        else:
            failed += 1

    logging.info(f"\nDone! Deleted: {success}, Failed: {failed}")


if __name__ == "__main__":
    main()
