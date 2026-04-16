# Deployment Guide - Render

Deploy the AI News Aggregator on Render with automatic daily scheduling.

## Prerequisites

- PostgreSQL database (Render PostgreSQL or external)
- OpenAI API key
- Gmail account with app password
- Render account

## Deployment Steps

### 1. Create PostgreSQL Database

**Option A: Use Render's PostgreSQL**
1. Create a new PostgreSQL database on Render
2. Note the connection details (host, user, password, database, port)

**Option B: External PostgreSQL**
- Ensure your database is accessible from Render
- Database must be initialized with the schema (see Step 4)

### 2. Push Code to GitHub

```bash
git add .
git commit -m "Deployment ready"
git push origin main
```

The repo must be public or you must grant Render access to your private repo.

### 3. Create Cron Job on Render

1. Go to [render.com](https://render.com)
2. Click "New" → "Cron Job"
3. Connect your GitHub repository
4. Use the `render.yaml` file (auto-detected)
5. Click "Create Cron Job"

### 4. Configure Environment Variables

In Render dashboard, go to **Environment** and add:

**Database (required):**
```
DB_HOST=your-db-host.render.com
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=ai_news_db
DB_PORT=5432
```

**API Keys (required):**
```
OPENAI_API_KEY=sk-your-key-here
```

**Email (required for digests):**
```
GMAIL_SENDER_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
EMAIL_RECIPIENT=recipient@example.com
EMAIL_HOURS=24
```

### 5. Initialize Database Schema

Before the cron job runs, initialize your database:

**Option A: Render Shell**
```bash
# In Render dashboard → Cron Job → Shell
uv sync --frozen
uv run python scripts/check_db.py  # This auto-initializes
```

**Option B: Local Machine**
```bash
# Set environment variables from .env
psql -h your-db-host -U your_user -d ai_news_db -c "
CREATE TABLE IF NOT EXISTS news_items (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50),
    title TEXT,
    url VARCHAR(500) UNIQUE,
    published_at TIMESTAMP,
    summary TEXT,
    transcript TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_source ON news_items(source);
CREATE INDEX idx_published_at ON news_items(published_at);
CREATE INDEX idx_created_at ON news_items(created_at);
"
```

### 6. Schedule & Verification

- **Schedule**: 12:00 AM IST (18:30 UTC) daily
- **Command**: `uv run python main.py all --hours 24`
- **Logs**: Check Render dashboard for execution logs

## Monitoring

### View Logs
- Render Dashboard → Cron Job → Logs
- Check for `✅ Done` or error messages

### Manual Test Run
Click "Run" button in Render dashboard to trigger immediately

### Email Verification
Check your email inbox at ~12:00 AM IST for the daily digest

## Troubleshooting

**Database Connection Failed**
- Verify `DB_HOST`, `DB_USER`, `DB_PASSWORD` are correct
- Ensure database is publicly accessible (or use private networking)
- Check PostgreSQL logs

**Email Not Sending**
- Verify Gmail 2FA is enabled
- Confirm app password is 16 characters (not main password)
- Check `GMAIL_SENDER_EMAIL` and `GMAIL_APP_PASSWORD` match

**No News Items Found**
- Check `--hours 24` isn't too restrictive
- Verify scraper APIs (OpenAI, Anthropic RSS) are accessible
- Check `OPENAI_API_KEY` is valid

**Build Fails**
- Ensure `pyproject.toml` is present
- Check `uv` is available in environment
- Review build logs in Render dashboard

## Cost Optimization

- **Cron Job Tier**: Use "Standard" for daily jobs
- **Database**: Render PostgreSQL free tier for small datasets
- **Costs**: Typically $5-15/month for basic setup

## Updating the Deployment

After pushing changes to main branch:

1. Render auto-detects changes
2. New build triggers on next scheduled run
3. Or manually trigger with "Run" button

## Rollback

If deployment breaks:
```bash
# Revert commit
git revert <commit-hash>
git push origin main
# Render will rebuild
```

---

For detailed database schema, see [Database Setup](./docs/DATABASE_SETUP.md)
