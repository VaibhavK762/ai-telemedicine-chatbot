import pytest
from backend.services.conversation import ConversationManager

def test_conversation_manager_add_and_get():
    mgr = ConversationManager(default_max_turns=3)
    session_id = "test_session_1"
    
    mgr.add_user_message(session_id, "Hello")
    mgr.add_assistant_message(session_id, "Hi there, how can I help?")
    
    history = mgr.get_history(session_id)
    assert len(history) == 2
    assert history[0] == {"role": "user", "content": "Hello"}
    assert history[1] == {"role": "assistant", "content": "Hi there, how can I help?"}

def test_conversation_manager_max_turns():
    mgr = ConversationManager(default_max_turns=2)  # max 4 messages
    session_id = "test_session_2"
    
    for i in range(5):
        mgr.add_user_message(session_id, f"User msg {i}")
        mgr.add_assistant_message(session_id, f"Assistant msg {i}")
        
    history = mgr.get_history(session_id)
    assert len(history) == 4  # max 2 turns * 2 messages
    assert history[0]["content"] == "User msg 3"
    assert history[-1]["content"] == "Assistant msg 4"

def test_conversation_manager_clear():
    mgr = ConversationManager()
    session_id = "test_session_3"
    mgr.add_user_message(session_id, "Hello")
    mgr.clear_history(session_id)
    assert len(mgr.get_history(session_id)) == 0
