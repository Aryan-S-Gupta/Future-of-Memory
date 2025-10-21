"""Shared utility functions for the backend."""

import logging

from langchain_ollama import OllamaEmbeddings

from shared.constants import OLLAMA_EMBED_MODEL


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_ollama_embeddings() -> OllamaEmbeddings:
    """Initialises and returns the Ollama embeddings model."""
    logger.debug("Initialising Ollama embedding model...")
    embeddings: OllamaEmbeddings
    try:
        embeddings = OllamaEmbeddings(model=OLLAMA_EMBED_MODEL)
        logger.info("Ollama embeddings model initialised successfully.")
    except Exception as e:
        logger.critical(
            "Failed to initialise Ollama embeddings model. An exception occurred."
        )
        raise e
    return embeddings
