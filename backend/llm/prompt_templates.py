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
2) Propose ONE clear, decision-driving question with EXACTLY two options (no yes/no). 
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
CONSTRAINTS
- The question must be specific and consequential for the next plot turn.
- The retrieval query must be standalone (<= 220 chars) and safe to send to RAG.
- keywords are 3–6 lowercase tokens, no punctuation, no duplicates.
- Options must be an array of exactly 2 strings. Avoid “Yes/No”.

OUTPUT FORMAT (STRICT)
Return ONLY valid JSON with this exact schema:
{{
  "query_text": "<single concise sentence for retrieval>",
  "keywords": ["<3-6 lowercase keywords>"],
  "question": "<one question ending with a question mark>",
  "options": ["<option A>", "<option B>"]
}}

NO extra commentary; JSON only.
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

NO extra commentary; JSON only.
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