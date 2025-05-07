"""
import sqlite3
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from huggingface_hub import InferenceClient

# Hugging Face Token
HUGGINGFACE_TOKEN = "your-token-here"

# === Step 1: Load data from SQLite ===
def load_documents_from_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Modify this query according to your actual table and columns
    cursor.execute("SELECT Name, timestamp FROM faces")  # <-- change 'faces' if your table has another name
    
    rows = cursor.fetchall()
    documents = []
    for name, reg_date in rows:
        content = f"Name: {name}, RegistrationDate: {reg_date}"
        documents.append(Document(page_content=content))

    conn.close()
    return documents

# Load documents from face_data.db
db_path = "C:/Users/KUBER/Desktop/Proj/backend/face_recognition/database/face_data.db"
documents = load_documents_from_db(db_path)

# === Step 2: Split text chunks ===
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

# === Step 3: Create Embeddings & FAISS ===
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.from_documents(docs, embedding_model)
retriever = db.as_retriever()

# === Step 4: Ask Question ===
question = input("You: ")
relevant_docs = retriever.get_relevant_documents(question)
context = "\n".join([doc.page_content for doc in relevant_docs])

prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
print("\n[Prompt sent to model]:\n", prompt)

# === Step 5: Answer using HF Inference API or local ===
try:
    client = InferenceClient(token=HUGGINGFACE_TOKEN)
    response = client.text_generation(model="google/flan-t5-small", inputs=prompt, max_new_tokens=100)
    answer = response
except Exception:
    print("Hugging Face Inference API failed, using local model...")
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=100)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("\nAI:", answer)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

import sqlite3
import sys
import json

from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from huggingface_hub import InferenceClient

# === Configuration ===
HUGGINGFACE_TOKEN = "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"
DB_PATH = "C:/Users/KUBER/Desktop/Proj/backend/face_recognition/database/face_data.db"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "google/flan-t5-small"

# === Flask Setup ===
app = Flask(__name__)
CORS(app)

# === 1. Load data from SQLite ===
def load_documents_from_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT Name, timestamp FROM faces")  # Adjust if needed
    rows = cursor.fetchall()
    conn.close()

    documents = []
    for name, reg_date in rows:
        content = f"Name: {name}, RegistrationDate: {reg_date}"
        documents.append(Document(page_content=content))
    return documents

# === 2. Create FAISS retriever ===
def create_faiss_vectorstore(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
    embedding_model = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    db = FAISS.from_documents(docs, embedding_model)
    return db.as_retriever()

# === 3. Generate LLM response ===
def generate_response(prompt):
    try:
        client = InferenceClient(token=HUGGINGFACE_TOKEN)
        response = client.text_generation(model=LLM_MODEL, inputs=prompt, max_new_tokens=100)
        return response
    except Exception as e:
        print("⚠️ Inference API failed, using local model...", file=sys.stderr)
        tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
        model = AutoModelForSeq2SeqLM.from_pretrained(LLM_MODEL)
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=100)
        return tokenizer.decode(outputs[0], skip_special_tokens=True)

# === 4. Main Logic ===
def main(question: str):
    documents = load_documents_from_db(DB_PATH)
    retriever = create_faiss_vectorstore(documents)
    relevant_docs = retriever.get_relevant_documents(question)
    context = "\n".join([doc.page_content for doc in relevant_docs])
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    print("\n[Prompt sent to model]:\n", prompt)
    return generate_response(prompt)

# === 5. Flask Endpoint ===
@app.route("/query", methods=["POST"])
def handle_query():
    try:
        data = request.get_json()
        question = data.get("question", "")

        if not question:
            return jsonify({"error": "No question provided"}), 400

        answer = main(question)
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === 6. Entry Point ===
if __name__ == "__main__":
    app.run(port=5002, debug=True)
