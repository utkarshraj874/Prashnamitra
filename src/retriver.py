from langchain_chroma import Chroma 
from src.logger import logger

class RetriverManager:
    """
    responsible for retriving the most relevant document chunks from the vector databas .
    """

    def __init__(self, vectorstore: Chroma):

        self.vectorstore = vectorstore

    def get_retriever(self):

        logger.info("Creating Retriever")

        retriever = self.vectorstore.as_retriever(
            search_type = "mmr",
            search_kwargs = {
                "k":4,
                "fetch_k":20,#mmr 20 v=chun nuthata ahia , usme se best 4 ko bhjna hai 
                "lambda_mult":0.5  # similarity aur diversity ka blance
            }
        )

        logger.info("Retriever ready ")

        return retriever
    
    def retrieve(self , query:str):

        retriever = self.get_retriever()

        logger.info(f"Searching for : {query}")

        documents = retriever.invoke(query)

        logger.info(f"Retrieved {len(documents)} documents")

        return documents        