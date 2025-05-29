# main.py
from server import mcp
# Import the module containing the tool to ensure it's registered
import render_eraser_diagram

# Entry point to run the server
if __name__ == "__main__":
    mcp.run()
