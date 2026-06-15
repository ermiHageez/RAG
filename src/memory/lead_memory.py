from src.memory.base import MemoryStore


LEADS_KEY = "leads"


class LeadMemory:
    def __init__(self, store: MemoryStore):
        self.store = store

    def save_leads(self, leads: list[dict]) -> None:
        existing = self.store.load(LEADS_KEY) or []
        existing.extend(leads)
        self.store.save(LEADS_KEY, existing)

    def get_leads(self) -> list[dict]:
        return self.store.load(LEADS_KEY) or []

    def deduplicate(self) -> list[dict]:
        leads = self.get_leads()
        seen = set()
        unique = []
        for lead in leads:
            name = lead.get("company_name", "").lower().strip()
            if name and name not in seen:
                seen.add(name)
                unique.append(lead)
        return unique

    def clear(self) -> None:
        self.store.delete(LEADS_KEY)
