# main.py
import argparse
import os

import uvicorn

from server import mcp, BearerAuthMiddleware

# Import the module containing the tool to ensure it's registered
import render_eraser_diagram


def main():
    parser = argparse.ArgumentParser(description="Eraser MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default=os.getenv("MCP_TRANSPORT", "stdio"),
        help="Transport protocol (default: stdio, env: MCP_TRANSPORT)",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("MCP_HOST", "0.0.0.0"),
        help="Host to bind to for HTTP transport (default: 0.0.0.0, env: MCP_HOST)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MCP_PORT", "8000")),
        help="Port to bind to for HTTP transport (default: 8000, env: MCP_PORT)",
    )
    args = parser.parse_args()

    if args.transport == "http":
        # Create FastMCP's streamable HTTP app
        app = mcp.streamable_http_app()

        # Add Bearer auth middleware
        app.add_middleware(BearerAuthMiddleware)

        print(f"Starting Eraser MCP server on http://{args.host}:{args.port}/mcp")
        uvicorn.run(app, host=args.host, port=args.port)
    else:
        mcp.run()  # stdio default


# Entry point to run the server
if __name__ == "__main__":
    main()
