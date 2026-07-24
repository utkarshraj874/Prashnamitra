# 📚 DocuMind AI

A Retrieval-Augmented Generation (RAG) chatbot that allows users to upload PDF documents and ask questions using **Mistral AI**, **LangChain**, and **ChromaDB**. The application retrieves relevant document chunks before generating answers and stores chat history in PostgreSQL.

---

## ✨ Features

- 📄 Chat with PDF documents
- 🔍 Semantic Search using Mistral Embeddings
- 🧠 Retrieval-Augmented Generation (RAG)
- 📦 ChromaDB Vector Store
- 💬 Persistent Chat History (PostgreSQL)
- 📝 Logging
- 🐳 Docker Support

---

## 🛠 Tech Stack

- Python
- Streamlit
- LangChain
- Mistral AI
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
└── README.md
```

---

## ⚙️ Installation

```bash
git clone https://github.com/your-username/DocuMind-AI.git

cd DocuMind-AI

python -m venv .venv

pip install -r requirements.txt
```

Create a `.env` file:

```env
MISTRAL_API_KEY=your_api_key

DATABASE_URL=postgresql://postgres:password@localhost:5432/documind
```

Run the application:

```bash
streamlit run app.py
```

---

## 🏗 Architecture

```text
PDF
 │
 ▼
Loader
 │
 ▼
Splitter
 │
 ▼
Embeddings
 │
 ▼
ChromaDB
 │
 ▼
Retriever
 │
 ▼
Mistral AI
 │
 ▼
Answer
 │
 ▼
PostgreSQL
```

---

## 🚀 Future Improvements

- Multi-PDF Support
- Source Citations
- User Authentication
- FastAPI Backend
- Cloud Deployment

---

## 👨‍💻 Author

**Utkarsh Raj**

If you found this project helpful, feel free to ⭐ the repository.