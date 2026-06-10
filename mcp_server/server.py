from mcp.server import FastMCP

from mcp_server.tools.search import discover_ethiopian_enterprises
from mcp_server.tools.tenders import fetch_active_tenders
from mcp_server.tools.n8n_hook import trigger_n8n_marketing_pipeline

server = FastMCP("eTech Agent MCP Server", instructions="MCP server for eTech marketing & sales agent tools")


@server.tool()
def discover_ethiopian_enterprises_tool(query: str) -> list[dict]:
    """Search for Ethiopian companies by sector or keyword. Use this to find potential leads in banking, insurance, logistics, manufacturing, government, or technology sectors."""
    return discover_ethiopian_enterprises(query)


@server.tool()
def fetch_active_tenders_tool(sector: str = "") -> list[dict]:
    """Fetch active procurement tenders from Ethiopian PPA/eGP portals. Optionally filter by sector (e.g. 'Security', 'ERP', 'ICT')."""
    return fetch_active_tenders(sector if sector else None)


@server.tool()
def trigger_n8n_marketing_pipeline_tool(
    lead_name: str,
    tender_requirements: str,
    validated_email: str,
    email_body: str,
) -> dict:
    """Send a marketing email payload to the n8n automation pipeline. Requires lead name, tender requirements summary, validated email address, and the generated email body."""
    payload = {
        "lead_name": lead_name,
        "tender_requirements": tender_requirements,
        "validated_email": validated_email,
        "email_body": email_body,
    }
    return trigger_n8n_marketing_pipeline(payload)
