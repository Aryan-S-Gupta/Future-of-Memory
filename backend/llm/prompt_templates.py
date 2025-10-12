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
- Options: Exactly 2 COMPLETE SENTENCES/POLICIES (10-18 words each), NOT keywords
- Do NOT include labels like "A." or "B." inside option strings
- Frame at societal/institutional level (governments, organizations, communities)
- Option queries: Exactly 2 KEYWORD PHRASES for research (≤80 characters each, no questions)
- CRITICAL: Options are full policy descriptions, option_queries are research keywords
- Example option: "Establish mandatory memory editing licenses for all practitioners"
- Example option_query: "memory editing safety protocols clinical trials"
- FORBIDDEN: Never include template variables, placeholders, or markup syntax
""".strip()


def build_description_prompt(
    year: int,
    background: str,
    context_block: str,
    current_question: str,
    selected_option: str,
) -> str:
    """
    Generate a prompt for LLM to create a progressive, time-aware scenario description
    based on the selected option. Includes world state evolution and narrative continuity.
    
    Returns:
        A single JSON object with scenario, scenario_summary, and query_text fields.
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

    # Build world context with conditional handling (like build_question_prompt)
    if "Story History:" in context_block:
        world_ctx = f"""CURRENT WORLD STATE
Year: {year}
Phase: {phase}
Phase-Themes: {phase_themes}

Story History (HIGH PRIORITY):
{context_block}

Current Question: {current_question}

Selected Option: {selected_option}

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

Current Question: {current_question}

Selected Option: {selected_option}
"""
    
    return f"""
ROLE
You are a narrative engine for a turn-based story about humanity's relationship with memory editing technology.

CORE MISSION
Produce a vivid, time-aware scenario description that incorporates the selected option and advances the story timeline appropriate for the '{phase}' phase.

WORLD STATE & DECISION CONTEXT (read carefully; highest priority)
{world_ctx}

WORLD STATE EVOLUTION PRINCIPLES
- The story progresses through distinct phases of societal change
- Historical Continuity: Each scenario must build upon previous developments and decisions
- Thematic Evolution: Move beyond basic implementations to explore complex consequences and reactions
- PRIORITY: Story Context/History above takes precedence over static background information

NARRATIVE PROGRESSION REQUIREMENTS
- MANDATORY: Analyze the Story Context/History to understand what has already happened
- FORBIDDEN: Do NOT retreat to earlier stages or repeat resolved conflicts
- REQUIRED: Focus on SPECIFIC outcomes, reactions, or new developments that arise from the selected option
- ADVANCEMENT: Each scenario should show how the world has changed and introduce emerging challenges
- SPECIFICITY: Address concrete consequences (policy implementations, public reactions, institutional changes, social conflicts)

SCENARIO DEVELOPMENT GUIDELINES
- Include specific details referencing the current year ({year}): concrete dates, locations, institution names, participant reactions, policy details, and sensory atmosphere
- Write as one flowing narrative paragraph with multiple detailed sentences (minimum 5-7 sentences for adequate length)
- Focus on institutional actors (clinics, agencies, councils, governments, consortia). Do not center individual doctors or patients; avoid personal names
- Structure: Institution takes action → Consequences unfold → Public reacts → Reflection question (don't force this pattern into every sentence)
- Use simple, accessible language with fresh expressions and varied institutional settings
- Make it vivid and engaging: include sensory details (lights, sounds, crowds) and small dramatic contrasts; at least one sentence should invite reflection with a question
- Write only natural sentences using fresh language; avoid overused phrases like "brightly lit", "holograms", "bustling public square" and technical symbols/labels

FOLLOW-UP RAG QUERY REQUIREMENTS
- Extract key entities and concepts from the scenario as a declarative keyword phrase
- Format: "topic keywords and concepts" (no questions or question marks)
- Examples: "memory editing consent procedures" | "clinical trial regulations" | "institutional oversight guidelines"

SCENARIO SUMMARY REQUIREMENTS
- Analyze how the selected option changes the world described in the Story Context
- Capture the key transformation: what shifts from the previous state to the new state
- Length: 20-30 words focusing on concrete institutional, social, or policy changes
- Example: "New international memory editing standards create citizen registry system, while underground modification networks emerge in response to restrictions"

TASK SPECIFICATION
1) Generate a concrete scenario paragraph which is vivid and engaging
2) Create a focused follow-up retrieval query as a declarative keyword phrase
3) Provide a scenario summary that captures world state changes

OUTPUT FORMAT (automatically validated):
- Valid JSON with exactly these fields: scenario, scenario_summary, query_text
- Scenario: Single coherent paragraph, 80-150 words (WILL BE REJECTED IF UNDER 80 words)
- Scenario summary: 20-30 words focusing on world state changes and story progression
- Query text: Declarative keyword phrase (no questions)
- FORBIDDEN: Template variables, brackets, HTML-like syntax, placeholder text
- No markdown, code fences, or extra commentary
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
