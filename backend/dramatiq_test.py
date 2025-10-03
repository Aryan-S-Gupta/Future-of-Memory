#!/usr/bin/env python
import os
import sys
import django
import time
import redis
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memory_sim.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from shared.models import Session, WorldBackground, DefaultQueryList, Turn, Option
from shared.tasks import start_turn_pipeline

def check_prerequisites():
    """Check if Redis and workers are running"""
    print("Checking prerequisites...")
    
    # Check Redis connection
    try:
        r = redis.Redis(host='localhost', port=6380, db=0)
        r.ping()
        print("✓ Redis is running")
    except Exception as e:
        print(f"✗ Redis not running: {e}")
        return False
    
    # Check if there are any tasks in queues (indicates workers might be down)
    queue_lengths = {
        'llm_queue': r.llen('dramatiq:llm_queue'),
        'image_queue': r.llen('dramatiq:image_queue'), 
        'default': r.llen('dramatiq:default')
    }
    
    total_queued = sum(queue_lengths.values())
    if total_queued > 10:
        print(f"⚠ Warning: {total_queued} tasks queued - workers may be down")
        print(f"Queue lengths: {queue_lengths}")
    else:
        print("✓ Queue lengths look normal")
    
    return True

def setup_test_data():
    """Create necessary test data"""
    print("Setting up test data...")
    
    # Create world background
    bg, created = WorldBackground.objects.get_or_create(
        defaults={'content': 'In 2035, memory editing technology has reached a critical juncture where society must decide how to regulate and implement these powerful capabilities that can reshape human consciousness and identity.'}
    )
    if created:
        print("✓ Created world background")
    else:
        print("✓ World background already exists")
    
    # Create default queries
    default_queries = ['memory editing ethics', 'consciousness technology', 'identity preservation', 'neural enhancement', 'cognitive modification']
    created_count = 0
    for query in default_queries:
        _, created = DefaultQueryList.objects.get_or_create(keyword=query)
        if created:
            created_count += 1
    
    print(f"✓ Default queries ready ({created_count} new, {len(default_queries)} total)")
    return bg

def monitor_pipeline_progress(session_id, year, max_wait_minutes=5):
    """Monitor the pipeline execution with detailed progress"""
    print(f"\nMonitoring pipeline progress for session {session_id}, year {year}")
    print("=" * 60)
    
    max_iterations = max_wait_minutes * 12  # Check every 5 seconds
    
    for i in range(max_iterations):
        turn = Turn.objects.filter(session=session_id, year=year).first()
        
        if not turn:
            print(f"[{i*5:3d}s] Step 1: Generating question and options...")
        else:
            options = Option.objects.filter(turn=turn)
            
            if not turn.question:
                print(f"[{i*5:3d}s] Step 1: Question record created, waiting for content...")
            elif options.count() < 2:
                print(f"[{i*5:3d}s] Step 1: Question ready, creating options...")
            else:
                # Check image texts
                has_image_texts = all(opt.image_text for opt in options)
                has_scenarios = all(opt.scenario for opt in options)
                
                if not has_image_texts:
                    print(f"[{i*5:3d}s] Step 2: Generating image descriptions...")
                elif not has_scenarios:
                    print(f"[{i*5:3d}s] Step 3: Generating scenarios (parallel with images)...")
                else:
                    print(f"[{i*5:3d}s] ✓ Pipeline complete!")
                    
                    # Show results
                    print("\nFinal Results:")
                    print("-" * 40)
                    print(f"Turn ID: {turn.id}")
                    print(f"Question: {turn.question[:80]}...")
                    print("Options:")
                    for opt in options:
                        print(f"  {opt.label}: {opt.option_text}")
                        print(f"     Image text: {opt.image_text[:50]}...")
                        print(f"     Scenario: {opt.scenario[:50]}...")
                    
                    return True
        
        time.sleep(5)
    
    print(f"\n✗ Timeout after {max_wait_minutes} minutes")
    return False

def test_individual_functions():
    """Test individual functions without the full pipeline"""
    print("\nTesting individual functions...")
    
    session = Session.objects.create()
    print(f"Created test session: {session.id}")
    
    try:
        from shared.services import generate_and_save_question
        print("Testing generate_and_save_question...")
        result = generate_and_save_question(session.id, 2035)
        print(f"✓ Question generated: {result['question'][:50]}...")
        
        turn_id = result['turn_id']
        
        # Test image text generation
        from shared.services import generate_and_save_image_text
        print("Testing generate_and_save_image_text...")
        image_result = generate_and_save_image_text(session.id, turn_id, 2035)
        print(f"✓ Image texts generated for {len(image_result['image_texts'])} options")
        
        # Test scenario generation  
        from shared.services import generate_and_save_scenario
        print("Testing generate_and_save_scenario...")
        scenario_result = generate_and_save_scenario(session.id, turn_id, 2035)
        print(f"✓ Scenarios generated for {len(scenario_result['scenarios'])} options")
        
        print("✓ All individual functions work")
        return True
        
    except Exception as e:
        print(f"✗ Individual function test failed: {e}")
        return False

def test_full_pipeline():
    """Test the complete pipeline with monitoring"""
    print("\nTesting complete pipeline...")
    
    # Create test session
    session = Session.objects.create()
    print(f"Created test session: {session.id}")
    
    # Start pipeline
    try:
        result = start_turn_pipeline.send(session.id, 2035)
        print(f"✓ Pipeline started with message ID: {result.message_id}")
    except Exception as e:
        print(f"✗ Failed to start pipeline: {e}")
        return False
    
    # Monitor progress
    success = monitor_pipeline_progress(session.id, 2035, max_wait_minutes=3)
    
    if success:
        print("\n✓ PIPELINE TEST PASSED")
    else:
        print("\n✗ PIPELINE TEST FAILED")
        print("Check worker logs for errors")
    
    return success

def main():
    print("Dramatiq Pipeline Test")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\nPlease start Redis and workers before testing:")
        print("1. redis-server")
        print("2. python manage.py rundramatiq --queues llm_queue,image_queue,default")
        return
    
    # Setup test data
    setup_test_data()
    
    # Test individual functions first
    if not test_individual_functions():
        print("\n✗ Individual function tests failed")
        print("Fix the service functions before testing the pipeline")
        return
    
    # Test full pipeline
    test_full_pipeline()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        session_id = int(sys.argv[2])
        print(f"Checking session {session_id}...")
        monitor_pipeline_progress(session_id, 2035, max_wait_minutes=1)
    else:
        main()