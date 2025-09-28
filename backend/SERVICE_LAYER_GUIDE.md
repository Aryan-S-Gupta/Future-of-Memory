# MemorySim Service Layer & Testing Guide

## Overview

The MemorySim service layer is a comprehensive business logic architecture that coordinates LLM generation, RAG retrieval, and database operations to implement the core functionality of the memory policy simulation game.

## Architecture Components

### Core File Structure
```
backend/
├── shared/
│   └── services.py              # Main service layer
├── complete_turn_test.py        # Complete turn generation test
├── simple_question_test.py      # Question continuation test
├── scenario_test.py             # Scenario generation test
├── image_text_test.py          # Image text generation test
├── create_background.py        # World background initialization
└── load_keywords_script.py     # Keywords loading script
```

---

## services.py Core Functions

### 1. Complete Turn Generation - `generate_complete_turn()`

**Most Important Function** - Orchestrates complete game turn generation

#### Function Description
- Automatic session management (create or continue)
- Intelligent year handling (2035-2085 limit)
- Three-step orchestration: Question → Image Text → Scenario
- Transaction safety and error handling
- Performance monitoring and logging

#### Usage
```python
from shared.services import generate_complete_turn

# Create new session and first turn
result = generate_complete_turn()

# Continue existing session
result = generate_complete_turn(session_id=15)

# Specify particular year
result = generate_complete_turn(session_id=15, year=2040)
```

#### Return Result
```python
{
    'session_id': 15,
    'turn_id': 28,
    'year': 2035,
    'total_duration': 73.75,
    'generation_steps': {
        'question': {
            'question': 'Question text...',
            'options': [...]
        },
        'image_texts': {
            'image_texts': [...]
        },
        'scenarios': {
            'scenarios': [...]
        }
    }
}
```

### 2. Question Generation - `generate_and_save_question()`

#### Function Description
- RAG-based contextual question generation
- Dual option generation (A/B choices)
- Historical continuity handling
- Automatic database saving

#### Usage
```python
result = generate_and_save_question(session_id=1, year=2035)
```

### 3. Image Text Generation - `generate_and_save_image_text()`

#### Function Description
- Generate image description text for each option
- Based on current context and historical background
- Prepare detailed descriptions for image generation

#### Usage
```python
result = generate_and_save_image_text(
    session_id=1, 
    turn_id=28, 
    year=2035
)
```

### 4. Scenario Generation - `generate_and_save_scenario()`

#### Function Description
- Generate detailed scenario descriptions of choice consequences
- Build future world states
- Prepare context for next round generation

#### Usage
```python
result = generate_and_save_scenario(
    session_id=1, 
    turn_id=28, 
    year=2035
)
```

### 5. Auxiliary Functions

#### Session Status Query
```python
status = get_session_status(session_id=1)
```

#### User Choice Recording
```python
choice_result = record_user_choice(turn_id=28, option_id=45)
```

---

## Testing Suite Details

### 1. Complete Turn Test - `complete_turn_test.py`

**Recommended Primary Use** - Most comprehensive test suite

#### Test Content
- New session creation test
- Existing session continuation test  
- Year limit handling test
- Complete workflow verification
- Database status display

#### How to Run
```bash
cd backend
python complete_turn_test.py
```

#### Output Example
```
MemorySim Complete Turn Generation Test Suite
============================================================

Test 1: New Session Generation
----------------------------------------
[SUCCESS] New session turn completed! (73.76s)
   Session ID: 15
   Turn ID: 28
   Year: 2035

Generation Steps:
   ✓ Question: Given the profound societal implications...
   ✓ Options: 2 generated
   ✓ Image Texts: 2 generated
   ✓ Scenarios: 2 generated

✓ Complete turn generation system working correctly!
```

### 2. Question Continuation Test - `simple_question_test.py`

#### Test Content
- Find latest session and turn
- Automatically handle missing user choices
- Generate next year question
- Session status display

#### How to Run
```bash
python simple_question_test.py
```

### 3. Scenario Generation Test - `scenario_test.py`

