#!/usr/bin/env python3
"""
Test script for the generate.py module

This script tests both generate_question and generate_description functions
with various scenarios to ensure they work correctly.

Prerequisites:
1. Ollama should be running on localhost:11434
2. The phi3:3.8b model should be available
3. All dependencies should be installed

Usage:
    python test_generate.py
    python test_generate.py --question-only
    python test_generate.py --description-only
"""

import sys
import json
import argparse
from typing import Dict, Any

# Import the functions we want to test
try:
    from generate import generate_question, generate_description
    print("✅ Successfully imported generate functions")
except ImportError as e:
    print(f"❌ Failed to import generate functions: {e}")
    print("Make sure you're running this from the llm directory")
    sys.exit(1)


def print_separator(title: str):
    """Print a formatted separator for test sections"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_result(result: Dict[str, Any], title: str):
    """Pretty print a result dictionary"""
    print(f"\n📋 {title}:")
    print("-" * 40)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def test_generate_question():
    """Test the generate_question function with sample data"""
    print_separator("TESTING GENERATE_QUESTION")
    
    # Test case 1: Basic memory editing scenario
    print("\n🧪 Test Case 1: Basic Memory Editing Scenario")
    
    try:
        result = generate_question(
            year=2035,
            background="In 2035, global regulations begin piloting clinical memory editing as part of mental health research.",
            context_block="(1) consent processes require strict multi-factor verification; (2) research reports show both benefits and risks for identity stability.",
            last_description="Public debate has intensified as clinics prepare to enroll participants in early programs."
        )
        
        print("✅ Question generation succeeded!")
        print_result(result, "Question Result")
        
        # Validate the result structure
        required_keys = ["query_text", "keywords", "question", "options"]
        missing_keys = [key for key in required_keys if key not in result]
        if missing_keys:
            print(f"⚠️  Missing keys: {missing_keys}")
        else:
            print("✅ All required keys present")
        
        # Validate options
        options = result.get("options", [])
        if len(options) == 2:
            print("✅ Correct number of options (2)")
            for i, option in enumerate(options):
                word_count = len(option.split())
                if 6 <= word_count <= 14:
                    print(f"✅ Option {i+1} word count OK ({word_count} words)")
                else:
                    print(f"⚠️  Option {i+1} word count issue ({word_count} words, should be 6-14)")
        else:
            print(f"❌ Wrong number of options: {len(options)} (should be 2)")
            
    except Exception as e:
        print(f"❌ Question generation failed: {e}")
        return False
    
    # Test case 2: With state JSON
    print("\n🧪 Test Case 2: With State JSON")
    
    try:
        state_json = json.dumps({
            "previous_decisions": ["allow_trials"],
            "public_opinion": "mixed",
            "regulatory_status": "pilot_phase"
        })
        
        result = generate_question(
            year=2036,
            background="Memory editing trials have been running for a year with mixed results.",
            context_block="(1) 60% of participants report positive outcomes; (2) 15% experienced unexpected side effects; (3) regulatory bodies are reviewing preliminary data.",
            last_description="The first year of memory editing trials concludes with researchers analyzing complex data patterns.",
            state_json=state_json
        )
        
        print("✅ Question generation with state JSON succeeded!")
        print_result(result, "Question with State")
        
    except Exception as e:
        print(f"❌ Question generation with state failed: {e}")
        return False
    
    return True


def test_generate_description():
    """Test the generate_description function with sample data"""
    print_separator("TESTING GENERATE_DESCRIPTION")
    
    # Test case 1: Basic description generation
    print("\n🧪 Test Case 1: Basic Description Generation")
    
    try:
        result = generate_description(
            year=2035,
            background="In 2035, global regulations begin piloting clinical memory editing as part of mental health research.",
            context_block="(1) consent processes require strict multi-factor verification; (2) research reports show both benefits and risks for identity stability.",
            last_description="Public debate has intensified as clinics prepare to enroll participants in early programs.",
            current_question="Should the government allow memory editing for clinical trials?",
            selected_option="The government should allow memory editing for clinical trials with strict safeguards"
        )
        
        print("✅ Description generation succeeded!")
        print_result(result, "Description Result")
        
        # Validate the result structure
        required_keys = ["scenario", "image_brief", "rag_query"]
        missing_keys = [key for key in required_keys if key not in result]
        if missing_keys:
            print(f"⚠️  Missing keys: {missing_keys}")
        else:
            print("✅ All required keys present")
        
        # Validate scenario
        scenario = result.get("scenario", [])
        if len(scenario) == 5:
            print("✅ Correct number of scenario sentences (5)")
            for i, sentence in enumerate(scenario):
                word_count = len(sentence.split())
                if 15 <= word_count <= 30:
                    print(f"✅ Sentence {i+1} word count OK ({word_count} words)")
                else:
                    print(f"⚠️  Sentence {i+1} word count issue ({word_count} words, should be 15-30)")
        else:
            print(f"❌ Wrong number of scenario sentences: {len(scenario)} (should be 5)")
        
        # Validate image_brief length
        image_brief = result.get("image_brief", "")
        if len(image_brief) <= 70:
            print(f"✅ Image brief length OK ({len(image_brief)} chars)")
        else:
            print(f"⚠️  Image brief too long ({len(image_brief)} chars, should be ≤70)")
            
    except Exception as e:
        print(f"❌ Description generation failed: {e}")
        return False
    
    # Test case 2: With state JSON
    print("\n🧪 Test Case 2: With State JSON")
    
    try:
        state_json = json.dumps({
            "trial_status": "approved",
            "public_sentiment": "cautiously_optimistic",
            "enrolled_participants": 0
        })
        
        result = generate_description(
            year=2035,
            background="Memory editing clinical trials have been approved and are beginning enrollment.",
            context_block="(1) first clinic opens in major medical center; (2) strict eligibility criteria established; (3) international oversight committee formed.",
            last_description="Regulatory approval has been granted for the first memory editing clinical trials.",
            current_question="How should the first clinical trial be structured?",
            selected_option="Start with a small group of volunteer participants in a controlled environment",
            state_json=state_json
        )
        
        print("✅ Description generation with state JSON succeeded!")
        print_result(result, "Description with State")
        
    except Exception as e:
        print(f"❌ Description generation with state failed: {e}")
        return False
    
    return True


def test_ollama_connectivity():
    """Test if Ollama is running and accessible"""
    print_separator("TESTING OLLAMA CONNECTIVITY")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]
            print("✅ Ollama is running!")
            print(f"📋 Available models: {model_names}")
            
            if "phi3:3.8b" in model_names:
                print("✅ phi3:3.8b model is available!")
                return True
            else:
                print("⚠️  phi3:3.8b model not found. Available models:")
                for name in model_names:
                    print(f"   - {name}")
                print("\nTo install phi3:3.8b, run: ollama pull phi3:3.8b")
                return False
        else:
            print(f"❌ Ollama responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Is it running on localhost:11434?")
        print("To start Ollama, run: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False


def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description="Test the generate.py module")
    parser.add_argument("--question-only", action="store_true", 
                       help="Only test question generation")
    parser.add_argument("--description-only", action="store_true", 
                       help="Only test description generation")
    args = parser.parse_args()
    
    print("🧪 MemorySim Generate.py Test Suite")
    print("=" * 60)
    
    # Check Ollama connectivity first
    if not test_ollama_connectivity():
        print("\n❌ Cannot proceed without Ollama connectivity")
        return False
    
    success = True
    
    # Run tests based on arguments
    if not args.description_only:
        success &= test_generate_question()
    
    if not args.question_only:
        success &= test_generate_description()
    
    # Summary
    print_separator("TEST SUMMARY")
    if success:
        print("🎉 All tests passed successfully!")
        print("\n📝 Next steps:")
        print("   1. Integrate these functions into your Django views")
        print("   2. Add error handling for production use")
        print("   3. Consider adding unit tests with mocked responses")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
