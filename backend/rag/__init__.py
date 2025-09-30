"""Package for setup and management of the RAG system which is used in-game to assist in storyline
and event generation."""

import logging

from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from shared.constants import VECTOR_DB_PATH
from langchain_core.vectorstores.base import VectorStoreRetriever

from shared.utils import get_ollama_embeddings
from rag.setup import setup_rag_system


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Number of chunks to retrieve per query
NUM_CHUNKS_PER_QUERY = 6

# Retriever for the RAG vector store
retriever: VectorStoreRetriever | None = None

setup_rag_system()
embeddings = get_ollama_embeddings()

# List of source, link, link_text for the documents that were retrieved in the last query
last_retrieved_files: dict[str, dict[str, str]] = {}

logger.debug(f"Loading vector store from {VECTOR_DB_PATH}...")
persisted_vectorstore = FAISS.load_local(
    VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True
)

# Create a retriever
logger.debug("Creating retriever from vector store...")
retriever = persisted_vectorstore.as_retriever(
    search_kwargs={"k": NUM_CHUNKS_PER_QUERY}
)  # Retrieve top N documents
