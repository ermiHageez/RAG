from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict
import operator


def _merge_lists(left: List | None, right: List | None) -> List:
    return (left or []) + (right or [])


def _override(val: Any | None, new_val: Any | None) -> Any | None:
    return new_val if new_val is not None else val


class AgentState(TypedDict):
    query: str

    route: Annotated[List[str], _merge_lists]

    qualified_leads: Annotated[List[Dict[str, Any]], _merge_lists]
    qualified_tenders: Annotated[List[Dict[str, Any]], _merge_lists]
    knowledge_context: Annotated[List[Dict[str, Any]], _merge_lists]

    sales_intelligence: Annotated[Optional[Dict[str, Any]], _override]

    draft_email: Annotated[Optional[Dict[str, Any]], _override]

    requires_human_approval: Annotated[Optional[bool], _override]
    approval_reason: Annotated[Optional[str], _override]

    n8n_payload: Annotated[Optional[Dict[str, Any]], _override]
