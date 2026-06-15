from statistics import mean
from src.agents.llm import get_reasoning_llm
from src.evaluation.base import Evaluator


def extract_score(text: str) -> float:
    import re
    match = re.search(r'(\d*\.?\d+)', str(text))
    return float(match.group(1)) if match else 0.5


class RAGPrecisionEvaluator(Evaluator):
    def __init__(self, llm=None):
        self._llm = llm or get_reasoning_llm()

    def name(self) -> str:
        return "rag_precision"

    def evaluate(self, query: str, output_data: list[dict], expected=None) -> dict:
        scores = []
        for result in output_data:
            text = result.get("text", "") or result.get("metadata", {}).get("text", "")
            prompt = f"Rate the relevance of this text to the query '{query}' from 0.0 to 1.0:\n{text[:1000]}"
            try:
                response = self._llm.invoke(prompt)
                score = extract_score(response.content)
                scores.append(score)
            except Exception:
                scores.append(0.5)

        return {
            "precision": mean(scores) if scores else 0.0,
            "individual_scores": scores,
            "retrieved_count": len(output_data),
        }
