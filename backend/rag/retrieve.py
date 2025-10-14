"""Retrieval logic for the RAG system."""

import logging

from rag.__init__ import retriever
from rag.utils.utils import vector_db_exists
import rag.__init__ as rag_init


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def retrieve_chunks(query: str) -> list[dict]:
    """
    Retrieve relevant chunks from the vector store based on the query.
    
    Return format:
    [
        {
            "text": "<chunk text>",
            "meta": {
                "source": "<document filename>",
                "title": "<original doucment title>",
                "licence": "<licensing information>",
                "authors": [
                    "<author name>",
                    ...
                ],
                "link_text": "<text to display in a link to the original document e.g. Cambridge
                Core article>",
                "link": "<link to original document>",
                "start_index": <int, location of this chunk in original document>
            },
            "metadata": <same as "meta">,
            "id": "<chunk id>",
        },
        ...
    ]
    """

    if not vector_db_exists():
        raise Exception(
            "Tried to retrieve chunks from the vector store but the RAG system was not set up. Set "
            "UPDATE_RAG to True in rag.config when running the backend to set up the RAG "
            "system."
        )

    logger.info(f"Searching for the query in the vector store: '{query}'\n")
    assert retriever is not None
    retrieved_documents = retriever.invoke(query)
    rag_init.last_retrieved_files = {doc.metadata["source"]: {"link": doc.metadata["link"], "link_text": doc.metadata["link_text"]} for doc in retrieved_documents}
    return [
        {
            "text": doc.page_content,
            "meta": doc.metadata,
            "metadata": doc.metadata,  # both 'meta' and 'metadata' included for backward compatibility
            "id": doc.id,
        }
        for doc in retrieved_documents
    ]
