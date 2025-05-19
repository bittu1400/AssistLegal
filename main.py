from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import firebase_admin
from firebase_admin import credentials, auth, firestore
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from chatbot import retrieve_context, generate_answer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# print(  {"apiKey": os.getenv("FIREBASE_API_KEY"),
#         "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
#         "projectId": os.getenv("FIREBASE_PROJECT_ID"),
#         "appId": os.getenv("FIREBASE_APP_ID"),
#         "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
#         "messagingSenderId": os.getenv("FIREBASE_MSG_SENDER_ID"),
#         "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
#         "databaseURL": os.getenv("DATABASEURL")})

# Initialize Firebase Admin
cred = credentials.Certificate(os.getenv("FIREBASE_ADMIN_KEY_PATH"))
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 token scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/firebase-config")
async def get_firebase_config():
    logger.info("Fetching Firebase config")
    return JSONResponse({
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "appId": os.getenv("FIREBASE_APP_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MSG_SENDER_ID"),
        "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
        "databaseURL": os.getenv("DATABASEURL")
    })


# Pydantic models
class ChatRequest(BaseModel):
    user_message: str

# Load vector DB
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
try:
    vectordb = FAISS.load_local("vectordb", embeddings, allow_dangerous_deserialization=True)
except Exception as e:
    logger.error(f"Failed to load vector DB: {str(e)}")
    raise RuntimeError(f"Vector DB not found or corrupted: {str(e)}")

@app.post("/chat")
async def chat(req: ChatRequest):
# async def chat(req: ChatRequest, token: str = Depends(oauth2_scheme)):
    print("ASdasdasd")
    try:
        # # Verify token
        # decoded_token = auth.verify_id_token(token)
        # uid = decoded_token['uid']
        # logger.info("Verified token for user: %s", uid)
        # # Get context from vector DB
        context = retrieve_context(req.user_message, vectordb)
        logger.info("Retrieved context")

        # Generate answer using Gemini
        answer = generate_answer(req.user_message, context)
        logger.info("Generated answer")

        # Save message & response to Firestore
        db.collection("messages").add({
            # "uid": uid,
            "user_message": req.user_message,
            "bot_reply": answer
        })

        return {"response": answer}
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Error: {str(e)}")
