#!/usr/bin/env python3
"""
Script to republish articles with double quotes in their titles.

These articles may have been published with broken YAML front matter,
causing them to display as "Untitled" on the Jekyll site.

Usage:
    python -m scripts.republish_quoted_titles --dry-run  # Preview affected articles
    python -m scripts.republish_quoted_titles            # Republish affected articles
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.operations import DatabaseOperations
from src.publishers.github_publisher import GitHubPublisher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def find_affected_articles(db: DatabaseOperations) -> list:
    """Find all published articles with double quotes in their titles."""
    try:
        # Get all published articles
        result = db.get_all_articles(limit=1000, status_filter="published")
        articles = result.get("articles", [])

        # Filter to those with double quotes in title
        affected = [
            article for article in articles if '"' in (article.original_title or "")
        ]

        return affected

    except Exception as e:
        logging.error(f"Error finding affected articles: {e}")
        return []


def republish_article(publisher: GitHubPublisher, article) -> bool:
    """Republish a single article with corrected title escaping."""
    try:
        article_data = {
            "original_title": article.original_title,
            "original_link": article.original_link,
            "original_source": article.original_source,
        }

        # Use the stored AI summary and image URL
        summary = article.ai_summary or article.original_summary or ""
        image_url = article.image_url or ""

        success = publisher.publish_article(article_data, summary, image_url)

        if success:
            logging.info(f"Republished: {article.original_title}")
        else:
            logging.error(f"Failed to republish: {article.original_title}")

        return success

    except Exception as e:
        logging.error(f"Error republishing article: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Republish articles with double quotes in titles"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show affected articles without republishing",
    )
    args = parser.parse_args()

    db = DatabaseOperations()
    publisher = GitHubPublisher()

    try:
        # Find affected articles
        affected = find_affected_articles(db)

        if not affected:
            logging.info("No articles with double quotes in titles found.")
            return

        logging.info(f"Found {len(affected)} articles with double quotes in titles:")
        for article in affected:
            logging.info(f"  - {article.original_title}")

        if args.dry_run:
            logging.info(
                "\nDry run - no changes made. Run without --dry-run to republish."
            )
            return

        # Republish each affected article
        logging.info("\nRepublishing affected articles...")
        success_count = 0
        fail_count = 0

        for article in affected:
            if republish_article(publisher, article):
                success_count += 1
            else:
                fail_count += 1

        logging.info(f"\nDone! Republished: {success_count}, Failed: {fail_count}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
