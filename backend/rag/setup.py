"""Clean RAG input files and create vector DB"""

import logging
import os

from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from rag.data_cleaning.clean_xml import xml_to_txt
from shared.utils import get_ollama_embeddings
from shared.constants import DB_PATH


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
    logger.debug("Creating FAISS vector store from document chunks...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    logger.info("FAISS vector store created successfully.")

    # Save the vector store
    vectorstore.save_local(DB_PATH)
    logger.info(f"Vector store saved to {DB_PATH}")


def setup() -> None:
    """Set up the RAG system by
    1. cleaning data
    2. creating the vector DB (if it doesn't already exist)
    """

    index_files = ["index.faiss", "index.pkl"]
    if not all(os.path.exists(os.path.join(DB_PATH, f)) for f in index_files):
        logger.info("Vector DB not found, setting up RAG system...")
        pmc_file_metadata = xml_to_txt()
        logger.info("Created PMC txt source files")
        documents = load_documents()
        for doc in documents:
            # todo test that this works (metadata recoded in vector store)
            source_filename = doc.metadata["source"]
            doc.metadata.extend(pmc_file_metadata[source_filename])
        logger.info("Loaded documents")
        create_vector_score(documents)
    else:
        logger.info("Vector DB already exists, skipping RAG setup")
