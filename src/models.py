from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from src.database import Base

class ChatHistory(Base):

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key = True)
    thread_id = Column(String(255), nullable=False, index=True, default="default")
    question = Column(Text,nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(
        DateTime,
        server_default=func.now()
    )