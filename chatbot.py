import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Set up Gemini
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

# Define the path for the vector database directory
pdf_path = "Electronic_Act_Law.pdf"

VECTOR_DB_DIR = 'vectordb'

# Step 1: Load PDF
def load_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    return pages

# Step 2: Split text into chunks
def split_text(pages):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(pages)
    return chunks

# Step 3: Create Embeddings and Vector Store
def create_vectorstore(chunks, embeddings):
    vectordb = FAISS.from_documents(chunks, embedding=embeddings)
    vectordb.save_local(VECTOR_DB_DIR)
    return vectordb

# Step 4: Load existing Vector Store
def load_vectorstore(embeddings):
    vectordb = FAISS.load_local(VECTOR_DB_DIR, embeddings, allow_dangerous_deserialization=True)
    return vectordb

# Step 5: Search relevant chunks
def retrieve_context(query, vectordb, k=5):
    docs = vectordb.similarity_search(query, k=k)
    context = "\n".join(doc.page_content for doc in docs)
    return context

# Step 6: Ask Gemini to answer
def generate_answer(query, context):
    prompt = f"""
You are a legal expert specializing in Nepal's Electronic Transactions Act (ETA) and associated cyber laws. Your primary responsibility is to assist users by providing clear, concise, and legally accurate information on topics related to:

1. Electronic records and digital signatures
2. Cybercrimes and their penalties
3. Legal recognition of electronic transactions
4. Roles and responsibilities of certifying authorities
5. Jurisdiction and enforcement of cyber laws in Nepal





Important Instructions:
- NO bullet points, NO special symbols like *, ~, # etc.
- Keep the formatting clean and formal.
- Do not hallucinate or add extra information.
- Answer length depends on the nature of the question and context.
- Maintain good grammar and professional tone.


Context:
{context}

User's Question:
{query}

Provide the answer following the exact format above.

Answer:
"""
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = load_vectorstore(embeddings)
    
    response = model.generate_content(prompt, generation_config={"temperature": 0, "max_output_tokens": 500})
    return response.text

def main():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("\n📚 Loading and Preparing PDF...")

    if os.path.exists(VECTOR_DB_DIR):
        print('Loading existing vector database...')
        vectordb = load_vectorstore(embeddings)
    else:
        print('Creating new vector database...')
        pages = load_pdf(pdf_path)
        chunks = split_text(pages)
        vectordb = create_vectorstore(chunks, embeddings)

    print("\n✅ Chatbot Ready! Type 'exit' to quit.\n")

    while True:
        query = input("You: ")
        if query.lower() == "exit":
            print("Goodbye!")
            break

        context = retrieve_context(query, vectordb)
        final_answer = generate_answer(query, context)
        print("\nChatbot:", final_answer, "\n")

if __name__ == "__main__":
    main()