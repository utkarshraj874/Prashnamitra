from typing import List

from langchain_core.documents import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import (CHUNK_SIZE, 
                             CHUNK_OVERLAP)
from src.logger import logger 


class DocumentSplitter:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size = CHUNK_SIZE,
            chunk_overlap = CHUNK_OVERLAP
        )

    def split(self, docs: List[Document]) -> List[Document]:

        chunks = self.splitter.split_documents(docs)

        logger.info(f"Created{len(chunks)} chunks ")

        return chunks
