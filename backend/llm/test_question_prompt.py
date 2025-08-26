import requests, json, re
from prompt_templates import build_question_prompt

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

# Call the Ollama API with the given prompt and return a JSON response dict
def call_ollama(prompt: str) -> dict:
    r = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False, "format": "json"},
        timeout=60
    )
    r.raise_for_status()
    data = r.json()  # Ollama's first JSON
    text = data.get("response", "").strip()  # Only get model output
    text = extract_json_block(text)          # Remove possible code blocks
    return json.loads(text)                  # Convert to Python dict

# check valid options
def valid_two_options(d: dict) -> bool:
    # Check if options key exists and is a list
    if "options" not in d or not isinstance(d["options"], list):
        return False
    options = d.get("options", [])
    # must be exactly 2 options
    if not options or len(options) != 2:
        return False
    for opt in options:
        if not isinstance(opt, str) or not (6 <= len(opt.split()) <= 14):
            return False
    return True

# refine the option
def refine_option_fix(oringinal_json: dict) -> dict:
    # if options are invilid, let the model to re-generate options
    question = oringinal_json.get("question", "")
    fix_prompt = f"""
    Return ONLY valid JSON.

    You previously produced a question but did not provide exactly two valid options.
    Rewrite ONLY the "options" array with EXACTLY TWO concise, mutually exclusive choices (6–14 words each).
    and do NOT repeat the question text.

    Question: {question}

    Output schema:
    {{
        "options": [
            "Option 1",
            "Option 2"
        ]
    }}
    """.strip()

    try:
        d = call_ollama(fix_prompt)
        if valid_two_options(d):
            original_json["options"] = d["options"]
    except Exception as e:
        print("refine_options_fix failed:", e)
    return original_json

# Check option validity before output the results
def ensure_valid_options(prompt: str) -> dict:
    """
    Step A: Main call ollama
    Step B: Check option validity
    Step C: Refine options if invalid
    Step D: Retry the main call again
    Step E: fallback
    """

    # Step A
    out = call_ollama(prompt)
    # Step B
    if valid_two_options(out):
        return out
    # Step C
    out = refine_options_fix(out)
    if valid_two_options(out):
        return out
    # Step D
    try:
        retry_out = call_ollama(prompt)
        if valid_two_options(retry_out):
            return retry_out
    except Exception as e:
        print("retry call failed:", e)
    # Step E
    out["options"] = [
        "Take an action that advances the situation forward",
        "Hold back and reconsider before making a move"
    ]
    return out



if __name__ == "__main__":
    prompt = build_question_prompt(
        2035,
        "In 2035, society pilots clinical memory editing under strict consent protocols.",
        "(1) clinical consent forms require two-factor identity; (2) trials show mixed outcomes on identity continuity.",
        "Lin located a clinic after a panic episode."
    )
    result = ensure_valid_options(prompt)
    print("Clean JSON:\n", json.dumps(result, ensure_ascii=False, indent=2))
    print("\nQuestion:", result["question"])
    print("Options:", result["options"])