# Database Setup Guide

This document explains how to set up PostgreSQL database for the AI News Aggregator.

## Why PostgreSQL?

- **Industry Standard** - Used in production systems worldwide
- **Advanced Features** - JSONB support for flexible data storage
- **Scalable** - Handles large datasets efficiently
- **Open Source** - Free and community-driven
- **Better than MySQL** - More robust for complex queries and data integrity

## Prerequisites

- PostgreSQL installed (or use Docker: `docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres`)
- pgAdmin or any PostgreSQL client for database management


## Database Schema

### Table: `news_items`

| Column       | Type         | Description                              |
|--------------|--------------|------------------------------------------|
| id           | SERIAL       | Auto-increment primary key               |
| source       | VARCHAR(50)  | "youtube", "openai", or "anthropic"      |
| title        | TEXT         | News item title                          |
| url          | VARCHAR(500) | Unique URL (prevents duplicates)         |
| published_at | TIMESTAMP    | Original publication date from source    |
| summary      | TEXT         | LLM-generated or extracted summary       |
| transcript   | TEXT         | YouTube transcript (if available)        |
| created_at   | TIMESTAMP    | When record was inserted (auto-set)      |

### Indexes

- `idx_source` - Fast filtering by source
- `idx_published_at` - Fast date-based queries
- `idx_created_at` - Fast recent-item queries
- `url` (UNIQUE) - Prevents duplicate insertions

## Useful PostgreSQL Queries

### View all items
```sql
SELECT * FROM news_items ORDER BY created_at DESC LIMIT 50;
```

### Filter by source
```sql
SELECT * FROM news_items WHERE source = 'youtube';
```

### Count items per source
```sql
SELECT source, COUNT(*) as count FROM news_items GROUP BY source;
```

### Find items from last 24 hours
```sql
SELECT * FROM news_items 
WHERE created_at >= NOW() - INTERVAL '24 HOURS';
```

### Delete old data
```sql
DELETE FROM news_items WHERE created_at < NOW() - INTERVAL '30 DAYS';
```

### Delete all data (cleanup)
```sql
DELETE FROM news_items;
```

## How It Works

1. `main.py` calls `run()` from `runner.py` to scrape all sources
2. Each `ScrapeResult` is converted to `NewsItem` using `NewsItem.from_scrape_result()`
3. `NewsRepository.insert_many()` stores items in PostgreSQL
4. Duplicates are automatically skipped (UNIQUE constraint on `url`)
