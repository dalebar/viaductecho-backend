#!/usr/bin/env python3
"""
Database migration: Create events and venues tables
Run with: python -m src.database.migrations.001_create_events_tables
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from sqlalchemy import text

from src.database.operations import DatabaseOperations

MIGRATION_SQL = """
-- ============================================
-- VENUES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS venues (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,

    -- Address
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    town VARCHAR(100),
    postcode VARCHAR(10),

    -- Geo
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),

    -- Details
    description TEXT,
    venue_type VARCHAR(50),
    capacity INTEGER,

    -- Contact
    website_url TEXT,
    phone VARCHAR(20),

    -- Media
    image_url TEXT,

    -- Source tracking
    source_name VARCHAR(100),
    source_id VARCHAR(200),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- EVENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(200) NOT NULL,

    -- Description
    description TEXT,
    short_description VARCHAR(500),

    -- Timing
    start_datetime TIMESTAMPTZ NOT NULL,
    end_datetime TIMESTAMPTZ,
    doors_time TIME,

    -- Location
    venue_id INTEGER REFERENCES venues(id),

    -- Categorisation
    event_type VARCHAR(50) NOT NULL,

    -- Media
    image_url TEXT,

    -- Tickets
    ticket_url TEXT,
    price_min DECIMAL(10,2),
    price_max DECIMAL(10,2),
    is_free BOOLEAN DEFAULT FALSE,

    -- Source tracking
    source_name VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(200),
    source_url TEXT,

    -- Deduplication
    event_hash VARCHAR(64) UNIQUE,

    -- Status
    status VARCHAR(20) DEFAULT 'active',
    is_featured BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_events_start_datetime ON events(start_datetime);
CREATE INDEX IF NOT EXISTS idx_events_venue_id ON events(venue_id);
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_source ON events(source_name, source_id);

CREATE INDEX IF NOT EXISTS idx_venues_postcode ON venues(postcode);
CREATE INDEX IF NOT EXISTS idx_venues_slug ON venues(slug);
CREATE INDEX IF NOT EXISTS idx_venues_source ON venues(source_name, source_id);
"""


def run_migration():
    """Execute the migration"""
    db = DatabaseOperations()
    try:
        print("Running migration: Create events and venues tables...")
        db.session.execute(text(MIGRATION_SQL))
        db.session.commit()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        db.session.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
