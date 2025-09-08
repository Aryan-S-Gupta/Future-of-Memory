#!/usr/bin/env python3
"""Test complete integration between RAG and LLM systems"""

import sys
import os
import django

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memory_sim.settings')
django.setup()

from rag.retrieve import retrieve_chunks
from llm.generate import generate_question, generate_description
from llm.rag_adapter import get_rag_context, format_rag_context_for_llm


def test_rag_retrieval():
    """Test RAG document retrieval functionality"""
    print("=== Testing RAG Retrieval ===")
    query = "memory consolidation sleep"
    
    try:
        # Direct test of RAG retrieval
        chunks = retrieve_chunks(query)
        print(f"Retrieved {len(chunks)} document chunks")
        
        for i, chunk in enumerate(chunks):
            print(f"\n--- Chunk {i+1} ---")
            print(f"Title: {chunk.get('meta', {}).get('title', 'Unknown')}")
            print(f"Content preview: {chunk.get('text', '')[:200]}...")
            
        return chunks
    except Exception as e:
        print(f"RAG retrieval failed: {e}")
        return None


def test_rag_adapter():
    """Test RAG adapter functionality"""
    print("\n=== Testing RAG Adapter ===")
    
    # Test generate_question output
    try:
        question_result = generate_question(
            year=2024,
            background="A study about memory and sleep",
            context_block="Research context about sleep and memory",
            last_description="Previous research findings"
        )
        print(f"LLM generation result: {question_result}")
        
        # Use adapter to get RAG context
        rag_context = get_rag_context(question_result)
        print(f"RAG query text: {rag_context}")
        
        # Retrieve relevant documents
        chunks = retrieve_chunks(rag_context)
        formatted_context = format_rag_context_for_llm(chunks)
        print(f"Formatted RAG context:\n{formatted_context}")
        
        return True
    except Exception as e:
        print(f"RAG adapter test failed: {e}")
        return False


def test_full_integration():
    """Test complete RAG-LLM integration workflow"""
    print("\n=== Testing Full Integration Workflow ===")
    
    try:
        # 1. Generate question
        print("1. Generating question...")
        question_result = generate_question(
            year=2024,
            background="Memory research study about sleep and consolidation",
            context_block="Scientific research context",
            last_description="Initial research setup"
        )
        print(f"Generated question: {question_result}")
        
        # 2. Get RAG context
        print("\n2. Getting RAG context...")
        query_text = get_rag_context(question_result)
        chunks = retrieve_chunks(query_text)
        rag_context = format_rag_context_for_llm(chunks)
        print(f"RAG context length: {len(rag_context)} characters")
        
        # 3. Generate description based on RAG context
        print("\n3. Generating description...")
        description_result = generate_description(
            year=2024,
            background="Memory research study",
            context_block=rag_context,
            last_description="Previous findings",
            current_question="Should policy be influenced by the latest research findings?",
            selected_option="Implement new guidelines for post-sleep activities at clinics"
        )
        print(f"Generated description: {description_result}")
        
        print("\n✅ Full integration test successful!")
        return True
        
    except Exception as e:
        print(f"Full integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting RAG-LLM integration tests...\n")
    
    # Test RAG retrieval
    chunks = test_rag_retrieval()
    
    if chunks:
        # Test adapter
        adapter_ok = test_rag_adapter()
        
        if adapter_ok:
            # Test full workflow
            integration_ok = test_full_integration()
            
            if integration_ok:
                print("\n🎉 All tests passed! RAG-LLM integration working properly.")
            else:
                print("\n❌ Full integration test failed")
        else:
            print("\n❌ RAG adapter test failed")
    else:
        print("\n❌ RAG retrieval test failed")
