from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"), override=True)
import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.runner import run
from db.connection import init_db
from services.email_service import send_daily_digest


def main(hours: int = 24):
    try:
        print("🚀 Running AI News Aggregator...")

        # Step 1: Initialize DB
        init_db()

        # Step 2: Run scrapers + save
        results = run(hours=hours)

        print(f"✅ Done. Processed {len(results)} items.")

    except Exception as e:
        print(f"❌ Error occurred: {e}")


def send_email_digest(hours: int = None):
    """Send email digest with latest AI news.

    Args:
        hours: Include news from last N hours. If None, reads from EMAIL_HOURS env var,
               defaults to 24 if not set.
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    sender_email = os.getenv("GMAIL_SENDER_EMAIL")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")
    recipient_email = os.getenv("EMAIL_RECIPIENT", "ujjwalsinghal1211@gmail.com")

    # Use hours from env var if not provided via command line
    if hours is None:
        hours = int(os.getenv("EMAIL_HOURS", "24"))


    # This function:
    # Fetches news from DB (last X hours)
    # Formats it nicely (subject + content)
    # Sends email via Gmail SMTP
    send_daily_digest(
        sender_email=sender_email,
        sender_password=sender_password,
        recipient_email=recipient_email,
        hours=hours
    )


def scrape_and_email(hours: int = 24):
    """
    Complete workflow: Scrape news into PostgreSQL AND send email digest.
    This is the single command for full automation.
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    print("=" * 50)
    print("🔄 STEP 1: Scraping news into PostgreSQL...")
    print("=" * 50)

    # Step 1: Initialize DB and scrape
    init_db()
    results = run(hours=hours)
    print(f"✅ Scraped {len(results)} news items")

    print("\n" + "=" * 50)
    print("🔄 STEP 2: Sending email digest...")
    print("=" * 50)

    # Step 2: Send email
    sender_email = os.getenv("GMAIL_SENDER_EMAIL")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")
    recipient_email = os.getenv("EMAIL_RECIPIENT", "ujjwalsinghal1211@gmail.com")

    send_daily_digest(
        sender_email=sender_email,
        sender_password=sender_password,
        recipient_email=recipient_email,
        hours=hours
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AI News Aggregator - Scrape and store AI news"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scrape only command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape news from all sources (no email)")
    scrape_parser.add_argument(
        "--hours",
        type=int,
        default=24
    )

    # Email only command
    email_parser = subparsers.add_parser("email", help="Send email digest only (no scraping)")
    email_parser.add_argument(
        "--hours",
        type=int,
        default=None
    )

    # Full workflow: scrape + email
    all_parser = subparsers.add_parser("all", help="Scrape news AND send email (complete workflow)")
    all_parser.add_argument(
        "--hours",
        type=int,
        default=24
    )

    args = parser.parse_args()

    if args.command == "all":
        scrape_and_email(hours=args.hours)
    elif args.command == "email":
        send_email_digest(hours=args.hours)
    elif args.command == "scrape" or args.command is None:
        main(hours=args.hours if hasattr(args, 'hours') else 24)
    else:
        parser.print_help()