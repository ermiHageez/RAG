from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict
import operator


def _merge_lists(left: List[Any] | None, right: List[Any] | None) -> List[Any]:
    if left is None:
        left = []
    if right is None:
        right = []
    return left + right


def _merge_dicts(left: Dict[str, Any] | None, right: Dict[str, Any] | None) -> Dict[str, Any]:
    return {**(left or {}), **(right or {})}


def _override(val: Any | None, new_val: Any | None) -> Any | None:
    return new_val if new_val is not None else val


class AgentState(TypedDict):
    query: str
    rag_context: Annotated[List[str], _merge_lists]
    found_leads: Annotated[List[Dict[str, Any]], _merge_lists]
    active_tender_listings: Annotated[List[Dict[str, Any]], _merge_lists]
    sales_intel: Annotated[List[Dict[str, Any]], _merge_lists]
    sales_report: Annotated[Optional[str], _override]
    email_drafts: Annotated[List[Dict[str, Any]], _merge_lists]
    n8n_payload: Optional[Dict[str, Any]]
