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
    trigger: Optional[str] = None
    history: List[Dict[str, str]] = []

@router.post("", response_model=ChatResponse)
@router.post("/send", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Core Chat Endpoint.
    Pipeline: Receive question -> Conversation history -> Safety layer -> Prompt builder -> LLM client -> Cleaner -> Return JSON
    """
    query = request.message.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")

    # 1. Get or initialize session ID
    session_id = conversation_manager.get_or_create_session(request.session_id)

    # 2. Safety Layer Check
    safety_result = check_safety(query)
    
    if safety_result["is_emergency"]:
        emergency_resp = safety_result["advice"]
        conversation_manager.add_user_message(session_id, query)
        conversation_manager.add_assistant_message(session_id, emergency_resp)
        return ChatResponse(
            response=emergency_resp,
            session_id=session_id,
            status=safety_result["status"],
            is_emergency=True,
            trigger=safety_result["trigger"],
            history=conversation_manager.get_history(session_id)
        )

    # 3. Retrieve conversation history
    history = conversation_manager.get_history(session_id)

    # 4. Prompt Builder
    prompt = build_prompt(current_question=query, history=history)

    # 5. LLM Client Generation
    raw_llm_output = generate(prompt)

    # 6. Response Cleaner
    cleaned_output = clean_response(raw_llm_output)

    # 7. Store user turn & assistant turn in conversation history
    conversation_manager.add_user_message(session_id, query)
    conversation_manager.add_assistant_message(session_id, cleaned_output)

    return ChatResponse(
        response=cleaned_output,
        session_id=session_id,
        status="NORMAL",
        is_emergency=False,
        trigger=None,
        history=conversation_manager.get_history(session_id)
    )

@router.delete("/history/{session_id}")
def clear_chat_history(session_id: str):
    """Clears history for a given session."""
    conversation_manager.clear_history(session_id)
    return {"message": f"History cleared for session {session_id}"}
