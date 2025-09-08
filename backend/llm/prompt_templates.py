from typing import List

def build_question_prompt(
    year: int,
    background: str,
    context_block: str,
    last_description: str,
) -> str:
    """
    STEP A: Ask the model to return a RAG query AND a multiple-choice style question with four options.
    OUTPUT must be STRICT JSON with fields: query_text, question, options[4]
    """
    return f"""
You are a narrative engine for a turn-based story.

TASK
1) Build a retrieval query to fetch 3–6 highly relevant factual snippets for grounding.
2) Propose ONE clear, decision-driving question WITH EXACTLY FOUR OPTIONS (A, B, C, D). 
   Each option must be short, mutually exclusive, and lead to meaningfully different outcomes.

STORY FRAME
Current Year: {year}

Background:
{background}

Previous Story Summary:
{last_description}

Retrieved Context (if any, distilled):
{context_block}


HARD CONSTRAINTS
- Return ONLY valid JSON (no markdown, no code fences).
- The question must be specific and consequential for the next plot turn.
- "options": an array of EXACTLY 4 strings. Avoid “Yes/No”.
- The retrieval query must be standalone (<= 110 chars) and safe to send to RAG.
- Each option must be short (6–14 words), mutually exclusive, concrete, and must NOT repeat the question text.
- Do NOT include labels like "A." or "B." inside option strings.
- If you initially think of only four options, you MUST ensure they are all distinct and plausible alternatives.
- Options should be self-contained and understandable without repeating the whole question.
- Frame the question at the societal, policy, or community level (e.g., citizens, regulators, clinics, researchers).

OUTPUT FORMAT (STRICT)
Return ONLY valid JSON with this exact schema:
{{
  "query_text": "<<=110 chars, standalone retrieval sentence>",
  "question": "<one question ending with a question mark>",
  "options": ["<option A>", "<option B>", "<option C>", "<option D>"]
}}

EXAMPLE (ONLY to learn the shape; DO NOT copy content):
{{
  "query_text": "clinical protocols for identity continuity in memory-editing pilots",
  "question": "Which approach should the regulatory committee prioritize?",
  "options": ["Establish mandatory waiting periods for all procedures", "Create independent patient advocate programs", "Require clinic self-regulation with professional guidelines", "Form community-based review boards for approvals"]
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
) -> str:
    """
    STEP B: Given the player's selected option, produce the Scenario + follow-up RAG query.
    OUTPUT must be STRICT JSON:
    - scenario: 5 sentences which is vivid and engaging.
    - query_text: query_text for the NEXT turn's retrieval.
    """
    return f"""
You are continuing a turn-based story. Incorporate the selected option and produce:
1) A concrete scenario with exactly 5 sentences which is vivid and engaging.
2) A focused follow-up retrieval query for the next turn.

CRITICAL VALIDATION REQUIREMENTS (Your response will be automatically validated):
1. MUST return valid JSON format (no extra text before/after)
2. MUST include "scenario" field as an array/list
3. MUST include exactly 5 items in the "scenario" array (not 4, not 6)
4. MUST include "query_text" field as a string
5. If any of these requirements are not met, your response will be rejected and retried

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

SCENARIO REQUIREMENTS
- Output "scenario" as an array of sentences.
- Exactly 5 sentences. Not 4. Not 6. Exactly 5.
- Each sentence must contain 15–30 words (count words by spaces). If a sentence is shorter, expand with concrete details until it meets 15–30 words.
- Focus on institutional actors (clinics, agencies, councils, governments, consortia). Do not center individual doctors or patients; avoid personal names.
- Overall causal arc: an institutional actor takes an action → visible consequences or public reactions. You do not need to repeat this structure inside every sentence.
- Use simple, everyday language suitable for museum visitors or high-school students.
- Make it vivid and engaging: include sensory details (lights, sounds, crowds) and small dramatic contrasts; at least one sentence should invite reflection with a question.
- Do not use arrows, symbols, headings, or labels like "result:"; write only natural sentences.

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
- Never include banned phrases.

FOLLOW-UP RAG QUERY
- Base the query strictly on entities, mechanisms, or ethical dilemmas explicitly raised in the scenario.
- Do not introduce unrelated topics.

OUTPUT FORMAT (STRICT)
CRITICAL: Your response will be validated automatically. It MUST pass these checks:
1. Valid JSON format (starts with {{ and ends with }})
2. Contains "scenario" field as an array
3. "scenario" array has EXACTLY 5 items (will be counted automatically)
4. Contains "query_text" field as a string
5. No extra text outside the JSON structure

Return ONLY valid JSON with this exact schema:
{{
  "scenario": [
    "<sentence 1>",
    "<sentence 2>",
    "<sentence 3>",
    "<sentence 4>",
    "<sentence 5>"
  ],
  "query_text": "<single concise sentence (<= 220 chars)>"
}}

REMINDER: If you return anything other than exactly 5 scenario items, your response will be rejected.
Return ONLY valid JSON. Do not include markdown, code fences, or commentary.
""".strip()


def build_image_text_prompt(
    year: int,
    background: str,
    last_description: str,
    question: str,
    option_text: str,
) -> str:
    """
    Build a prompt to generate an image description for a specific option.
    This predicts what the visual scene would look like if this option is chosen.
    """
    return f"""
You are helping generate speculative art style image prompts for an AI image generation model.

The current world state is: {background}

Previous events: {last_description}

Current situation (Year {year}): {question}

If this option is chosen: {option_text}

Your task: Write one single detailed image prompt that captures the atmosphere of this world after choosing this specific option.

STRICT REQUIREMENTS:
- Output EXACTLY ONE sentence (no line breaks, no multiple sentences)
- Maximum 70 words (count your words carefully)
- Maximum 350 characters including spaces
- Use concrete, visual language only
- No quotes, no explanations, no meta-commentary
- No instruction acknowledgments (do not say "Here's" or "I'll create")

Focus on:
- The environment and overall scene (urban, rural, futuristic, dystopian, natural, etc.)
- The emotional mood (hopeful, doomed, neutral, chaotic, peaceful, tense, etc.) 
- The artistic style (speculative art, cinematic, surreal, painterly textures, neon lighting)

Do not describe exact numbers of people or micro actions. Instead, describe the overall crowd impression and the vibe of the world.

EXAMPLES (for structure reference only, create original content):
- "A cinematic government facility bathed in cold fluorescent lighting with officials reviewing documents at sterile desks"
- "Speculative art scene of a bustling clinic courtyard with hopeful citizens waiting under warm sunset lighting"

CRITICAL: Output only the final image prompt as one complete sentence. No additional text, explanations, or commentary.
""".strip()