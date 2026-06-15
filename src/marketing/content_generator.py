from src.agents.llm import get_content_llm

PRODUCT_PROMPTS = {
    "Ehealth": (
        "You are a healthcare technology marketing writer for eTech S.C., an Ethiopian tech company. "
        "Write 2-3 professional sentences promoting eTech's eHealth platform to {customer_name}, "
        "a {customer_sector} organization. Customer needs: {customer_needs}. "
        "Focus on EHR, ambulance tracking, pharmacy POS, and patient records. "
        "Mention MeQrez General Hospital as a reference. End with a call to action for a demo."
    ),
    "ERP": (
        "You are an enterprise software marketing writer for eTech S.C., an Ethiopian tech company. "
        "Write 2-3 professional sentences promoting eTech's ERP system to {customer_name}, "
        "a {customer_sector} organization. Customer needs: {customer_needs}. "
        "Focus on finance, inventory, HR, and procurement automation. "
        "Mention eTech's 200+ clients. End with a call to action for a consultation."
    ),
    "SCCO": (
        "You are a financial technology marketing writer for eTech S.C., an Ethiopian tech company. "
        "Write 2-3 professional sentences promoting eTech's eShare and financial systems to {customer_name}, "
        "a {customer_sector} organization. Customer needs: {customer_needs}. "
        "Focus on share registry, dividend processing, and banking integrations. "
        "Mention Zemen Bank, Ahadu Bank, and Tsedey Bank as references. End with a call to action."
    ),
    "eShare": (
        "You are a financial technology marketing writer for eTech S.C., an Ethiopian tech company. "
        "Write 2-3 professional sentences promoting eTech's eShare platform to {customer_name}, "
        "a {customer_sector} organization. Customer needs: {customer_needs}. "
        "Focus on shareholder management, dividend tracking, and regulatory compliance. "
        "End with a call to action for a demonstration."
    ),
}


DEFAULT_PROMPT = (
    "You are a B2B marketing writer for eTech S.C., an Ethiopian technology company. "
    "Write 2-3 professional sentences introducing eTech's solutions to {customer_name}, "
    "a {customer_sector} organization. Customer needs: {customer_needs}. "
    "Mention eTech's end-to-end ICT capabilities. End with a call to action."
)


class ContentGenerator:
    def __init__(self):
        self.llm = get_content_llm()

    def generate_email_body(self, product: str, customer_name: str,
                            customer_sector: str, customer_needs: str) -> str:
        prompt_template = PRODUCT_PROMPTS.get(product, DEFAULT_PROMPT)
        prompt = prompt_template.format(
            customer_name=customer_name,
            customer_sector=customer_sector,
            customer_needs=customer_needs,
        )
        response = self.llm.invoke(prompt)
        return response.content.strip()
