from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

from backend.services.conversation import conversation_manager
from backend.services.safety import check_safety
from backend.services.prompt_builder import build_prompt
from backend.services.llm_client import generate
from backend.services.response_cleaner import clean_response

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str
    is_emergency: bool
    is_urgent: bool = False
    trigger: Optional[str] = None
    history: List[Dict[str, str]] = []

@router.post("", response_model=ChatResponse)
@router.post("/send", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Core Chat Endpoint.
    Pipeline: Receive question -> Session -> Safety layer -> Prompt builder -> LLM client -> Cleaner -> Store history -> Return JSON
    """
    query = request.message.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")

    # 1. Get or initialize session ID
    session_id = conversation_manager.get_or_create_session(request.session_id)
    print(f"\n[chat] === INCOMING REQUEST [Session: {session_id}] ===")
    print(f"[chat] Query: {query}")

    # 2. Safety Layer Check (NORMAL / URGENT / EMERGENCY)
    safety_result = check_safety(query)
    print(f"[safety] Triage Status: {safety_result['status']} | Trigger: {safety_result['trigger']}")
    
    if safety_result["is_emergency"]:
        emergency_resp = safety_result["advice"]
        conversation_manager.add_user_message(session_id, query)
        conversation_manager.add_assistant_message(session_id, emergency_resp)
        return ChatResponse(
            response=emergency_resp,
            session_id=session_id,
            status=safety_result["status"],
            is_emergency=True,
            is_urgent=False,
            trigger=safety_result["trigger"],
            history=conversation_manager.get_history(session_id)
        )

    # 3. Retrieve conversation history
    history = conversation_manager.get_history(session_id)

    # 4. Prompt Builder with Clinical Urgency Constraints if URGENT status detected
    urgent_context = None
    if safety_result["is_urgent"]:
        trigger_clean = (safety_result.get("trigger") or "symptoms").upper()
        q_list = safety_result.get("questions", [])
        q_formatted = "\n".join([f"- {q}" for q in q_list]) if q_list else "- What is your age and period status?\n- Could you be pregnant?"

        urgent_context = (
            f"[CLINICAL URGENCY PROTOCOL: {trigger_clean}]\n"
            "Instructions for Medical Assistant:\n"
            "1. BEFORE discussing general possibilities, START your response by asking these specific clarifying questions to gather essential context:\n"
            f"{q_formatted}\n"
            "2. Do NOT jump to a single diagnosis (e.g. do NOT diagnose an infection, PID, cancer, or cysts).\n"
            "3. Do NOT assume unstated context such as normal menstruation or pregnancy.\n"
            "4. Do NOT prescribe antibiotics, suggest tests like Pap smears for acute bleeding, or list broad lab panels (LFT, blood sugar).\n"
            "5. Advise prompt clinical evaluation by a healthcare provider or specialist."
        )

    prompt = build_prompt(current_question=query, history=history, context_data=urgent_context)
    print(f"[chat] ASSEMBLED PROMPT SENT TO MODEL:\n{prompt}\n")

    # 5. LLM Client Generation
    raw_llm_output = generate(prompt)

    # 6. Response Cleaner
    cleaned_output = clean_response(raw_llm_output)

    # If urgent warning was triggered, prepend advice to cleaned output
    if safety_result["is_urgent"]:
        cleaned_output = f"{safety_result['advice']}\n\n{cleaned_output}"

    print(f"[chat] CLEANED RESPONSE:\n{cleaned_output}\n")

    # 7. Store user turn & assistant turn in conversation history
    conversation_manager.add_user_message(session_id, query)
    conversation_manager.add_assistant_message(session_id, cleaned_output)

    return ChatResponse(
        response=cleaned_output,
        session_id=session_id,
        status=safety_result["status"],
        is_emergency=False,
        is_urgent=safety_result["is_urgent"],
        trigger=safety_result["trigger"],
        history=conversation_manager.get_history(session_id)
    )

@router.delete("/history/{session_id}")
def clear_chat_history(session_id: str):
    """Clears history for a given session."""
    conversation_manager.clear_history(session_id)
    return {"message": f"History cleared for session {session_id}"}
