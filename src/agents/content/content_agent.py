import re
from typing import Any
from src.agents.llm import get_content_llm
from src.agents.state import AgentState
from langchain_core.prompts import ChatPromptTemplate

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a professional B2B marketing writer for eTech, an Ethiopian technology company. "
        "Write formal, concise, and personalized outreach emails. "
        "Do not use markdown formatting. Keep the tone professional and respectful. "
        "Each email must include: a subject line (prefixed with 'Subject:'), "
        "a greeting, 2-3 body paragraphs referencing the prospect's needs and eTech's relevant features, "
        "and a professional signature.",
    ),
    (
        "human",
        "Write a personalized outreach email to {company_name} ({sector} sector).\n"
        "Their potential needs: {description}\n"
        "eTech's relevant features: {features}\n"
        "{tender_context}",
    ),
])


def _validate_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def _personalization_score(email_body: str, company_name: str, sector: str) -> float:
    body_lower = email_body.lower()
    score = 0.0
    if company_name.lower() in body_lower:
        score += 0.3
    if sector.lower() in body_lower:
        score += 0.2
    if "ethiopia" in body_lower:
        score += 0.1
    if len(email_body) > 100:
        score += 0.1
    generic = ["dear sir/madam", "to whom it may concern", "valued customer"]
    if any(p in body_lower for p in generic):
        score -= 0.2
    return max(0.0, min(1.0, score))


def _generate_email(
    company_name: str,
    sector: str,
    description: str,
    features: list[str],
    tender_title: str | None = None,
) -> dict[str, Any]:
    llm = get_content_llm()
    fallback_body = (
        f"Dear {company_name},\n\n"
        f"[LLM unavailable — please draft manually]\n\n"
        f"Best,\neTech Team"
    )

    features_text = "\n".join(f"- {f}" for f in features)
    tender_context = ""
    if tender_title:
        tender_context = f"They have an active tender: {tender_title}"

    prompt = PROMPT_TEMPLATE.format(
        company_name=company_name,
        sector=sector,
        description=description,
        features=features_text,
        tender_context=tender_context,
    )

    try:
        response = llm.invoke(prompt)
        raw_content = getattr(response, "content", response)
        if isinstance(raw_content, list):
            content = " ".join(str(item) for item in raw_content)
        else:
            content = str(raw_content)
        subject = f"Partnership Opportunity — {company_name}"
        if "Subject:" in content:
            parts = content.split("Subject:", 1)
            subject_line = parts[1].split("\n", 1)[0].strip()
            if subject_line:
                subject = subject_line
        return {
            "lead_name": company_name,
            "validated_email": "",
            "tender_requirements": (
                f"{description} | Related tender: {tender_title}"
                if tender_title else description
            ),
            "email_body": content,
            "subject": subject,
            "personalization_score": 0.0,
        }
    except Exception as e:
        print(f"[ContentAgent] Generation failed for {company_name}: {e}")
        return {
            "lead_name": company_name,
            "validated_email": "",
            "tender_requirements": description,
            "email_body": fallback_body,
            "subject": f"Partnership Opportunity — {company_name}",
            "personalization_score": 0.0,
        }


def content_agent(state: AgentState) -> dict:
    sales_intel = state.get("sales_intelligence", {})
    insights = sales_intel.get("insights", []) if isinstance(sales_intel, dict) else []
    knowledge = state.get("knowledge_context", [])

    lead_items = [i for i in insights if i.get("type") == "lead"]
    tender_items = [i for i in insights if i.get("type") == "tender"]

    drafts = []
    for item in lead_items:
        company = item.get("company_name", "")
        sector = item.get("sector", "")
        description = item.get("description", "")
        contact = item.get("contact", "")
        if not company:
            continue
        matching_tenders = item.get("matching_tenders", [])
        tender_title = matching_tenders[0] if matching_tenders else None
        features = [c.get("text", "") for c in knowledge[:3]] or ["eTech provides ICT solutions to Ethiopian enterprises"]
        draft = _generate_email(company, sector, description, features, tender_title)
        if contact and _validate_email(contact):
            draft["validated_email"] = contact.strip()
        draft["personalization_score"] = _personalization_score(
            draft["email_body"], company, sector
        )
        drafts.append(draft)

    if not drafts and tender_items:
        for item in tender_items:
            draft = _generate_email(
                "Procurement Team",
                item.get("category", ""),
                item.get("description", ""),
                ["eTech provides ICT solutions, security systems, and ERP implementation services"],
                item.get("title", ""),
            )
            draft["personalization_score"] = _personalization_score(
                draft["email_body"], "Procurement Team", item.get("category", "")
            )
            drafts.append(draft)

    email_draft = None
    if drafts:
        email_draft = drafts[0]

    print(f"[ContentAgent] Generated {len(drafts)} drafts")
    return {"draft_email": email_draft}
