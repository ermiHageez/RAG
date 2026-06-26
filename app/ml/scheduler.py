from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from threading import Event, Thread

from app.ml.dataset_builder import DatasetBuilder, build

logger = logging.getLogger(__name__)

SCHEDULE_INTERVAL_SECONDS = int(os.getenv("DATASET_BUILD_INTERVAL", "3600"))
STATE_FILE = Path(__file__).resolve().parents[2] / "ml" / "datasets" / ".scheduler_state.json"

_stop_event = Event()


def _get_last_record_count() -> int:
    if not STATE_FILE.exists():
        return 0
    try:
        with STATE_FILE.open("r") as f:
            return json.load(f).get("last_record_count", 0)
    except Exception:
        return 0


def _save_state(count: int) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with STATE_FILE.open("w") as f:
        json.dump({"last_record_count": count, "updated_at": time.time()}, f)


def _get_current_record_count() -> int:
    from app.ml.training_sink import RAW_INTERACTIONS_PATH
    if not RAW_INTERACTIONS_PATH.exists():
        return 0
    count = 0
    with RAW_INTERACTIONS_PATH.open("r") as f:
        for _ in f:
            count += 1
    return count


def run_build_if_needed() -> bool:
    last = _get_last_record_count()
    current = _get_current_record_count()
    if current <= last:
        logger.info("No new records since last build (%d <= %d)", current, last)
        return False
    logger.info("New records detected (%d > %d), running build...", current, last)
    try:
        count = build()
        _save_state(current)
        logger.info("Build complete: %d records processed", count)
        return True
    except Exception as e:
        logger.error("Build failed: %s", e)
        return False


def start_scheduler(interval: int = SCHEDULE_INTERVAL_SECONDS) -> Thread:
    thread = Thread(target=_scheduler_loop, args=(interval,), daemon=True, name="dataset-builder-scheduler")
    thread.start()
    logger.info("Dataset builder scheduler started (interval=%ds)", interval)
    return thread


def stop_scheduler() -> None:
    _stop_event.set()


def _scheduler_loop(interval: int) -> None:
    while not _stop_event.is_set():
        run_build_if_needed()
        _stop_event.wait(interval)


def main() -> None:
    logger.info("Running one-off build...")
    count = build()
    print(f"Built {count} records")
    summary = DatasetBuilder.get_quality_summary()
    print(f"Quality: {summary}")


if __name__ == "__main__":
    main()
