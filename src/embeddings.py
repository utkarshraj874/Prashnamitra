from typing import List

from langchain_core.documents import Document
from langchain_mistralai import MistralAIEmbeddings

from src.logger import logger

class EmbeddingGenerator:
    """ responsible for converting documents chunks into embeddings """

    def __init__(self):
        self.embedding_model = MistralAIEmbeddings(
            model = "mistral-embed "
        )

        logger.info("Mistral Embedding Model Initialized ")

    def get_embedding_model(self):

        return self.embedding_model
    def embed_documents(self, chunks:List[Document]):

        logger.info(f"Generating embedding for {len(chunks)} chunks")

        texts = [# extract only the texts(page content) from each documents
            chunk.page_content
            for chunk in chunks 
        ]
        embeddings = self.embedding_model.embed_documents(texts) # model ko text dikhaye jaate hai wo embedding(vectors genrate akrta hai )
               # embed_documents ये MistralAIEmbeddings class का method है (जो langchain_mistralai library में पहले से बना हुआ है)।
        logger.info("Embeddings generated sucessfully ")

        return embeddings