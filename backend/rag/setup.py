"""Clean RAG input files and create vector DB"""

import logging
import os
from pathlib import Path
import json

from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from rag.data_cleaning.clean_xml import xml_to_txt
from shared.utils import get_ollama_embeddings
from shared.constants import VECTOR_DB_PATH
from rag.config import UPDATE_RAG, LATEST_VERSION
from rag.utils.utils import vector_db_exists


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DOCUMENT_PATH = os.path.abspath(os.path.join("rag", "cleaned_data"))


def load_documents() -> list[Document]:
    """Load and return documents from the specified directory."""

    loader = DirectoryLoader(DOCUMENT_PATH, glob="*.txt")
    documents = loader.load()

    # Update metadata to only include the base filename, not the full path
    for doc in documents:
        doc.metadata["source"] = os.path.basename(doc.metadata["source"])

    return documents


def create_vector_score(documents: list[Document]) -> None:
    """Create the vector store from given documents and save to DB_PATH. Do not call if
    DB already exists, it takes a long time.
    """

    logger.info(f"Loaded {len(documents)} documents from {DOCUMENT_PATH}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # chunk size (characters)
        chunk_overlap=200,  # chunk overlap (characters)
        add_start_index=True,  # track index in original document
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split documents into {len(chunks)} chunks.")

    embeddings = get_ollama_embeddings()

    # Create FAISS vector store
    logger.info("Creating FAISS vector store from document chunks...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    logger.info("FAISS vector store created successfully.")

    # Save the vector store
    vectorstore.save_local(VECTOR_DB_PATH)
    logger.info(f"Vector store saved to {VECTOR_DB_PATH}")


def setup_rag_system() -> None:
    """If UPDATE_RAG is True, update the RAG system if it is outdated. This involves:
    - cleaning texual data
    - writing PMC document metadata to JSON
    - creating the vector DB
    """

    if UPDATE_RAG:

        # Decide if update is required
        current_version: int | None = None
        current_version_filepath = Path(VECTOR_DB_PATH, "current_version.txt")
        if current_version_filepath.exists():
            with open(current_version_filepath, "r", encoding="utf-8") as file:
                current_version = int(file.read().strip())

        # Update if required
        if current_version is None or current_version < LATEST_VERSION:
            logger.info("Current RAG system is outdated. Updating RAG system...")
            pmc_file_metadata = xml_to_txt()
            logger.info("Created PMC txt source files.")
            documents = load_documents()
            other_metadata: dict
            with open(
                Path("rag", "cleaned_data", "metadata", "other_metadata.json"),
                "r",
                encoding="utf-8",
            ) as file:
                other_metadata = json.load(file)
            for doc in documents:
                source_filename = doc.metadata["source"]
                if source_filename in pmc_file_metadata:
                    doc.metadata.update(pmc_file_metadata[source_filename])
                elif source_filename in other_metadata:
                    doc.metadata.update(other_metadata[source_filename])
                else:
                    raise Exception(f"Metadata not found for file: {source_filename}")
            logger.info("Loaded documents.")
            create_vector_score(documents)
            with open(current_version_filepath, "w", encoding="utf-8") as file:
                file.write(str(LATEST_VERSION))

        else:
            logger.info(
                "Vector DB already exists and is up-to-date. Skipping RAG setup."
            )

    else:

        # Not updating, check if vector database already exists
        if not vector_db_exists():
            logger.warning(
                "Vector database not found, this may lead to errors. Run the backend with "
                "UPDATE_RAG in backend/rag/config.py set to True to set up the vector database."
            )
        else:
            logger.warning(
                "Vector database already exists but has not been updated, and so may be outdated. "
                "Run the backend with UPDATE_RAG in backend/rag/config.py set to True to set up "
                "the vector database."
            )
