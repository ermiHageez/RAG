import enum
import uuid
from dataclasses import dataclass, field
from typing import Optional


class SalesPhase(str, enum.Enum):
    DISCOVERY = "DISCOVERY"
    RESEARCH = "RESEARCH"
    GENERATION = "GENERATION"
    COMPLETE = "COMPLETE"


LEGAL_TRANSITIONS = {
    SalesPhase.DISCOVERY: {SalesPhase.RESEARCH},
    SalesPhase.RESEARCH: {SalesPhase.GENERATION},
    SalesPhase.GENERATION: {SalesPhase.COMPLETE},
    SalesPhase.COMPLETE: set(),
}


@dataclass
class SalesSession:
    session_id: str
    phase: SalesPhase = SalesPhase.DISCOVERY
    customer_info: dict = field(default_factory=dict)
    research_data: dict = field(default_factory=dict)
    proposal_text: Optional[str] = None
    proposal_pdf_path: Optional[str] = None
    email_body: Optional[str] = None
    approved: bool = False
    messages: list[dict] = field(default_factory=list)


class SalesEngine:
    def __init__(self):
        self._sessions: dict[str, SalesSession] = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = SalesSession(session_id=session_id)
        return session_id

    def get_session(self, session_id: str) -> Optional[SalesSession]:
        return self._sessions.get(session_id)

    def transition(self, session_id: str, target_phase: SalesPhase) -> bool:
        session = self.get_session(session_id)
        if session is None:
            return False
        current = session.phase
        allowed = LEGAL_TRANSITIONS.get(current, set())
        if target_phase not in allowed:
            return False
        session.phase = target_phase
        return True

    def reset_session(self, session_id: str) -> bool:
        session = self.get_session(session_id)
        if session is None:
            return False
        session.phase = SalesPhase.DISCOVERY
        session.customer_info = {}
        session.research_data = {}
        session.proposal_text = None
        session.proposal_pdf_path = None
        session.email_body = None
        session.approved = False
        session.messages = []
        return True

    def add_message(self, session_id: str, role: str, content: str):
        session = self.get_session(session_id)
        if session:
            session.messages.append({"role": role, "content": content})
