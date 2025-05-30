import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import google.generativeai as genai
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppresses INFO, WARNING, and ERROR logs

# Load environment variables
load_dotenv()

# Setup Gemini model
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

# File paths
pdf_path = "Electronic_Act_Law.pdf"
VECTOR_DB_DIR = 'vectordb'

# Step 1: Load PDF
def load_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    return loader.load()

# Step 2: Split text into chunks
def split_text(pages):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    return splitter.split_documents(pages)

# Step 3: Create and save vector store
def create_vectorstore(chunks, embeddings):
    vectordb = FAISS.from_documents(chunks, embedding=embeddings)
    vectordb.save_local(VECTOR_DB_DIR)
    return vectordb

# Step 4: Load existing vector store
def load_vectorstore(embeddings):
    return FAISS.load_local(VECTOR_DB_DIR, embeddings, allow_dangerous_deserialization=True)

# Step 5: Retrieve context (multi-turn version)
def retrieve_context(message_chain, vectordb, k=3):
    """
    Builds context dynamically, minimizing redundancy and prioritizing relevant info.
    """
    # Step 1: Collect only the latest distinct user-bot interactions
    recent_messages = []
    seen = set()
    for msg in reversed(message_chain):
        user_text = msg.get("user")
        if user_text and user_text not in seen:
            recent_messages.append(f"User: {user_text}\nBot: {msg.get('bot')}")
            seen.add(user_text)
        if len(recent_messages) >= 3:  # Keep up to 3 recent interactions
            break
    recent_messages.reverse()

    # Step 2: Build history context from recent messages
    history_context = "\n".join(recent_messages)

    # Step 3: Vector search for relevant legal text
    latest_query = message_chain[-1]['user']
    relevant_docs = vectordb.similarity_search(latest_query, k=k)
    legal_context = "\n".join(doc.page_content for doc in relevant_docs)

    # Step 4: Combine for a focused context
    full_context = f"{history_context}\nRelevant Legal Texts:\n{legal_context}"
    return full_context.strip()

# Step 6: Generate answer using Gemini
# d ef generate_answer(query, context):
    prompt = f"""
You are a legal expert specializing in Nepal's Electronic Transactions Act (ETA) and cyber law.

Your task is to answer user questions in a professional, easy-to-understand format.

**Response Guidelines:**
- If the question requires explanation, provide a brief explanation first.
- Include relevant sections or clauses from the law in bullet points.
- Add a short summary **only if needed** (for complex queries).
- If the question is simple, provide a clean, direct answer without extra explanation or summary.
- Use **clear formatting**, no unnecessary symbols like *, #, ~ etc.
- Maintain a **formal and respectful tone**. Avoid hallucinating information.

**Example Format for Complex Queries:**
Explanation(Don't write this Explanation before giving answer just explain it as the query requires):
[Brief explanation]

Relevant Legal Sections(Don't write this Relevant Legal Sections before giving answer just give in bullet points as the query requires):
- Section X: Description
- Section Y: Description

Summary(Don't write this Summary before giving answer just explain it as the query requires):
[Only if necessary]

Now based on the following context and question, respond appropriately.

Context:
{context}

User's Question:
{query}

Provide the answer following the exact format above.

Answer:
"""
    response = model.generate_content(prompt, generation_config={"temperature": 0.2, "top_p" :0.95,"top_k":40, "max_output_tokens": 1024})
    return response.text.strip()

def generate_answer(query, context):
    prompt = f"""
You are a legal expert specializing in Nepal's Electronic Transactions Act (ETA) and cyber law.

Your task is to answer user questions in a professional, easy-to-understand format.

**Response Guidelines:**
- If the question requires explanation, provide a brief explanation first.
- Include relevant sections or clauses from the law in bullet points.
- Add a short summary **only if needed**.
- If the question is simple, provide a clean, direct answer without extra explanation or summary.
- Use **clear formatting**, no unnecessary symbols like *, #, ~ etc.
- Maintain a **formal and respectful tone**. Avoid hallucinating information.

**Use Bullet points to show Legal Sections:**
- Section X: Description
- Section Y: Description

Summary(Don't write this Summary before giving answer just explain it as the query requires):
[Only if necessary]

Now, based on the user's question and the relevant legal context provided, respond appropriately.

Legal Context:
{context}

User's Question:
{query}

Answer:
"""
    response = model.generate_content(
        prompt, 
        generation_config={"temperature": 0.2, "top_p": 0.95, "top_k": 40, "max_output_tokens": 1024}
    )
    return response.text.strip()

# Step 7: CLI testing (for local testing, optional)
def main():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("\nLoading and Preparing Vector Store...")

    if os.path.exists(VECTOR_DB_DIR):
        vectordb = load_vectorstore(embeddings)
        print("Vector store loaded.")
    else:
        print("Creating new vector store...")
        pages = load_pdf(pdf_path)
        chunks = split_text(pages)
        vectordb = create_vectorstore(chunks, embeddings)
        print("Vector store created.")

    print("\nChatbot Ready! Type 'exit' to quit.\n")
    conversation = []  # Message history list

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Append current user message to conversation
        conversation.append({"user": user_input, "bot": None})

        # Retrieve multi-turn context
        context = retrieve_context(conversation[-6:], vectordb)  # last 3 turns

        # Generate reply
        bot_reply = generate_answer(user_input, context)
        print("\nChatbot:", bot_reply, "\n")

        # Store bot reply in conversation
        conversation[-1]['bot'] = bot_reply

if __name__ == "__main__":
    main()
