import sys
import argparse


def main():
    from mcp_server.server import server

    parser = argparse.ArgumentParser(description="eTech MCP Server")
    parser.add_argument("--sse", action="store_true", help="Run with SSE transport")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (SSE only)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (SSE only)")
    args = parser.parse_args()

    if args.sse:
        print(f"[INFO] Starting eTech MCP server on SSE {args.host}:{args.port}...", file=sys.stderr)
        server.run(transport="sse", host=args.host, port=args.port)
    else:
        print("[INFO] Starting eTech MCP server on stdio...", file=sys.stderr)
        server.run(transport="stdio")


if __name__ == "__main__":
    main()
