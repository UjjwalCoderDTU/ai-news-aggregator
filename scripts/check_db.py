"""
Quick script to check database contents.
Run: uv run python scripts/check_db.py
"""

from db.connection import SessionLocal
from db.news_item import NewsItem
from sqlalchemy import text


def check_db():
    db = SessionLocal()

    try:
        # 🔹 1. List all tables
        print("\n=== Tables in Database ===")
        tables = db.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """))

        for table in tables:
            print(f"  - {table[0]}")

        # 🔹 2. Count rows
        print("\n=== news_items Table ===")
        total = db.query(NewsItem).count()
        print(f"Total rows: {total}")

        # 🔹 3. Show records (latest first)
        print("\n=== Latest Records ===")
        records = (
            db.query(NewsItem)
            .order_by(NewsItem.id.desc())
            .limit(20)   # limit for readability
            .all()
        )

        for row in records:
            print(f"[{row.id}] {row.source.upper()} - {row.title}")
            print(f"  URL: {row.url}")
            print(f"  Published: {row.published_at}")
            print(f"  Created: {row.created_at}")

            if row.summary:
                preview = (
                    row.summary[:150] + "..."
                    if len(row.summary) > 150 else row.summary
                )
                print(f"  Summary: {preview}")

            print("-" * 60)

    except Exception as e:
        print(f"❌ Error checking DB: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    check_db()