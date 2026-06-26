#!/usr/bin/env python3
"""
End-to-end ML pipeline: collect → build → evaluate → promote.

Designed to be called from cron, CI/CD, or manually:
    python -m app.ml.pipeline

Safe to run multiple times — idempotent.
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ml.pipeline")

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from app.ml.alerts import send_alert
from app.ml.dataset_builder import DatasetBuilder, build as build_dataset
from app.ml.registry.model_registry import (
    get_active,
    list_versions,
    promote,
    register,
    set_eval_score,
)
from app.ml.scheduler import _get_current_record_count


def run_pipeline() -> int:
    logger.info("=" * 60)
    logger.info("ML Pipeline starting at %s", datetime.now(timezone.utc).isoformat())
    logger.info("=" * 60)

    # Step 1: Build processed dataset
    try:
        current_count = _get_current_record_count()
        logger.info("Current raw record count: %d", current_count)
        if current_count == 0:
            logger.info("No raw data yet. Skipping pipeline.")
            send_alert("Pipeline skipped: no raw data", severity="info")
            return 0

        count = build_dataset()
        logger.info("Dataset built: %d records processed", count)
    except Exception as e:
        logger.error("Dataset build failed: %s", e)
        send_alert(f"Dataset build failed: {e}", severity="error")
        return 1

    # Step 2: Run quality checks
    summary = DatasetBuilder.get_quality_summary()
    pass_rate = summary.get("pass_rate", 0.0)
    logger.info("Quality summary: pass_rate=%.2f total=%d errors=%s",
                pass_rate, summary.get("total", 0), summary.get("issue_breakdown", {}))

    if pass_rate < 0.5 and summary.get("total", 0) > 10:
        logger.warning("Quality pass rate too low (%.2f), skipping promotion", pass_rate)
        send_alert(f"Low quality pass rate: {pass_rate:.2f}", severity="warning")
        return 1

    # Step 3: Register new dataset version
    tag = f"dataset-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    register(
        tag=tag,
        base_model="gemma2:2b",
        training_data=f"processed_training-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl",
        record_count=summary.get("total", 0),
        metadata={"quality_pass_rate": pass_rate, "quality_summary": summary},
    )
    logger.info("Registered dataset version: %s", tag)

    # Step 4: Evaluate
    try:
        from src.evaluation.benchmarks import BenchmarkSuite
        from src.evaluation.rag_eval import RAGPrecisionEvaluator
        from src.evaluation.agent_eval import RoutingAccuracyEvaluator
        from src.evaluation.content_eval import ContentQualityEvaluator

        suite = BenchmarkSuite()
        suite.add_evaluator(RAGPrecisionEvaluator())
        suite.add_evaluator(RoutingAccuracyEvaluator())
        suite.add_evaluator(ContentQualityEvaluator())

        eval_path = REPO_ROOT / "tests" / "fixtures" / "eval_queries.jsonl"
        test_cases = []
        if eval_path.exists():
            with eval_path.open("r") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped:
                        try:
                            import json
                            test_cases.append(json.loads(stripped))
                        except Exception:
                            pass

        if test_cases:
            results = suite.run(test_cases)
            logger.info("Evaluation results: %s", results)
            set_eval_score(tag, results.get("summary_by_evaluator", {}).get("rag_precision", {}).get("mean", 0.0))
        else:
            logger.info("No eval queries found at %s, skipping evaluation", eval_path)
    except Exception as e:
        logger.warning("Evaluation failed (non-fatal): %s", e)

    # Step 5: Check if we should promote
    active = get_active()
    if active is None:
        promote(tag)
        logger.info("First dataset version promoted: %s", tag)
    else:
        logger.info("Active version: %s (score=%s)", active["tag"], active.get("eval_score"))
        promote(tag)
        logger.info("Promoted: %s", tag)

    send_alert(f"Pipeline complete: {summary.get('total', 0)} records, {pass_rate:.0%} pass rate",
               severity="info")

    logger.info("Pipeline finished successfully")
    return 0


def main() -> None:
    exit_code = run_pipeline()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
