## Home Page
**View**  
```python
create_session(request)
```

**Backend sequence**  
- Creates a new session.  
- Returns session ID.  

**Response**  
```json
{
  "session_id": 42
}
```

**Frontend**  
- Stores `session_id`.  

---

## Intro Page
**View**  
```python
start_prerendering(request, session_id, year)
```

**Backend sequence**  
1. **Step 1**: Generate question + options 
2. **Step 2**: Generate image texts for all options
3. Parallel:  
   - **Step 3a**: Generate images for all options
   - **Step 3b**: Generate scenario for all options
4. Save results in database  

---

## Static Background Page
**View**  
- No backend call required  

---

## Question Display Page
**View**  
```python
display_question_and_options(request, session_id)
```

**Backend sequence**  
- Uses `session_id` to get the **latest turn**  
- Uses that `turn_id` to find the question and options  

**Response**  
```json
{
  "message": "ok",
  "data": {
    "turn_id": 7,
    "year": 2036,
    "question": "Should governments regulate the sale of personal memories in the open market?",
    "options": [
      {
        "option_id": 15,
        "label": "A",
        "option_text": "Yes, regulation is necessary to protect citizens from exploitation."
      },
      {
        "option_id": 16,
        "label": "B",
        "option_text": "No, individuals should be free to trade their memories without restrictions."
      }
    ]
  }
}
```

**Frontend**  
- Stores `turn_id`  

---

## Scenario & Image Display Page
**View**  
```python
display_scenario_and_image(request, session_id, turn_id, year, option_id)
```

**Backend**  
- Uses **turn_id** to get the turn  
- Uses **turn** and **option_id** to get the chosen option  
- Retrieves scenario
- Retrieves image info from **display_by_option(session_id, turn_id, option_id)** in images.render_pipeline.py
- **start_turn_pipeline(request, session_id, year)** starts the generation of next turn's question ...  

**Response**  
```json
{
  "success": true,
  "session_id": 42,
  "turn_id": 7,
  "year": 2036,
  "scenario": {
    "text": "Citizens debate whether memory trading should be regulated by the state or left to the free market."
  },
  "image": {
    "status": "ready",
    "url": "http://127.0.0.1:9000/media/comfyui/output/option_A_world.png"
  }
}
```

**Frontend**  
- Updates `year`  
