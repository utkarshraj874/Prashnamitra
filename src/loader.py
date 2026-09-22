# from pathlib import Path
# from typing import List

# from langchain_community.document_loaders import PyPDFLoader
# # Pypdfloader  Ye LangChain ka loader hai,Ye PDF read karta hai.
# from langchain_core.documents import Document
# #document har ek page ko represent karta hai 


# from src.logger import logger

# class PDFLoader:

#     def __init__(self, pdf_path:str|Path):
#         self.pdf_path = Path(pdf_path)

#     def load_documents(self, pdf_paths:List[Path]) -> List[Document]:
#         documents = []

#         for pdf in pdf_paths:
#             try:
#                 logger.info(f"Loading PDF : {pdf.name}")

#                 loader = PyPDFLoader(str(pdf))
#                 #pdf load karta ahib ,
#                 docs = loader.load()#pdf ko pages me devide akrta hai


#                 # add file name in meta data 
#                 # har page ke uper extra info add akrenge 
#                 for doc in docs:
              
#                     doc.metadata["source_file"] = pdf.name
                
#                 documents.extend(docs)# collect all the pages of every pdf in a single placce 

#                 logger.info(f"{pdf.name} loaded sucessfully")

#             except Exception as e:

#                 logger.error(f"Error loading{pdf.name}: {e}")

#         return documents

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
# Pypdfloader  Ye LangChain ka loader hai,Ye PDF read karta hai.
from langchain_core.documents import Document
#document har ek page ko represent karta hai 

from src.logger import logger


class PDFLoader:

    def __init__(self, pdf_path: str | Path):
        self.pdf_path = Path(pdf_path)

    def load(self) -> list[Document]:

        try:
            logger.info(f"Loading PDF: {self.pdf_path.name}")

            loader = PyPDFLoader(str(self.pdf_path))#PyPDFLoader को path दिया जाता है।,

            documents = loader.load()#.load pdf ko padhkar usko list of page bana deta hai 

            for doc in documents:
                doc.metadata["source_file"] = self.pdf_path.name # har document ke metadat ame source file ka name add kar diya jaata hai , 
                # isse pta chalta ahi ki kon sa chunk kis pdf ka hai 

            logger.info(f"{self.pdf_path.name} loaded successfully")

            return documents

        except Exception as e:

            logger.exception(e)

            raise