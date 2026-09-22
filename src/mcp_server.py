import ast
import re
from typing import Any, Iterable

from mcp.server.fastmcp import FastMCP

from config.settings import CHROMA_DIR
from src.logger import logger
from src.retriver import RetriverManager
from src.vectordb import VectorStoreManager

mcp = FastMCP("DocuMind")


def safe_calculate(expression: str) -> float | int:
    """Evaluate simple numeric math safely without using eval()."""
    cleaned = (expression or "").strip()
    if not cleaned:
        raise ValueError("Calculator input is empty.")

    normalized = (
        cleaned.replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace("−", "-")
    )

    percentage_match = re.search(
        r"(?P<percent>\d+(?:\.\d+)?)\s*%\s*of\s*(?P<base>\d+(?:\.\d+)?)",
        normalized,
        flags=re.IGNORECASE,
    )
    if percentage_match:
        percent = float(percentage_match.group("percent"))
        base = float(percentage_match.group("base"))
        result = (percent / 100) * base
        return int(result) if result.is_integer() else result

    try:
        parsed = ast.parse(normalized, mode="eval")
    except SyntaxError as exc:
        raise ValueError("Invalid calculator input.") from exc

    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Constant,
    )

    for node in ast.walk(parsed):
        if not isinstance(node, allowed_nodes):
            raise ValueError("Invalid calculator input.")

    result = eval(compile(parsed, "<calculator>", "eval"), {"__builtins__": {}}, {})
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return result


def _load_vectorstore():
    try:
        db = VectorStoreManager(persist_directory=CHROMA_DIR)
        return db.load_vectorstore()
    except Exception as exc:
        logger.warning(f"Could not load existing vector store for MCP tools: {exc}")
        return None


@mcp.tool()
def search_documents(query: str) -> list[dict[str, Any]]:
    """Search the existing ChromaDB documents for matching chunks."""
    vectorstore = _load_vectorstore()
    if vectorstore is None:
        return [{"error": "No documents uploaded yet."}]

    documents = RetriverManager(vectorstore).retrieve(query)
    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source_file", "unknown"),
            "page": doc.metadata.get("page", "unknown"),
        }
        for doc in documents
    ]


@mcp.tool()
def list_documents() -> list[str]:
    """List the documents currently available in the Chroma vector store."""
    vectorstore = _load_vectorstore()
    if vectorstore is None:
        return []

    try:
        metadata = vectorstore.get(include=["metadatas"])
        sources = []
        for source in metadata.get("metadatas", []):
            source_name = source.get("source_file")
            if source_name and source_name not in sources:
                sources.append(source_name)
        return sources
    except Exception as exc:
        logger.exception(exc)
        return []


@mcp.tool()
def get_document_metadata() -> list[dict[str, Any]]:
    """Return a lightweight view of current document metadata."""
    vectorstore = _load_vectorstore()
    if vectorstore is None:
        return []

    try:
        data = vectorstore.get(include=["metadatas", "documents"])
        results = []
        for idx, metadata in enumerate(data.get("metadatas", [])):
            item = {
                "source": metadata.get("source_file", "unknown"),
                "page": metadata.get("page", "unknown"),
                "chunk_index": idx,
                "preview": (data.get("documents", [""])[idx][:200] if idx < len(data.get("documents", [])) else ""),
            }
            results.append(item)
        return results
    except Exception as exc:
        logger.exception(exc)
        return []


@mcp.tool()
def calculator(expression: str) -> float | int:
    """Perform a safe arithmetic calculation for simple numeric expressions."""
    return safe_calculate(expression)


if __name__ == "__main__":
    mcp.run()
