from sqlalchemy.orm import Session
from db.news_item import NewsItem
from datetime import datetime


def parse_datetime(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None


def insert_news_item(db: Session, scrape_result):
    existing = db.query(NewsItem).filter(NewsItem.url == scrape_result.url).first()

    if existing:
        print(f"⚠️ Skipping duplicate: {scrape_result.url}")
        return

    news = NewsItem(
        source=scrape_result.source,
        title=scrape_result.title,
        url=scrape_result.url,
        published_at=parse_datetime(scrape_result.published_at),
        summary=scrape_result.summary,
        transcript=scrape_result.transcript
    )

    db.add(news)
    db.commit()
    db.refresh(news)

    print(f"✅ Inserted: {news.title}")


def bulk_insert(db: Session, results: list):
    for result in results:
        insert_news_item(db, result)