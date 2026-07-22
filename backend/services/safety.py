import re
from typing import Dict, Any

EMERGENCY_KEYWORDS = [
    # Chest pain & Cardiac
    r"\bchest\s+pain\b",
    r"\bheart\s+attack\b",
    r"\bcardiac\s+arrest\b",

    # Difficulty breathing
    r"\bdifficulty\s+breathing\b",
    r"\bshortness\s+of\s+breath\b",
    r"\bcannot\s+breathe\b",
    r"\bcan't\s+breathe\b",
    r"\basphyxiation\b",

    # Stroke symptoms
    r"\bstroke\b",
    r"\bfacial\s+droop\b",
    r"\bsudden\s+numbness\b",
    r"\bslurred\s+speech\b",

    # Heavy bleeding
    r"\bheavy\s+bleeding\b",
    r"\buncontrolled\s+bleeding\b",
    r"\bhemorrhage\b",

    # Unconscious / Fainting
    r"\bunconscious\b",
    r"\bpassed\s+out\b",
    r"\bunresponsive\b",

    # Suicidal / Self-harm
    r"\bsuicidal\b",
    r"\bsuicide\b",
    r"\bkill\s+myself\b",
    r"\bend\s+my\s+life\b",
    r"\bself[- ]harm\b",

    # Poisoning / Overdose / Seizure
    r"\bpoison(ed)?\b",
    r"\boverdose\b",
    r"\bswallowed\s+toxic\b",
    r"\bseizure\b",
    r"\bconvulsions\b"
]

URGENT_KEYWORDS = [
    # Appendicitis / Abdominal / Stomach pain (including lower right, RLQ, abdominal pain, stomach pain)
    r"\bappendicitis\b",
    r"\b(lower\s+right|right\s+lower|rlq)\b",
    r"\b(abdominal|stomach|belly|flank)\s+pain\b",
    r"\bpain\s+in\s+(my\s+)?(abdomen|stomach|belly|flank|lower\s+right)\b",
    r"\b(stomach|abdominal)\s+ache\b",

    # Kidney stones
    r"\bkidney\s+stone(s)?\b",

    # High fever / Pneumonia
    r"\bhigh\s+fever\b",
    r"\bpneumonia\b",

    # Difficulty swallowing / Vision changes / Vomiting / Nausea
    r"\bsevere\s+difficulty\s+swallowing\b",
    r"\bsudden\s+vision\s+loss\b",
    r"\b(persistent\s+)?vomiting\b",
    r"\bnausea\b"
]

GYNECOLOGICAL_EMERGENCY_PATTERNS = [
    # Vaginal bleeding combined with emergency indicators (pregnancy, miscarriage, fainting, dizziness, severe pain, heavy flow/clots)
    r"(?=.*\b(bleeding|blood)\b.*\b(vagina|vaginal|pussy|down\s+there)\b)(?=.*\b(pregnant|pregnancy|miscarriage|fainting|faint|dizzy|dizziness|shock|soaking|soak|clots|severe\s+pain)\b)",
    r"(?=.*\b(vagina|vaginal|pussy|down\s+there)\b.*\b(bleeding|blood)\b)(?=.*\b(pregnant|pregnancy|miscarriage|fainting|faint|dizzy|dizziness|shock|soaking|soak|clots|severe\s+pain)\b)",
    r"\b(bleeding\s+during\s+pregnancy|pregnant\s+and\s+bleeding|miscarriage\s+bleeding)\b",
    r"\bsoaking\s+(a\s+)?pad\s+every\s+hour\b",
    r"\bsoaking\s+through\s+pads\b"
]

GYNECOLOGICAL_URGENT_PATTERNS = [
    # Unexplained vaginal bleeding / abnormal bleeding (matches 'bleeding from my pussy', 'blood from vagina', etc.)
    r"\b(bleeding|blood)\b.{0,30}\b(vagina|vaginal|pussy|down\s+there)\b",
    r"\b(vagina|vaginal|pussy|down\s+there)\b.{0,30}\b(bleeding|blood)\b",
    r"\b(abnormal\s+vaginal\s+bleeding|spotting\s+between\s+periods|heavy\s+period)\b"
]

