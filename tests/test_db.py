#!/usr/bin/env python3
"""
Test script for database connection and table creation
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add src to path so we can import our modules from the parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from database.models import Base, RSSArticle


def test_database_connection():
    """Test database connection and operations"""
    print("Testing database connection...")

    # Load environment variables from parent directory
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("Please check your .env file")
        return False

    try:
        # Test basic connection
        engine = create_engine(database_url)
        print("✅ Database engine created successfully")

        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")

        # Test table creation
        print("\nTesting table creation...")
        Base.metadata.create_all(engine)
        print("✅ Tables created successfully")

        # Test session creation
        Session = sessionmaker(bind=engine)
        session = Session()

        # Test a simple query
        count = session.query(RSSArticle).count()
        print(f"✅ Current articles in database: {count}")

        session.close()
        print("\n🎉 All database tests passed!")
        return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_database_operations():
    """Test database operations from our operations module"""
    print("\nTesting database operations module...")

    try:
        from database.operations import DatabaseOperations

        db = DatabaseOperations()
        print("✅ DatabaseOperations initialized successfully")

        # Test article exists check with a fake URL
        test_url = "https://example.com/test-article"
        exists = db.article_exists(test_url)
        print(f"✅ Article exists check: {exists} (expected False for test URL)")

        db.close()
        print("✅ Database operations test passed!")
        return True

    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False


if __name__ == "__main__":
    print("=== Viaduct Echo Database Connection Test ===\n")

    success1 = test_database_connection()
    success2 = test_database_operations()

    if success1 and success2:
        print("\n🎉 All tests passed! Your database is ready to use.")
    else:
        print("\n❌ Some tests failed. Please check your database configuration.")
        sys.exit(1)
