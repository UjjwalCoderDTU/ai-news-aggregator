import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

# Used for PostgreSql locally
# # Fix password issue (@ → %40)
# from urllib.parse import quote_plus
# encoded_password = quote_plus(DB_PASSWORD)

# Create engine
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_engine(DATABASE_URL ,pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)

