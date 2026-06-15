import enum
import os
from pathlib import Path


TEMPLATES_DIR = Path("n8nemail")


class ProductTemplate(str, enum.Enum):
    EHEALTH = "Ehealth"
    ERP = "ERP"
    SCCO = "SCCO"
    ESHARE = "eShare"
    GENERAL = "General"


PRODUCT_TEMPLATE_MAP = {
    ProductTemplate.EHEALTH: "email3.html",
    ProductTemplate.ERP: "email2.html",
    ProductTemplate.SCCO: "email5.html",
    ProductTemplate.ESHARE: "email.html",
    ProductTemplate.GENERAL: "email4.html",
}


class TemplateEngine:
    def __init__(self, templates_dir: str = None):
        self.templates_dir = Path(templates_dir) if templates_dir else TEMPLATES_DIR

    def get_template_file(self, product: str) -> str:
        try:
            pt = ProductTemplate(product)
        except ValueError:
            pt = ProductTemplate.GENERAL
        filename = PRODUCT_TEMPLATE_MAP[pt]
        return str(self.templates_dir / filename)

    def render_template(self, product: str, variables: dict) -> str:
        filepath = self.get_template_file(product)
        if not os.path.exists(filepath):
            return ""
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
        for key, value in variables.items():
            placeholder = "{{" + key + "}}"
            html = html.replace(placeholder, str(value))
        return html

    def list_templates(self) -> list[dict]:
        results = []
        for pt, filename in PRODUCT_TEMPLATE_MAP.items():
            filepath = self.templates_dir / filename
            results.append({
                "product": pt.value,
                "filename": filename,
                "exists": filepath.exists(),
            })
        return results

    def get_template_html(self, product: str) -> str:
        filepath = self.get_template_file(product)
        if not os.path.exists(filepath):
            return ""
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def update_template_html(self, product: str, html: str) -> bool:
        filepath = self.get_template_file(product)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        return True
