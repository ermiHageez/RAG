"""
Generate a Modelfile with system prompt and training examples injected.

Usage:
    python app/ml/registry/generate_modelfile.py \
        --processed ml/datasets/processed_training.jsonl \
        --output app/ml/registry/Modelfile.generated

This script reads processed training data, selects the best quality
examples, and generates a Modelfile with them inlined into the SYSTEM block.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are eTech Custom AI Agent, an expert assistant for Ethiopian enterprise intelligence.
You help sales and marketing teams discover leads, analyze tenders, draft content, and track campaigns.

CAPABILITIES:
- Search Ethiopian enterprises across all sectors
- Find active tenders (ጨረታ) with deadlines and categories
- Draft personalized sales emails, proposals, and campaign content
- Analyze market intelligence and competition
- Generate follow-up sequences and track campaigns

RESPONSE GUIDELINES:
- Be concise, structured, and actionable
- For companies: include name, sector, location, contact, and description
- For tenders: include title, deadline, category, urgency, and source
- When searching: use the available tools rather than inventing data
- If unsure: state what you don't know rather than making up information
- Prefer bullet points and short paragraphs over long blocks of text"""

EXAMPLE_TEMPLATE = """User: {user}
Assistant: {assistant}"""

BASE_MODEL = "gemma2:2b"
PARAM_TEMPERATURE = "0.2"
PARAM_NUM_CTX = "4096"
PARAM_NUM_THREAD = "2"
MAX_EXAMPLES = 5
MIN_QUERY_LENGTH = 15
MAX_QUERY_LENGTH = 300


def _score_example(record: dict) -> float:
    """Score a record for quality — higher is better for few-shot examples."""
    messages = record.get("messages", [])
    if len(messages) != 2:
        return -1
    user = messages[0].get("content", "")
    assistant = messages[1].get("content", "")
    score = 0.0
    if len(user) >= MIN_QUERY_LENGTH:
        score += 1.5
    if len(assistant) >= 100:
        score += 1.5
    if any(w in user.lower() for w in ["search", "find", "list", "show", "draft"]):
        score += 2.0
    if any(w in user.lower() for w in ["etech", "ethiopia", "ethiopian"]):
        score += 0.5
    if any(kw in user.lower() for kw in ["lead", "tender", "sacco", "bank", "email", "proposal", "temple", "campaign"]):
        score += 2.0
    if len(user) > MAX_QUERY_LENGTH:
        score -= 2.0
    template_words = ["cannot", "unable", "don't have", "not provided", "not mentioned"]
    if any(w in assistant.lower() for w in template_words):
        score -= 4.0
    # Penalize failed search results (JSON containing "unavailable" or "timeout")
    if assistant.strip().startswith("{"):
        try:
            d = json.loads(assistant)
            name_val = d.get("name", "")
            if "unavailable" in name_val.lower() or "error" in name_val.lower():
                score -= 10.0
        except json.JSONDecodeError:
            pass
    # Penalize very short/non-substantive responses
    stripped = assistant.strip()
    if len(stripped) < 50:
        score -= 3.0
    # Penalize commands like /generate-proposal etc
    if user.startswith("/"):
        score -= 3.0
    return score


def _select_examples(records: list[dict], max_examples: int = MAX_EXAMPLES) -> list[dict]:
    scored = [(r, _score_example(r)) for r in records]
    scored.sort(key=lambda x: x[1], reverse=True)
    # Filter out reject and keep top candidates
    candidates = [r for r, s in scored if s > 0]
    if len(candidates) < max_examples:
        candidates = [r for r, s in scored if s >= 0][:max_examples * 2]
    # Ensure variety: pick from different topics
    topics_seen: set[str] = set()
    diverse: list[dict] = []
    for r in candidates:
        msgs = r.get("messages", [])
        user = msgs[0].get("content", "").lower() if msgs else ""
        topic = "lead_search" if any(w in user for w in ["search", "find", "list", "sacco", "bank"]) else \
                "tender" if "tender" in user else \
                "email_draft" if any(w in user for w in ["email", "draft", "proposal", "temple", "campaign"]) else \
                "company_info" if any(w in user for w in ["tell", "what", "know", "about"]) else \
                "cybersecurity" if any(w in user for w in ["cyber", "security"]) else \
                "mcp_tool" if any(w in user for w in ["mcp", "/make", "host-international"]) else \
                "other"
        if topic not in topics_seen:
            topics_seen.add(topic)
            diverse.append(r)
            if len(diverse) >= max_examples:
                break
    # Fill remaining slots with highest-scored not yet included
    if len(diverse) < max_examples:
        for r in candidates:
            if r not in diverse:
                diverse.append(r)
                if len(diverse) >= max_examples:
                    break
    return diverse[:max_examples]


def generate_modelfile(
    processed_path: Path,
    output_path: Path,
    max_examples: int = MAX_EXAMPLES,
) -> str:
    if not processed_path.exists():
        logger.warning("Processed training data not found at %s — building without examples", processed_path)
        modelfile = _build_modelfile([])
    else:
        records: list[dict] = []
        with processed_path.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    try:
                        records.append(json.loads(stripped))
                    except json.JSONDecodeError:
                        continue
        logger.info("Loaded %d records from %s", len(records), processed_path)
        examples = _select_examples(records, max_examples)
        logger.info("Selected %d examples for few-shot injection", len(examples))
        modelfile = _build_modelfile(examples)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(modelfile, encoding="utf-8")
    logger.info("Generated Modelfile at %s (%d bytes)", output_path, len(modelfile))
    return modelfile


def _build_modelfile(examples: list[dict]) -> str:
    lines: list[str] = []
    lines.append(f"FROM {BASE_MODEL}")
    lines.append("")
    lines.append(f"PARAMETER temperature {PARAM_TEMPERATURE}")
    lines.append(f"PARAMETER num_ctx {PARAM_NUM_CTX}")
    lines.append(f"PARAMETER num_thread {PARAM_NUM_THREAD}")
    lines.append("")
    lines.append('SYSTEM """')
    lines.append(SYSTEM_PROMPT)
    lines.append("")

    if examples:
        lines.append("EXAMPLE INTERACTIONS:")
        lines.append("")
        for i, record in enumerate(examples, 1):
            msgs = record.get("messages", [])
            user = msgs[0].get("content", "") if len(msgs) > 0 else ""
            assistant = msgs[1].get("content", "") if len(msgs) > 1 else ""
            lines.append(f"Example {i}:")
            lines.append(EXAMPLE_TEMPLATE.format(user=user, assistant=assistant))
            lines.append("")

    lines.append('"""')
    lines.append("")
    modelfile = "\n".join(lines)
    return modelfile


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Modelfile with training examples")
    parser.add_argument("--processed", default="ml/datasets/processed_training.jsonl",
                        help="Path to processed training JSONL")
    parser.add_argument("--output", default="app/ml/registry/Modelfile.generated",
                        help="Output path for generated Modelfile")
    parser.add_argument("--max-examples", type=int, default=MAX_EXAMPLES,
                        help=f"Maximum number of examples to inject (default: {MAX_EXAMPLES})")
    args = parser.parse_args()

    root = Path.cwd()
    processed_path = root / args.processed
    output_path = root / args.output

    generate_modelfile(processed_path, output_path, args.max_examples)
    print(f"Generated Modelfile at {output_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
