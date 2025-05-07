# Face Recognition Platform with Real-Time AI Q&A 

# Overview

This project is a browser-based platform that enables users to:

  Register their faces using a webcam.

  Recognize faces in real-time with multi-face support.

  Ask questions through a chat interface powered by RAG (Retrieval-Augmented Generation) to get real-time insights into face registration events.

# Features

# 1. Face Registration

  Detects faces using webcam (React frontend).

  Assigns a name and stores encoding, timestamp, and metadata in a database.

  Built using Python (Face Recognition Library).

# 2. Live Recognition
   
  Real-time scanning from webcam.

  Overlays name and bounding box on recognized faces.

  Handles multiple faces per frame.

# 3. Chat-Based Query Interface
   
  Users can query using natural language.

  Backend uses RAG pipeline (LangChain + FAISS + OpenAI).

  Answers include:

  "Who was the last person registered?"

  "How many people are currently registered?"


# Setup Instructions

# Clone the repository :

git clone https://github.com/codzzninja/Face_Recognition.git

cd Face_Recognition

# Frontend Setup

cd frontend

npm install

npm run dev

# Recognition Setup

cd backend/face_recognition

python recognize.py

# Registration Setup

cd backend/face_recognition

python register.py

# Q&A Setup

cd backend/rag_engine

python query.py

# Credits

This project is a part of a hackathon run by https://katomaran.com
