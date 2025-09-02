#!/usr/bin/env python3
"""
Comprehensive test suite for DatabaseOperations class
"""

import os
import sys
from datetime import datetime, timezone
import pytest
from unittest.mock import patch

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from database.operations import DatabaseOperations
from database.models import RSSArticle


class TestDatabaseOperations:
    """Test suite for DatabaseOperations class"""

    @pytest.fixture(scope="class")
    def db_ops(self):
        """Fixture to provide DatabaseOperations instance for tests"""
        return DatabaseOperations()

    @pytest.fixture(scope="class")
    def sample_article_data(self):
        """Fixture providing sample article data for testing"""
        return {
            "original_title": "Test Article About Stockport",
            "original_link": "https://example.com/test-article-stockport",
            "original_summary": "This is a test summary about Stockport news",
            "original_source": "Test News Source",
            "source_type": "Test RSS",
            "original_pubdate": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        }

    @pytest.fixture(scope="class")
    def sample_article_data_minimal(self):
        """Fixture providing minimal article data for testing"""
        return {
            "original_title": "Minimal Test Article",
            "original_link": "https://example.com/minimal-test",
            "original_source": "Minimal Source",
        }

    def test_database_connection_established(self, db_ops):
        """Test that database connection is established successfully"""
        assert db_ops.engine is not None
        assert db_ops.session is not None

    def test_article_exists_false_for_new_url(self, db_ops):
        """Test that article_exists returns False for a new URL"""
        test_url = "https://example.com/non-existent-article"
        result = db_ops.article_exists(test_url)
        assert result is False

    def test_insert_article_success(self, db_ops, sample_article_data):
        """Test successful article insertion"""
        # Clean up any existing test data
        existing = (
            db_ops.session.query(RSSArticle).filter_by(original_link=sample_article_data["original_link"]).first()
        )
        if existing:
            db_ops.session.delete(existing)
            db_ops.session.commit()

        # Insert article
        article = db_ops.insert_article(sample_article_data)

        # Verify article was inserted
        assert article is not None
        assert article.id is not None
        assert article.original_title == sample_article_data["original_title"]
        assert article.original_link == sample_article_data["original_link"]
        assert article.original_summary == sample_article_data["original_summary"]
        assert article.original_source == sample_article_data["original_source"]
        assert article.source_type == sample_article_data["source_type"]
        assert article.original_pubdate == sample_article_data["original_pubdate"]
        assert article.url_hash is not None
        assert article.created_at is not None
        assert article.processed is False

    def test_insert_article_minimal_data(self, db_ops, sample_article_data_minimal):
        """Test article insertion with minimal required data"""
        # Clean up any existing test data
        existing = (
            db_ops.session.query(RSSArticle)
            .filter_by(original_link=sample_article_data_minimal["original_link"])
            .first()
        )
        if existing:
            db_ops.session.delete(existing)
            db_ops.session.commit()

        # Insert article with minimal data
        article = db_ops.insert_article(sample_article_data_minimal)

        # Verify article was inserted with defaults
        assert article is not None
        assert article.original_title == sample_article_data_minimal["original_title"]
        assert article.original_link == sample_article_data_minimal["original_link"]
        assert article.original_source == sample_article_data_minimal["original_source"]
        assert article.original_summary == ""  # Default value
        assert article.source_type == "RSS"  # Default value
        assert article.original_pubdate is None  # Not provided
        assert article.processed is False

    def test_article_exists_true_after_insertion(self, db_ops, sample_article_data):
        """Test that article_exists returns True for an inserted article"""
        # Ensure article exists (from previous test)
        result = db_ops.article_exists(sample_article_data["original_link"])
        assert result is True

    def test_mark_processed_success(self, db_ops, sample_article_data):
        """Test marking an article as processed"""
        # Mark article as processed
        db_ops.mark_processed(sample_article_data["original_link"])

        # Verify article is marked as processed
        import hashlib

        url_hash = hashlib.md5(sample_article_data["original_link"].encode()).hexdigest()
        article = db_ops.session.query(RSSArticle).filter_by(url_hash=url_hash).first()

        assert article is not None
        assert article.processed is True

    def test_mark_processed_nonexistent_article(self, db_ops):
        """Test marking a non-existent article as processed (should not error)"""
        # This should not raise an exception
        db_ops.mark_processed("https://example.com/does-not-exist")

    def test_url_hash_generation(self, db_ops):
        """Test that URL hash is generated correctly"""
        import hashlib

        test_url = "https://example.com/test-hash"
        expected_hash = hashlib.md5(test_url.encode()).hexdigest()

        # Test with article_exists (which uses the same hash logic)
        with patch.object(db_ops.session, "query") as mock_query:
            mock_query.return_value.filter_by.return_value.first.return_value = None

            db_ops.article_exists(test_url)

            # Verify the hash was used correctly
            mock_query.return_value.filter_by.assert_called_with(url_hash=expected_hash)

    def test_duplicate_article_prevention(self, db_ops):
        """Test that inserting the same article twice creates only one record"""
        duplicate_data = {
            "original_title": "Duplicate Test Article",
            "original_link": "https://example.com/duplicate-test",
            "original_source": "Duplicate Source",
        }

        # Clean up any existing test data
        existing = db_ops.session.query(RSSArticle).filter_by(original_link=duplicate_data["original_link"]).first()
        if existing:
            db_ops.session.delete(existing)
            db_ops.session.commit()

        # Insert first article
        article1 = db_ops.insert_article(duplicate_data)

        # Try to insert duplicate (should fail due to unique constraint)
        with pytest.raises(Exception):
            article2 = db_ops.insert_article(duplicate_data)

    def test_close_connection(self, db_ops):
        """Test closing the database connection"""
        # This should not raise an exception
        db_ops.close()

        # Create a new instance for remaining tests if needed
        new_db_ops = DatabaseOperations()
        assert new_db_ops.session is not None
        new_db_ops.close()

    @pytest.fixture(autouse=True, scope="class")
    def cleanup_test_data(self, db_ops):
        """Cleanup test data after all tests complete"""
        yield

        # Clean up test articles
        test_urls = [
            "https://example.com/test-article-stockport",
            "https://example.com/minimal-test",
            "https://example.com/duplicate-test",
        ]

        for url in test_urls:
            import hashlib

            url_hash = hashlib.md5(url.encode()).hexdigest()
            article = db_ops.session.query(RSSArticle).filter_by(url_hash=url_hash).first()
            if article:
                db_ops.session.delete(article)

        try:
            db_ops.session.commit()
        except:
            db_ops.session.rollback()

        db_ops.close()


