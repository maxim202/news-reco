-- Data Warehouse for News Articles (SQLite Version)
-- Star Schema Design

-- Dimension Table: Time (Date Information)
CREATE TABLE IF NOT EXISTS dim_time (
    time_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    week_of_year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

-- Dimension Table: Source (News Sources)
CREATE TABLE IF NOT EXISTS dim_source (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension Table: Author
CREATE TABLE IF NOT EXISTS dim_author (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fact Table: Articles
CREATE TABLE IF NOT EXISTS fact_articles (
    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    image_url TEXT,
    
    -- Foreign Keys to Dimensions
    source_id INTEGER REFERENCES dim_source(source_id),
    author_id INTEGER REFERENCES dim_author(author_id),
    published_time_id INTEGER REFERENCES dim_time(time_id),
    
    -- Metrics
    content_length INTEGER NOT NULL,
    word_count INTEGER NOT NULL,
    has_image BOOLEAN NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_fact_articles_source_id ON fact_articles(source_id);
CREATE INDEX IF NOT EXISTS idx_fact_articles_author_id ON fact_articles(author_id);
CREATE INDEX IF NOT EXISTS idx_fact_articles_published_time_id ON fact_articles(published_time_id);
CREATE INDEX IF NOT EXISTS idx_fact_articles_url ON fact_articles(url);
CREATE INDEX IF NOT EXISTS idx_dim_time_date ON dim_time(date);