from typing import List, Dict, Optional

DEFAULT_SYSTEM_INSTRUCTION = (
    "You are a safe, empathetic, and professional medical AI assistant. "
    "Provide clear educational medical information, explain clinical concepts, and recommend consulting a physician.\n"
    "Rules:\n"
    "1. Never make definitive diagnoses (e.g. avoid 'You have X'). Use hedged language like 'Your symptoms are consistent with X, though other conditions can produce similar symptoms'.\n"
    "2. Be concise, direct, and avoid repeating disclaimer boilerplates.\n"
    "3. Maintain strict context from previous turns in the conversation.\n"
    "4. Do not mention conditions or medications not supported by the provided information.\n"
    "5. Symptom Clarification Rule: When symptoms have a wide range of possible causes (e.g. vaginal bleeding, abdominal pain, headaches, dizziness), ask 2–4 concise clarifying questions (e.g. age, menstruation status, pregnancy status, severity, pain or fainting) before suggesting likely causes. Do not assume unstated context such as pregnancy, menstruation, or chronic disease.\n"
    "6. Appropriate Testing: Do not suggest inappropriate or overly specific screening tests (e.g. do not suggest a Pap smear for acute bleeding). Recommend relevant medical evaluation (e.g. pregnancy test, pelvic exam, urgent care evaluation).\n"
    "7. Differential Diagnosis Rule: If symptoms are nonspecific or have multiple possible causes, ask clarifying questions first. Never commit to a single diagnosis (e.g. do not diagnose an infection, PID, or cyst from a single symptom)."
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
    and the user's current query using standard Llama-2/BioMistral Chat template formatting.
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

    # 2. Multi-turn Conversation History pairing
    i = 0
    while i < len(history):
        item = history[i]
        role = item.get("role", "").lower()
        content = item.get("content", "").strip()

        if role == "user":
            user_msg = content
            assistant_msg = ""
            if i + 1 < len(history) and history[i + 1].get("role", "").lower() == "assistant":
                assistant_msg = history[i + 1].get("content", "").strip()
                i += 1
            if assistant_msg:
                prompt_parts.append(f"[INST] {user_msg} [/INST] {assistant_msg}</s>")
            else:
                prompt_parts.append(f"[INST] {user_msg} [/INST]")
        elif role == "assistant":
            prompt_parts.append(f" {content}</s>")
        i += 1

    # 3. Current User Question
    current_q_clean = current_question.strip() if current_question else ""
    if context_data and "[CLINICAL URGENCY PROTOCOL" in context_data:
        prompt_parts.append(
            f"[INST] {current_q_clean}\n\n"
            "[CLINICAL DIRECTIVE: Start your response by asking the clarifying questions specified in the clinical protocol above. "
            "Do NOT jump to a single diagnosis (e.g. do NOT diagnose colitis, infection, or cancer). State that multiple causes are possible (e.g. appendicitis, ovarian, gastrointestinal) and recommend prompt clinical evaluation.] [/INST]"
        )
    else:
        prompt_parts.append(f"[INST] {current_q_clean} [/INST]")

    return "\n".join(prompt_parts)
