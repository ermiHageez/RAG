import os
import time
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2.0

REQUIRED_FIELDS = ["lead_name", "tender_requirements", "validated_email", "email_body"]


def _validate_payload(payload: Dict[str, Any]) -> Optional[str]:
    for field in REQUIRED_FIELDS:
        if field not in payload:
            return f"Missing required field: '{field}'"
        if not payload[field]:
            return f"Field '{field}' is empty"
    return None


def trigger_n8n_marketing_pipeline(payload: Dict[str, Any]) -> Dict[str, Any]:
    validation_error = _validate_payload(payload)
    if validation_error:
        return {"success": False, "error": validation_error, "response": None}

    webhook_url = os.getenv("N8N_WEBHOOK_URL", "")
    if not webhook_url:
        return {
            "success": True,
            "error": None,
            "response": {
                "status": "mock_acknowledged",
                "message": "N8N_WEBHOOK_URL not set — payload logged only",
                "payload": payload,
            },
        }

    import httpx

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = httpx.post(
                webhook_url,
                json=payload,
                timeout=10.0,
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            return {
                "success": True,
                "error": None,
                "response": {
                    "status": "sent",
                    "status_code": resp.status_code,
                    "body": resp.json() if resp.content else {},
                },
            }
        except httpx.TimeoutException as e:
            last_error = f"Timeout on attempt {attempt}: {e}"
        except httpx.HTTPStatusError as e:
            last_error = f"HTTP {e.response.status_code} on attempt {attempt}: {e}"
        except Exception as e:
            last_error = f"Error on attempt {attempt}: {e}"

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY_SECONDS * attempt)

    return {"success": False, "error": last_error, "response": None}
