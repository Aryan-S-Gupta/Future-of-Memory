"""Retrieval logic for the RAG system."""

import logging

from rag.__init__ import retriever


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def retrieve_chunks(query: str) -> list[dict]:
    """Retrieve relevant chunks from the vector store based on the query.

    Each chunk is a dictionary containing a 'text' attribute for document text and a 'meta'
    attribute for document metadata."""

    logger.info(f"Searching for the query in the vector store: '{query}'\n")

    retrieved_documents = retriever.invoke(query)

    return [
        {"text": doc.page_content, "meta": doc.metadata} for doc in retrieved_documents
    ]
