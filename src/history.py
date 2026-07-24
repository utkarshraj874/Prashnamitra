from src.database import SessionLocal, engine
from src.models import Base, ChatHistory

Base.metadata.create_all(bind = engine)


class HistoryManager:

    def save(self, question, answer):

        db = SessionLocal()

        chat = ChatHistory(
            question = question,
            answer = answer 
        )

        db.add(chat)

        db.commit()

        db.close()

    def get_all(self):

        db = SessionLocal()

        chats = db.query(ChatHistory).all()

        db.close()

        return chats

    def clear(self):

        db = SessionLocal()

        db.query(ChatHistory).delete()

        db.commit()

        db.close()
