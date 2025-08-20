"""Clean RAG input files and create vector DB
"""

import logging
import os

from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

from rag.data_cleaning.clean_xml import xml_to_txt

import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DOCUMENT_PATH = os.path.abspath(os.path.join("rag", "cleaned_data"))

DB_PATH = os.path.abspath(os.path.join("rag", "db", "faiss_db"))

def setup() -> None:
    
    xml_to_txt()
    logger.info("Set up txt source files")
    
    documents = load_documents()
    logger.info(f"Loaded {len(documents)} documents from {DOCUMENT_PATH}")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # chunk size (characters)
        chunk_overlap=200,  # chunk overlap (characters)
        add_start_index=True,  # track index in original document
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split documents into {len(chunks)} chunks.")
    
    logger.debug("Initialising Ollama embedding model...")
    embeddings: OllamaEmbeddings
    try:
        embeddings = OllamaEmbeddings(model="tinyllama")
        logger.info("Ollama embeddings model initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize Ollama embeddings model. An exception occurred.")
        raise e

    # Create FAISS vector store
    logger.debug("Creating FAISS vector store from document chunks...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    logger.info("FAISS vector store created successfully.")

    # Save and reload the vector store
    vectorstore.save_local(DB_PATH)
    logger.info(f"Vector store saved to {DB_PATH}.")
    logger.debug(f"Loading persisted vector store from {DB_PATH}...")
    persisted_vectorstore = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)

    # Create a retriever
    logger.debug("Creating retriever from persisted vector store...")
    retriever = persisted_vectorstore.as_retriever()
    
    query = "What is episodic memory?"
    logger.info(f"Searching for the query: '{query}'\n")

    retrieved_documents = retriever.invoke(query)

    # 5. Print the content of the retrieved document(s)
    if retrieved_documents:
        print(f"Found {len(retrieved_documents)} relevant documents:")
        for i, doc in enumerate(retrieved_documents):
            print(f"\n--- Retrieved Document {i+1} ---\n")
            print(f"Source: {doc.metadata.get('source', 'N/A')}, Page: {doc.metadata.get('page', 'N/A')}")
            print(doc.page_content)
            print(doc.metadata.get("abc", "No additional metadata found"))
    else:
        print("No relevant documents found for the query.")


def load_documents():
    loader = DirectoryLoader(DOCUMENT_PATH, glob="*.txt")
    documents = loader.load()
    for doc in documents:
        doc.metadata["abc"] = "abc"
    return documents

if __name__ == "__main__":
    setup()
