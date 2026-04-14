from datetime import datetime, timedelta, timezone
from typing import List, Optional
import feedparser
from docling.document_converter import DocumentConverter
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

import os
from dotenv import load_dotenv

load_dotenv()

import logging
logging.getLogger("docling").setLevel(logging.ERROR)


class AnthropicArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    summary: str


class AnthropicScraper:

    def __init__(self):
        self.rss_urls = [
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml"
        ]
        self.converter = DocumentConverter()
        api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini")


    def generate_summary(self, description: str, markdown: str) -> str:
        content = f"{description}\n\n{markdown}" if markdown else description
        prompt = f"Summarize the following article in 2-3 concise paragraphs with easy and understandable format so that the context of the full text is driven by reading that:\n\n{content}"
        response = self.llm.invoke([HumanMessage(content = prompt)])
        return response.content
    



    def url_to_markdown(self, url: str) -> Optional[str]:
        try:
            result = self.converter.convert(url)
            return result.document.export_to_markdown()
        except Exception:
            return None



    def get_articles(self, hours: int = 24) -> List[AnthropicArticle]:
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=hours)
        articles = []
        seen_guids = set()

        for rss_url in self.rss_urls:
            feed = feedparser.parse(rss_url)
            if not feed.entries:
                continue

            for entry in feed.entries:
                published_parsed = getattr(entry, "published_parsed", None)
                if not published_parsed:
                    continue

                published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                if published_time >= cutoff_time:
                    guid = entry.get("id", entry.get("link", ""))
                    if guid not in seen_guids:
                        seen_guids.add(guid)

                        description = entry.get("description", "")
                        markdown = self.url_to_markdown(entry.get("link", ""))
                        summary = self.generate_summary(description, markdown)

                        articles.append(AnthropicArticle(
                            title=entry.get("title", ""),
                            description=description,
                            url=entry.get("link", ""),
                            guid=guid,
                            published_at=published_time,
                            summary=summary,
                        ))

        return articles


if __name__ == "__main__":
    scraper = AnthropicScraper()
    articles: List[AnthropicArticle] = scraper.get_articles(hours=400)
    for article in articles:
        print(f"Title: {article.title}")
        print(f"Summary: {article.summary}")
        print(f"URL: {article.url}")
        print("-" * 80)
