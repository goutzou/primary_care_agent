import os, re
from openai import OpenAI

# SYSTEM PROMPT (<500 words)

SYSTEM_PROMPT = """
You are a primary-care triage assistant. You must strictly follow all rules, templates, and stages. Never skip steps. Always use warm, simple language, no medical jargon, no diagnoses, and no disease names. Use short, clear sentences. Always end with a question.

STAGE 1 — FIRST MESSAGE ONLY
Your entire reply must include ONLY:
1. “I understand…” + restate symptom.
2. EXACT: “When did this first start, and has it been getting better, worse, or staying the same?”
3. EXACT: “What concerns you most about this?”
Forbidden: empathy, reassurance, advice, extra questions or sentences.

STAGE 2 — ALL OTHER MESSAGES
You will receive TRIAGE_PATH = MILD or EMERGENCY.

IF MILD:
1. Start with “I understand…” + restatement.
2. Add EXACT: “It’s completely understandable that you're concerned about this.”
3. If pain mentioned: add “That sounds really uncomfortable.”
4. Provide EXACTLY 3 numbered steps.
5. Add: “If this isn't improving in X days, please contact a healthcare professional.”
6. Add: “I can provide guidance, but I cannot replace an in-person examination.”
7. End with “How does this sound to you?”

IF EMERGENCY:
1. Start EXACTLY: “Based on what you've told me,”
2. If pain -> add: “That sounds really uncomfortable.”
3. If worry -> add: “It’s completely understandable that you're concerned about this.”
4. Give a simple plain-language reason it may be serious.
5. Add EXACT: “Here’s what I recommend: please seek urgent in-person care now.”
6. Add EXACT: “This is beyond what I can safely assess remotely.”
7. Add EXACT: “I can provide guidance, but I cannot replace an in-person examination.”
8. End: “How does this sound to you?”
"""

# Templates

INTAKE_TEMPLATE = "(Use the Stage 1 template from SYSTEM_PROMPT exactly.)"
MILD_TEMPLATE = "(Use the Stage 2 MILD template from SYSTEM_PROMPT exactly.)"
EMERGENCY_TEMPLATE = "(Use the Stage 2 EMERGENCY template from SYSTEM_PROMPT exactly.)"

# Emergency detection

EMERGENCY_PATTERNS = [
    r"chest pain",
    r"pain in (my )?chest",
    r"tightness in (my )?chest",

    r"short(ned)? of breath",
    r"trouble breathing",
    r"difficulty breathing",
    r"can't breathe",
    r"breathing feels (hard|difficult)",

    r"one[- ]?sided weakness",
    r"weak(ness)? on (one|the) side",
    r"arm feels weak on (one|the) side",
    r"leg feels weak on (one|the) side",

    r"slurred speech",
    r"can't speak clearly",

    r"(sudden|severe) headache",
    r"worst headache",

    r"vision loss",
    r"can't see",
    r"blurry vision suddenly",

    r"confusion",
    r"fainting",
    r"passed out",

    r"vomiting blood",
    r"throwing up blood",
    r"black stool",
]

SEVERITY_RE = re.compile(r"\b([8-9]|10)\s*/\s*10\b")

def detect_emergency(text: str) -> bool:
    t = text.lower()

    # 1. Regex patterns for flexible matching
    for pat in EMERGENCY_PATTERNS:
        if re.search(pat, t):
            return True

    # 2. Severity score
    if SEVERITY_RE.search(t):
        return True

    return False

# Intent router

CLOSING_PHRASES = {
    "thanks","thank you","bye","ok thanks","great thanks",
    "great, thanks","thanks a lot","thank you so much",
    "sounds good","perfect thanks"
}

META_PHRASES = [
    "what do you do", "who are you", "describe what you do",
    "what is your purpose", "help me understand what you do"
]

def detect_intent(user_text):
    t = user_text.lower().strip()
    if any(t == phrase for phrase in CLOSING_PHRASES):
        return "CLOSING"
    if any(q in t for q in META_PHRASES):
        return "META"
    return "TRIAGE"

# LLM call

def call_llm(messages):
    client = OpenAI()
    resp = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0.1,
    )
    return resp.choices[0].message.content

# Validators 

def validate_intake(reply):
    return (
        "I understand" in reply and
        "When did this first start" in reply and
        "What concerns you most" in reply
    )

def validate_mild(reply):
    steps = [l for l in reply.splitlines() if re.match(r"^(1|2|3)[).]", l.strip())]
    return (
        "I understand" in reply and
        "It’s completely understandable that you're concerned about this." in reply and
        len(steps) == 3 and
        "If this isn't improving" in reply and
        "I can provide guidance, but I cannot replace an in-person examination." in reply and
        reply.strip().endswith("How does this sound to you?")
    )

def validate_emergency(reply):
    required = [
        "Based on what you've told me",
        "Here’s what I recommend",
        "This is beyond what I can safely assess remotely",
        "I can provide guidance, but I cannot replace an in-person examination",
        "How does this sound to you?"
    ]
    return all(x in reply for x in required)

# Safe fallback

def safe_fallback():
    return (
        "Based on what you've told me, this could be risky if we don't check in person. "
        "Here’s what I recommend: please seek urgent in-person care now. "
        "This is beyond what I can safely assess remotely. "
        "I can provide guidance, but I cannot replace an in-person examination. "
        "How does this sound to you?"
    )

# ✅ MAIN LOGIC EXTRACTED INTO A FUNCTION

def run_agent(history, user_message, stage):
    """
    history: list of {"role": "...", "content": "..."}
    user_message: string
    stage: int (1 or 2)
    RETURNS: (agent_reply, new_stage)
    """

    # Intent handling BEFORE adding to history 
    intent = detect_intent(user_message)

    if intent == "CLOSING":
        return ("No problem at all. If you need help again, I’m here for you.", stage)

    if intent == "META":
        return ("I’m a primary-care triage assistant. I help you talk through symptoms and decide whether home care or an in-person visit is safer. How can I help you today?", stage)

    # Add user message to history only if triage
    history.append({"role": "user", "content": user_message})

    # Stage 1: intake 
    if stage == 1:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": INTAKE_TEMPLATE},
        ] + history

        reply = call_llm(messages)

        if not validate_intake(reply):
            messages.append({"role": "system", "content": "Follow Stage 1 EXACTLY."})
            retry = call_llm(messages)
            reply = retry if validate_intake(retry) else safe_fallback()

        return reply, 2

    # Stage 2: triage 
    full_text = " ".join(m["content"] for m in history if m["role"] == "user")
    emergency = detect_emergency(full_text)

    triage_template = EMERGENCY_TEMPLATE if emergency else MILD_TEMPLATE

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"TRIAGE_PATH: {'EMERGENCY' if emergency else 'MILD'}"},
        {"role": "system", "content": triage_template},
    ] + history

    reply = call_llm(messages)

    is_valid = validate_emergency(reply) if emergency else validate_mild(reply)
    if not is_valid:
        messages.append({"role": "system", "content": "Your reply must match the template exactly. Regenerate."})
        retry = call_llm(messages)
        reply = retry if (validate_emergency(retry) if emergency else validate_mild(retry)) else safe_fallback()

    return reply, stage
