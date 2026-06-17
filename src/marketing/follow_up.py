from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from src.marketing.sheets_tracker import SheetsTracker
from src.marketing.content_generator import ContentGenerator
from src.marketing.template_engine import TemplateEngine
from mcp_server.tools.n8n_hook import trigger_n8n_marketing_pipeline


@dataclass
class FollowUpConfig:
    enabled: bool = True
    initial_delay_days: int = 3
    max_follow_ups: int = 3
    cadence_days: int = 7


class FollowUpManager:
    def __init__(self):
        self.config = FollowUpConfig()
        self.tracker = SheetsTracker()
        self.content_gen = ContentGenerator()
        self.template_engine = TemplateEngine()

    def set_config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    def check_due_follow_ups(self) -> list[dict]:
        if not self.config.enabled:
            return []
        leads = self.tracker.get_all_leads()
        due = []
        now = datetime.now()

        for lead in leads:
            status = lead["status"]
            follow_up_count = lead.get("follow_up_count", 0)

            if follow_up_count >= self.config.max_follow_ups:
                continue

            if status == "Sent":
                sent_date_str = lead.get("sent_date")
                if sent_date_str:
                    sent_date = datetime.fromisoformat(sent_date_str)
                    if now - sent_date >= timedelta(days=self.config.initial_delay_days):
                        due.append(lead)
            elif status.startswith("FollowUp_"):
                last_fu_str = lead.get("last_follow_up_date")
                if last_fu_str:
                    last_fu = datetime.fromisoformat(last_fu_str)
                    if now - last_fu >= timedelta(days=self.config.cadence_days):
                        due.append(lead)

        return due

    def send_follow_up(self, session_id: str) -> dict:
        leads = self.tracker.get_all_leads()
        lead = None
        for l in leads:
            if l["session_id"] == session_id:
                lead = l
                break
        if not lead:
            return {"success": False, "error": "Lead not found"}

        follow_up_number = lead.get("follow_up_count", 0) + 1
        if follow_up_number > self.config.max_follow_ups:
            return {"success": False, "error": "Max follow-ups reached"}

        email_body = self.content_gen.generate_email_body(
            product=lead["product"],
            customer_name=lead["customer_name"],
            customer_sector="General",
            customer_needs="Following up on previous proposal",
        )

        payload = {
            "lead_name": lead["customer_name"],
            "validated_email": lead["email"],
            "tender_requirements": f"Follow-up #{follow_up_number}",
            "email_body": email_body,
        }

        result = trigger_n8n_marketing_pipeline(payload)

        new_status = f"FollowUp_{follow_up_number}"
        self.tracker.update_status(session_id, new_status)

        return {
            "success": result.get("success", False),
            "follow_up_number": follow_up_number,
            "email_body": email_body,
            "n8n_response": result.get("response"),
        }

    def get_follow_up_schedule(self, session_id: str) -> dict:
        leads = self.tracker.get_all_leads()
        for lead in leads:
            if lead["session_id"] == session_id:
                return {
                    "session_id": session_id,
                    "customer_name": lead["customer_name"],
                    "current_status": lead["status"],
                    "follow_up_count": lead.get("follow_up_count", 0),
                    "max_follow_ups": self.config.max_follow_ups,
                    "last_follow_up_date": lead.get("last_follow_up_date"),
                    "next_follow_up_due": "N/A",
                }
        return {"error": "Lead not found"}
