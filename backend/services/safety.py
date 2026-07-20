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
    
    # Poisoning
    r"\bpoison\b",
    r"\bpoisoned\b",
    r"\bswallowed\s+toxic\b",
    r"\bswallowed\s+bleach\b",
    
    # Overdose
    r"\boverdose\b",
    r"\btook\s+too\s+many\s+pills\b",
    
    # Seizure
    r"\bseizure\b",
    r"\bconvulsions\b"
]

EMERGENCY_ADVICE = (
    "CRITICAL MEDICAL EMERGENCY DETECTED: If you or someone around you is experiencing severe symptoms "
    "such as chest pain, difficulty breathing, stroke signs, heavy bleeding, loss of consciousness, poisoning, "
    "or suicidal thoughts, please contact your local emergency services (like 911, 112, or 999) or proceed "
    "to the nearest emergency room immediately."
)

def check_safety(query: str) -> Dict[str, Any]:
    """
    Evaluates user input for emergency medical red flags.
    Returns a dictionary with status ("EMERGENCY" or "NORMAL"), detected triggers, and emergency guidance.
    """
    if not query:
        return {
            "status": "NORMAL",
            "is_emergency": False,
            "trigger": None,
            "advice": None
        }

    text = query.lower()

    for pattern in EMERGENCY_KEYWORDS:
        match = re.search(pattern, text)
        if match:
            trigger_text = match.group(0)
            return {
                "status": "EMERGENCY",
                "is_emergency": True,
                "trigger": trigger_text,
                "advice": EMERGENCY_ADVICE
            }

    return {
        "status": "NORMAL",
        "is_emergency": False,
        "trigger": None,
        "advice": None
    }
