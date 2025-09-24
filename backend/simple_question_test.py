#!/usr/bin/env python3
"""
MemorySim Question Continuation Test Suite
Simple test for generating the next question in an existing session
"""

import os
import sys
import logging
import time
import random
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

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memory_sim.settings')
django.setup()

from shared.models import Session, Turn, Option
from shared.services import generate_and_save_question

def main():
    """Generate next question for the latest session"""
    start_time = time.time()
    
    print("MemorySim Question Continuation Test")
    print("=" * 50)
    print()
    
    try:
        # Step 1: Find latest session
        step_start = time.time()
        print("Step 1: Finding latest session...")
        
        latest_session = Session.objects.order_by('-id').first()
        if not latest_session:
            print("[ERROR] No sessions found!")
            return False
        
        step_duration = time.time() - step_start
        print(f"[SUCCESS] Found session: {latest_session.id} ({step_duration:.2f}s)")
        
        # Step 2: Find latest turn in this session
        step_start = time.time()
        print("Step 2: Finding latest turn...")
        
        latest_turn = Turn.objects.filter(session=latest_session).order_by('-year').first()
        if not latest_turn:
            print("[ERROR] No turns found in session!")
            return False
        
        print(f"[SUCCESS] Latest turn: {latest_turn.id} (Year: {latest_turn.year})")
        
        # Check if user choice exists
        if latest_turn.user_choice:
            print(f"   Has user choice: Option {latest_turn.user_choice.label}")
        else:
            print("   No user choice - will set random choice")
            # Set random choice
            options = Option.objects.filter(turn=latest_turn)
            if options.count() >= 2:
                chosen_option = random.choice(list(options))
                latest_turn.user_choice = chosen_option
                latest_turn.save()
                print(f"   Set random choice: Option {chosen_option.label}")
            else:
                print("[ERROR] Turn has no options!")
                return False
        
        step_duration = time.time() - step_start
        print(f"   Turn analysis completed ({step_duration:.2f}s)")
        print()
        
        # Step 3: Generate next year's question
        step_start = time.time()
        next_year = latest_turn.year + 1
        
        # Check if next year already exists
        if Turn.objects.filter(session=latest_session, year=next_year).exists():
            print(f"[INFO] Year {next_year} already exists in this session")
            print("[RESULT] Session is already up to date")
            return True
        
        print(f"Step 3: Generating question for year {next_year}...")
        print(f"   Previous year: {latest_turn.year}")
        print(f"   Based on choice: Option {latest_turn.user_choice.label}")
        print()
        
        # Generate the question
        result = generate_and_save_question(latest_session.id, next_year)
        
        step_duration = time.time() - step_start
        print(f"[SUCCESS] Question generated! ({step_duration:.2f}s)")
        print(f"   New Turn ID: {result['turn_id']}")
        print(f"   Year: {result['year']}")
        print()
        print("Generated Question:")
        print(f"   {result['question']}")
        print()
        print("Generated Options:")
        for option in result['options']:
            print(f"   {option['label']}: {option['text']}")
        print()
        
        # Step 4: Summary
        total_duration = time.time() - start_time
        print("=== SUMMARY ===")
        print(f"[SUCCESS] Question continuation completed!")
        print(f"   Session: {latest_session.id}")
        print(f"   Previous Turn: {latest_turn.id} (Year {latest_turn.year})")
        print(f"   New Turn: {result['turn_id']} (Year {result['year']})")
        print(f"   Total time: {total_duration:.2f}s")
        
        return True
        
    except Exception as e:
        total_duration = time.time() - start_time
        print(f"\n[ERROR] Test failed: {e}")
        print(f"   Total execution time: {total_duration:.2f}s")
        
        import traceback
        print("\nDetailed traceback:")
        traceback.print_exc()
        
        return False

def show_session_status():
    """Show current session status"""
    print("\n" + "=" * 50)
    print("CURRENT SESSION STATUS")
    print("=" * 50)
    
    try:
        sessions = Session.objects.order_by('-id')[:3]  # Show last 3 sessions
        
        for session in sessions:
            turns = Turn.objects.filter(session=session).order_by('year')
            print(f"\nSession {session.id}:")
            
            if not turns.exists():
                print("   No turns")
                continue
            
            print(f"   Years: {turns.first().year} - {turns.last().year} ({turns.count()} turns)")
            
            for turn in turns:
                choice_info = f"Choice: {turn.user_choice.label}" if turn.user_choice else "No choice"
                option_count = Option.objects.filter(turn=turn).count()
                print(f"   • Year {turn.year}: {option_count} options, {choice_info}")
        
    except Exception as e:
        print(f"[ERROR] Failed to show session status: {e}")

if __name__ == "__main__":
    overall_start_time = time.time()
    
    # Show current status first
    show_session_status()
    
    # Run main test
    success = main()
    
    # Final summary
    overall_duration = time.time() - overall_start_time
    print("\n" + "=" * 50)
    print("FINAL RESULT")
    print("=" * 50)
    print(f"Test result: {'PASSED' if success else 'FAILED'}")
    print(f"Total execution time: {overall_duration:.2f}s")
    
    if success:
        print("\n✓ Question continuation system working correctly!")
    else:
        print("\n✗ Question continuation system needs debugging")
    
    sys.exit(0 if success else 1)
