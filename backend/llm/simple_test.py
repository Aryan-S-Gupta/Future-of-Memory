#!/usr/bin/env python3
"""
Simple test script for generate.py functions

This is a minimal test script that you can run directly in the llm directory.
Make sure Ollama is running before executing this script.

Usage:
    cd backend/llm
    python simple_test.py
"""

import sys
import os
import json

# Add current directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic functionality of both functions"""
    print("🧪 Testing MemorySim Generate Functions")
    print("=" * 50)
    
    try:
        # Import after path adjustment
        from generate import generate_question, generate_description
        print("✅ Successfully imported functions")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Make sure you're in the backend/llm directory")
        return False
    
    # Test data
    test_year = 2035
    test_background = "In 2035, global regulations begin piloting clinical memory editing as part of mental health research."
    test_context = "(1) consent processes require strict multi-factor verification; (2) research reports show both benefits and risks for identity stability."
    test_description = "Public debate has intensified as clinics prepare to enroll participants in early programs."
    
    # Test generate_question
    print("\n📝 Testing generate_question...")
    try:
        question_result = generate_question(
            year=test_year,
            background=test_background,
            context_block=test_context,
            last_description=test_description
        )
        
        print("✅ Question generation successful!")
        print(f"Question: {question_result.get('question', 'N/A')}")
        print(f"Options: {question_result.get('options', [])}")
        print(f"Query: {question_result.get('query_text', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Question generation failed: {e}")
        return False
    
    # Test generate_description
    print("\n📖 Testing generate_description...")
    try:
        description_result = generate_description(
            year=test_year,
            background=test_background,
            context_block=test_context,
            last_description=test_description,
            current_question=question_result.get('question', 'Test question?'),
            selected_option=question_result.get('options', ['Test option'])[0]
        )
        
        print("✅ Description generation successful!")
        print(f"Scenario sentences: {len(description_result.get('scenario', []))}")
        print(f"Image brief: {description_result.get('image_brief', 'N/A')}")
        
        # Print first scenario sentence as example
        scenario = description_result.get('scenario', [])
        if scenario:
            print(f"First sentence: {scenario[0]}")
        
    except Exception as e:
        print(f"❌ Description generation failed: {e}")
        return False
    
    print("\n🎉 All tests completed successfully!")
    return True

def check_ollama():
    """Quick check if Ollama is accessible"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("Checking Ollama connectivity...")
    if not check_ollama():
        print("⚠️  Warning: Cannot connect to Ollama at localhost:11434")
        print("Make sure Ollama is running: ollama serve")
        print("And phi3:3.8b model is available: ollama pull phi3:3.8b")
        print("\nProceeding with test anyway...\n")
    else:
        print("✅ Ollama is accessible\n")
    
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
