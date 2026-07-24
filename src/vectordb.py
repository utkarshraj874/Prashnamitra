from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_chroma import Chroma

from src.embeddings import EmbeddingGenerator
from src.logger import logger

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