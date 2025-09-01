import requests, json, re
from prompt_templates import build_description_prompt

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:3.8b"

# Helper function to extract JSON from text
def extract_json_block(text: str) -> str:
    """
    Ensure we always get a valid JSON string.
    Handles cases like:
    1) pure JSON
    2) ```json ... ```
    3) ``` ... ```
    """
    # First match ```json ... ```
    m = re.search(r"```json\s*(\{.*\})\s*```", text, flags=re.S)
    if m:
        return m.group(1).strip()
    # Second match ``` ... ```
    m = re.search(r"```\s*(\{.*\})\s*```", text, flags=re.S)
    if m:
        return m.group(1).strip()
    # Otherwise, return the original text
    return text.strip()

# Helper: Validate scenario
def validate_scenario(result: dict) -> bool:
    """
    Validate that scenario meets requirements:
    - 5 sentences
    """
    scenario = result.get("scenario", [])
    if not isinstance(scenario, list):
        return False

    if len(scenario) != 5:
        return False
    
    return True

# Call the Ollama API with the given prompt and return a JSON response dict with retries
def call_ollama(prompt: str, max_retries: int = 3) -> dict:
    payload = {"model": MODEL, "prompt": prompt}
    
    for attempt in range(max_retries):
        response = requests.post(OLLAMA_URL, json=payload, stream=True)
        collected_output = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                collected_output += data.get("response", "")
        
        try:
            result = json.loads(extract_json_block(collected_output))
        except Exception as e:
            print(f"[Attempt {attempt+1}] JSON parse failed:", e)
            continue
        
        # Post-check
        if validate_scenario(result):
            return result
        else:
            print(f"[Attempt {attempt+1}] Scenario validation failed, retrying...")
    
    # If all attempts fail, return the last result (may be invalid)
    return result

# Test description prompt
if __name__ == "__main__":
    prompt = build_description_prompt(
        year=2035,
        background="In 2035, global regulations begin piloting clinical memory editing as part of mental health research.",
        context_block="(1) consent processes require strict multi-factor verification; (2) research reports show both benefits and risks for identity stability.",
        last_description="Public debate has intensified as clinics prepare to enroll participants in early programs.",
        current_question="Should the government allow memory editing for clinical trials?",
        selected_option="The government should allow memory editing for clinical trials with strict safeguards",
    )
    result = call_ollama(prompt)
    print("Clean JSON:\n", json.dumps(result, ensure_ascii=False, indent=2))