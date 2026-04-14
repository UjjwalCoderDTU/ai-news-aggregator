# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

```bash
uv sync                          # Install dependencies
uv run python main.py            # Run all scrapers + store in PostgreSQL
uv run python main.py --hours 72 # Custom time window
```

## Commands

| Command | Description |
|---------|-------------|
| `uv run python main.py scrape --hours N` | Scrape news from last N hours |
| `uv run python main.py email --hours N` | Send email digest for last N hours |
| `uv run python main.py all --hours N` | Scrape + email (complete workflow) |
| `uv run python scripts/check_db.py` | Query database contents |

Individual scrapers:
- `uv run python scrapers/openai_scraper.py` - OpenAI RSS + LLM summary
- `uv run python scrapers/anthropic_scraper.py` - Anthropic RSS + Docling + LLM
- `uv run python scrapers/youtube.py` - YouTube videos + transcripts

## Architecture

```
main.py              # Entry point: argparse CLI (scrape/email/all commands)
services/runner.py   # Orchestrator: runs all scrapers, saves to DB
db/                  # SQLAlchemy + PostgreSQL
  connection.py      # DB engine, session factory, init_db()
  news_item.py       # NewsItem model (ORM)
  repository.py      # CRUD: bulk_insert(), deduplication by URL
scrapers/            # Source-specific scrapers (return ScrapeResult or dict)
  openai_scraper.py  # RSS feed + GPT-4o-mini summary
  anthropic_scraper.py # 3 RSS feeds + Docling HTML→Markdown + GPT summary
  youtube.py         # yt-dlp (video metadata) + youtube-transcript-api
services/
  runner.py          # NewsRunner class, run() returns list[ScrapeResult]
  config.py          # YOUTUBE_CHANNELS list
  email_service.py   # SMTP via Gmail, sends formatted digest
```

## Data Flow

1. `main.py` calls `services/runner.run(hours=N)`
2. `NewsRunner` fetches from all sources → `list[ScrapeResult]`
3. `save_to_db()` converts to `NewsItem` ORM objects
4. `repository.bulk_insert()` saves with deduplication (UNIQUE constraint on `url`)

## Configuration

**Environment (.env):**
```env
OPENAI_API_KEY=sk-...
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=...
DB_NAME=ai_news_db
DB_PORT=5432
GMAIL_SENDER_EMAIL=...
GMAIL_APP_PASSWORD=...   # Gmail app password
EMAIL_RECIPIENT=...
```

**YouTube channels:** Edit `services/config.py`:
```python
YOUTUBE_CHANNELS = ["@matthew_berman", "@vaibhavsisinty", "@mreflow"]
```

## Database Schema

Table `news_items`:
- `id` (SERIAL PK), `source` (youtube/openai/anthropic), `title`, `url` (UNIQUE)
- `published_at`, `summary`, `transcript`, `created_at` (auto)

Indexes: `source`, `published_at`, `created_at`

## Troubleshooting

- **No articles found**: Increase `--hours` flag (e.g., `--hours 500`)
- **YouTube transcript errors**: Some videos require cookies; see [yt-dlp cookies guide](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)
- **Database connection errors**: Verify PostgreSQL is running and `.env` credentials are correct
