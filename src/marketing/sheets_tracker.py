import json
import os
from datetime import datetime
from typing import Optional

TRACKING_FILE = "data/campaign_tracking.json"

VALID_STATUSES = ["New", "Sent", "Opened", "Replied", "Meeting Booked"]
VALID_TRANSITIONS = {
    "New": {"Sent"},
    "Sent": {"Opened", "FollowUp_1"},
    "Opened": {"Replied", "FollowUp_1"},
    "Replied": {"Meeting Booked"},
    "FollowUp_1": {"Sent", "FollowUp_2", "Opened"},
    "FollowUp_2": {"Sent", "FollowUp_3", "Opened"},
    "FollowUp_3": {"Sent", "Opened"},
    "Meeting Booked": set(),
}


class SheetsTracker:
    def __init__(self, file_path: str = TRACKING_FILE):
        self.file_path = file_path

    def _load(self) -> list[dict]:
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, "r") as f:
            return json.load(f)

    def _save(self, data: list[dict]):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)

    def add_lead(self, session_id: str, customer_name: str, email: str,
                 product: str, status: str = "New") -> bool:
        if status not in VALID_STATUSES:
            return False
        data = self._load()
        data.append({
            "session_id": session_id,
            "customer_name": customer_name,
            "email": email,
            "product": product,
            "status": status,
            "follow_up_count": 0,
            "last_follow_up_date": None,
            "sent_date": datetime.now().isoformat() if status == "Sent" else None,
            "created_at": datetime.now().isoformat(),
        })
        self._save(data)
        return True

    def update_status(self, session_id: str, new_status: str) -> bool:
        if new_status not in VALID_STATUSES and not new_status.startswith("FollowUp_"):
            return False
        data = self._load()
        for lead in data:
            if lead["session_id"] == session_id:
                current = lead["status"]
                allowed = VALID_TRANSITIONS.get(current, set())
                if new_status not in allowed and new_status != current:
                    # allow FollowUp_N transitions
                    if not (new_status.startswith("FollowUp_") and current in ("Sent", "Opened", "FollowUp_1", "FollowUp_2")):
                        return False
                lead["status"] = new_status
                if new_status == "Sent" and not lead.get("sent_date"):
                    lead["sent_date"] = datetime.now().isoformat()
                if new_status.startswith("FollowUp_"):
                    lead["follow_up_count"] = lead.get("follow_up_count", 0) + 1
                    lead["last_follow_up_date"] = datetime.now().isoformat()
                self._save(data)
                return True
        return False

    def get_campaign_stats(self) -> dict:
        data = self._load()
        stats = {
            "total": len(data),
            "by_status": {},
            "by_product": {},
        }
        for lead in data:
            s = lead["status"]
            stats["by_status"][s] = stats["by_status"].get(s, 0) + 1
            p = lead["product"]
            stats["by_product"][p] = stats["by_product"].get(p, 0) + 1
        if data:
            stats["conversion_rate"] = round(
                stats["by_status"].get("Meeting Booked", 0) / stats["total"] * 100, 1
            )
        return stats

    def get_leads_by_status(self, status: str) -> list[dict]:
        data = self._load()
        return [lead for lead in data if lead["status"] == status]

    def get_all_leads(self) -> list[dict]:
        return self._load()
