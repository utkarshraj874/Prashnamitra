from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)


def ensure_chat_history_schema():
    try:
        inspector = inspect(engine)
        if not inspector.has_table("chat_history"):
            return

        columns = [column["name"] for column in inspector.get_columns("chat_history")]
        if "thread_id" in columns:
            return

        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE chat_history ADD COLUMN thread_id VARCHAR(255) DEFAULT 'default'"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_chat_history_thread_id ON chat_history (thread_id)"))
    except Exception:
        pass


ensure_chat_history_schema()

SessionLocal = sessionmaker(
    bind = engine,
    autoflush=False,
    autocommit = False
)

Base = declarative_base()