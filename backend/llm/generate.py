"""
LLM Generation Module for MemorySim

This module provides functions to generate questions and descriptions using Ollama API
for the MemorySim narrative game. It handles JSON validation, retries, and error handling.
"""

import requests
import json
import re
from typing import Dict, Any, Optional
from prompt_templates import build_question_prompt, build_description_prompt

# Configuration constants
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:3.8b"


# ---------- Shared helpers ----------

def extract_json_block(text: str) -> str:
    """
    Extract JSON from text that may contain markdown code blocks.
    
    Handles cases like:
    1) Pure JSON
    2) ```json ... ```
    3) ``` ... ```
    
    Args:
        text: Raw text that may contain JSON
        
    Returns:
        str: Cleaned JSON string
    """
    # First match ```json ... ```
    m = re.search(r"```json\s*(\{.*\})\s*```", text, flags=re.S)
    if m:
        return m.group(1).strip()
    
    # Second match ``` ... ```
    m = re.search(r"```\s*(\{.*\})\s*```", text, flags=re.S)
    if m:
        return m.group(1).strip()
    
    # Otherwise, return the original text
    return text.strip()


def call_ollama(prompt: str) -> dict:
    """
    Call the Ollama API with the given prompt and return parsed JSON response.
    
    Args:
        prompt: The prompt to send to the model
        
    Returns:
        dict: Parsed JSON response from the model
        
    Raises:
        requests.RequestException: If the API call fails
        json.JSONDecodeError: If the response is not valid JSON
    """
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False, "format": "json"},
        timeout=60
    )
    response.raise_for_status()
    
    data = response.json()  # Ollama's response wrapper
    text = data.get("response", "").strip()  # Extract model output
    text = extract_json_block(text)  # Remove possible code blocks
    
    return json.loads(text)  # Convert to Python dict


def call_ollama_streaming(prompt: str) -> dict:
    """
    Call the Ollama API with streaming and return parsed JSON response.
    Used for description generation which may take longer.
    
    Args:
        prompt: The prompt to send to the model
        
    Returns:
        dict: Parsed JSON response from the model
        
    Raises:
        requests.RequestException: If the API call fails
        json.JSONDecodeError: If the response is not valid JSON
    """
    payload = {"model": MODEL, "prompt": prompt}
    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    response.raise_for_status()
    
    collected_output = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            collected_output += data.get("response", "")
    
    text = extract_json_block(collected_output)
    return json.loads(text)

# ---------- Light validators ----------

def validate_question_options(result: dict) -> bool:
    """
    Validate that question result has exactly two valid options.
    
    Args:
        result: The question generation result to validate
        
    Returns:
        bool: True if options are valid, False otherwise
    """
    # Check if options key exists and is a list
    if "options" not in result or not isinstance(result["options"], list):
        return False
    
    options = result.get("options", [])
    
    # Must be exactly 2 options
    if len(options) != 2:
        return False
    
    # Each option must be a string with 6-14 words
    for opt in options:
        if not isinstance(opt, str) or not (6 <= len(opt.split()) <= 14):
            return False
    
    return True


def validate_description_scenario(result: dict) -> bool:
    """
    Validate that description result has exactly 5 scenario sentences.
    
    Args:
        result: The description generation result to validate
        
    Returns:
        bool: True if scenario is valid, False otherwise
    """
    scenario = result.get("scenario", [])
    
    if not isinstance(scenario, list):
        return False
    
    if len(scenario) != 5:
        return False
    
    return True


def refine_question_options(original_result: dict) -> dict:
    """
    Attempt to fix invalid options by regenerating only the options array.
    
    Args:
        original_result: The original question result with invalid options
        
    Returns:
        dict: Updated result with refined options
    """
    question = original_result.get("question", "")
    fix_prompt = f"""
    Return ONLY valid JSON.

    You previously produced a question but did not provide exactly two valid options.
    Rewrite ONLY the "options" array with EXACTLY TWO concise, mutually exclusive choices (6–14 words each).
    and do NOT repeat the question text.

    Question: {question}

    Output schema:
    {{
        "options": [
            "Option 1",
            "Option 2"
        ]
    }}
    """.strip()

    try:
        refined_result = call_ollama(fix_prompt)
        if validate_question_options(refined_result):
            original_result["options"] = refined_result["options"]
    except Exception as e:
        print(f"Failed to refine options: {e}")
    
    return original_result

