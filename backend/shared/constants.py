"""Constants used across the backend.
"""
import os

OLLAMA_LLM_MODEL   = "phi3:3.8b"         # for story generation
OLLAMA_EMBED_MODEL = "nomic-embed-text"   # for text embedding

# Directory containing RAG vector database files
VECTOR_DB_PATH = os.path.abspath(os.path.join("rag", "db", "faiss_db"))
