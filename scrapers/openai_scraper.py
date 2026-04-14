from datetime import datetime, timedelta, timezone
from typing import List
import feedparser
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv
import os

load_dotenv()


class OpenAIArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    summary: str


class OpenAIScraper:
    def __init__(self):
        self.rss_url = "https://openai.com/news/rss.xml"
        api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini")

    def get_articles(self, hours: int = 24) -> List[OpenAIArticle]:

        feed = feedparser.parse(self.rss_url)
        if not feed.entries:
            return []

        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=hours)
        articles = []

        for entry in feed.entries:
            published_parsed = getattr(entry, "published_parsed", None)
            if not published_parsed:
                continue

            published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc)
            if published_time >= cutoff_time:
                article = OpenAIArticle(
                    title=entry.get("title", ""),
                    description=entry.get("description", ""),
                    url=entry.get("link", ""),
                    guid=entry.get("id", entry.get("link", "")),
                    published_at=published_time,
                    summary=""
                )

                # Summarize with LLM 
                prompt = f"Summarize the following article in 2-3 concise paragraphs with easy and understandable format so that the context of the full text is driven by reading that:\n\nTitle: {article.title}\n\n{article.description}"
                response = self.llm.invoke([HumanMessage(content=prompt)])
                article.summary = response.content

                articles.append(article)

        return articles


if __name__ == "__main__":
    scraper = OpenAIScraper()
    articles = scraper.get_articles(hours=24)

    for article in articles:
        print(f"\nTitle: {article.title}")
        print(f"URL: {article.url}")
        print(f"Summary: {article.summary}")