from __future__ import annotations

import logging
import os

import httpx

logger = logging.getLogger(__name__)

ALERT_WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "")


def send_alert(message: str, severity: str = "info") -> None:
    if not ALERT_WEBHOOK_URL:
        logger.debug("No ALERT_WEBHOOK_URL configured, skipping alert: %s", message)
        return
    try:
        payload = {
            "text": f"[ML Pipeline] {severity.upper()}: {message}",
        }
        resp = httpx.post(ALERT_WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Alert sent: severity=%s message=%s", severity, message)
    except Exception as e:
        logger.warning("Failed to send alert: %s", e)
