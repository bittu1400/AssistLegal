from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv
import os
from injetion import ChatbotService
from chatbot import retrieve_context, generate_answer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env
load_dotenv()

# Initialize Firebase Admin
cred = credentials.Certificate(os.getenv("FIREBASE_ADMIN_KEY_PATH"))
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
chatbot_service = ChatbotService()

@app.get("/firebase-config")
async def get_firebase_config():
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

class ChatRequest(BaseModel):
    user_message: str
    uid: str | None

async def verify_firebase_token(token: str = Depends(oauth2_scheme)):
    try:
        decoded_token = auth.verify_id_token(token)
        if not decoded_token.get('email_verified'):
            raise HTTPException(status_code=403, detail="Email not verified")
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        # Step 1: Verify User
        user = auth.get_user(req.uid)
        if not user.email_verified:
            raise HTTPException(status_code=401, detail="Email not verified")
        user_email = user.email

        # Step 2: Retrieve last N distinct message pairs from Firestore
        messages_ref = db.collection("users").document(user.uid).collection("messages") \
                         .order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10)
        docs = list(messages_ref.stream())

        previous_messages = []
        seen_texts = set()
        for doc in reversed(docs):
            data = doc.to_dict()
            user_msg = data.get("user_message")
            bot_reply = data.get("bot_reply")
            if user_msg and bot_reply and user_msg not in seen_texts:
                previous_messages.append({
                    "user": user_msg,
                    "bot": bot_reply
                })
                seen_texts.add(user_msg)

        # Debug logging
        logger.info(f"previous_messages count: {len(previous_messages)}")
        logger.info(f"previous_messages: {previous_messages}")

        # Step 3: Construct context with cleaned history (handle empty)
        vectordb = chatbot_service.get_vectordb()
        if len(previous_messages) == 0:
            context = ""  # No prior context, safe default
        else:
            context = retrieve_context(previous_messages, vectordb)

        logger.info(f"Context for model:\n{context}")

        # Step 4: Generate response using context and current input
        answer = generate_answer(req.user_message, context)

        # Step 5: Save the new message pair
        message_data = {
            "user_message": req.user_message,
            "bot_reply": answer,
            "user_email": user_email,
            "user_uid": user.uid,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        doc_ref = db.collection("users").document(user.uid).collection("messages").add(message_data)
        logger.info(f"Stored message with document ID: {doc_ref[1].id}")

        # Step 6: Return JSON-wrapped response
        return {"response": answer}

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/chat/history")
async def chat_history(token: str = Depends(oauth2_scheme)):
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        logger.info(f"Fetching chat history for UID: {uid}")

        messages_ref = db.collection("users").document(uid).collection("messages") \
                         .order_by("timestamp")
        docs = list(messages_ref.stream())

        history = []
        for doc in docs:
            data = doc.to_dict()
            history.append({
                "user_message": data.get("user_message"),
                "bot_reply": data.get("bot_reply"),
                "timestamp": data.get("timestamp"),
                "document_id": doc.id
            })

        return {"history": history}

    except Exception as e:
        logger.error(f"Error fetching chat history: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or failed to fetch history")
