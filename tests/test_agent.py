from unittest.mock import Mock, patch

import httpx

from src.agent import AgentManager
from src.llm import LLMManager


def test_calculator_tool_handles_percentage_expression():
    manager = AgentManager()

    result = manager.safe_calculate("25% of 800")

    assert result == 200


def test_document_task_route_detects_summary_query():
    manager = AgentManager()

    assert manager.route_question("Summarize this document.") == "document_task"
    assert manager.route_question("Calculate 25% of 800.") == "calculator"


def test_llm_rate_limit_raises_user_friendly_error():
    manager = LLMManager()
    manager.llm = Mock()
    manager.llm.invoke.side_effect = httpx.HTTPStatusError(
        "rate limited",
        request=httpx.Request("POST", "https://example.com"),
        response=httpx.Response(429, request=httpx.Request("POST", "https://example.com")),
    )

    try:
        manager.generate_from_prompt("hello")
        assert False, "Expected ValueError for rate-limited API call"
    except ValueError as exc:
        assert "rate-limited" in str(exc).lower()


@patch("src.llm.ChatGroq")
@patch("src.llm.ChatMistralAI")
def test_llm_prefers_groq_when_api_key_is_present(mistral_mock, groq_mock):
    with patch("src.llm.GROQ_API_KEY", "test-groq-key"), patch("src.llm.MISTRAL_API_KEY", None):
        manager = LLMManager()

    assert manager.llm is groq_mock.return_value
    mistral_mock.assert_not_called()
    groq_mock.assert_called_once()


def test_history_manager_keeps_messages_per_thread(monkeypatch):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from src.database import Base
    from src.history import HistoryManager

    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr("src.history.SessionLocal", SessionLocal)

    manager = HistoryManager()
    manager.save("first", "one", thread_id="thread-a")
    manager.save("second", "two", thread_id="thread-b")
    manager.save("third", "three", thread_id="thread-a")

    thread_a = manager.get_thread("thread-a")
    thread_b = manager.get_thread("thread-b")

    assert [item["content"] for item in thread_a if item["role"] == "user"] == ["first", "third"]
    assert [item["content"] for item in thread_b if item["role"] == "user"] == ["second"]


def test_agent_uses_previous_messages_in_prompt():
    manager = AgentManager()
    history_messages = [
        {"role": "user", "content": "My name is Manish."},
        {"role": "assistant", "content": "Nice to meet you, Manish!"},
    ]

    prompt = manager._build_history_prompt("What is my name?", history_messages)

    assert "My name is Manish." in prompt
    assert "Current user question: What is my name?" in prompt
