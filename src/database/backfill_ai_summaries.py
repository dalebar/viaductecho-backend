#!/usr/bin/env python3
"""
Backfill AI summaries for existing articles that don't have them yet
"""
import logging
import os
import sys
import time
from datetime import datetime

# Setup path to import from src
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))  # noqa

from src.database.models import RSSArticle  # noqa
from src.database.operations import DatabaseOperations  # noqa
from src.processors.ai_summarizer import AISummarizer  # noqa
from src.processors.content_extractor import ContentExtractor  # noqa


def setup_logging():
    """Setup logging for the backfill process"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logs_dir = os.path.join(os.path.dirname(__file__), "../../logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_filename = os.path.join(logs_dir, f"backfill_ai_summaries_{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
    )
    logging.info(f"Backfill AI summaries started - logging to {log_filename}")


def main():
    setup_logging()

    db = DatabaseOperations()
    ai_summarizer = AISummarizer()
    content_extractor = ContentExtractor()

    try:
        # Get articles without AI summaries
        articles_without_summary = (
            db.session.query(RSSArticle)
            .filter((RSSArticle.ai_summary.is_(None)) | (RSSArticle.ai_summary == ""))
            .all()
        )

        total_articles = len(articles_without_summary)
        logging.info(f"Found {total_articles} articles without AI summaries")

        if total_articles == 0:
            logging.info("All articles already have AI summaries!")
            return

        processed_count = 0
        error_count = 0

        for i, article in enumerate(articles_without_summary, 1):
            try:
                logging.info(
                    f"Processing article {i}/{total_articles}: "
                    f"{article.original_title}"
                )

                # If no extracted content, try to extract it first
                content_to_summarize = article.extracted_content

                if not content_to_summarize or content_to_summarize.strip() == "":
                    logging.info(
                        f"No extracted content, extracting from URL: "
                        f"{article.original_link}"
                    )
                    try:
                        content_data = content_extractor.extract_content(
                            article.original_link,
                            article.original_source,
                        )
                        content_to_summarize = content_data.get("content", "")

                        # Update the extracted content in database
                        if content_to_summarize:
                            db.update_article_content(
                                article.original_link,
                                content_to_summarize,
                                content_data.get("image_url"),
                            )
                    except Exception as e:
                        logging.warning(
                            f"Content extraction failed for "
                            f"{article.original_title}: {e}"
                        )
                        # Fall back to using the summary as content
                        content_to_summarize = article.original_summary

                # Generate AI summary
                if content_to_summarize and content_to_summarize.strip():
                    ai_summary = ai_summarizer.summarize(content_to_summarize)

                    if ai_summary and ai_summary.strip():
                        # Update database with AI summary
                        db.update_article_ai_summary(article.original_link, ai_summary)
                        processed_count += 1
                        logging.info(
                            f"✓ Added AI summary for: " f"{article.original_title}"
                        )
                    else:
                        logging.warning(
                            f"AI summarizer returned empty result for: "
                            f"{article.original_title}"
                        )
                        error_count += 1
                else:
                    logging.warning(
                        f"No content available to summarize for: "
                        f"{article.original_title}"
                    )
                    error_count += 1

                # Rate limiting - be nice to OpenAI API
                if i % 10 == 0:
                    logging.info(
                        f"Progress: {i}/{total_articles} processed. "
                        f"Taking a short break..."
                    )
                    time.sleep(2)
                else:
                    time.sleep(0.5)

            except Exception as e:
                logging.error(f"Error processing article {article.original_title}: {e}")
                error_count += 1
                continue

        # Final statistics
        logging.info("Backfill completed!")
        logging.info(f"Successfully processed: {processed_count}")
        logging.info(f"Errors: {error_count}")
        logging.info(f"Total articles: {total_articles}")

    except Exception as e:
        logging.error(f"Fatal error in backfill process: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
