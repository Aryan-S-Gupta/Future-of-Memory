"""Package for setup and management of the RAG system which is used in-game to assist in storyline
and event generation."""

import logging

from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from shared.constants import VECTOR_DB_PATH
from langchain_core.vectorstores.base import VectorStoreRetriever

from shared.utils import get_ollama_embeddings
from rag.setup import setup_rag_system
from rag.config import SKIP_RAG_SETUP


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Number of chunks to retrieve per query
NUM_CHUNKS_PER_QUERY = 6

# Retriever for the RAG vector store
retriever: VectorStoreRetriever | None = None

if not SKIP_RAG_SETUP:

    setup_rag_system()
    embeddings = get_ollama_embeddings()

    logger.debug(f"Loading vector store from {VECTOR_DB_PATH}...")
    persisted_vectorstore = FAISS.load_local(
        VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True
    )

    # Create a retriever
    logger.debug("Creating retriever from vector store...")
    retriever = persisted_vectorstore.as_retriever(
        search_kwargs={"k": NUM_CHUNKS_PER_QUERY}
    )  # Retrieve top N documents