class TestDatabaseOperationsIntegration:
    """Integration tests for DatabaseOperations with real database"""

    def test_full_article_lifecycle(self):
        """Test complete article lifecycle: insert -> exists -> process -> cleanup"""
        db_ops = DatabaseOperations()

        article_data = {
            "original_title": "Integration Test Article",
            "original_link": "https://example.com/integration-test",
            "original_summary": "Integration test summary",
            "original_source": "Integration Test Source",
            "source_type": "Integration Test",
            "original_pubdate": datetime(2024, 1, 20, 15, 45, 0, tzinfo=timezone.utc),
        }

        try:
            # Clean up any existing data
            existing = db_ops.session.query(RSSArticle).filter_by(original_link=article_data["original_link"]).first()
            if existing:
                db_ops.session.delete(existing)
                db_ops.session.commit()

            # 1. Article should not exist initially
            assert db_ops.article_exists(article_data["original_link"]) is False

            # 2. Insert article
            article = db_ops.insert_article(article_data)
            assert article is not None

            # 3. Article should now exist
            assert db_ops.article_exists(article_data["original_link"]) is True

            # 4. Article should not be processed initially
            import hashlib

            url_hash = hashlib.md5(article_data["original_link"].encode()).hexdigest()
            stored_article = db_ops.session.query(RSSArticle).filter_by(url_hash=url_hash).first()
            assert stored_article.processed is False

            # 5. Mark as processed
            db_ops.mark_processed(article_data["original_link"])

            # 6. Verify it's marked as processed
            db_ops.session.refresh(stored_article)
            assert stored_article.processed is True

        finally:
            # Cleanup
            if "stored_article" in locals():
                db_ops.session.delete(stored_article)
                db_ops.session.commit()
            db_ops.close()

    def test_database_error_handling(self):
        """Test error handling with invalid data"""
        db_ops = DatabaseOperations()

        try:
            # Test with missing required field
            invalid_data = {
                "original_link": "https://example.com/invalid-test",
                # Missing original_title and original_source
            }

            with pytest.raises(Exception):
                db_ops.insert_article(invalid_data)

        finally:
            db_ops.close()
