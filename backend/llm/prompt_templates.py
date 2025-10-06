from typing import List

def build_question_prompt(
    year: int,
    background: str,
    context_block: str,
) -> str:
    """
    Generate a prompt for LLM to create a progressive, time-aware 2-option question
    with per-option RAG queries. Includes anti-repetition and theme progression.
    
    Returns:
        A single JSON object (no markdown).
    """
    # Map year to developmental phase and thematic focus
    if year < 2045:
        phase = "early-adoption"
        phase_themes = "regulation, safety, clinical oversight, commercialization onset, privacy concerns"
    elif year < 2060:
        phase = "social-integration" 
        phase_themes = "labor market shifts, insurance, education, unequal access, platform monopolies, cross-border trade"
    elif year < 2075:
        phase = "governance-and-geopolitics"
        phase_themes = "international standards, sanctions, memory IP, state surveillance, collective archives, cultural conflict"
    else:
        phase = "long-term-consequences"
        phase_themes = "intergenerational effects, historical revision, identity fragmentation, collective trauma, black markets"

    # Check if context_block contains compressed context from story state
    if "Story History:" in context_block:
        world_ctx = f"""CURRENT WORLD STATE
Year: {year}
Phase: {phase}
Phase-Themes: {phase_themes}

Story History (HIGH PRIORITY):
{context_block}

Initial Setting (reference only): {background}
"""
    else:
        world_ctx = f"""CURRENT WORLD STATE
Year: {year}
Phase: {phase}
Phase-Themes: {phase_themes}

Setting (first turn or RAG-only):
{background}

Available Context:
{context_block}
"""
    
    return f"""
ROLE
You are a narrative engine for a turn-based story about humanity's relationship with memory editing technology.

CORE MISSION
Produce a story-progressive, time-aware question that reflects CURRENT world state and introduces NEW challenges appropriate for the '{phase}' phase.

WORLD STATE & HISTORY (read carefully; highest priority)
{world_ctx}

WORLD STATE EVOLUTION PRINCIPLES
- The story progresses through distinct phases of societal change
- Historical Continuity: Each question must build upon previous developments and decisions  
- Thematic Evolution: Move beyond basic "is memory editing ethical" to explore complex consequences
- PRIORITY: Story Context/History above takes precedence over static background information

NARRATIVE PROGRESSION REQUIREMENTS
- MANDATORY: Analyze the Story Context/History above to understand what has already happened
- FORBIDDEN: Do NOT repeat basic questions like "Should memory editing be allowed?" or "Is this technology ethical?"
- REQUIRED: Focus on SPECIFIC consequences, complications, or new developments that arise from previous decisions
- ADVANCEMENT: Each question should introduce novel challenges that emerge as technology and society evolve
- SPECIFICITY: Address concrete scenarios (new regulations, technological breakthroughs, social conflicts, international tensions, economic impacts, cultural shifts)

QUESTION DEVELOPMENT GUIDELINES
- Build upon previous story developments rather than rehashing basic ethical debates
- ALIGN WITH CURRENT PHASE: Focus on the Phase-Themes listed in the world state above
- Focus on EMERGING issues that society hasn't faced before in this timeline
- Present dilemmas that arise FROM the world state, not abstract philosophical questions
- Phase-Specific Focus: Address challenges that naturally emerge during the current developmental phase
- Consider secondary effects: economic disruption, generational divides, international competition, cultural evolution

TASK SPECIFICATION
1) Generate ONE story-progressive question WITH EXACTLY TWO OPTIONS (A, B)
   - Question must reflect current world developments and introduce NEW challenges
   - Options must be concrete responses to this specific situation, not generic approaches
   - Each option should lead to meaningfully different societal trajectories
2) Create TWO targeted retrieval queries (one for each option) for factual grounding

OUTPUT REQUIREMENTS
- MUST return valid JSON with fields: question, options, option_queries
- Question: 18-30 words, specific, time-aware, builds on history
- Options: Exactly 2 strings, 10-18 words each, concrete policy/action, mutually exclusive
- Do NOT include labels like "A." or "B." inside option strings
- Frame at societal/institutional level (governments, organizations, communities)
- Option queries: Exactly 2 keyword phrases, ≤80 characters each (no questions)
- Example query format: "memory editing safety protocols clinical trials"
- FORBIDDEN: Never include template variables, placeholders, or markup syntax
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
    - scenario: single paragraph string which is vivid and engaging.
    - query_text: declarative keyword phrase (no questions) for the NEXT turn's retrieval.
    """
    return f"""
You are continuing a turn-based story. Incorporate the selected option and produce:
1) A concrete scenario paragraph which is vivid and engaging.
2) A focused follow-up retrieval query as a declarative keyword phrase (not a question).

CRITICAL VALIDATION REQUIREMENTS (Your response will be automatically validated):
1. MUST return valid JSON format (no extra text before/after)
2. MUST include "scenario" field as a string paragraph
3. MUST include "query_text" field as a string
4. Total word count for the scenario paragraph must be between 80-150 words
5. FORBIDDEN: Never include template tags, brackets, or HTML-like syntax such as curly braces, angle brackets, slashes with brackets, etc.
6. FORBIDDEN: Never include placeholder text like "retrieval_query", "option_text", or similar template variables
7. If any of these requirements are not met, your response will be rejected and retried

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
- Output "scenario" as a single coherent paragraph string.
- CRITICAL LENGTH REQUIREMENT: Target 80-120 words for optimal length. Aim for approximately 100 words. Count carefully as you write.
- MANDATORY: Your response will be automatically REJECTED if under 80 words. Ensure sufficient detail and elaboration.
- Write as one flowing narrative paragraph with multiple detailed sentences (minimum 5-7 sentences for adequate length).
- Focus on institutional actors (clinics, agencies, councils, governments, consortia). Do not center individual doctors or patients; avoid personal names.
- Overall causal arc: an institutional actor takes an action → visible consequences or public reactions. You do not need to repeat this structure inside every sentence.
- Use simple, everyday language suitable for museum visitors or high-school students.
- Make it vivid and engaging: include sensory details (lights, sounds, crowds) and small dramatic contrasts; at least one sentence should invite reflection with a question.
- Add specific details: mention concrete locations, times, numbers, reactions, and outcomes to reach the required length.
- Do not use arrows, symbols, headings, or labels like "result:"; write only natural sentences.

ANTI-COPYING & VARIATION
- Do not copy wording from any example. Use different phrasing and fresh details.
- Avoid these phrases entirely: "brightly lit", "holograms", "bustling public square", "marble walls", "glowing buttons".
- Use different cities/venues than any example; vary institutions and settings.

EXAMPLE TEMPLATE (structure only, NOT content to copy - this example is approximately 95 words):
"scenario": "<Government/Agency/Clinic/Consortium> announces a comprehensive policy/action at <specific venue and city> on <specific date>, explaining detailed goals and multiple safeguards while diverse audiences react with curiosity and measured caution about identity preservation and privacy implications. <Regulatory body/Clinic network> demonstrates standardized procedures under strict multi-step consent checks, describing verification protocols and displaying preliminary results as visitors carefully weigh potential cognitive benefits against possible psychological risks and societal consequences. <Council/Agency> hosts an extensive public session in <concrete setting and time>, where detailed signage, ambient sounds, and interactive screen visuals shape the contemplative mood and make complex scientific ideas feel tangible and accessible. <Government/Consortium> coordinates systematically with regional partners, promising rigorous oversight and transparent reporting, while ongoing debates and news coverage amplify both hopes alongside growing doubts about long-term consequences. What fundamental aspects of human identity should be protected if memories become editable in daily life?"

CRITICAL LENGTH REQUIREMENT - READ CAREFULLY
- MANDATORY: Write EXACTLY 80-120 words. Your response will be AUTOMATICALLY REJECTED if outside this range.
- TARGET: Aim for 90-110 words as the sweet spot for detailed but concise narrative.
- VERIFICATION: Count words as you write. Use specific details to reach the word count:
  * Specific dates, locations, and institution names (adds 5-10 words)
  * Participant reactions and emotions (adds 10-15 words) 
  * Policy details and implementation steps (adds 10-15 words)
  * Sensory details and atmosphere (adds 5-10 words)
- STRUCTURE: 5-7 detailed sentences with rich descriptions to naturally reach word count.
- Never use banned phrases or copy example content.

FOLLOW-UP RAG QUERY REQUIREMENTS
- Base the query strictly on entities, mechanisms, or ethical dilemmas explicitly raised in the scenario.
- Do not introduce unrelated topics.
- CRITICAL: Write as a DECLARATIVE STATEMENT, not a question.
- Format: "topic keywords and concepts" or "subject matter and related terms"
- Examples: "memory editing consent procedures and safety protocols" | "clinical trial regulations and patient rights" | "institutional oversight and ethical guidelines"
- Do NOT use question words (what, how, why, should, can, will, etc.) or question marks (?)

SCENARIO SUMMARY REQUIREMENTS
- CRITICAL: Provide "scenario_summary" field that captures WORLD STATE CHANGES and STORY PROGRESSION
- Length: 20-30 words focusing on societal shifts, policy changes, or cultural developments
- MUST emphasize what is NEW or DIFFERENT in the world after this decision
- Include concrete changes to institutions, public attitudes, technology adoption, or social structures
- Use language that advances the narrative timeline and sets up future developments
- Focus on measurable outcomes and their implications for society's relationship with memory editing
- Example: "New international memory editing standards create citizen registry system, while underground modification networks emerge in response to restrictions"

OUTPUT FORMAT (STRICT)
CRITICAL: Your response will be validated automatically. It MUST pass these checks:
1. Valid JSON format (starts with {{ and ends with }})
2. Contains "scenario" field as a string paragraph
3. MANDATORY: Total word count of the scenario paragraph must be between 80-150 words (WILL BE REJECTED IF UNDER 80)
4. Contains "scenario_summary" field as a 20-30 word summary
5. Contains "query_text" field as a string
6. No extra text outside the JSON structure

BEFORE SUBMITTING: Count the words in your scenario. If under 80 words, add more specific details, institutional reactions, timeline information, or consequences until you reach at least 80 words.

Return ONLY valid JSON with this exact schema:
{{
  "scenario": "<one coherent paragraph with 80-150 words total>",
  "scenario_summary": "<20-30 word summary of key developments and context>",
  "query_text": "<declarative keyword phrase - no questions or question marks>"
}}

REMINDER: If the total word count is not between 80-150 words, your response will be rejected.
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
