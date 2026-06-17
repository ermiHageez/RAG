from src.evaluation.base import Evaluator


class RoutingAccuracyEvaluator(Evaluator):
    def name(self) -> str:
        return "routing_accuracy"

    def evaluate(
        self,
        input_data: str,
        output_data: list[str],
        expected: list[str] | None = None,
    ) -> dict:
        if expected is None:
            return {"exact_match": True, "precision": 1.0, "recall": 1.0, "f1": 1.0}

        actual_set = set(output_data)
        expected_set = set(expected)

        correct = actual_set == expected_set
        precision = len(actual_set & expected_set) / max(len(actual_set), 1)
        recall = len(actual_set & expected_set) / max(len(expected_set), 1)
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        return {
            "exact_match": correct,
            "precision": precision,
            "recall": recall,
            "f1": round(f1, 4),
        }
