import ast
import re
from typing import Literal, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from config.prompts import (
    STUDY_GUIDE_PROMPT,
    SUMMARY_PROMPT,
    QUESTION_GENERATION_PROMPT,
)
from src.llm import LLMManager
from src.mcp_server import safe_calculate
from src.rag import RAGpipeline


class AgentState(TypedDict):
    messages: list[str]
    query: str
    documents: list
    tool_result: str
    answer: str
    context: str
    route: str
    error: str


class AgentManager:
    """Simple LangGraph-based orchestration layer around the existing RAG and MCP tools."""

    def __init__(self, vectorstore=None):
        self.vectorstore = vectorstore
        self.llm = LLMManager()
        self.checkpointer = MemorySaver()

    def route_question(self, question: str) -> str:
        if not question or not question.strip():
            return "empty"

        text = question.strip().lower()

        if re.search(r"\d.*[%]|%\s*of\s*\d|calculate|calculator", text):
            return "calculator"

        if any(keyword in text for keyword in ["summarize", "summary", "study guide", "study", "generate questions", "questions from this document"]):
            return "document_task"

        if self.vectorstore is not None and any(keyword in text for keyword in ["document", "pdf", "report", "according to", "based on"]):
            return "rag"

        return "general"

    def safe_calculate(self, expression: str):
        return safe_calculate(expression)

    def _build_history_prompt(self, question: str, history_messages: list | None = None) -> str:
        if not history_messages:
            return question

        recent_messages = history_messages[-8:]
        formatted_history = []
        for item in recent_messages:
            if not item or not item.get("content"):
                continue
            role = "User" if item.get("role") == "user" else "Assistant"
            formatted_history.append(f"{role}: {item['content']}")

        if not formatted_history:
            return question

        return (
            "Conversation history:\n"
            + "\n".join(formatted_history)
            + f"\n\nCurrent user question: {question}"
        )

    def _direct_llm(self, question: str, history_messages: list | None = None):
        prompt = self._build_history_prompt(question, history_messages)
        return self.llm.generate_direct_answer(prompt)

    def _rag_answer(self, question: str):
        if self.vectorstore is None:
            raise ValueError("No document has been uploaded yet.")
        rag = RAGpipeline(self.vectorstore)
        return rag.ask(question)

    def _document_task(self, question: str):
        if self.vectorstore is None:
            raise ValueError("Please upload a PDF before asking for document tasks.")

        rag = RAGpipeline(self.vectorstore)
        text = question.strip().lower()

        if "summarize" in text or "summary" in text:
            return rag.summarize_document(question)
        if "study guide" in text or "study" in text:
            return rag.create_study_guide(question)
        if "generate questions" in text or "questions" in text:
            return rag.generate_questions(question)

        return rag.ask(question)

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("router", self._router_node)
        workflow.add_node("calculator", self._calculator_node)
        workflow.add_node("document_task", self._document_task_node)
        workflow.add_node("rag", self._rag_node)
        workflow.add_node("general", self._general_node)
        workflow.add_node("finalize", self._finalize_node)

        workflow.set_entry_point("router")
        workflow.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "calculator": "calculator",
                "document_task": "document_task",
                "rag": "rag",
                "general": "general",
                "empty": "finalize",
            },
        )
        workflow.add_edge("calculator", "finalize")
        workflow.add_edge("document_task", "finalize")
        workflow.add_edge("rag", "finalize")
        workflow.add_edge("general", "finalize")
        workflow.add_edge("finalize", END)
        return workflow.compile(checkpointer=self.checkpointer)

    def _route_decision(self, state: AgentState) -> str:
        return state.get("route", "general")

    def _router_node(self, state: AgentState):
        query = state.get("query", "")
        route = self.route_question(query)
        state["route"] = route
        return state

    def _calculator_node(self, state: AgentState):
        try:
            value = self.safe_calculate(state["query"])
            state["tool_result"] = str(value)
            state["answer"] = f"Result: {value}"
        except ValueError as exc:
            state["error"] = str(exc)
            state["answer"] = str(exc)
        return state

    def _document_task_node(self, state: AgentState):
        query = state["query"]
        try:
            result = self._document_task(query)
            state["answer"] = result["answer"]
            state["context"] = result.get("context", "")
            state["documents"] = result.get("documents", [])
        except Exception as exc:
            state["error"] = str(exc)
            state["answer"] = str(exc)
        return state

    def _rag_node(self, state: AgentState):
        query = state["query"]
        try:
            result = self._rag_answer(query)
            state["answer"] = result["answer"]
            state["context"] = result.get("context", "")
            state["documents"] = result.get("documents", [])
        except Exception as exc:
            state["error"] = str(exc)
            state["answer"] = str(exc)
        return state

    def _general_node(self, state: AgentState):
        try:
            history_messages = state.get("messages") or []
            state["answer"] = self._direct_llm(state["query"], history_messages)
        except Exception as exc:
            state["error"] = str(exc)
            state["answer"] = str(exc)
        return state

    def _finalize_node(self, state: AgentState):
        if not state.get("answer"):
            state["answer"] = "I could not generate a response."
        return state

    def process(self, question: str, vectorstore=None, thread_id="default", history_messages=None):
        if question is None or not str(question).strip():
            return {"answer": "Please enter a valid question.", "documents": [], "context": "", "route": "empty"}

        if vectorstore is not None:
            self.vectorstore = vectorstore

        graph = self._build_graph()
        state = {
            "messages": history_messages or [],
            "query": question,
            "documents": [],
            "tool_result": "",
            "answer": "",
            "context": "",
            "route": "",
            "error": "",
        }

        config = {"configurable": {"thread_id": thread_id}}

        try:
            result = graph.invoke(state, config=config)
        except Exception as exc:
            return {
                "answer": "The AI service is temporarily unavailable. Please try again in a moment.",
                "context": "",
                "documents": [],
                "route": "general",
                "error": str(exc),
            }

        return {
            "answer": result.get("answer", ""),
            "context": result.get("context", ""),
            "documents": result.get("documents", []),
            "route": result.get("route", "general"),
            "error": result.get("error", ""),
        }

    def process_stream(self, question: str, vectorstore=None, thread_id="default", history_messages=None):
        if question is None or not str(question).strip():
            yield "Please enter a valid question."
            return

        if vectorstore is not None:
            self.vectorstore = vectorstore

        route = self.route_question(question)
        if route == "general":
            prompt = self._build_history_prompt(question, history_messages)
            yield from self.llm.generate_direct_answer_stream(prompt)
            return

        result = self.process(question, vectorstore=vectorstore, thread_id=thread_id, history_messages=history_messages)
        if result.get("answer"):
            yield result["answer"]
