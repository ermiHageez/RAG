from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REGISTRY_PATH = Path(__file__).resolve().parents[3] / "ml" / "registry" / "model_registry.json"


def _load() -> dict:
    if not REGISTRY_PATH.exists():
        return {"versions": [], "active": None}
    try:
        with REGISTRY_PATH.open("r") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("Failed to load model registry: %s", e)
        return {"versions": [], "active": None}


def _save(registry: dict) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REGISTRY_PATH.open("w") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def register(
    tag: str,
    base_model: str,
    training_data: str = "",
    record_count: int = 0,
    eval_score: float | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict:
    registry = _load()
    for v in registry["versions"]:
        if v["tag"] == tag:
            logger.warning("Model version %s already exists, updating", tag)
            v.update({
                "base_model": base_model,
                "training_data": training_data,
                "training_date": datetime.now(timezone.utc).isoformat(),
                "record_count": record_count,
                "eval_score": eval_score,
                "metadata": metadata or {},
            })
            _save(registry)
            return v
    entry = {
        "tag": tag,
        "base_model": base_model,
        "training_data": training_data,
        "training_date": datetime.now(timezone.utc).isoformat(),
        "record_count": record_count,
        "eval_score": eval_score,
        "metadata": metadata or {},
        "status": "registered",
    }
    registry["versions"].append(entry)
    _save(registry)
    logger.info("Registered model version: %s", tag)
    return entry


def promote(tag: str) -> dict | None:
    registry = _load()
    for v in registry["versions"]:
        if v["tag"] == tag:
            v["status"] = "active"
            registry["active"] = tag
            for other in registry["versions"]:
                if other["tag"] != tag and other.get("status") == "active":
                    other["status"] = "archived"
            _save(registry)
            logger.info("Promoted model version: %s", tag)
            return v
    logger.warning("Cannot promote: version %s not found", tag)
    return None


def rollback() -> dict | None:
    registry = _load()
    if not registry["active"]:
        logger.warning("No active version to rollback from")
        return None
    active_tag = registry["active"]
    active_idx = -1
    for i, v in enumerate(registry["versions"]):
        if v["tag"] == active_tag:
            active_idx = i
            break
    if active_idx <= 0:
        logger.warning("No previous version to rollback to")
        return None
    prev = registry["versions"][active_idx - 1]
    return promote(prev["tag"])


def list_versions() -> list[dict]:
    registry = _load()
    return registry["versions"]


def get_active() -> dict | None:
    registry = _load()
    if not registry["active"]:
        return None
    for v in registry["versions"]:
        if v["tag"] == registry["active"]:
            return v
    return None


def set_eval_score(tag: str, score: float) -> None:
    registry = _load()
    for v in registry["versions"]:
        if v["tag"] == tag:
            v["eval_score"] = score
            _save(registry)
            logger.info("Set eval score %.4f for %s", score, tag)
            return
    logger.warning("Cannot set eval score: version %s not found", tag)
