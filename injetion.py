# chatbot_service.py

import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        try:
            self.vectordb = FAISS.load_local("vectordb", self.embeddings, allow_dangerous_deserialization=True)
            logger.info("Vector DB loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load vector DB: {str(e)}")
            raise RuntimeError(f"Vector DB not found or corrupted: {str(e)}")

    def get_vectordb(self):
        return self.vectordb


# Singleton pattern: instantiate once and reuse
chatbot_service = ChatbotService()
