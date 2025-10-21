#!/usr/bin/env python3
"""
MemorySim Complete Turn Generation Test Suite
Tests the generate_complete_turn function with various scenarios
"""

import os
import sys
import logging
import time
import django
from django.test.utils import setup_test_environment

# Configure logging to reduce noise
logging.getLogger("rag.setup").setLevel(logging.WARNING)
logging.getLogger("rag.retrieve").setLevel(logging.WARNING)
logging.getLogger("rag").setLevel(logging.WARNING)
logging.getLogger("shared.utils").setLevel(logging.WARNING)
logging.getLogger("faiss.loader").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Keep LLM-related logging
logging.getLogger("shared.services").setLevel(logging.INFO)

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "memory_sim.settings")
django.setup()

from shared.models import Session, Turn, Option
from shared.services import generate_complete_turn


def test_new_session():
    """Test complete turn generation with new session"""
    print("Test 1: New Session Generation")
    print("-" * 40)

    start_time = time.time()

    try:
        # Call without session_id to create new session
        result = generate_complete_turn()

        duration = time.time() - start_time
        print(f"[SUCCESS] New session turn completed! ({duration:.2f}s)")
        print(f"   Session ID: {result['session_id']}")
        print(f"   Turn ID: {result['turn_id']}")
        print(f"   Year: {result['year']}")
        print(f"   Total duration: {result['total_duration']:.2f}s")
        print()

        # Verify all steps completed
        steps = result["generation_steps"]
        print("Generation Steps:")
        print(f"   ✓ Question: {steps['question']['question'][:60]}...")
        print(f"   ✓ Options: {len(steps['question']['options'])} generated")
        print(f"   ✓ Image Texts: {len(steps['image_texts']['image_texts'])} generated")
        print(f"   ✓ Scenarios: {len(steps['scenarios']['scenarios'])} generated")
        print()

        return result["session_id"], result["turn_id"]

    except Exception as e:
        print(f"[ERROR] New session test failed: {e}")
        return None, None


def test_existing_session(session_id):
    """Test complete turn generation with existing session"""
    print("Test 2: Existing Session Continuation")
    print("-" * 40)

    start_time = time.time()

    try:
        # Call with existing session_id to continue
        result = generate_complete_turn(session_id=session_id)

        duration = time.time() - start_time
        print(f"[SUCCESS] Existing session turn completed! ({duration:.2f}s)")
        print(f"   Session ID: {result['session_id']}")
        print(f"   Turn ID: {result['turn_id']}")
        print(f"   Year: {result['year']}")
        print(f"   Total duration: {result['total_duration']:.2f}s")
        print()

        # Verify all steps completed
        steps = result["generation_steps"]
        print("Generation Steps:")
        print(f"   ✓ Question: {steps['question']['question'][:60]}...")
        print(f"   ✓ Options: {len(steps['question']['options'])} generated")
        print(f"   ✓ Image Texts: {len(steps['image_texts']['image_texts'])} generated")
        print(f"   ✓ Scenarios: {len(steps['scenarios']['scenarios'])} generated")
        print()

        return True

    except Exception as e:
        print(f"[ERROR] Existing session test failed: {e}")
        return False


def test_year_limit():
    """Test year limit handling (>2085)"""
    print("Test 3: Year Limit Handling")
    print("-" * 40)

    start_time = time.time()

    try:
        # Call with year > 2085 to test limit handling
        result = generate_complete_turn(year=2090)

        duration = time.time() - start_time
        print(f"[SUCCESS] Year limit handling completed! ({duration:.2f}s)")
        print(f"   Requested year: 2090")
        print(f"   Actual year: {result['year']} (should be 2035)")
        print(f"   New session created: {result['session_id']}")
        print(f"   Total duration: {result['total_duration']:.2f}s")
        print()

        return result["year"] == 2035

    except Exception as e:
        print(f"[ERROR] Year limit test failed: {e}")
        return False


def show_database_state():
    """Show current database state"""
    print("\n" + "=" * 50)
    print("CURRENT DATABASE STATE")
    print("=" * 50)

    sessions = Session.objects.order_by("-id")[:3]

    for session in sessions:
        turns = Turn.objects.filter(session=session).order_by("year")
        print(f"\nSession {session.id}:")

        if not turns.exists():
            print("   No turns")
            continue

        for turn in turns:
            options = Option.objects.filter(turn=turn).order_by("label")

            # Check completion status
            has_question = bool(turn.question)
            has_image_texts = all(opt.image_text for opt in options)
            has_scenarios = all(opt.scenario for opt in options)

            status_marks = []
            status_marks.append("Q" if has_question else "○")
            status_marks.append("I" if has_image_texts else "○")
            status_marks.append("S" if has_scenarios else "○")
            status = "[" + "/".join(status_marks) + "]"

            print(f"   Turn {turn.id} (Year {turn.year}) {status}:")
            print(
                f"      Question: {turn.question[:50] if turn.question else 'None'}..."
            )

            for option in options:
                completeness = []
                if option.image_text:
                    completeness.append("I")
                if option.scenario:
                    completeness.append("S")
                comp_str = (
                    "(" + "/".join(completeness) + ")" if completeness else "(empty)"
                )
                print(
                    f"         {option.label}: {option.option_text[:30]}... {comp_str}"
                )


def main():
    """Run all tests"""
    overall_start = time.time()

    print("MemorySim Complete Turn Generation Test Suite")
    print("=" * 60)

    # Show initial state
    show_database_state()
    print()

    # Test 1: New session
    session_id, turn_id = test_new_session()

    # Test 2: Existing session (if Test 1 succeeded)
    if session_id:
        # Set a random user choice to enable continuation
        try:
            turn = Turn.objects.get(id=turn_id)
            options = Option.objects.filter(turn=turn)
            if options.count() >= 2:
                import random

                chosen_option = random.choice(list(options))
                turn.user_choice = chosen_option
                turn.save()
                print(
                    f"Set user choice: Option {chosen_option.label} for continuation test\n"
                )

            existing_success = test_existing_session(session_id)
        except Exception as e:
            print(f"[ERROR] Failed to set up continuation test: {e}")
            existing_success = False
    else:
        existing_success = False

    # Test 3: Year limit
    year_limit_success = test_year_limit()

    # Final summary
    overall_duration = time.time() - overall_start
    print("=" * 60)
    print("FINAL TEST SUMMARY")
    print("=" * 60)
    print(f"New session test: {'PASSED' if session_id else 'FAILED'}")
    print(f"Existing session test: {'PASSED' if existing_success else 'FAILED'}")
    print(f"Year limit test: {'PASSED' if year_limit_success else 'FAILED'}")
    print(f"Overall execution time: {overall_duration:.2f}s")

    all_passed = session_id and existing_success and year_limit_success

    if all_passed:
        print("\n✓ Complete turn generation system working correctly!")
        print(
            "  All three generation steps (Question → Image Text → Scenario) integrated successfully!"
        )
    else:
        print("\n✗ Some tests failed - check error messages above")

    # Show final state
    show_database_state()

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
