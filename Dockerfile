FROM python:3.10-slim

WORKDIR /app

# Install uv for faster package installation
RUN pip install --no-cache-dir uv

# Copy dependency files first for better caching
COPY pyproject.toml .
COPY .python-version .

# Install dependencies
RUN uv pip install --system .

# Copy application code
COPY main.py server.py render_eraser_diagram.py ./
COPY eraser-standard-icons.csv ./

# Expose MCP port
EXPOSE 8000

# Set environment variables
ENV MCP_TRANSPORT=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

# Run the server with HTTP transport
CMD ["python", "main.py", "--transport", "http"]
