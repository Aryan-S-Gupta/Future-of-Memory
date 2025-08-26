from typing import List, Optional

def build_question_prompt(
    year: int,
    background: str,
    context_block: str,
    last_description: str,
    state_json: Optional[str] = None,
) -> str:
    """
    STEP A: Ask the model to return a RAG query AND a multiple-choice style question with two options.
    OUTPUT must be STRICT JSON with fields: query_text, keywords[], question, options[2]
    """
    state_hint = f"\nState Memory (JSON):\n{state_json}\n" if state_json else ""
    return f"""
You are a narrative engine for a turn-based story.

TASK
1) Build a retrieval query to fetch 3–6 highly relevant factual snippets for grounding.
2) Propose ONE clear, decision-driving question WITH EXACTLY TWO OPTIONS (no yes/no). 
   Each option must be short, mutually exclusive, and lead to meaningfully different outcomes.

STORY FRAME
Current Year: {year}

Background:
{background}

Previous Story Summary:
{last_description}

Retrieved Context (if any, distilled):
{context_block}
{state_hint}


HARD CONSTRAINTS
- Return ONLY valid JSON (no markdown, no code fences).
- The question must be specific and consequential for the next plot turn.
- "options": an array of EXACTLY 2 strings. Avoid “Yes/No”.
- The retrieval query must be standalone (<= 110 chars) and safe to send to RAG.
- keywords are 1–3 lowercase tokens, no punctuation, no duplicates.
- Each option must be short (6–14 words), mutually exclusive, concrete, and must NOT repeat the question text.
- Do NOT include labels like "A." or "B." inside option strings.
- If you initially think of only one option, you MUST invent a second plausible alternative.
- Options should be self-contained and understandable without repeating the whole question.
- Frame the question at the societal, policy, or community level (e.g., citizens, regulators, clinics, researchers).

OUTPUT FORMAT (STRICT)
Return ONLY valid JSON with this exact schema:
{{
  "query_text": "<<=110 chars, standalone retrieval sentence>",
  "keywords": ["<1-3 lowercase keywords>"],
  "question": "<one question ending with a question mark>",
  "options": ["<concise option without labels>", "<second concise option without labels>"]
}}

EXAMPLE (ONLY to learn the shape; DO NOT copy content):
{{
  "query_text": "clinical protocols for identity continuity in memory-editing pilots",
  "keywords": ["consent", "identity", "protocols", "clinic"],
  "question": "Which path should Lin choose before the pilot review?",
  "options": ["Schedule a supervised integration session at the clinic", "Pause treatment to consult an external ethics counselor"]
}}

Return ONLY valid JSON. Do not include markdown, code fences, or commentary.
""".strip()


def build_description_prompt(
    year: int,
    background: str,
    context_block: str,
    last_description: str,
    current_question: str,
    selected_option: str,   # one of the strings from the options array
    state_json: Optional[str] = None,
) -> str:
    """
    STEP B: Given the player's selected option, produce the Scenario + Image brief + follow-up RAG query.
    OUTPUT must be STRICT JSON:
    - scenario: one paragraph (no line breaks).
    - image_brief: subject, scene, mood, style, keywords[] (3–8 compact tokens for the image pipeline).
    - rag_query: query_text + keywords[] for the NEXT turn’s retrieval.
    """
    state_hint = f"\nState Memory (JSON):\n{state_json}\n" if state_json else ""
    return f"""
You are continuing a turn-based story. Incorporate the selected option and produce:
1) A concrete scenario paragraph (one natural paragraph).
2) An image brief for the art pipeline (Stable Diffusion / ComfyUI).
3) A focused follow-up retrieval query for the next turn.

STORY FRAME
Current Year: {year}

Background:
{background}

Previous Story Summary:
{last_description}

Retrieved Context (if any, distilled):
{context_block}

Current Question:
{current_question}

Selected Option:
{selected_option}
{state_hint}
SCENARIO REQUIREMENTS
- One paragraph (5–8 sentences), no line breaks.
- Structure: Who → Did what → Result/Consequence (cause→effect).
- Include at least one named entity (person/clinic/agency) and one setting detail (location/time/tech).
- Stay consistent with the year and prior facts; be specific, not vague.

IMAGE BRIEF REQUIREMENTS
- Fields:
  - subject: main subject(s) (e.g., "lab technician reviewing synaptic imprint logs")
  - scene: place/time/visual setting (e.g., "after-hours neuroclinic corridor, cool fluorescents")
  - mood: emotional tone (e.g., "tense, procedural, sterile")
  - style: visual style/camera hint (e.g., "documentary mid-shot, realistic")
  - keywords: 3–8 terse tokens for the image model (e.g., ["neon signage","glass partition","ID badge","bokeh"])
- Keep each field short and descriptive; no long sentences.

FOLLOW-UP RAG QUERY
- Target concrete entities/mechanisms raised by this option; provide 3–6 keywords.

OUTPUT FORMAT (STRICT)
Return ONLY valid JSON with this exact schema:
{{
  "scenario": "<one paragraph, no line breaks>",
  "image_brief": {{
    "subject": "<short phrase>",
    "scene": "<short phrase>",
    "mood": "<short phrase>",
    "style": "<short phrase>",
    "keywords": ["<3-8 short tokens for image generation>"]
  }},
  "rag_query": {{
    "query_text": "<single concise sentence (<= 220 chars)>",
    "keywords": ["<3-6 lowercase keywords>"]
  }}
}}

Return ONLY valid JSON. Do not include markdown, code fences, or commentary.
""".strip()


# Optional helper: turn ContextItem[] into a compact block for the prompts
def compose_context_block_from_items(items: List[dict]) -> str:
    """
    Convert a list of ContextItem-like dicts into compact lines.
    Each item may have: text, meta{title, source, year}.
    """
    lines = []
    for i, it in enumerate(items[:8], 1):
        meta = it.get("meta", {})
        lines.append(
            f"({i}) {it.get('text','').strip()} "
            f"[title:{meta.get('title')}, source:{meta.get('source')}, year:{meta.get('year')}]"
        )
    return "\\n".join(lines)