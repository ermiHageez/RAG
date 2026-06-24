from src.agents.llm import get_reasoning_llm
from src.evaluation.base import Evaluator


class ContentQualityEvaluator(Evaluator):
    def __init__(self, llm=None):
        self._llm = llm or get_reasoning_llm()

    def name(self) -> str:
        return "content_quality"

    def evaluate(
        self, input_data: dict, output_data: dict, expected=None
    ) -> dict:
        body = output_data.get("email_body", "") or output_data.get("body", "")
        context = input_data if isinstance(input_data, (list, str)) else input_data.get("context", [])

        has_greeting = bool("Dear" in body)
        has_signature = bool("Best" in body or "Sincerely" in body or "Regards" in body)
        has_subject = bool("Subject:" in body or output_data.get("subject"))

        prompt = (
            f"Does this email contain claims NOT supported by the provided context?\n"
            f"Context: {str(context)[:2000]}\n"
            f"Email: {body[:2000]}\n"
            "Respond with a JSON object: {{\"hallucination_detected\": bool, \"confidence\": 0.0-1.0}}"
        )
        hallucination_detected = False
        confidence = 0.0
        try:
            response = self._llm.invoke(prompt)
            import json, re
            match = re.search(r'\{[\s\S]*\}', str(response.content))
            if match:
                data = json.loads(match.group())
                hallucination_detected = data.get("hallucination_detected", False)
                confidence = data.get("confidence", 0.0)
        except Exception:
            pass

        return {
            "hallucination_detected": hallucination_detected,
            "hallucination_confidence": confidence,
            "has_greeting": has_greeting,
            "has_signature": has_signature,
            "has_subject": has_subject,
            "length_chars": len(body),
            "quality_score": round(
                0.3 * has_greeting
                + 0.3 * has_signature
                + 0.2 * has_subject
                + 0.2 * (1.0 - confidence if hallucination_detected else 1.0),
                4,
            ),
        }
