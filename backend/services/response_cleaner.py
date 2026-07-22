import re

SPECIAL_TOKENS = [
    r"\[INST\]",
    r"\[/INST\]",
    r"<s>",
    r"</s>",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    r"\[SYSTEM INSTRUCTION\]",
    r"\[ADDITIONAL CLINICAL CONTEXT\]"
]

BOILERPLATE_PATTERNS = [
    r"(?i)\bChat\s*Doctor\b[ \t,.]*",
    r"(?i)\bRegards\b[ \t,.]*",
    r"(?i)\bBest\s+Wishes\b[ \t,.]*",
    r"(?i)\bThanks\s+for\s+writing\s+(in)?\b[ \t,.]*",
    r"(?i)\bHello\s+dear\b[ \t,.]*",
    r"(?i)\bHi\s+dear\b[ \t,.]*",
    r"(?i)\bHope\s+this\s+helps\b[ \t,.]*",
    r"(?i)\bBest\s+regards\b[ \t,.]*",
    r"(?i)\bSincerely\b[ \t,.]*",
    r"(?i)\bTake\s+care\b[ \t,.]*",
    r"(?i)\bLy/[a-zA-Z0-9_-]*",
    r"https?://\S+",
    r"bit\.ly/\S+"
]

def clean_response(text: str) -> str:
    """
    Cleans raw text output from the model by stripping special LLM tokens,
    ChatDoctor signatures, boilerplates, duplicate punctuation, and multiple blank lines.
    """
    if not text:
        return ""

    cleaned = text

    # 1. Strip special tokens and instruction tags
    for token_pattern in SPECIAL_TOKENS:
        cleaned = re.sub(token_pattern, "", cleaned)

    # 2. Remove boilerplate phrases & URLs
    for pattern in BOILERPLATE_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned)

    # 3. Clean up orphaned punctuation (e.g. ", ,", "^,", "^.")
    cleaned = re.sub(r"^\s*[,.]\s*", "", cleaned)
    cleaned = re.sub(r"\s*,\s*,\s*", ", ", cleaned)
    cleaned = re.sub(r"\s*\.\s*\.\s*", ". ", cleaned)
    cleaned = re.sub(r"\s+([,.:;?!])", r"\1", cleaned)

    # 4. Clean up duplicate punctuation
    cleaned = re.sub(r"(!){2,}", "!", cleaned)
    cleaned = re.sub(r"(\?){2,}", "?", cleaned)
    cleaned = re.sub(r"(,){2,}", ",", cleaned)
    cleaned = re.sub(r"(?<!\.)\.\.(?!\.)", ".", cleaned)  # double dot into single dot

    # 5. Normalize trailing commas / whitespace at end of text
    cleaned = re.sub(r"\s*,+\s*$", "", cleaned)

    # 6. Normalize multiple blank lines (3 or more newlines into 2)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # 7. Clean up right-side whitespace on each line while preserving empty lines
    lines = [line.rstrip() for line in cleaned.split("\n")]
    cleaned = "\n".join(lines).strip()

    return cleaned



