# AI News Aggregator

Scrapes news articles and YouTube videos from AI company sources (OpenAI, Anthropic, YouTube) with LLM-powered summarization and PostgreSQL storage.

## Quick Start

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and PostgreSQL credentials

# Run aggregator (stores results in PostgreSQL)
uv run python main.py

# Run with custom time window
uv run python main.py --hours 72
```

## Project Structure

```
AI NEWS AGGREATOR/
├── db/                      # Database layer
│   ├── __init__.py
│   ├── connection.py        # PostgreSQL connection & schema init
│   └── repository.py        # CRUD operations
│   └── news_item.py         # NewsItem (converts ScrapeResult → DB)
├── scrapers/                # Source-specific scrapers
│   ├── __init__.py
│   ├── openai_scraper.py    # OpenAI RSS + LLM summary
│   ├── anthropic_scraper.py # Anthropic RSS + Docling
│   └── youtube.py           # YouTube + transcripts
├── services/                # Core services
│   ├── __init__.py
│   ├── config.py            # YouTube channels config
│   └── runner.py            # Orchestrates all scrapers
├── docs/                    # Documentation
│   └── DATABASE_SETUP.md    # PostgreSQL setup guide
├── .env.example             # Template
├── main.py                  # Entry point
└── pyproject.toml           # Dependencies
```

## Commands

| Command | Description |
|---------|-------------|
| `uv sync` | Install dependencies |
| `uv run python main.py` | Run all scrapers + store in DB |
| `uv run python main.py --hours 72` | Custom time window |
| `uv run python services/runner.py` | Run scrapers (no DB) |
| `uv run python scrapers/openai_scraper.py` | Run OpenAI scraper only |
| `uv run python scrapers/youtube.py` | Run YouTube scraper only |

## Database

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| source | VARCHAR | "youtube", "openai", "anthropic" |
| title | TEXT | News item title |
| url | VARCHAR | UNIQUE (deduplication) |
| published_at | TIMESTAMP | Original publication date |
| summary | TEXT | LLM-generated summary |
| transcript | TEXT | YouTube transcript |
| created_at | TIMESTAMP | Insert timestamp (auto) |

### View Data

**pgAdmin:**
```sql
SELECT * FROM news_items ORDER BY id ASC;
```

**Terminal:**
```bash
uv run python scripts/check_db.py
```

## Configuration

### YouTube Channels
Edit `services/config.py`:
```python
YOUTUBE_CHANNELS = ["@TwoMinutePapers", "@AssemblyAI"]
```

### Environment (.env)
```env
OPENAI_API_KEY=sk-your-key-here
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=ai_news_db
DB_PORT=5432
```

## Troubleshooting

**YouTube transcript errors** - Some videos require cookies. See [yt-dlp cookies guide](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)

**No articles found** - Increase time window: `uv run python main.py --hours 500`