from sqlalchemy import inspect

from src.database import SessionLocal, engine, ensure_chat_history_schema
from src.models import Base, ChatHistory

Base.metadata.create_all(bind=engine)
ensure_chat_history_schema()


class HistoryManager:

    def _has_thread_column(self):
        try:
            inspector = inspect(engine)
            columns = [column["name"] for column in inspector.get_columns("chat_history")]
            return "thread_id" in columns
        except Exception:
            return False

    def save(self, question, answer, thread_id="default"):
        db = SessionLocal()

        data = {
            "question": question,
            "answer": answer,
        }
        if self._has_thread_column():
            data["thread_id"] = thread_id

        chat = ChatHistory(**data)

        db.add(chat)
        db.commit()
        db.refresh(chat)
        db.close()
        return chat

    def get_all(self, thread_id=None):
        db = SessionLocal()

        query = db.query(ChatHistory)
        if thread_id and self._has_thread_column():
            query = query.filter(ChatHistory.thread_id == thread_id)
        chats = query.order_by(ChatHistory.created_at.asc()).all()

        db.close()
        return chats

    def get_thread(self, thread_id="default"):
        chats = self.get_all(thread_id=thread_id)
        messages = []
        for chat in chats:
            messages.append({"role": "user", "content": chat.question})
            messages.append({"role": "assistant", "content": chat.answer})
        return messages

    def clear(self, thread_id=None):
        db = SessionLocal()

        query = db.query(ChatHistory)
        if thread_id and self._has_thread_column():
            query = query.filter(ChatHistory.thread_id == thread_id)
        query.delete()
        db.commit()
        db.close()

    def clear_thread(self, thread_id):
        self.clear(thread_id=thread_id)

