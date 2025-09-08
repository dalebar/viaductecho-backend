#!/usr/bin/env python3
"""
Check the current status of AI summaries in the database
"""
import os
import sys

# Setup path to import from src
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))  # noqa

from src.database.models import RSSArticle  # noqa
from src.database.operations import DatabaseOperations  # noqa


def main():
    db = DatabaseOperations()

    try:
        # Get total articles
        total_articles = db.session.query(RSSArticle).count()

        # Get articles with AI summaries
        articles_with_summary = (
            db.session.query(RSSArticle)
            .filter((RSSArticle.ai_summary.isnot(None)) & (RSSArticle.ai_summary != ""))
            .count()
        )

        # Get articles without AI summaries
        articles_without_summary = (
            db.session.query(RSSArticle)
            .filter((RSSArticle.ai_summary.is_(None)) | (RSSArticle.ai_summary == ""))
            .count()
        )

        # Get processed articles
        processed_articles = (
            db.session.query(RSSArticle).filter(RSSArticle.processed.is_(True)).count()
        )

        print("\n=== AI Summary Status Report ===")
        print(f"Total articles in database: {total_articles}")
        print(f"Articles with AI summaries: {articles_with_summary}")
        print(f"Articles without AI summaries: {articles_without_summary}")
        print(f"Processed articles: {processed_articles}")
        completion_rate = (
            f"{(articles_with_summary / total_articles * 100):.1f}%"
            if total_articles > 0
            else "N/A"
        )
        print(f"AI summary completion rate: {completion_rate}")

        if articles_without_summary > 0:
            print(
                f"\n💡 You can run 'python src/database/"
                f"backfill_ai_summaries.py' to generate summaries for "
                f"{articles_without_summary} articles"
            )
        else:
            print("\n✅ All articles have AI summaries!")

        print("\n=== Recent articles without summaries ===")
        recent_without_summary = (
            db.session.query(RSSArticle)
            .filter((RSSArticle.ai_summary.is_(None)) | (RSSArticle.ai_summary == ""))
            .order_by(RSSArticle.created_at.desc())
            .limit(5)
            .all()
        )

        for article in recent_without_summary:
            print(f"- {article.original_title[:80]}...")
            print(f"  Source: {article.original_source}")
            print(f"  Created: {article.created_at}")
            print()

    except Exception as e:
        print(f"Error checking AI summary status: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
