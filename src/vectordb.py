from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_chroma import Chroma

from src.embeddings import EmbeddingGenerator
from src.logger import logger


class FolderDocumentIndexer:
    """Load supported files from a connected folder and turn them into LangChain documents."""

    SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}

    @staticmethod
    def list_supported_files(folder_path: str | Path) -> List[Path]:
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return []

        files = []
        for file_path in folder.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in FolderDocumentIndexer.SUPPORTED_EXTENSIONS:
                files.append(file_path)
        return sorted(files)

    @classmethod
    def load_documents(cls, folder_path: str | Path) -> List[Document]:
        documents: List[Document] = []

        for file_path in cls.list_supported_files(folder_path):
            if file_path.suffix.lower() == ".pdf":
                loader = PyPDFLoader(str(file_path))
                loaded_docs = loader.load()
            else:
                loader = TextLoader(str(file_path), encoding="utf-8")
                loaded_docs = loader.load()

            for doc in loaded_docs:
                doc.metadata["source_file"] = file_path.name
                doc.metadata["source_path"] = str(file_path)
                documents.append(doc)

        return documents

    @classmethod
    def index_folder(cls, folder_path: str | Path, persist_directory: str | Path):
        documents = cls.load_documents(folder_path)
        if not documents:
            raise ValueError("No supported documents were found in the selected folder.")

        vector_store_manager = VectorStoreManager(persist_directory=persist_directory)
        vectorstore = vector_store_manager.create_vectorstore(documents)
        return vectorstore, documents


class VectorStoreManager: # jab vectorstore manager call hoga , yani object banega , tab python khud se inital setup akr dega 
    """
    Responsible for creating  and loading the chroma Vector Database
    """

    def __init__(self , persist_directory: Path):# init func ko python khud se hi call karta hai,hme call nhi akrna padta hai

        self.persist_directory = persist_directory #persisit_directory means permanent directory 
         # persisit  directory sirf function ke ander exxit karta hai , function khattma variable khattam , isliye humne self.persistdiectory banaya hai
         #taki pure function me use kar sake 
        embedding_generator = EmbeddingGenerator()

        self.embedding_model = embedding_generator.get_embedding_model()


    def create_vectorstore(self,
                          chunks:List[Document]
                          )-> Chroma:
        logger.info("creating chroma Vector Database")

        vectorstore = Chroma.from_documents( # chunk->embedding model -> vector ->store ->index ->database ready 
            documents=chunks,   # docment se vector bana ndo isliye from_document , .mere pass document hai
            embedding=self.embedding_model,
            persist_directory=str(self.persist_directory)
        )

        logger.info("Vector Database Created Successfully ")

        return vectorstore
    def load_vectorstore(self) -> Chroma:
#go to chroma_db -> reead existng database -> load all Database -> load all vectors -> return Chroma object
        logger.info("Loading Existing vector Database")

        vectorstore = Chroma(#mere pass database hai chroma usse data load karo 
            persist_directory=str(self.persist_directory),
            embedding_function= self.embedding_model #ye embeding questing ki embedding banane ke liye , abb compare karega 
        )

        logger.info("vector Database Loaded Successfully ")

        return vectorstore