from pathlib import Path # used for handling file folder path 
from dotenv import load_dotenv
import os

load_dotenv()

# project path 

BASE_DIR =Path(__file__).resolve().parent # __file__ current file ka name 
DATA_DIR = BASE_DIR/"data"
UPLOAD_DIR = DATA_DIR/"uploads"
CHROMA_DIR = DATA_DIR/"chroma"

UPLOAD_DIR.mkdir(parents=True,exist_ok = True)#if upload folder doesn't exist then mkdir would made this  
CHROMA_DIR.mkdir(parents=True,exist_ok=True)

#api keys

def _clean_key(key_name: str):
    value = os.getenv(key_name)
    if value is None:
        return None
    value = value.strip().strip('"').strip("'")
    return value or None


GROQ_API_KEY = _clean_key("GROQ_API_KEY") or _clean_key("GROQCLOUD_API_KEY")
MISTRAL_API_KEY = _clean_key("MISTRAL_API_KEY")

# models

EMBEDDING_MODEL = "mistral-embed"  # used for vector generation
CHAT_MODEL = "openai/gpt-oss-20b"  # working Groq model for this API key
TEMPERATURE = 0.2

#chunk Settings

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150 # devide the pdf into chunks of 1000 words and take 150 words from  previous chunks


#Retriver

TOP_K = 4 #kitne best result return karne hai 

FETCH_K = 10 # kitne documents fetch karne hai 

SEARCH_TYPE = "mmr" #maximal marginal relevance search strategy 

#stremlit 

APP_TITLE = "PrashnaMitra"
PAGE_LAYOUT = "wide"