CLINICAL_QUESTIONS_MAP = {
    "gynecological": [
        "Are you currently on your period, or near your expected menstrual cycle?",
        "Are you pregnant, or is there any possibility you could be pregnant?",
        "How heavy is the bleeding (e.g., light spotting vs. soaking a pad every hour)?",
        "Are you experiencing severe abdominal/pelvic pain, fever, dizziness, or fainting?"
    ],
    "kidney_stone": [
        "Where is your pain located (e.g., lower back/flank, side, or radiating to the groin)?",
        "Are you experiencing burning during urination, cloudy/bloody urine, or fever?",
        "Is the pain severe, sharp, or coming in waves?",
        "Are you experiencing persistent nausea or vomiting?"
    ],
    "appendicitis": [
        "Did the pain start around your belly button and move to the lower right side of your abdomen?",
        "Does the pain worsen when you walk, cough, or press on your abdomen?",
        "Are you experiencing fever, loss of appetite, nausea, or vomiting?"
    ],
    "general": [
        "How long have you been experiencing these symptoms?",
        "How severe is the discomfort or pain on a scale of 1 to 10?",
        "Are you experiencing any other associated symptoms like fever, shortness of breath, or dizziness?"
    ]
}

EMERGENCY_ADVICE = (
    "CRITICAL MEDICAL EMERGENCY DETECTED: If you or someone around you is experiencing severe symptoms "
    "such as chest pain, difficulty breathing, stroke signs, heavy bleeding (such as soaking through pads rapidly), "
    "bleeding during pregnancy, loss of consciousness, severe abdominal pain, poisoning, or suicidal thoughts, "
    "please contact your local emergency services (like 911, 112, or 999) or proceed to the nearest emergency room immediately."
)

URGENT_ADVICE = (
    "URGENT MEDICAL EVALUATION RECOMMENDED: Symptoms such as lower right abdominal pain, unexplained vaginal bleeding, "
    "suspected appendicitis, kidney stone pain, high fever, or severe persistent symptoms warrant prompt medical attention. "
    "Please visit an urgent care center or contact your healthcare provider promptly for clinical evaluation."
)


def _get_clinical_questions(text: str) -> list:
    if re.search(r"\b(vagina|vaginal|pussy|bleeding|blood|period|pregnancy|pregnant)\b", text):
        return CLINICAL_QUESTIONS_MAP["gynecological"]
    if re.search(r"\b(kidney\s+stone|flank\s+pain)\b", text):
        return CLINICAL_QUESTIONS_MAP["kidney_stone"]
    if re.search(r"\b(appendicitis|stomach|abdominal|belly|lower\s+right|rlq)\b", text):
        return CLINICAL_QUESTIONS_MAP["appendicitis"]
    return CLINICAL_QUESTIONS_MAP["general"]


def check_safety(query: str) -> Dict[str, Any]:
    """
    Evaluates user input for emergency medical red flags, contextual red flags, and urgent symptoms.
    Returns a dictionary with status ("EMERGENCY", "URGENT", or "NORMAL"), detected triggers, guidance, and questions.
    """
    if not query:
        return {
            "status": "NORMAL",
            "is_emergency": False,
            "is_urgent": False,
            "trigger": None,
            "advice": None,
            "questions": []
        }

    text = query.lower()

    # 1. Check General & Gynecological Emergency Keywords
    for pattern in EMERGENCY_KEYWORDS + GYNECOLOGICAL_EMERGENCY_PATTERNS:
        match = re.search(pattern, text)
        if match:
            trigger_text = match.group(0)
            return {
                "status": "EMERGENCY",
                "is_emergency": True,
                "is_urgent": False,
                "trigger": trigger_text,
                "advice": EMERGENCY_ADVICE,
                "questions": _get_clinical_questions(text)
            }

    # 2. Check General & Gynecological Urgent Keywords
    for pattern in URGENT_KEYWORDS + GYNECOLOGICAL_URGENT_PATTERNS:
        match = re.search(pattern, text)
        if match:
            trigger_text = match.group(0)
            return {
                "status": "URGENT",
                "is_emergency": False,
                "is_urgent": True,
                "trigger": trigger_text,
                "advice": URGENT_ADVICE,
                "questions": _get_clinical_questions(text)
            }

    # 3. Default Normal Status
    return {
        "status": "NORMAL",
        "is_emergency": False,
        "is_urgent": False,
        "trigger": None,
        "advice": None,
        "questions": []
    }
