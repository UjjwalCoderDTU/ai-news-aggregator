from dataclasses import dataclass
from typing import Optional

from scrapers.youtube import scrape_channel as scrape_youtube_channel
from scrapers.openai_scraper import OpenAIScraper
from scrapers.anthropic_scraper import AnthropicScraper
from services.config import YOUTUBE_CHANNELS

from db.connection import SessionLocal
from db.repository import bulk_insert   

@dataclass
class ScrapeResult:
    source: str  # "youtube", "openai", "anthropic"
    title: str
    url: str
    published_at: Optional[str]
    summary: Optional[str] = None
    transcript: Optional[str] = None


class NewsRunner:
    def __init__(self):
        self.openai_scraper = OpenAIScraper()
        self.anthropic_scraper = AnthropicScraper()

    def get_youtube_results(self, hours: int = 24) -> list[ScrapeResult]:
        """Scrape all configured YouTube channels."""
        results = []
        for channel in YOUTUBE_CHANNELS:
            try:
                videos = scrape_youtube_channel(channel, hours=hours)
                for video in videos:
                    results.append(ScrapeResult(
                        source="youtube",
                        title=video["title"],
                        url=video["url"],
                        published_at=video["published_at"],
                        transcript=video.get("transcript"),
                        summary=video.get("transcript"),
                    ))
            except Exception as e:
                print(f"❌ Error scraping YouTube channel {channel}: {e}")
        return results

    def get_openai_results(self, hours: int = 24) -> list[ScrapeResult]:
        """Scrape OpenAI news articles."""
        results = []
        try:
            articles = self.openai_scraper.get_articles(hours=hours)
            for article in articles:
                results.append(ScrapeResult(
                    source="openai",
                    title=article.title,
                    url=article.url,
                    published_at=article.published_at.isoformat(),
                    summary=article.summary,
                ))
        except Exception as e:
            print(f"❌ Error scraping OpenAI: {e}")
        return results

    def get_anthropic_results(self, hours: int = 24) -> list[ScrapeResult]:
        """Scrape Anthropic news articles."""
        results = []
        try:
            articles = self.anthropic_scraper.get_articles(hours=hours)
            for article in articles:
                results.append(ScrapeResult(
                    source="anthropic",
                    title=article.title,
                    url=article.url,
                    published_at=article.published_at.isoformat(),
                    summary=article.summary,
                ))
        except Exception as e:
            print(f"❌ Error scraping Anthropic: {e}")
        return results

    def get_all_results(self, hours: int = 24) -> list[ScrapeResult]:
        results = []
        results.extend(self.get_youtube_results(hours=hours))
        results.extend(self.get_openai_results(hours=hours))
        results.extend(self.get_anthropic_results(hours=hours))
        return results


def save_to_db(results: list[ScrapeResult]):
    db = SessionLocal()
    try:
        bulk_insert(db, results)
    finally:
        db.close()


def run(hours: int = 24) -> list[ScrapeResult]:
    """
    Run all scrapers and optionally save results to DB.

    Args:
        hours: Fetch content from last N hours
        save: Whether to store results in PostgreSQL

    Returns:
        List of ScrapeResult
    """
    runner = NewsRunner()
    results = runner.get_all_results(hours=hours)

    print("\n🚀 Saving results to PostgreSQL...")
    save_to_db(results)

    return results

