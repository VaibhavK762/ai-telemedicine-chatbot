from typing import Dict, List
import uuid

class ConversationManager:
    """
    In-memory conversation state manager that tracks user and assistant messages per session.
    """

    def __init__(self, default_max_turns: int = 6):
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self.default_max_turns = default_max_turns

    def get_or_create_session(self, session_id: str = None) -> str:
        """Generates or validates session ID."""
        if not session_id or session_id not in self.sessions:
            session_id = session_id or str(uuid.uuid4())
            self.sessions[session_id] = []
        return session_id

    def add_message(self, session_id: str, role: str, content: str):
        """Appends a message (user or assistant) to a session history."""
        session_id = self.get_or_create_session(session_id)
        self.sessions[session_id].append({
            "role": role,
            "content": content
        })

    def add_user_message(self, session_id: str, content: str):
        self.add_message(session_id, "user", content)

    def add_assistant_message(self, session_id: str, content: str):
        self.add_message(session_id, "assistant", content)

    def get_history(self, session_id: str, max_turns: int = None) -> List[Dict[str, str]]:
        """
        Returns the last N messages for a given session.
        A turn equals 2 messages (user + assistant).
        """
        if session_id not in self.sessions:
            return []
        
        limit = max_turns if max_turns is not None else self.default_max_turns
        messages = self.sessions[session_id]
        
        # Calculate message count (max_turns * 2)
        max_messages = limit * 2
        return messages[-max_messages:] if len(messages) > max_messages else list(messages)

    def clear_history(self, session_id: str):
        """Clears stored history for a session."""
        if session_id in self.sessions:
            self.sessions[session_id] = []

# Global singleton instance
conversation_manager = ConversationManager()
