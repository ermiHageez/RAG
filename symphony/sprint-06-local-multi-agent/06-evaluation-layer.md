# Sprint 6.6 — Evaluation Layer

> Add evaluation and benchmarking infrastructure for RAG quality, agent routing accuracy, and content quality.

---

## Goal

Create interfaces and implementations for measuring system performance:

- RAG retrieval precision & relevance
- Agent routing accuracy
- Lead/tender qualification quality
- Email content quality & hallucination detection

---

## Structure

```
src/evaluation/
├── __init__.py
├── base.py              # Abstract evaluator interface
├── rag_eval.py          # RAG retrieval metrics
├── agent_eval.py        # Agent routing & qualification metrics
├── content_eval.py      # Email quality & hallucination checks
└── benchmarks.py        # Benchmark runner
```

---

## Abstract Interface (`src/evaluation/base.py`)

```python
from abc import ABC, abstractmethod
from typing import Any

class Evaluator(ABC):
    @abstractmethod
    def evaluate(self, input_data: Any, output_data: Any, expected: Any | None = None) -> dict:
        """Return metrics dict with scores."""
        ...

    @abstractmethod
    def name(self) -> str:
        ...
```

---

## RAG Evaluation (`src/evaluation/rag_eval.py`)

```python
class RAGPrecisionEvaluator(Evaluator):
    """Evaluate if retrieved chunks are relevant to the query."""

    def __init__(self, llm=None):
        self.llm = llm or get_reasoning_llm()

    def evaluate(self, query: str, results: list[dict], expected: list[str] | None = None) -> dict:
        scores = []
        for r in results:
            prompt = f"Rate relevance (0-1) of this text to query '{query}':\n{r.get('text', '')}"
            response = self.llm.invoke(prompt)
            score = extract_score(response.content)
            scores.append(score)

        return {
            "precision": mean(scores) if scores else 0.0,
            "individual_scores": scores,
            "retrieved_count": len(results),
        }
```

**Metrics:**
- `precision` — Fraction of retrieved chunks rated relevant (>0.5)
- `mean_reciprocal_rank` — If expected documents known
- `latency_ms` — Retrieval time

---

## Agent Evaluation (`src/evaluation/agent_eval.py`)

```python
class RoutingAccuracyEvaluator(Evaluator):
    """Evaluate if supervisor routes to correct agents."""

    def evaluate(self, query: str, actual_route: list[str], expected_route: list[str]) -> dict:
        correct = set(actual_route) == set(expected_route)
        precision = len(set(actual_route) & set(expected_route)) / max(len(actual_route), 1)
        recall = len(set(actual_route) & set(expected_route)) / max(len(expected_route), 1)

        return {
            "exact_match": correct,
            "precision": precision,
            "recall": recall,
            "f1": 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0,
        }
```

---

## Content Evaluation (`src/evaluation/content_eval.py`)

```python
class ContentQualityEvaluator(Evaluator):
    """Evaluate email quality and detect hallucinations."""

    def __init__(self):
        self.llm = get_reasoning_llm()

    def evaluate(self, email: dict, context: list[dict]) -> dict:
        body = email.get("body", "")
        context_text = "\n".join(c.get("text", "") for c in context)

        # Hallucination check
        prompt = f"""Does this email contain claims NOT supported by the context?
        Context: {context_text[:2000]}
        Email: {body[:2000]}
        Respond with JSON: {{"hallucination_detected": bool, "hallucinated_claims": [...], "confidence": 0-1}}"""
        response = self.llm.invoke(prompt)

        return {
            "hallucination_detected": response.get("hallucination_detected", False),
            "hallucinated_claims": response.get("hallucinated_claims", []),
            "has_greeting": "Dear" in body,
            "has_signature": "Best" in body or "Sincerely" in body,
            "length_chars": len(body),
        }
```

---

## Benchmark Runner (`src/evaluation/benchmarks.py`)

```python
class BenchmarkSuite:
    def __init__(self):
        self.evaluators: list[Evaluator] = []
        self.results: list[dict] = []

    def add_evaluator(self, evaluator: Evaluator) -> None:
        self.evaluators.append(evaluator)

    def run(self, test_cases: list[dict]) -> dict:
        for case in test_cases:
            for evaluator in self.evaluators:
                result = evaluator.evaluate(
                    case.get("input"),
                    case.get("output"),
                    case.get("expected")
                )
                self.results.append({
                    "case": case.get("name"),
                    "evaluator": evaluator.name(),
                    "result": result,
                })
        return self.summarize()

    def summarize(self) -> dict:
        # Aggregate all scores
        ...
```

---

## Test Cases

Store benchmark test cases in:
```
tests/fixtures/
├── rag_test_cases.json        # query + expected chunks
├── routing_test_cases.json    # query + expected route
└── content_test_cases.json    # context + expected email traits
```

---

## Files Changed

| File | Change |
|---|---|
| `src/evaluation/__init__.py` | **NEW** |
| `src/evaluation/base.py` | **NEW** |
| `src/evaluation/rag_eval.py` | **NEW** |
| `src/evaluation/agent_eval.py` | **NEW** |
| `src/evaluation/content_eval.py` | **NEW** |
| `src/evaluation/benchmarks.py` | **NEW** |
| `tests/fixtures/` | **NEW** — test case JSON files |

---

## Verification

```python
from src.evaluation.rag_eval import RAGPrecisionEvaluator

evaluator = RAGPrecisionEvaluator()
results = evaluator.evaluate(
    query="Who is the CEO of eTech?",
    results=[{"text": "The CEO is Ermi ..."}, {"text": "Annual report 2022..."}]
)
print(results["precision"])
```
