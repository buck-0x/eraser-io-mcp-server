# Eraser Diagram Renderer

A Python MCP (Model Context Protocol) server and CLI tool to render diagrams using the [Eraser](https://www.eraser.io/) API.

## Features

- 📊 **Multiple Diagram Types**: Sequence, flowchart, ER, cloud architecture, and more
- 🎨 **Customizable**: Themes, backgrounds, and scaling options
- 📦 **Flexible Output**: Get image URLs or base64-encoded file content
- 🔗 **Eraser File URL**: Returns link to edit diagram in Eraser
- ✅ **Icon Validation**: Checks for undefined icons and provides warnings

## Documentation

- [MCP Usage Guide](MCP_USAGE.md) - How to use with Claude Desktop, VS Code, Windsurf, or other environments.
- [Eraser Docs](https://docs.eraser.io/docs/what-is-eraser) - General Eraser documentation
- [Eraser Diagram-as-code Documentation](https://docs.eraser.io/docs/diagram-as-code) - Information about the syntax
- [Eraser DSL API Reference](https://docs.eraser.io/reference/generate-diagram-from-eraser-dsl) - Information about the endpoints and parameters used

## Basic Usage

```bash
python render_eraser_diagram.py --diagram-type sequence-diagram --code "Alice -> Bob: Hello"
```

This will output JSON with the image URL:

```json
{
  "success": true,
  "message": "Diagram rendered successfully",
  "image_url": "https://app.eraser.io/workspace/...",
  "create_eraser_file_url": "https://app.eraser.io/workspace/..."
}
```

If undefined icons are detected:

```json
{
  "success": true,
  "message": "Diagram rendered successfully",
  "image_url": "https://app.eraser.io/workspace/...",
  "create_eraser_file_url": "https://app.eraser.io/workspace/...",
  "warning": "Warning: The following icons are not defined in the standard Eraser icons list: custom-icon. These icons may not render correctly. You can disable this warning by setting SKIP_ICON_CHECK=true."
}
```

## Parameters

- `--diagram-type` (required): Type of diagram (e.g., sequence-diagram, cloud-architecture-diagram)
- `--code` (required): Diagram code in Eraser syntax
- `--return-file`: Return base64-encoded image data instead of URL (defaults to False)
- `--background`: Include background (defaults to False)
- `--theme`: Choose "light" or "dark" theme (defaults to "dark")
- `--scale`: Scale factor from 1.0 to 5.0 (defaults to "1")

## Authentication

For CLI usage, set your Eraser API token in one of these ways:

1. **Environment variable**:

   ```bash
   export ERASER_API_TOKEN=your_token_here
   python render_eraser_diagram.py --diagram-type sequence-diagram --code "A -> B"
   ```
2. **`.env` file** in the project directory:

   ```bash
   echo "ERASER_API_TOKEN=your_token_here" > .env
   ```

For MCP server usage with Claude Desktop, see the [MCP Usage Guide](MCP_USAGE.md).

## Icon Validation

This tool validates icon references against the standard Eraser icons list (provided in `eraser-standard-icons.csv`). If you use custom icons that aren't in the standard list:

- You'll receive a warning in the response
- The diagram will still be generated
- To disable icon validation, set `SKIP_ICON_CHECK=true`:

  ```bash
  SKIP_ICON_CHECK=true python render_eraser_diagram.py --diagram-type flowchart --code "custom-icon: My Service"
  ```

## Handling Special Characters

For multi-line diagrams and special characters:

- Use `\n` for line breaks
- Use `\"` for quotes within the code
- Use `\\` for literal backslashes

## Examples

### Multi-line sequence diagram (returns URL):

```bash
python render_eraser_diagram.py --diagram-type sequence-diagram \
  --code "Alice -> Bob: Hello\nBob -> Alice: Hi there\nAlice -> Bob: How are you?"
```

Output:

```json
{
  "success": true,
  "message": "Diagram rendered successfully",
  "image_url": "https://app.eraser.io/workspace/...",
  "create_eraser_file_url": "https://app.eraser.io/workspace/..."
}
```

### With JSON data and return file:

```bash
python render_eraser_diagram.py --diagram-type sequence-diagram \
  --code "User -> API: POST /data {\"key\": \"value\"}\nAPI -> User: 200 OK" \
  --return-file
```

Output:

```json
{
  "success": true,
  "message": "Diagram rendered successfully",
  "image_blob": "iVBORw0KGgoAAAANSUhEUgA..."
}
```

### Cloud architecture with light theme:

```bash
python render_eraser_diagram.py --diagram-type cloud-architecture-diagram \
  --code "AWS S3 Bucket\n|\nAWS Lambda" --theme light --background
```

### Debug mode to see processed code:

```bash
DEBUG=1 python render_eraser_diagram.py --diagram-type sequence-diagram \
  --code "A -> B: Test\nB -> C: Response"
```

## Supported Diagram Types

- `sequence-diagram`
- `cloud-architecture-diagram`
- `flowchart`
- `entity-relationship-diagram`
- And more (check [Eraser Diagram-as-code documentation](https://docs.eraser.io/docs/diagram-as-code))

## Requirements

- Python 3.10 or higher
- Eraser API token

## Installation

Using pip:
```bash
pip install -e .
```

Using uv (fast Python package manager):
```bash
uv pip install -e .
```

## Troubleshooting

- If you get an API error, check that your token in `.env` is valid
- Use `DEBUG=1` to see how your code is being processed
- Ensure proper escaping of special characters in your shell
- If you see icon warnings, check if your icons are custom or set `SKIP_ICON_CHECK=true`
