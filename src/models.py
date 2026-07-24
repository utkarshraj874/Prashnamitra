from sqlalchemy import Column, Integer,Text,DateTime
from sqlalchemy.sql import func

from src.database import Base

class ChatHistory(Base):

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key = True)

    question = Column(Text,nullable=False)

    answer = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )