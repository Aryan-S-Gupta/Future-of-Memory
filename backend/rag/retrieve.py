"""Retrieval logic for the RAG system."""

import logging

from rag.__init__ import retriever
from rag.utils.utils import vector_db_exists
import rag.__init__ as rag_init


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retrieve_chunks(query: str) -> list[dict]:
    """Retrieve relevant chunks from the vector store based on the query.

    Each chunk is a dictionary containing a 'text' attribute for document text and a 'meta'
    attribute for document metadata."""

    if not vector_db_exists():
        raise Exception(
            "Tried to retrieve chunks from the vector store but the RAG system was not set up. Set "
            "UPDATE_RAG to True in rag.config when running the backend to set up the RAG "
            "system."
        )
    else:
        logger.info(f"Searching for the query in the vector store: '{query}'\n")
        assert retriever is not None
        retrieved_documents = retriever.invoke(query)
        rag_init.last_retrieved_files = [{"source": doc.metadata["source"], "link": doc.metadata["link"], "link_text": doc.metadata["link_text"]} for doc in retrieved_documents]
        return [
            {
                "text": doc.page_content,
                "meta": doc.metadata,
                "metadata": doc.metadata,  # both 'meta' and 'metadata' included for backward compatibility
                "id": doc.id,
            }
            for doc in retrieved_documents
        ]
