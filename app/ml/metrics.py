from __future__ import annotations

import logging
import time
from collections import Counter
from typing import Any

logger = logging.getLogger(__name__)

_metrics: dict[str, Any] = {
    "records_collected": 0,
    "records_rejected": 0,
    "records_duplicate": 0,
    "records_redacted": 0,
    "queue_depth": 0,
    "worker_write_time_ms": 0.0,
    "dataset_size_bytes": 0,
    "embedding_query_count": 0,
    "embedding_cache_hits": 0,
    "vector_query_count": 0,
    "vector_cache_hits": 0,
    "llm_call_count": 0,
    "llm_fallback_count": 0,
    "errors_by_type": Counter(),
    "latency_histogram_ms": [],
}

_MAX_LATENCY_SAMPLES = 1000


def increment(name: str, count: int = 1) -> None:
    if name in _metrics and isinstance(_metrics[name], (int, float)):
        _metrics[name] += count
    elif name == "errors_by_type":
        _metrics[name][count] += 1
    else:
        _metrics.setdefault(name, 0)
        _metrics[name] += count


def record_latency(duration_ms: float) -> None:
    samples = _metrics["latency_histogram_ms"]
    samples.append(duration_ms)
    while len(samples) > _MAX_LATENCY_SAMPLES:
        samples.pop(0)


def get_metrics() -> dict[str, Any]:
    result = {}
    for k, v in _metrics.items():
        if k == "errors_by_type":
            result[k] = dict(v)
        elif k == "latency_histogram_ms":
            samples = v
            if samples:
                sorted_s = sorted(samples)
                result["latency_p50_ms"] = sorted_s[len(sorted_s) // 2]
                result["latency_p95_ms"] = sorted_s[int(len(sorted_s) * 0.95)]
                result["latency_p99_ms"] = sorted_s[int(len(sorted_s) * 0.99)]
                result["latency_mean_ms"] = sum(sorted_s) / len(sorted_s)
                result["latency_samples"] = len(sorted_s)
            else:
                result["latency_p50_ms"] = 0
                result["latency_p95_ms"] = 0
                result["latency_p99_ms"] = 0
                result["latency_mean_ms"] = 0
                result["latency_samples"] = 0
        elif isinstance(v, Counter):
            result[k] = dict(v)
        else:
            result[k] = v
    return result


def reset_metrics() -> None:
    for k in list(_metrics.keys()):
        if k == "errors_by_type":
            _metrics[k] = Counter()
        elif k == "latency_histogram_ms":
            _metrics[k] = []
        elif isinstance(_metrics[k], Counter):
            _metrics[k] = Counter()
        else:
            _metrics[k] = 0


def format_prometheus() -> str:
    lines = ["# HELP ml_pipeline_metrics Metrics from the ML pipeline", "# TYPE ml_pipeline_metrics gauge"]
    data = get_metrics()
    for k, v in data.items():
        if isinstance(v, (int, float)):
            key = k.replace(" ", "_").replace("-", "_")
            lines.append(f"ml_{key} {v}")
    return "\n".join(lines)
