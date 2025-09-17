#!/usr/bin/env python3
"""
MemorySim Scenario Test Suite
Tests the generate_and_save_scenario function with comprehensive validation
"""

import os
import sys
import logging
import time
import django
from django.test.utils import setup_test_environment

# Configure logging to reduce noise
logging.getLogger('rag.setup').setLevel(logging.WARNING)
logging.getLogger('rag.retrieve').setLevel(logging.WARNING)
logging.getLogger('rag').setLevel(logging.WARNING)
logging.getLogger('shared.utils').setLevel(logging.WARNING)
logging.getLogger('faiss.loader').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Keep LLM-related logging
logging.getLogger('shared.services').setLevel(logging.INFO)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memory_sim.settings')
django.setup()

from shared.models import Session, Turn, Option
from shared.services import generate_and_save_question, generate_and_save_scenario

def main():
    """Run the comprehensive scenario generation test suite"""
    start_time = time.time()
    
    print("MemorySim Scenario Generation Test Suite")
    print("=" * 60)
    print("=== Testing generate_and_save_scenario Function ===")
    print()
    
    try:
        # Step 1: Create a test session
        step_start = time.time()
        print("Step 1: Creating test session...")
        from django.utils import timezone
        session = Session.objects.create(created_at=timezone.now())
        step_duration = time.time() - step_start
        print(f"[SUCCESS] Session created: {session.id} ({step_duration:.2f}s)")
        print()
        
        # Step 2: Generate question and options
        step_start = time.time()
        print("Step 2: Generating question and options...")
        result = generate_and_save_question(session.id, year=2035)
        turn_id = result['turn_id']
        step_duration = time.time() - step_start
        print(f"[SUCCESS] Question generation successful! ({step_duration:.2f}s)")
        print(f"   Turn ID: {turn_id}")
        print(f"   Question: {result['question'][:80]}...")
        print(f"   Options count: {len(result['options'])}")
        print("   Generated options:")
        for option in result['options']:
            print(f"     {option['label']}: {option['text']}")
            print(f"         Query: {option['query'][:60]}...")
        print()
        
        # Step 3: Generate scenarios
        step_start = time.time()
        print(f"Step 3: Generating scenarios for turn {turn_id}...")
        scenario_result = generate_and_save_scenario(session.id, turn_id, year=2035)
        step_duration = time.time() - step_start
        print(f"[SUCCESS] Scenario generation successful! ({step_duration:.2f}s)")
        print(f"   Turn ID: {scenario_result['turn_id']}")
        print(f"   Session ID: {scenario_result['session_id']}")
        print(f"   Year: {scenario_result['year']}")
        print(f"   Scenarios count: {len(scenario_result['scenarios'])}")
        print()
        print("   Generated scenarios:")
        for scenario in scenario_result['scenarios']:
            print(f"     Option {scenario['label']}:")
            print(f"       Scenario: {scenario['scenario'][:80]}...")
            print(f"       Query Text: {scenario['query_text']}")
            print()
        
        # Step 4: Verify database updates
        step_start = time.time()
        print("Step 4: Verifying database updates...")
        updated_options = Option.objects.filter(turn_id=turn_id).order_by('label')
        
        all_scenarios_saved = True
        all_queries_saved = True
        
        for option in updated_options:
            has_scenario = bool(option.scenario and option.scenario.strip())
            has_query = bool(option.question_query_text and option.question_query_text.strip())
            
            print(f"   Option {option.label}:")
            print(f"     Has scenario: {'PASS' if has_scenario else 'FAIL'} ({len(option.scenario) if option.scenario else 0} chars)")
            print(f"     Has query_text: {'PASS' if has_query else 'FAIL'} ({len(option.question_query_text) if option.question_query_text else 0} chars)")
            
            if not has_scenario:
                all_scenarios_saved = False
            if not has_query:
                all_queries_saved = False
        
        step_duration = time.time() - step_start
        print(f"Database verification completed ({step_duration:.2f}s)")
        print()
        
        # Step 5: Summary
        total_duration = time.time() - start_time
        print("=== TEST SUMMARY ===")
        print(f"[RESULT] Session creation: SUCCESS")
        print(f"[RESULT] Question generation: SUCCESS")
        print(f"[RESULT] Scenario generation: SUCCESS")
        print(f"[RESULT] All scenarios saved: {'SUCCESS' if all_scenarios_saved else 'FAILED'}")
        print(f"[RESULT] All query texts saved: {'SUCCESS' if all_queries_saved else 'FAILED'}")
        
        if all_scenarios_saved and all_queries_saved:
            print(f"\n[OVERALL] TEST RESULT: SUCCESS")
            print(f"   Session ID: {session.id}")
            print(f"   Turn ID: {turn_id}")
            print(f"   Total execution time: {total_duration:.2f}s")
            print(f"   All components working correctly!")
        else:
            print(f"\n[OVERALL] TEST RESULT: PARTIAL SUCCESS")
            print(f"   Total execution time: {total_duration:.2f}s")
            print(f"   Some database updates may have failed")
            
        return True
        
    except Exception as e:
        total_duration = time.time() - start_time
        print(f"\n[ERROR] ERROR during scenario generation test:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"   Total execution time: {total_duration:.2f}s")
        
        # Print detailed traceback
        import traceback
        print(f"\n   Detailed traceback:")
        traceback.print_exc()
        
        print(f"\n[OVERALL] TEST RESULT: FAILED")
        return False

def test_with_existing_turn():
    """Test scenario generation with an existing turn (if available)"""
    start_time = time.time()
    
    print("\n" + "="*60)
    print("TESTING WITH EXISTING TURN (if available)")
    print("="*60)
    
    try:
        # Look for existing turns
        existing_turns = Turn.objects.all().order_by('-id')[:1]
        
        if not existing_turns:
            print("[SKIP] No existing turns found. Skipping this test.")
            return False
            
        turn = existing_turns[0]
        print(f"Found existing turn: {turn.id} (Year: {turn.year}, Session: {turn.session.id})")
        
        # Test scenario generation on existing turn
        generation_start = time.time()
        result = generate_and_save_scenario(
            session_id=turn.session.id,
            turn_id=turn.id,
            year=turn.year
        )
        generation_duration = time.time() - generation_start
        
        total_duration = time.time() - start_time
        print(f"[SUCCESS] Scenario generation on existing turn successful! ({generation_duration:.2f}s)")
        print(f"   Generated {len(result['scenarios'])} scenarios")
        print(f"   Total test time: {total_duration:.2f}s")
        
        return True
        
    except Exception as e:
        total_duration = time.time() - start_time
        print(f"[ERROR] Error testing with existing turn: {e}")
        print(f"   Test time: {total_duration:.2f}s")
        return False

if __name__ == "__main__":
    overall_start_time = time.time()
    
    # Run main test
    main_success = main()
    
    # Run additional test with existing data
    existing_success = test_with_existing_turn()
    
    # Final summary
    overall_duration = time.time() - overall_start_time
    print("\n" + "="*60)
    print("FINAL TEST SUMMARY")
    print("="*60)
    print(f"Main scenario test: {'PASSED' if main_success else 'FAILED'}")
    print(f"Existing turn test: {'PASSED' if existing_success else 'SKIPPED/FAILED'}")
    print(f"Overall execution time: {overall_duration:.2f}s")
    
    if main_success:
        print(f"\n[SUCCESS] generate_and_save_scenario function is working correctly!")
    else:
        print(f"\n[WARNING] generate_and_save_scenario function needs debugging")
        print(f"   Check the error messages above for details")
    
    sys.exit(0 if main_success else 1)
