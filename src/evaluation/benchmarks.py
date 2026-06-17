from typing import Any, Optional
from src.evaluation.base import Evaluator


class BenchmarkSuite:
    def __init__(self):
        self.evaluators: list[Evaluator] = []
        self.results: list[dict] = []

    def add_evaluator(self, evaluator: Evaluator) -> None:
        self.evaluators.append(evaluator)

    def run(self, test_cases: list[dict]) -> dict:
        self.results = []
        for case in test_cases:
            for evaluator in self.evaluators:
                result = evaluator.evaluate(
                    case.get("input"),
                    case.get("output"),
                    case.get("expected"),
                )
                self.results.append({
                    "case": case.get("name", "unnamed"),
                    "evaluator": evaluator.name(),
                    "result": result,
                })
        return self.summarize()

    def summarize(self) -> dict:
        if not self.results:
            return {}
        by_evaluator: dict[str, list[float]] = {}
        for r in self.results:
            eval_name = r["evaluator"]
            if eval_name not in by_evaluator:
                by_evaluator[eval_name] = []
            res = r["result"]
            for key, val in res.items():
                if isinstance(val, (int, float)):
                    by_evaluator[eval_name].append(val)

        summary = {}
        for eval_name, scores in by_evaluator.items():
            if scores:
                summary[eval_name] = {
                    "mean": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores),
                    "count": len(scores),
                }
        return {"summary_by_evaluator": summary, "total_cases": len(self.results)}
