-- Initial database setup for Viaduct Echo
-- This script runs when the PostgreSQL container starts for the first time

-- Create the main database (if not exists)
-- Note: The database is already created by POSTGRES_DB env var

-- Connect to the viaduct_echo database
\c viaduct_echo;

-- Create the rss_articles table if it doesn't exist
-- This matches the SQLAlchemy model definition
CREATE TABLE IF NOT EXISTS rss_articles (
    id SERIAL PRIMARY KEY,
    original_title VARCHAR(500) NOT NULL,
    original_link TEXT UNIQUE NOT NULL,
    original_summary TEXT,
    original_source VARCHAR(100) NOT NULL,
    source_type VARCHAR(50),
    original_pubdate TIMESTAMP WITH TIME ZONE,
    url_hash VARCHAR(64) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    extracted_content TEXT,
    ai_summary TEXT,
    ai_image_url TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better API performance
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON rss_articles(created_at);
CREATE INDEX IF NOT EXISTS idx_articles_source ON rss_articles(original_source);
CREATE INDEX IF NOT EXISTS idx_articles_pubdate ON rss_articles(original_pubdate);
CREATE INDEX IF NOT EXISTS idx_articles_processed ON rss_articles(processed);
CREATE INDEX IF NOT EXISTS idx_articles_source_created ON rss_articles(original_source, created_at);

-- Create a trigger to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_rss_articles_updated_at
    BEFORE UPDATE ON rss_articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for development/testing
INSERT INTO rss_articles
    (original_title, original_link, original_summary, original_source, source_type, original_pubdate, processed, extracted_content, ai_summary, ai_image_url)
VALUES
    (
        'Stockport Market renovation begins with major investment',
        'https://example.com/stockport-market-renovation',
        'Historic market to undergo significant improvements',
        'Manchester Evening News',
        'RSS News',
        '2024-01-15 10:30:00+00',
        true,
        'The historic Stockport Market is set to undergo a major renovation...',
        'Stockport''s historic market is getting a major upgrade with new facilities and improved accessibility.',
        'https://example.com/stockport-market-image.jpg'
    ),
    (
        'Manchester United announces youth academy expansion',
        'https://example.com/manchester-united-academy',
        'Football club invests in future talent development',
        'BBC News',
        'RSS News',
        '2024-01-16 14:20:00+00',
        true,
        'Manchester United has announced plans to expand their youth academy...',
        'Man United is expanding their youth academy to develop the next generation of football talent.',
        'https://example.com/manchester-united-image.jpg'
    ),
    (
        'High Peak National Park sees record visitor numbers',
        'https://example.com/high-peak-visitors',
        'Tourism boost brings economic benefits to local area',
        'Stockport Nub News',
        'Web scraping',
        '2024-01-17 09:15:00+00',
        true,
        'High Peak National Park has reported record visitor numbers this year...',
        'High Peak National Park is experiencing a tourism boom with record visitor numbers.',
        'https://example.com/high-peak-image.jpg'
    )
ON CONFLICT (original_link) DO NOTHING;

-- Grant permissions to the application user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO viaduct;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO viaduct;
