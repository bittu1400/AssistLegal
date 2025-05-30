# injection.py

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import logging

logger = logging.getLogger(__name__)

VECTOR_DB_DIR = "vectordb"
PDF_PATH = "Electronic_Act_Law.pdf"

class ChatbotService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        try:
            self.vectordb = self._load_or_create_vectordb()
            logger.info("Vector DB loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load vector DB: {str(e)}")
            raise RuntimeError(f"Vector DB not found or corrupted: {str(e)}")

    def _load_or_create_vectordb(self):
        if os.path.exists(VECTOR_DB_DIR):
            logger.info("Loading existing vector DB from disk...")
            return FAISS.load_local(VECTOR_DB_DIR, self.embeddings, allow_dangerous_deserialization=True)
        else:
            logger.info("Vector DB not found. Creating new vector DB from PDF...")
            loader = PyPDFLoader(PDF_PATH)
            pages = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
            chunks = splitter.split_documents(pages)
            vectordb = FAISS.from_documents(chunks, embedding=self.embeddings)
            vectordb.save_local(VECTOR_DB_DIR)
            logger.info("Vector DB created and saved successfully.")
            return vectordb

    def get_vectordb(self):
        return self.vectordb
