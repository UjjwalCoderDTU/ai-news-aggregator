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
GMAIL_SENDER_EMAIL=your.email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
EMAIL_RECIPIENT=ujjwalsinghal1211@gmail.com
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

## Automation (Optional)

### Option 1: Cron Job (macOS/Linux)

Add to your crontab (`crontab -e`):

```cron
# Send AI news digest every day at 8 AM
0 8 * * * cd /Users/ujjwal/Desktop/AI\ NEWS\ AGGREATOR && /path/to/uv run python main.py email
```

### Option 2: Python Script with Schedule

Create `scripts/send_daily_email.py`:

```python
#!/usr/bin/env python3
"""Send daily AI news digest at 8 AM"""
import sys
sys.path.insert(0, '..')
from main import send_email_digest

send_email_digest(hours=24)
```

Then schedule with cron or Task Scheduler.

## Troubleshooting

### "Missing email credentials"
- Ensure `GMAIL_SENDER_EMAIL` and `GMAIL_APP_PASSWORD` are set in `.env`
- Make sure there are no extra spaces or quotes

### "Authentication failed"
- Double-check your App Password (should be 16 characters, no spaces)
- Ensure 2FA is enabled on your Google Account
- Try regenerating the App Password

### "No news items to send"
- Run `uv run python main.py scrape` first to populate the database
- Check that your PostgreSQL database is running

### Gmail rate limits
- Gmail allows ~500 emails/day for free accounts
- For higher limits, consider Google Workspace

## Security Notes

- Never commit your `.env` file to git
- The App Password gives access to your Gmail - keep it secure
- Consider using a dedicated Gmail account for automated emails
