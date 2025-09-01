import logging
import time

from apscheduler.schedulers.blocking import BlockingScheduler

from .database.operations import DatabaseOperations
from .processors.ai_summarizer import AISummarizer
from .processors.content_extractor import ContentExtractor
from .publishers.github_publisher import GitHubPublisher
from .sources.bbc_source import BBCSource
from .sources.men_source import MENSource
from .sources.nub_source import NubSource

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ViaductEcho:
    def __init__(self):
        self.db = DatabaseOperations()
        self.sources = [BBCSource(), MENSource(), NubSource()]
        self.content_extractor = ContentExtractor()
        self.ai_summarizer = AISummarizer()
        self.github_publisher = GitHubPublisher()

    def process_article(self, article_data: dict):
        """Process single article through entire pipeline"""
        try:
            article = self.db.insert_article(article_data)

            content_data = self.content_extractor.extract_content(article.original_link, article.original_source)

            summary = self.ai_summarizer.summarize(content_data["content"])

            success = self.github_publisher.publish_article(article_data, summary, content_data["image_url"])

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
