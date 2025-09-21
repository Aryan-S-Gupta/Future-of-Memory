# bg manager
# sequence: step 1: question + options --> step2: image_texts --> step 3a: image + step 3b: scenario
import dramatiq
from images.render_pipeline import generate_two_images_blocking
from .models import Session
from .services import generate_and_save_image_text, generate_and_save_scenario, generate_and_save_question
from images.render_pipeline import generate_two_images_blocking

@dramatiq.actor(queue_name="llm_queue")
def step1_generate_question(session_id: int, year: int):
    """Step 1: Generate question and options"""
    result = generate_and_save_question(session_id, year)
    turn_id = result['turn_id']
    
    # trigger step 2
    step2_generate_image_texts.send(session_id, turn_id, year)
    return result

@dramatiq.actor(queue_name="llm_queue") 
def step2_generate_image_texts(session_id: int, turn_id: int, year: int):
    """Step 2: Generate image descriptions"""
    result = generate_and_save_image_text(session_id, turn_id, year)
    
    # trigger parallel step 3
    step3a_generate_images.send(session_id, turn_id)
    step3b_generate_scenarios.send(session_id, turn_id, year)
    return result

@dramatiq.actor(queue_name="image_queue")
def step3a_generate_images(session_id: int, turn_id: int):
    """Step 3a: Generate actual images (runs in parallel with scenarios)"""
    return generate_two_images_blocking(session_id, turn_id)

@dramatiq.actor(queue_name="llm_queue")
def step3b_generate_scenarios(session_id: int, turn_id: int, year: int):
    """Step 3b: Generate scenarios (runs in parallel with images)"""
    return generate_and_save_scenario(session_id, turn_id, year)

@dramatiq.actor(queue_name="default")
def start_turn_pipeline(session_id: int, year: int):
    """Entry point: Handle session setup then start pipeline"""
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return {"status": "error", "error": f"Session {session_id} not found"}

    if year is None:
        latest_turn = Turn.objects.filter(session=session).order_by('-year').first()
        target_year = latest_turn.year + 1 if latest_turn else 2035
    else:
        target_year = year

    step1_generate_question.send(session_id, target_year)
    return {"status": "pipeline_started"}