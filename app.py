import streamlit as st 

from config.settings import APP_TITLE,PAGE_LAYOUT

from src.logger import logger
from src.loader import PDFLoader
from src.splitter import DocumentSplitter
from src.embeddings import EmbeddingGenerator
from src.vectordb import VectorStoreManager
from src.rag import RAGpipeline

from src.history import HistoryManager
from src.utils import (
    save_uploaded_file,
    delete_file,
    build_context,
)

from config.settings import(
    UPLOAD_DIR,
    CHROMA_DIR,
)

  # streamlit config 
st.set_page_config(
    page_title="DocuMind AI",
    page_icon ="📚",
    layout = PAGE_LAYOUT,
)


st.title("📚 DocuMind AI")
st.caption("chat with your PDF using RAG + Mistral AI + ChromaDB")
logger.info("Application satrted ")

history = HistoryManager()

#sESSION STATE

if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag" not in st.session_state:
    st.session_state.rag = None

if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:

    st.title("Chat History")
    chats = history.get_all()

    if chats:

        for chat in reversed(chats):

            with st.expander(chat.question):

                st.write(chat.answer)

    else:

        st.info("No Chat history ")

    st.divider()

    if st.button(" clear History "):

        history.clear()

        st.success("History cleared")

        st.rerun()


# uplod pdf 

uploaded_file = st.file_uploader(
    "Upload  a PDF ",
    type = ["pdf"]
)

if uploaded_file and not st.session_state.pdf_uploaded:
    try:
        logger.info("Uploading  PDF ")

        pdf_path = save_uploaded_file(
            uploaded_file,
            UPLOAD_DIR,
        )

        st.success("PDF Uploaded Successfully ")

        #load pdf

        loader = PDFLoader(pdf_path)

        documents = loader.load()
 
        #split Documents

        splitter = DocumentSplitter()

        chunks = splitter.split(documents)

        # Embedding model

        embedding = EmbeddingGenerator()

        #Vector Database

        # db = VectorStoreManager(
        #     embedding_model = embedding.get_embedding_model(),
        #     persist_directory=CHROMA_DIR
        # )
        db = VectorStoreManager(
           persist_directory = CHROMA_DIR
           )


        vectorstore = db.create_vectorstore(chunks)

        # rag pipeline

        st.session_state.rag = RAGpipeline(vectorstore)
        st.session_state.pdf_uploaded = True

        delete_file(pdf_path)

        logger.info("Rag pip pipeline Ready")
    
    except Exception as e:

        logger.exception(e)

        st.error(str(e))
# --------------------------------------------------
# Display Previous Chat
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            if "context" in message:

                with st.expander("📄 Retrieved Context"):

                    st.write(message["context"])


# --------------------------------------------------
# Chat Input
# --------------------------------------------------

if st.session_state.rag:

    question = st.chat_input("Ask anything about your PDF...")

    if question:

        # -------- User Message --------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):

            st.markdown(question)

        # -------- AI Response --------

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                result = st.session_state.rag.ask(question)

            answer = result["answer"]

            st.markdown(answer)

            with st.expander("📄 Retrieved Context"):

                st.write(result["context"])

        # -------- Save Chat --------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "context": result["context"],
            }
        )

        history.save(
            question,
            answer,
        )

else:

    st.info("📄 Upload a PDF to start chatting.")

#         st.divider()

#         question = st.text_input("Ask your question ")

#         if question:

#             result= rag.ask(question)

#             history.save(question,
#                          result["answer"])

#             st.subheader("Answer")

#             st.write(result["answer"])

#             with st.expander("Retrieved Context"):

#                 st.write(result["context"])

#         delete_file(pdf_path)

#     except Exception as e:
#         logger.exception(e)

#         st.error(str(e))


# else:
#     st.info("Please uploads a PDF to continue")
       