# ---------- Public API ----------

def generate_question(
    *,
    year: int,
    background: str,
    context_block: str,
    last_description: str,
    state_json: Optional[str] = None,
    max_retries: int = 3,
) -> Dict[str, Any]:
    """
    Generate a question with two options using the Ollama API.
    
    This function creates a decision point in the narrative by generating a question
    with exactly two mutually exclusive options that advance the story.
    
    Args:
        year: The current year in the story timeline
        background: The overall story background/setting
        context_block: Retrieved context information for grounding
        last_description: Previous story summary/description
        state_json: Optional JSON state for maintaining story continuity
        max_retries: Maximum number of retry attempts for validation
        
    Returns:
        Dict[str, Any]: Question result with keys:
            - query_text: RAG query for retrieving relevant information
            - keywords: List of keywords for search
            - question: The generated question
            - options: List of exactly two option strings
            
    Raises:
        Exception: If generation fails after all retries
    """
    prompt = build_question_prompt(
        year, background, context_block, last_description, state_json
    )
    
    # Step A: Main generation attempt
    try:
        result = call_ollama(prompt)
        if validate_question_options(result):
            return result
    except Exception as e:
        print(f"Initial question generation failed: {e}")
    
    # Step B: Try to refine options if main generation had invalid options
    if 'result' in locals():
        result = refine_question_options(result)
        if validate_question_options(result):
            return result
    
    # Step C: Retry main generation
    for attempt in range(max_retries):
        try:
            result = call_ollama(prompt)
            if validate_question_options(result):
                return result
        except Exception as e:
            print(f"Retry attempt {attempt + 1} failed: {e}")
    
    # Step D: Fallback with default options
    if 'result' in locals():
        result["options"] = [
            "Take an action that advances the situation forward",
            "Hold back and reconsider before making a move"
        ]
        return result
    
    # Ultimate fallback
    return {
        "query_text": "memory editing ethical considerations",
        "keywords": ["memory", "ethics", "policy"],
        "question": "How should society proceed with memory editing technology?",
        "options": [
            "Take an action that advances the situation forward",
            "Hold back and reconsider before making a move"
        ]
    }


def generate_description(
    *,
    year: int,
    background: str,
    context_block: str,
    last_description: str,
    current_question: str,
    selected_option: str,
    state_json: Optional[str] = None,
    max_retries: int = 3,
) -> Dict[str, Any]:
    """
    Generate a story description based on the selected option.
    
    This function creates the next part of the narrative by incorporating the
    player's choice and generating a vivid scenario with accompanying metadata.
    
    Args:
        year: The current year in the story timeline
        background: The overall story background/setting
        context_block: Retrieved context information for grounding
        last_description: Previous story summary/description
        current_question: The question that was presented to the player
        selected_option: The option chosen by the player
        state_json: Optional JSON state for maintaining story continuity
        max_retries: Maximum number of retry attempts for validation
        
    Returns:
        Dict[str, Any]: Description result with keys:
            - scenario: List of exactly 5 scenario sentences
            - image_brief: Brief description for image generation
            - rag_query: Object with query_text and keywords for next turn
            
    Raises:
        Exception: If generation fails after all retries
    """
    prompt = build_description_prompt(
        year, background, context_block, last_description,
        current_question, selected_option, state_json
    )
    
    # Attempt generation with retries
    for attempt in range(max_retries):
        try:
            result = call_ollama_streaming(prompt)
            
            if validate_description_scenario(result):
                return result
            else:
                print(f"Attempt {attempt + 1}: Scenario validation failed, retrying...")
                
        except Exception as e:
            print(f"Attempt {attempt + 1}: Generation failed - {e}")
    
    # If all attempts fail, return a fallback result
    return {
        "scenario": [
            "The selected decision creates immediate ripple effects across institutions and communities.",
            "Stakeholders gather in meeting rooms and public spaces to discuss the implications of this choice.",
            "New policies and procedures begin to take shape based on the direction that was chosen.",
            "Citizens and experts alike watch closely as the consequences of this decision unfold in real time.",
            "The path forward remains uncertain, but the choice has been made and will shape future developments."
        ],
        "image_brief": "Meeting room with people discussing policy decisions",
        "rag_query": {
            "query_text": "policy implementation and social consequences of memory editing decisions",
            "keywords": ["policy", "implementation", "consequences", "society"]
        }
    }