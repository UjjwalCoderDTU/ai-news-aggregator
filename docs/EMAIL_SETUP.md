# Email Digest Setup Guide

This guide explains how to set up automated AI news digest emails.

## Quick Setup

### Step 1: Generate Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Enable **2-Factor Authentication** (if not already enabled)
3. Go to App Passwords: https://myaccount.google.com/apppasswords
4. Click **Create app password**
5. Select app: **Mail**
6. Select device: **Other** (name it "AI News Aggregator")
7. Click **Generate**
8. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)

### Step 2: Configure .env File

Add your credentials to `.env`:

```env
GMAIL_SENDER_EMAIL=sender.email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
EMAIL_RECIPIENT=receiver.email@gmail.com
```

### Step 3: Test the Email

Run the email command:

```bash
# Using uv (recommended)
uv run python main.py email

# Or with custom time range (e.g., last 12 hours)
uv run python main.py email --hours 12
```

## Usage

### Single Command: Scrape + Email (Recommended)

This is the easiest way - scrapes news into PostgreSQL AND sends email in one go:

```bash
# Latest 24 hours (default)
uv run python main.py all

# Latest 100 hours
uv run python main.py all --hours 100

# Latest 12 hours
uv run python main.py all --hours 12
```

### Email Only (uses existing data in database)

```bash
# Uses EMAIL_HOURS from .env (default: 24)
uv run python main.py email

# Override hours
uv run python main.py email --hours 100
```

### Scrape Only (no email)

```bash
uv run python main.py scrape
uv run python main.py scrape --hours 100
```

## Email Format

The email includes:
- **Header**: Styled banner with date
- **YouTube Videos**: Latest AI video content with transcript previews
- **OpenAI News**: Articles with summaries
- **Anthropic News**: Articles with summaries
- **Footer**: Auto-generated notice

Each news item shows:
- Bold title (clickable link)
- Source and publish time
- Summary (if available)
- Transcript preview (for YouTube videos)

