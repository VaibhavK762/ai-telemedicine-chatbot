import re

BOILERPLATE_PATTERNS = [
    r"(?i)\bChat\s*Doctor\b[ \t,.]*",
    r"(?i)\bRegards\b[ \t,.]*",
    r"(?i)\bThanks\s+for\s+writing\s+in\b[ \t,.]*",
    r"(?i)\bHello\s+dear\b[ \t,.]*",
    r"(?i)\bHope\s+this\s+helps\b[ \t,.]*",
    r"(?i)\bBest\s+regards\b[ \t,.]*",
    r"(?i)\bSincerely\b[ \t,.]*",
    r"(?i)\bTake\s+care\b[ \t,.]*"
]

def clean_response(text: str) -> str:
    """
    Cleans raw text output from the model by stripping common chat doctor signatures,
    boilerplates, duplicate punctuation, and multiple blank lines.
    """
    if not text:
        return ""

    cleaned = text

    # Remove boilerplate phrases
    for pattern in BOILERPLATE_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned)

    # Clean up orphaned punctuation (e.g. ", ,", "^,", "^.")
    cleaned = re.sub(r"^\s*[,.]\s*", "", cleaned)
    cleaned = re.sub(r"\s*,\s*,\s*", ", ", cleaned)
    cleaned = re.sub(r"\s*\.\s*\.\s*", ". ", cleaned)
    cleaned = re.sub(r"\s+([,.:;?!])", r"\1", cleaned)

    # Clean up duplicate punctuation (e.g. "!!" -> "!", "??" -> "?", ",," -> ",")
    cleaned = re.sub(r"(!){2,}", "!", cleaned)
    cleaned = re.sub(r"(\?){2,}", "?", cleaned)
    cleaned = re.sub(r"(,){2,}", ",", cleaned)
    cleaned = re.sub(r"(?<!\.)\.\.(?!\.)", ".", cleaned)  # double dot into single dot

    # Normalize trailing commas / whitespace at end of text
    cleaned = re.sub(r"\s*,+\s*$", "", cleaned)

    # Normalize multiple blank lines (3 or more newlines into 2)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Clean up right-side whitespace on each line while preserving empty lines (paragraph breaks)
    lines = [line.rstrip() for line in cleaned.split("\n")]
    cleaned = "\n".join(lines).strip()

    return cleaned



