import logging
import os
import time
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from .database.operations import DatabaseOperations
from .processors.ai_summarizer import AISummarizer
from .processors.content_extractor import ContentExtractor
from .publishers.github_publisher import GitHubPublisher
from .sources.bbc_source import BBCSource
from .sources.men_source import MENSource
from .sources.nub_source import NubSource
from .sources.onestockport_source import OneStockportSource
from .sources.stockportcouncil_source import StockportCouncilSource
from .sources.totallystockport_source import TotallyStockportSource


def setup_logging():
    """Setup logging with timestamped file output"""
    # Create organized logs directory structure
    os.makedirs("logs/sessions", exist_ok=True)

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/sessions/session_{timestamp}.log"

    # Configure logging to write to both file and console
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
    )

    logging.info(f"Session started - logging to {log_filename}")


setup_logging()


class ViaductEcho:
    def __init__(self):
        self.db = DatabaseOperations()
        self.sources = [
            BBCSource(),
            MENSource(),
            NubSource(),
            TotallyStockportSource(),
            OneStockportSource(),
            StockportCouncilSource(),
        ]
        self.content_extractor = ContentExtractor()
        self.ai_summarizer = AISummarizer()
        self.github_publisher = GitHubPublisher()

    def process_article(self, article_data: dict):
        """Process single article through entire pipeline"""
        try:
            article = self.db.insert_article(article_data)

            content_data = self.content_extractor.extract_content(
                article.original_link, article.original_source
            )

            # Store extracted content and image URL in database
            self.db.update_article_content(
                article.original_link,
                content_data["content"],
                content_data.get("image_url"),
            )

            # Validate content before AI summarization
            content = content_data["content"]
            summary = None

            if not content or len(content.strip()) < 100:
                logging.warning(
                    f"Content too short or empty for AI summary ({len(content) if content else 0} chars): {article.original_title}"
                )
                # Use original summary from RSS feed as fallback
                summary = article_data.get("original_summary", "")
                if summary:
                    logging.info(
                        f"Using RSS summary as fallback for: {article.original_title}"
                    )
            else:
                # Content is valid, generate AI summary
                summary = self.ai_summarizer.summarize(content)

            # Store AI summary in database
            if summary:
                self.db.update_article_ai_summary(article.original_link, summary)

            success = self.github_publisher.publish_article(
                article_data, summary, content_data["image_url"]
            )

            if success:
                self.db.mark_processed(article.original_link)

        except Exception as e:
            logging.error(f"Article processing error: {e}")

    def run_aggregation(self):
        """Main aggregation process"""
        logging.info("Starting aggregation run")

        for source in self.sources:
            try:
                articles = source.fetch_articles()

                for article in articles:
                    if not self.db.article_exists(article["original_link"]):
                        self.process_article(article)
                        time.sleep(2)

            except Exception as e:
                logging.error(f"Source {source.source_name} error: {e}")

        logging.info("Aggregation run completed")

    def start_scheduler(self):
        """Start scheduled execution"""
        scheduler = BlockingScheduler()
        scheduler.add_job(self.run_aggregation, "cron", hour="5-20", minute=0)

        logging.info("Scheduler started - running hourly between 5 AM and 8 PM")

        try:
            scheduler.start()
        except KeyboardInterrupt:
            logging.info("Scheduler stopped")
            self.db.close()

    def run_once(self):
        """Run aggregation once (for testing)"""
        try:
            self.run_aggregation()
        finally:
            self.db.close()


if __name__ == "__main__":
    echo = ViaductEcho()

    # For testing, run once
    # echo.run_once()

    # For production, start scheduler
    echo.start_scheduler()
