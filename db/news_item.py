# models/news_item.py

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, JSON
from sqlalchemy.sql import func
from db.connection import Base


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False)
    title = Column(Text, nullable=False)
    url = Column(String, unique=True, nullable=False)
    published_at = Column(TIMESTAMP, nullable=True)
    summary = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())