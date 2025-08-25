"""Constants used across the backend.
"""
import os

OLLAMA_MODEL = "phi3:mini"

# Directory containing RAG vector database files
DB_PATH = os.path.abspath(os.path.join("rag", "db", "faiss_db"))
