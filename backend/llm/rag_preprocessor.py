"""
RAG Content Preprocessor Module

This module provides functionality to preprocess RAG (Retrieval-Augmented Generation) 
content before feeding it to the main LLM generation pipeline. The preprocessor 
summarizes and extracts key information to improve generation quality and speed.
"""

import requests
import logging
from typing import Optional

# Handle imports for both relative (Django) and absolute (standalone) usage
try:
    from ..shared.constants import OLLAMA_PREPROCESS_MODEL
except ImportError:
    from shared.constants import OLLAMA_PREPROCESS_MODEL

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_PREPROCESS_MODEL = OLLAMA_PREPROCESS_MODEL

logger = logging.getLogger(__name__)


def create_preprocessing_prompt(content: str) -> str:
    """
    Create preprocessing prompt for RAG content summarization
    
    Args:
        content: The content to be preprocessed
        
    Returns:
        str: The preprocessing prompt
    """
    return f"""
You are a research assistant that extracts key information from scientific literature about memory technology and ethics.

Your task: Analyze the following research content and create a concise summary that preserves the most important facts, findings, and ethical considerations.

CRITICAL REQUIREMENTS:
- STRICT WORD LIMIT: Output must be EXACTLY 50 words or fewer
- COUNT YOUR WORDS: Ensure final output does not exceed 50 words
- MANDATORY: If your summary approaches 50 words, stop immediately
- Focus on: research findings, technological capabilities, ethical implications, policy considerations
- Preserve specific numbers, dates, and technical details when relevant
- Use bullet points for clarity
- Remove redundant information and general background

RESEARCH CONTENT:
{content}

OUTPUT FORMAT:
Return a clear, structured summary that preserves essential information for story generation about memory technology futures.

FINAL CHECK: Before submitting, count your words. Your response must be 50 words or fewer.
""".strip()


def call_preprocess_model(prompt: str, timeout: int = 45) -> Optional[str]:
    """
    Call the preprocessing model via Ollama API
    
    Args:
        prompt: The preprocessing prompt
        timeout: Timeout duration in seconds
        
    Returns:
        Optional[str]: Preprocessing result as plain text, None if failed
    """
    try:
        payload = {
            "model": DEFAULT_PREPROCESS_MODEL,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        result = data.get("response", "").strip()
        
        # Validate result quality - check word count, not character count
        word_count = len(result.split())
        if word_count >= 10:  # Ensure substantial content (minimum 10 words)
            return result
        else:
            logger.warning(f"Preprocessor returned short result: {word_count} words")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("Preprocessing timeout - Ollama API took too long to respond")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Preprocessing network error: {e}")
        return None
    except Exception as e:
        logger.error(f"Preprocessing unexpected error: {e}")
        return None


def preprocess_rag_content(content: str) -> str:
    """
    Preprocess RAG content by extracting key information and summarizing
    Only processes content when word count exceeds 50 words
    
    Args:
        content: The RAG content string to be preprocessed
        
    Returns:
        str: The preprocessed content
    """
    # Check input
    if not content or not content.strip():
        logger.debug("Empty content, returning as-is")
        return content
    
    # Check word count, only preprocess if greater than 50 words
    word_count = len(content.split())
    if word_count <= 50:
        logger.debug(f"Content already short ({word_count} words), skipping preprocessing")
        return content
    
    logger.info(f"Starting preprocessing: {word_count} words → target 50 words")
    
    # Create preprocessing prompt
    prompt = create_preprocessing_prompt(content)
    
    # Call preprocessing model
    processed_content = call_preprocess_model(prompt)
    
    if processed_content:
        processed_words = len(processed_content.split())
        logger.info(f"Preprocessing successful: {word_count} → {processed_words} words")
        return processed_content
    else:
        # Preprocessing failed, return original content
        logger.warning("Preprocessing failed, returning original content")
        return content


def preprocess_rag_chunks(rag_chunks: list[dict]) -> str:
    """
    Preprocess RAG chunks and format them for LLM input
    First format and combine all chunks, then preprocess the entire content for compression
    
    Args:
        rag_chunks: List of RAG retrieved chunks
        
    Returns:
        str: Formatted and preprocessed context string
    """
    if not rag_chunks:
        return ""
    
    # Step 1: Format all chunks following original format_rag_context_for_llm logic
    formatted_chunks = []
    for i, chunk in enumerate(rag_chunks, 1):
        meta = chunk.get("meta", {})
        title = meta.get("title") or meta.get("article_title", "Unknown Source")
        text = chunk.get("text", "")
        formatted_chunks.append(f"[{i}] {title}: {text}")
    
    # Step 2: Combine all chunks into a single string
    combined_content = "\n\n".join(formatted_chunks)
    
    # Step 3: Preprocess the entire content for compression (only if word count > 50)
    processed_content = preprocess_rag_content(combined_content)
    return processed_content

