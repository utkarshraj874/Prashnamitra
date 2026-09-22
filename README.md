# 📚 PrashnaMitra

PrashnaMitra is a Retrieval-Augmented Generation (RAG) chatbot that now adds a lightweight LangGraph agent layer and a small MCP tool layer on top of the current document workflow. Users can upload PDFs, ask document-based questions, use a calculator tool, and trigger document actions such as summarization, study guides, and question generation.

---

## ✨ Features

- 📄 Upload and chat with PDF documents
- 🔍 Semantic search using embeddings and ChromaDB
- 🧠 Existing RAG flow preserved and wrapped by LangGraph
- 🤖 Agentic routing between document retrieval, MCP tools, and direct LLM answers
- ⚙️ MCP tools for document search, document listing, document metadata, and calculator actions
- 📚 Document tasks: summarize document, create study guide, generate questions
- 💬 Persistent chat history in PostgreSQL
- 📝 Basic error handling for empty inputs, missing documents, tool failures, and invalid calculator input
- 🐳 Docker support for the app and Postgres service

---

## 🛠 Tech Stack

- Python
- Streamlit
- LangChain
- LangGraph
- MCP
- Groq AI
- ChromaDB
- PostgreSQL
- SQLAlchemy
- Docker

---

## 📂 Project Structure

```text
DocuMind-AI/
│
├── app.py
├── config/
├── src/
├── data/
├── logs/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── tests/
```

---

## ⚙️ Installation

```bash
git clone https://github.com/your-username/DocuMind-AI.git

cd DocuMind-AI

python -m venv .venv

./venv/Scripts/Activate.ps1   # Windows PowerShell
# or source venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_key
DATABASE_URL=postgresql://postgres:password@localhost:5432/documind
```

Run the application:

```bash
streamlit run app.py
```

---

## 🏗 Architecture

```text
User
  |
  v
Streamlit UI
  |
  v
LangGraph Agent / Router
  |-------------------------|
  |                         |
  v                         v
RAG Pipeline              MCP Tools
  |                         |
  v                         +--> calculator
ChromaDB + Retriever       +--> search_documents
  |                         +--> list_documents
  v                         +--> get_document_metadata
Groq LLM
  |
  v
PostgreSQL Chat History
```

The current RAG path remains the backbone of the app: upload PDF → loader → splitter → embeddings → ChromaDB → retriever → Groq answer. LangGraph simply decides whether the request should go through retrieval, an MCP tool, or direct LLM generation.

---

## 🚀 Agentic Examples

Try prompts like:

```text
What is this document about?
Summarize this document.
Create a study guide from this document.
Generate 10 questions from this document.
Calculate 25% of 800.
```

---

## ⚠️ Notes

- The app still requires a valid uploaded PDF for document retrieval tasks.
- General questions and arithmetic queries can work without a document if they do not require retrieval.
- The PostgreSQL chat history remains active and is not replaced by a second storage layer.

---

## 👨‍💻 Author

**manish kumar **

If you found this project helpful, feel free to ⭐ the repository.