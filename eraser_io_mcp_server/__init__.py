"""Eraser.io MCP Server - A tool for rendering diagrams using the Eraser API."""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .server import mcp
from .render_eraser_diagram import render_diagram

__all__ = ["mcp", "render_diagram"]
