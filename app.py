import uuid
from pathlib import Path

import streamlit as st

from config.settings import CHROMA_DIR, PAGE_LAYOUT, UPLOAD_DIR
from src.agent import AgentManager
from src.embeddings import EmbeddingGenerator
from src.history import HistoryManager
from src.loader import PDFLoader
from src.logger import logger
from src.rag import RAGpipeline
from src.splitter import DocumentSplitter
from src.utils import delete_file, save_uploaded_file
from src.vectordb import VectorStoreManager

st.set_page_config(
    page_title="PrashnaMitra",
    page_icon="📚",
    layout=PAGE_LAYOUT,
)

st.title("📚 PrashnaMitra")
st.caption("Agentic RAG + MCP + Groq AI + ChromaDB")
logger.info("Application started")

history = HistoryManager()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = uuid.uuid4().hex

if "messages" not in st.session_state:
    st.session_state.messages = history.get_thread(st.session_state.thread_id)

if st.session_state.messages == []:
    st.session_state.messages = history.get_thread(st.session_state.thread_id)

if "rag" not in st.session_state:
    st.session_state.rag = None

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "agent" not in st.session_state:
    st.session_state.agent = AgentManager()

if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False

if "connected_folder" not in st.session_state:
    st.session_state.connected_folder = ""

if "workspace_documents" not in st.session_state:
    st.session_state.workspace_documents = []

with st.sidebar:
    st.title("Chat History")
    st.caption(f"Thread: {st.session_state.thread_id[:8]}")
    chats = history.get_all(thread_id=st.session_state.thread_id)

    if chats:
        for chat in reversed(chats):
            with st.expander(chat.question):
                st.write(chat.answer)
    else:
        st.info("No chat history")

    if st.button("New Thread"):
        st.session_state.thread_id = uuid.uuid4().hex
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Agent Mode")
    st.markdown(
        "- Answer questions\n"
        "- Summarize docs\n"
        "- Create study guide\n"
        "- Generate questions\n"
        "- Use calculator"
    )

    if st.button("Clear History"):
        history.clear(st.session_state.thread_id)
        st.session_state.messages = []
        st.success("History cleared")
        st.rerun()

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file and not st.session_state.pdf_uploaded:
    try:
        logger.info("Uploading PDF")
        pdf_path = save_uploaded_file(uploaded_file, UPLOAD_DIR)
        st.success("PDF uploaded successfully")

        loader = PDFLoader(pdf_path)
        documents = loader.load()

        splitter = DocumentSplitter()
        chunks = splitter.split(documents)

        _ = EmbeddingGenerator()

        db = VectorStoreManager(persist_directory=CHROMA_DIR)
        vectorstore = db.create_vectorstore(chunks)

        st.session_state.vectorstore = vectorstore
        st.session_state.rag = RAGpipeline(vectorstore)
        st.session_state.agent = AgentManager(vectorstore)
        st.session_state.pdf_uploaded = True

        delete_file(pdf_path)
        logger.info("RAG pipeline ready")
    except Exception as exc:
        logger.exception(exc)
        st.error(str(exc))

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "context" in message:
            with st.expander("📄 Retrieved Context"):
                st.write(message["context"])

question = st.chat_input("Ask PrashnaMitra to answer, summarize, study, or calculate...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            stream = st.session_state.agent.process_stream(
                question,
                st.session_state.vectorstore,
                thread_id=st.session_state.thread_id,
                history_messages=st.session_state.messages,
            )
            answer = st.write_stream(stream)

        context = ""
        result = st.session_state.agent.process(
            question,
            st.session_state.vectorstore,
            thread_id=st.session_state.thread_id,
            history_messages=st.session_state.messages,
        )
        answer = result.get("answer") or answer or "I could not generate an answer."
        context = result.get("context", "")

        if context:
            with st.expander("📄 Retrieved Context"):
                st.write(context)

        if result.get("error"):
            st.warning(result["error"])

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "context": context,
    })

    history.save(question, answer, thread_id=st.session_state.thread_id)

elif not st.session_state.rag:
    st.info("📄 Upload a PDF to enable document retrieval, or ask a general question without a document.")

