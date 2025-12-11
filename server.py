# server.py
import os
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Simple Bearer token authentication middleware for HTTP transport."""

    async def dispatch(self, request: Request, call_next):
        expected_token = os.getenv("MCP_AUTH_TOKEN")

        # Skip auth if no token is configured
        if not expected_token:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"error": "Unauthorized", "message": "Bearer token required"},
                status_code=401,
            )

        token = auth_header[7:]  # Remove "Bearer " prefix
        if token != expected_token:
            return JSONResponse(
                {"error": "Forbidden", "message": "Invalid token"},
                status_code=403,
            )

        return await call_next(request)


# This is the shared MCP server instance
mcp = FastMCP("eraser_mcp_server")
