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
    - scenario: 5-8 sentences which is vivid and engaging.
    - image_brief: subject, scene, mood, style, keywords[] (3–6 compact tokens for the image pipeline).
    - rag_query: query_text + keywords[] for the NEXT turn’s retrieval.
    """
    state_hint = f"\nState Memory (JSON):\n{state_json}\n" if state_json else ""
    return f"""
You are continuing a turn-based story. Incorporate the selected option and produce:
1) A concrete scenario with 5-8 sentences which is vivid and engaging.
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
- Output "scenario" as an array of sentences.
- Exactly 5 sentences. Not 4. Not 6. Exactly 5.
- Each sentence must contain 15–30 words (count words by spaces). If a sentence is shorter, expand with concrete details until it meets 15–30 words.
- Focus on institutional actors (clinics, agencies, councils, governments, consortia). Do not center individual doctors or patients; avoid personal names.
- Overall causal arc: an institutional actor takes an action → visible consequences or public reactions. You do not need to repeat this structure inside every sentence.
- Use simple, everyday language suitable for museum visitors or high-school students.
- Make it vivid and engaging: include sensory details (lights, sounds, crowds) and small dramatic contrasts; at least one sentence should invite reflection with a question.
- Do not use arrows, symbols, headings, or labels like "result:"; write only natural sentences.
- Consistency rule: "image_brief" and "rag_query" must only use entities/imagery already present in the "scenario". Do not invent new places or actors.

ANTI-COPYING & VARIATION
- Do not copy wording from any example. Use different phrasing and fresh details.
- Avoid these phrases entirely: "brightly lit", "holograms", "bustling public square", "marble walls", "glowing buttons".
- Use different cities/venues than any example; vary institutions and settings.

EXAMPLE TEMPLATE (structure only, NOT content to copy):
"scenario": [
  "<Government/Agency/Clinic/Consortium> announces a policy/action in <specific venue and city>, explaining goals and safeguards while audiences react with curiosity and caution about identity and privacy.",
  "<Regulatory body/Clinic network> demonstrates procedures under strict consent checks, describing verification steps and displaying results as visitors weigh potential benefits against possible risks they can easily imagine.",
  "<Council/Agency> hosts a public session in <concrete setting and time>, where signage, ambient sounds, or screen visuals shape the mood and make complex ideas feel tangible to everyday people.",
  "<Government/Consortium> coordinates with partners across regions, promising oversight and transparency, while passerby debates and news tickers amplify hopes for treatment alongside doubts about unintended consequences.",
  "<Parliament/Ethics council> invites reflection with a clear question about values and trade-offs, encouraging citizens to consider what should be protected if memories become editable in daily life."
]

HARD REMINDER
- If the "scenario" array is not exactly 5 items, regenerate until it is exactly 5.
- If any sentence is not within 15–30 words, regenerate until all five sentences meet 15–30 words.
- Never include banned phrases. Never introduce entities not present in "scenario" into "image_brief" or "rag_query".

IMAGE BRIEF REQUIREMENTS
- Provide a single short descriptive sentence (≤70 characters).
- This description must summarize the main subject, setting, and mood of the scenario in one line.
- Do not break into fields (no subject/scene/mood/style separation).
- Do not output keywords or arrays.
- Use simple, direct language suitable for an image generation model.
- The description must directly reflect the scenario above; do not invent new places, actors, or details.

FOLLOW-UP RAG QUERY
- Base the query strictly on entities, mechanisms, or ethical dilemmas explicitly raised in the scenario.
- Do not introduce unrelated topics.
- Provide 3–4 keywords separately, all extracted or derived from the scenario.
- Each keyword should be a single lowercase token, no punctuation.

OUTPUT FORMAT (STRICT)
Return ONLY valid JSON with this exact schema:
{{
  "scenario": [
    "<sentence 1>",
    "<sentence 2>",
    "<sentence 3>",
    "<sentence 4>",
    "<sentence 5>"
  ],
  "image_brief": "Short one-sentence description (≤70 characters, from scenario)",
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