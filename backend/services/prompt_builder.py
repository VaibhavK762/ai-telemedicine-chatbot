from typing import List, Dict, Optional

DEFAULT_SYSTEM_INSTRUCTION = (
    "You are a safe, professional medical AI assistant. Provide educational medical information, "
    "explain concepts clearly, and emphasize seeking professional medical care when appropriate. "
    "Do not provide definitive medical diagnoses or prescribe medications."
)

def build_prompt(
    current_question: str,
    history: Optional[List[Dict[str, str]]] = None,
    system_instruction: Optional[str] = None,
    context_data: Optional[str] = None
) -> str:
    """
    Constructs a structured prompt for the LLM combining system instructions,
    additional context (such as lab report analysis), multi-turn conversation history,
    and the user's current query.
    """
    if history is None:
        history = []
    if system_instruction is None:
        system_instruction = DEFAULT_SYSTEM_INSTRUCTION

    prompt_parts = []
    
    # 1. System Instruction & Context Header
    header = f"[SYSTEM INSTRUCTION]\n{system_instruction.strip()}"
    if context_data and context_data.strip():
        header += f"\n\n[ADDITIONAL CLINICAL CONTEXT]\n{context_data.strip()}"
    
    prompt_parts.append(f"<s>[INST] {header} [/INST] Understood. I will provide safe, educational medical guidance.</s>")

    # 2. Multi-turn Conversation History
    for turn in history:
        role = turn.get("role", "user").lower()
        content = turn.get("content", "").strip()
        if role == "user":
            prompt_parts.append(f"[INST] {content} [/INST]")
        elif role == "assistant":
            prompt_parts.append(f" {content}</s>")

    # 3. Current User Question
    current_q_clean = current_question.strip() if current_question else ""
    prompt_parts.append(f"[INST] {current_q_clean} [/INST]")

    return "\n".join(prompt_parts)
