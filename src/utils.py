from pathlib import Path
from uuid import uuid4
import shutil # built in module hai , iska kaam file folder  cpy, move, delete karana ahai 

from langchain_core.documents import Document

from src.logger import logger


def save_uploaded_file(uploaded_file , upload_dir:Path)-> Path:
    """
    save uploaded pdf into the uploads directory.
    returns the saved file path. 
    
    """

    upload_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{uuid4()}_{uploaded_file.name}"  # uuid4 unique id generate karta hai ,agr resume.pdf upload hua hai to  ye pura line 7uhfgresume.pdf return akrega 

    file_path = upload_dir / file_name # directory bana rhe ahi 

    with open(file_path, "wb") as f:# write , b=binaary
        f.write(uploaded_file.getbuffer())#ram(memory) me jo pdf hai uska  raw byte niaklta hai 

    logger.info(f"File saved : {file_path}")

    return file_path

def build_context(documents: list[Document]) -> str:
    """
    convert rerieved documents 
    into a single context string"""

    logger.info("building Context ")

    context = "\n\n".join(doc.page_content # har ek page ka content utho aur usko join karke return kar do 
                          for doc in  documents
                          )
    return context

def delete_file(file_path: Path):

    if file_path.exists():

        file_path.unlink() # sirf ek file delete karta hai 

        logger.info(f"Deleted File : {file_path}")


def clear_directory(directory: Path):

    if directory.exists():

        shutil.rmtree(directory)# pura folder delete kardeta hai 

        directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"cleared Directory : {directory}")
    


# User Upload PDF ->Streamlit -> uploaded_file ->getbuffer() -> Binary Bytes
#write()-> Hard Disk -> loader.py->splitter.py ->vectordb.py ->retriever.py ->documents -> join  -> context -> llm

