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

## Setup Steps

### 1. Install PostgreSQL Driver

```bash
uv sync
```

This installs `psycopg2-binary` automatically.

### 2. Configure Environment Variables

Copy the example env file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:

```env
OPENAI_API_KEY=sk-your-api-key-here

DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_NAME=ai_news_db
DB_PORT=5432
```

### 3. Create Database

**Option A: Let the app create it automatically**

The first time you run `main.py`, it will create the database and tables:

```bash
uv run python main.py
```

**Option B: Create manually using psql or pgAdmin**

```sql
CREATE DATABASE ai_news_db;
\c ai_news_db

CREATE TABLE news_items (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    url VARCHAR(500) UNIQUE NOT NULL,
    published_at TIMESTAMP,
    summary TEXT,
    transcript TEXT,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_source ON news_items (source);
CREATE INDEX idx_published_at ON news_items (published_at);
CREATE INDEX idx_created_at ON news_items (created_at);
```

### 4. Run the Aggregator

```bash
uv run python main.py
```

You should see:
```
✓ Connected to PostgreSQL database: ai_news_db
✓ Table 'news_items' created/verified
✓ Inserted X new items into database
```

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

## File Structure

```
AI NEWS AGGREATOR/
├── db/
│   ├── __init__.py          # Package exports
│   ├── connection.py        # PostgreSQL connection & init
│   └── repository.py        # CRUD operations (insert, delete, query)
│   └── news_item.py         # NewsItem data model (converts ScrapeResult)
├── docs/
│   └── DATABASE_SETUP.md    # This file
├── .env                     # Your credentials (create from .env.example)
├── .env.example             # Template for .env
└── main.py                  # Main entry point - runs scrapers and stores in DB
```

## How It Works

1. `main.py` calls `run()` from `runner.py` to scrape all sources
2. Each `ScrapeResult` is converted to `NewsItem` using `NewsItem.from_scrape_result()`
3. `NewsRepository.insert_many()` stores items in PostgreSQL
4. Duplicates are automatically skipped (UNIQUE constraint on `url`)

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Set up your .env file
cp .env.example .env
# Edit .env with your PostgreSQL credentials and OPENAI_API_KEY

# 3. Run the aggregator (database auto-creates on first run)
uv run python main.py
```
