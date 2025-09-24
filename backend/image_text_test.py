#!/usr/bin/env python3
"""
MemorySim Image Text Generation Test Suite
Tests the generate_and_save_image_text function
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

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memory_sim.settings')
django.setup()

from shared.models import Session, Turn, Option
from shared.services import generate_and_save_image_text

def main():
    """Test image text generation for the latest turn"""
    start_time = time.time()
    
    print("MemorySim Image Text Generation Test")
    print("=" * 50)
    print()
    
    try:
        # Step 1: Find latest session and turn
        step_start = time.time()
        print("Step 1: Finding latest session and turn...")
        
        latest_session = Session.objects.order_by('-id').first()
        if not latest_session:
            print("[ERROR] No sessions found!")
            return False
        
        latest_turn = Turn.objects.filter(session=latest_session).order_by('-year').first()
        if not latest_turn:
            print("[ERROR] No turns found in session!")
            return False
        
        step_duration = time.time() - step_start
        print(f"[SUCCESS] Found session {latest_session.id}, turn {latest_turn.id} (Year: {latest_turn.year}) ({step_duration:.2f}s)")
        
        # Check current state
        options = Option.objects.filter(turn=latest_turn).order_by('label')
        print(f"   Turn has {options.count()} options")
        
        for option in options:
            has_image_text = bool(option.image_text and option.image_text.strip())
            print(f"   Option {option.label}: {'Has image text' if has_image_text else 'No image text'}")
            if has_image_text:
                print(f"      Current: {option.image_text[:60]}...")
        print()
        
        # Step 2: Generate image texts
        step_start = time.time()
        print(f"Step 2: Generating image texts for turn {latest_turn.id} (Year {latest_turn.year})...")
        print(f"   Question: {latest_turn.question[:80]}...")
        print()
        
        result = generate_and_save_image_text(
            session_id=latest_session.id,
            turn_id=latest_turn.id,
            year=latest_turn.year
        )
        
        step_duration = time.time() - step_start
        print(f"[SUCCESS] Image texts generated! ({step_duration:.2f}s)")
        print(f"   Turn ID: {result['turn_id']}")
        print(f"   Session ID: {result['session_id']}")
        print(f"   Year: {result['year']}")
        print()
        
        # Step 3: Display generated image texts
        print("Generated Image Texts:")
        for image_text_info in result['image_texts']:
            print(f"   Option {image_text_info['label']}:")
            print(f"      {image_text_info['image_text']}")
            print()
        
        # Step 4: Verify database updates
        print("Step 3: Verifying database updates...")
        updated_options = Option.objects.filter(turn_id=latest_turn.id).order_by('label')
        
        all_image_texts_saved = True
        
        for option in updated_options:
            has_image_text = bool(option.image_text and option.image_text.strip())
            
            print(f"   Option {option.label}:")
            print(f"     Has image_text: {'PASS' if has_image_text else 'FAIL'} ({len(option.image_text) if option.image_text else 0} chars)")
            
            if not has_image_text:
                all_image_texts_saved = False
        
        print()
        
        # Step 5: Summary
        total_duration = time.time() - start_time
        print("=== SUMMARY ===")
        print(f"[SUCCESS] Image text generation completed!")
        print(f"   Session: {latest_session.id}")
        print(f"   Turn: {latest_turn.id} (Year {latest_turn.year})")
        print(f"   All image texts saved: {'YES' if all_image_texts_saved else 'NO'}")
        print(f"   Total time: {total_duration:.2f}s")
        
        return all_image_texts_saved
        
    except Exception as e:
        total_duration = time.time() - start_time
        print(f"\n[ERROR] Test failed: {e}")
        print(f"   Total execution time: {total_duration:.2f}s")
        
        import traceback
        print("\nDetailed traceback:")
        traceback.print_exc()
        
        return False

def show_current_state():
    """Show current state of sessions and turns"""
    print("\n" + "=" * 50)
    print("CURRENT DATABASE STATE")
    print("=" * 50)
    
    try:
        sessions = Session.objects.order_by('-id')[:2]  # Show last 2 sessions
        
        for session in sessions:
            turns = Turn.objects.filter(session=session).order_by('-year')
            print(f"\nSession {session.id}:")
            
            if not turns.exists():
                print("   No turns")
                continue
            
            for turn in turns:
                options = Option.objects.filter(turn=turn).order_by('label')
                image_text_count = options.filter(
                    image_text__isnull=False
                ).exclude(image_text__exact='').count()
                
                print(f"   Turn {turn.id} (Year {turn.year}):")
                print(f"      Question: {turn.question[:60]}...")
                print(f"      Options: {options.count()}, Image texts: {image_text_count}")
                
                for option in options:
                    has_image = bool(option.image_text and option.image_text.strip())
                    status = "✓" if has_image else "○"
                    print(f"         {status} Option {option.label}: {option.option_text[:40]}...")
                    if has_image:
                        print(f"           Image: {option.image_text[:50]}...")
        
    except Exception as e:
        print(f"[ERROR] Failed to show current state: {e}")

if __name__ == "__main__":
    overall_start_time = time.time()
    
    # Show current state first
    show_current_state()
    
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
        print("\n✓ Image text generation system working correctly!")
    else:
        print("\n✗ Image text generation system needs debugging")
    
    sys.exit(0 if success else 1)
