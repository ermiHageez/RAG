import json
import re
from src.agents.llm import get_router_llm
from src.agents.state import AgentState


def _parse_route(text: str) -> list[str]:
    if not text:
        return ["knowledge"]
    try:
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            data = json.loads(match.group())
            route = data.get("route", [])
            if isinstance(route, list) and route:
                return route
    except (json.JSONDecodeError, TypeError):
        pass
    text_lower = text.lower()
    route = []
    if any(w in text_lower for w in ["lead", "company", "enterprise", "business"]):
        route.append("lead")
    if any(w in text_lower for w in ["tender", "procurement", "bid", "ጨረታ"]):
        route.append("tender")
    if any(w in text_lower for w in ["know", "what", "who", "how", "capability", "service", "product"]):
        route.append("knowledge")
    return route or ["knowledge"]


def supervisor_agent(state: AgentState) -> dict:
    llm = get_router_llm()
    query = state.get("query", "")

    prompt = (
        f"Classify this sales/marketing query and determine which agents are required.\n\n"
        f"Query: {query}\n\n"
        f"Available agents:\n"
        f"- lead: discover companies, find prospects, search for businesses\n"
        f"- tender: find procurement tenders, bids, RFPs\n"
        f"- knowledge: answer questions about company capabilities, products, services\n\n"
        f"Respond with ONLY a JSON object: {{\"route\": [\"agent1\", \"agent2\", ...]}}"
    )

    try:
        response = llm.invoke(prompt)
        route = _parse_route(str(response.content))
    except Exception as e:
        print(f"[Supervisor] LLM routing failed ({e}), falling back to keyword matching")
        route = _parse_route(query)

    print(f"[Supervisor] Query: '{query}' -> Route: {route}")
    return {"route": route}
