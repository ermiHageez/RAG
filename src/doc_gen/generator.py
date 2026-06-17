import os
import re
from datetime import datetime
from pathlib import Path


HTML_OUTPUT_DIR = "data/proposals"


class ProposalGenerator:
    def __init__(self, output_dir: str = HTML_OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(self, session_id: str, markdown_text: str, customer_name: str = "Customer") -> str:
        html = self._markdown_to_html(markdown_text, customer_name)
        file_path = os.path.join(self.output_dir, f"{session_id}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        return file_path

    def _markdown_to_html(self, md: str, customer_name: str) -> str:
        date_str = datetime.now().strftime("%B %d, %Y")
        lines = md.split("\n")
        body_parts = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                body_parts.append("<br>")
            elif re.match(r"^# (.+)$", stripped):
                title = re.match(r"^# (.+)$", stripped).group(1)
                body_parts.append(f'<h1 style="color:#0b2240;border-bottom:2px solid #0b2240;padding-bottom:6px;">{title}</h1>')
            elif re.match(r"^## (.+)$", stripped):
                title = re.match(r"^## (.+)$", stripped).group(1)
                body_parts.append(f'<h2 style="color:#1a3a6b;margin-top:20px;">{title}</h2>')
            elif re.match(r"^### (.+)$", stripped):
                title = re.match(r"^### (.+)$", stripped).group(1)
                body_parts.append(f'<h3 style="color:#333;">{title}</h3>')
            elif stripped.startswith("- ") or stripped.startswith("* "):
                text = stripped[2:]
                body_parts.append(f'<li style="margin-left:20px;">{text}</li>')
            else:
                body_parts.append(f'<p style="line-height:1.6;color:#444;">{stripped}</p>')

        body_html = "\n".join(body_parts)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sales Proposal - {customer_name}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f4f6f9; }}
  .page {{ max-width: 800px; margin: 30px auto; background: #fff; padding: 50px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
  .title-page {{ text-align: center; padding: 80px 0; }}
  .title-page h1 {{ font-size: 32px; color: #0b2240; margin-bottom: 10px; }}
  .title-page .subtitle {{ font-size: 18px; color: #555; margin-bottom: 30px; }}
  .title-page .meta {{ font-size: 14px; color: #777; }}
  .footer {{ text-align: center; font-size: 12px; color: #999; margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; }}
</style>
</head>
<body>
<div class="page">
  <div class="title-page">
    <h1>Sales Proposal</h1>
    <div class="subtitle">Prepared for {customer_name}</div>
    <div class="meta">Date: {date_str}<br>Prepared by eTech S.C.</div>
    <div class="meta" style="margin-top:10px;font-style:italic;">Ethical | Ethiopian | End-to-End</div>
  </div>
  <hr style="border:none;border-top:2px solid #0b2240;margin:30px 0;">
  {body_html}
  <div class="footer">
    Confidential — eTech S.C. | www.etechsc.com | +251 992 900 007
  </div>
</div>
</body>
</html>"""