#### Test Content
- Complete scenario generation process
- New session and existing turn tests
- Database verification
- Performance monitoring

#### How to Run
```bash
python scenario_test.py
```

### 4. Image Text Test - `image_text_test.py`

#### Test Content
- Image description text generation
- Existing turn lookup and update
- Database status verification

#### How to Run
```bash
python image_text_test.py
```

---

## Quick Start Guide

### 1. Environment Setup
```bash
# Ensure in backend directory
cd backend

# Activate Python environment (if using virtual environment)
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Ensure Ollama is running
ollama serve
```

### 2. Initialize Data
```bash
# Create world background
python create_background.py

# Load keywords (if keywords.txt exists)
python load_keywords_script.py

# Run Django migrations
python manage.py migrate
```

### 3. Run Tests
```bash
# Recommended: run complete test
python complete_turn_test.py

# Or run specific tests
python simple_question_test.py
python scenario_test.py
python image_text_test.py
```

### 4. Usage in Code
```python
# Usage in Django project
from shared.services import generate_complete_turn

# Generate complete game turn
try:
    result = generate_complete_turn()
    print(f"Successfully generated Turn {result['turn_id']}")
    
    # Process results...
    question = result['generation_steps']['question']['question']
    options = result['generation_steps']['question']['options']
    
except Exception as e:
    print(f"Generation failed: {e}")
```

---

## Performance Benchmarks

### Typical Execution Times
- **Question Generation**: 15-25 seconds
- **Image Text Generation**: 8-12 seconds  
- **Scenario Generation**: 35-45 seconds
- **Complete Turn**: 70-80 seconds

### System Requirements
- **Memory**: Recommended 8GB+ (LLM models)
- **Storage**: RAG database requires additional space
- **Network**: Ollama API connection

---

## Troubleshooting

### Common Issues

#### 1. "No sessions found" Error
```bash
# Run complete test to create session
python complete_turn_test.py
```

#### 2. RAG Retrieval Failure
```bash
# Check if FAISS database exists
ls rag/db/

# Rebuild RAG database
python rag/setup.py
```

#### 3. LLM Connection Error
```bash
# Check Ollama status
ollama list
ollama pull phi3:3.8b

# Restart Ollama service
ollama serve
```

#### 4. Database Issues
```bash
# Re-migrate database
python manage.py migrate

# View database status
python manage.py dbshell
```

### Debugging Tips

#### 1. Enable Verbose Logging
```python
import logging
logging.getLogger('shared.services').setLevel(logging.DEBUG)
```

#### 2. Check Database Status
```python
from shared.models import Session, Turn, Option
print(f"Sessions: {Session.objects.count()}")
print(f"Turns: {Turn.objects.count()}")
print(f"Options: {Option.objects.count()}")
```

#### 3. Use Django Shell for Debugging
```bash
python manage.py shell
```

---

## Advanced Configuration

### Custom LLM Parameters
```python
# Adjust in llm/generate.py
# Temperature, max_tokens, etc.
```

### Modify RAG Search
```python
# Adjust in rag/retrieve.py
# Search result count, similarity threshold, etc.
```

### Database Optimization
```python
# Adjust in shared/models.py
# Field lengths, indexes, etc.
```

---

## Extension Guide

### Adding New Generation Steps
1. Add generation function in `llm/generate.py`
2. Create service function in `shared/services.py`
3. Update `generate_complete_turn()` orchestration
4. Create corresponding test file

### API Integration Preparation
Service layer is ready for REST API development:
```python
# Usage in Django views
from shared.services import generate_complete_turn

def create_turn_api(request):
    result = generate_complete_turn(
        session_id=request.data.get('session_id')
    )
    return JsonResponse(result)
```

---

## Summary

MemorySim service layer provides:
- **Complete business logic encapsulation**
- **Transaction-safe data operations**  
- **Robust error handling**
- **High-performance LLM integration**
- **Comprehensive test coverage**

Recommended to use `generate_complete_turn()` as the main interface, paired with `complete_turn_test.py` for development and debugging. This architecture is ready for API development and frontend integration.
