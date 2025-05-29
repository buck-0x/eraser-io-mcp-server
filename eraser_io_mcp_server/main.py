# main.py
from .server import mcp
# Import the module containing the tool to ensure it's registered
from . import render_eraser_diagram

def main():
    """Entry point for the MCP server."""
    mcp.run()


# Entry point to run the server
if __name__ == "__main__":
    main()
