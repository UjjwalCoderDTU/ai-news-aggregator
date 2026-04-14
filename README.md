# AI News Aggregator

Scrapes news articles and YouTube videos from AI company sources (OpenAI, Anthropic, YouTube) with LLM-powered summarization, PostgreSQL storage, and automated email digest delivery.

## Quick Start

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your API keys, database, and email credentials

# Scrape news and store in PostgreSQL
uv run python main.py scrape --hours 24

# Send email digest from latest news
uv run python main.py email --hours 24

# Complete workflow: scrape + send email (recommended)
uv run python main.py all --hours 24
```

## Project Structure

```
AI NEWS AGGREATOR/
├── db/                           # Database layer
│   ├── __init__.py
│   ├── connection.py             # PostgreSQL connection & schema init
│   ├── repository.py             # CRUD operations
│   └── news_item.py              # NewsItem ORM model
├── scrapers/                     # Source-specific scrapers
│   ├── __init__.py
│   ├── openai_scraper.py         # OpenAI RSS + GPT-4o-mini summary
│   ├── anthropic_scraper.py      # Anthropic RSS + Docling + LLM
│   └── youtube.py                # YouTube videos + transcripts
├── services/                     # Core services & orchestration
│   ├── __init__.py
│   ├── runner.py                 # NewsRunner: orchestrates all scrapers
│   ├── config.py                 # YouTube channels configuration
│   └── email_service.py          # Email digest formatting & sending
├── scripts/                      # Utility scripts
│   └── check_db.py               # Query and view database contents
├── docs/                         # Documentation
│   └── DATABASE_SETUP.md         # PostgreSQL setup guide
├── .env.example                  # Environment template
├── main.py                       # CLI entry point (argparse)
└── pyproject.toml                # Dependencies
```

## Commands

| Command | Description |
|---------|-------------|
| `uv sync` | Install dependencies |
| `uv run python main.py scrape --hours N` | Scrape news from last N hours, save to DB |
| `uv run python main.py email --hours N` | Send email digest from last N hours |
| `uv run python main.py all --hours N` | Complete workflow: scrape + email |
| `uv run python scripts/check_db.py` | Query and display database contents |

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
Edit `services/config.py` to add or remove channels:
```python
YOUTUBE_CHANNELS = ["@matthew_berman", "@vaibhavsisinty", "@mreflow"]
```

### Environment (.env)
Create `.env` file with the following variables:

**Required for scraping:**
```env
OPENAI_API_KEY=sk-your-key-here
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=ai_news_db
DB_PORT=5432
```

**Required for email digest:**
```env
GMAIL_SENDER_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
EMAIL_RECIPIENT=recipient@example.com
EMAIL_HOURS=24          # Optional: hours window for digest (default: 24)
```

**Gmail Setup:**
1. Enable 2-factor authentication on your Google account
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Use the 16-character app password in `GMAIL_APP_PASSWORD`

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  SCRAPE WORKFLOW (scrape/all)               │
├─────────────────────────────────────────────────────────────┤
│  1. NewsRunner orchestrates 3 scrapers                      │
│     ├─ OpenAI RSS + GPT-4o-mini summary                     │
│     ├─ Anthropic RSS + Docling HTML→Markdown + LLM         │
│     └─ YouTube channels + video transcripts                │
│  2. All scrapers return ScrapeResult objects                │
│  3. Results converted to NewsItem ORM objects               │
│  4. Bulk insert into PostgreSQL with URL deduplication     │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    PostgreSQL news_items
                    (UNIQUE constraint on url)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  EMAIL WORKFLOW (email/all)                 │
├─────────────────────────────────────────────────────────────┤
│  1. Fetch latest news from DB (last N hours)               │
│  2. Group by source (YouTube, OpenAI, Anthropic)            │
│  3. Format as plain text email with summaries               │
│  4. Send via Gmail SMTP to recipient                        │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

**No articles found** - Increase time window: `uv run python main.py scrape --hours 500`

**YouTube transcript errors** - Some videos require cookies. See [yt-dlp cookies guide](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)

**Email not sending** - Verify:
- Gmail 2FA is enabled
- App password is 16 characters (not your main password)
- `GMAIL_SENDER_EMAIL` and `GMAIL_APP_PASSWORD` are correct in `.env`
- Recipient email is set in `EMAIL_RECIPIENT`

**Database connection errors** - Verify PostgreSQL is running:
```bash
psql -h localhost -U postgres -d ai_news_db
```