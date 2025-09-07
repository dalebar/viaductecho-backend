#!/usr/bin/env python3
"""
Check the current status of AI summaries in the database
"""
import sys

# Setup path to import from src
sys.path.append('./src')

from src.database.operations import DatabaseOperations
from src.database.models import RSSArticle


def main():
    db = DatabaseOperations()
    
    try:
        # Get total articles
        total_articles = db.session.query(RSSArticle).count()
        
        # Get articles with AI summaries
        articles_with_summary = db.session.query(RSSArticle).filter(
            (RSSArticle.ai_summary.isnot(None)) & (RSSArticle.ai_summary != "")
        ).count()
        
        # Get articles without AI summaries
        articles_without_summary = db.session.query(RSSArticle).filter(
            (RSSArticle.ai_summary.is_(None)) | (RSSArticle.ai_summary == "")
        ).count()
        
        # Get processed articles
        processed_articles = db.session.query(RSSArticle).filter(RSSArticle.processed == True).count()
        
        print("\n=== AI Summary Status Report ===")
        print(f"Total articles in database: {total_articles}")
        print(f"Articles with AI summaries: {articles_with_summary}")
        print(f"Articles without AI summaries: {articles_without_summary}")
        print(f"Processed articles: {processed_articles}")
        print(f"AI summary completion rate: {(articles_with_summary/total_articles*100):.1f}%" if total_articles > 0 else "N/A")
        
        if articles_without_summary > 0:
            print(f"\n💡 You can run 'python backfill_ai_summaries.py' to generate summaries for {articles_without_summary} articles")
        else:
            print(f"\n✅ All articles have AI summaries!")
        
        print("\n=== Recent articles without summaries ===")
        recent_without_summary = db.session.query(RSSArticle).filter(
            (RSSArticle.ai_summary.is_(None)) | (RSSArticle.ai_summary == "")
        ).order_by(RSSArticle.created_at.desc()).limit(5).all()
        
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