# Using Eraser MCP Server

This guide explains how to use the Eraser MCP server to generate diagrams programmatically.

## Local Setup

### 1. Install the MCP Server

```bash
# Clone the repository
git clone https://github.com/buck-0x/eraser-io-mcp-server
cd eraser-io-mcp-server

# Install dependencies
# Using uv (fast Python package manager)
uv pip install -e .

# Or using standard pip
pip install -e .
```

### 2. Get Your Eraser API Token

You'll need an API token from Eraser. You can set it in one of two ways:

**Option A: Environment Variable in Claude Desktop Config (Recommended)**
Set it directly in the Claude Desktop configuration (see step 3).

**Option B: Local .env File**
Create a `.env` file in the project directory:

```bash
ERASER_API_TOKEN=your_token_here
```

### 3. Configure Host

#### Claude Desktop

**Important**: Requires Python 3.10 or higher.

Add the MCP server to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "eraser": {
      "command": "python",
      "args": ["/path/to/eraser-io-mcp-server/main.py"],
      "env": {
        "ERASER_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

**Note**: If you set the token in the Claude Desktop config (recommended), you don't need a `.env` file. The token in the config takes precedence.

## Using the MCP Tool

Once configured, you can use the `render_diagram` tool in your client to generate diagrams.

### Tool Parameters

- `diagram_type` (required): Type of diagram to render
  - `sequence-diagram`
  - `cloud-architecture-diagram`
  - `flowchart-diagram`
  - `entity-relationship-diagram`
- `code` (required): Diagram code in Eraser syntax
- `return_file` (optional, default: false): Whether to return base64 image data
- `background` (optional, default: false): Include background in diagram
- `theme` (optional, default: "light"): Choose "light" or "dark" theme
- `scale` (optional, default: "1"): Scale factor - "1", "2", or "3"

**Known Issue**: The Eraser API has a caching bug where images are cached based only on the diagram code. Changing `theme` or `background` parameters without changing the code will return the previously cached image instead of generating a new one with the updated settings.

### Example Usage

#### Basic Sequence Diagram (returns URL)

```
Please create a sequence diagram showing a user login flow using the Eraser tool.
```

The host will use:

```python
render_diagram(
    diagram_type="sequence-diagram",
    code="User -> Frontend: Enter credentials\nFrontend -> API: POST /login\nAPI -> Database: Verify credentials\nDatabase -> API: User data\nAPI -> Frontend: JWT token\nFrontend -> User: Login successful"
)
```

Response:

```json
{
  "success": true,
  "image_url": "https://app.eraser.io/api/render/...",
  "create_eraser_file_url": "https://app.eraser.io/workspace/...",
  "message": "Successfully rendered sequence-diagram diagram"
}
```

Note: If undefined icons are detected, you may also see a `warning` field in the response.

##### Cloud Architecture Diagram with File Content

```
Create a cloud architecture diagram for a serverless app and return the image file content.
```

The host will use:

```python
render_diagram(
    diagram_type="cloud-architecture-diagram",
    code="AWS S3 Bucket\n|\nAWS Lambda Function\n|\nAWS API Gateway\n|\nReact Frontend",
    return_file=True,
    theme="light",
    background=True
)
```

Response:

```json
{
  "success": true,
  "image_blob": "iVBORw0KGgoAAAANSUhEUgA...",
  "message": "Successfully rendered cloud-architecture-diagram diagram"
}
```

### Tips

1. **Diagram Code Formatting**: Use `\n` for line breaks in your diagram code
2. **Special Characters**: Escape quotes and backslashes properly
3. **Token Management**: The token is automatically loaded from the environment - no need to pass it explicitly
4. **File Handling**: When `return_file=True`, you'll get base64 data that Claude can save to a file
5. **Icon Validation**: The tool validates icon references and warns about undefined icons. Set `SKIP_ICON_CHECK=true` in the environment to disable this

### Common Diagram Types

#### Sequence Diagrams

```
Alice -> Bob: Hello
Bob -> Alice: Hi there
Note over Alice, Bob: Greeting complete
```

#### Flowcharts

```
Start -> Decision: Is valid?
Decision -> Process: Yes
Decision -> Error: No
Process -> End
Error -> End
```

#### Entity Relationship Diagrams

```
User ||--o{ Order : places
Order ||--|{ OrderItem : contains
Product ||--o{ OrderItem : "ordered in"
```

#### Cloud Architecture

```
Users -> CloudFront
CloudFront -> S3 Bucket: Static Assets
CloudFront -> ALB: Dynamic Content
ALB -> ECS Cluster
ECS Cluster -> RDS Database
```

## Troubleshooting

1. **MCP Not Available**: Restart the MCP server in your host after updating configuration
2. **Authentication Error**: Verify your ERASER_API_TOKEN is correct
3. **Diagram Syntax Error**: Check Eraser documentation for correct syntax
4. **No Response**: Enable debug mode with `DEBUG=1` in the environment
   ```json
   {
     "mcpServers": {
       "eraser": {
         "command": "python",
         "args": ["/path/to/eraser-io-mcp-server/main.py"],
         "env": {
           "ERASER_API_TOKEN": "your_token_here",
           "DEBUG": "1"
         }
       }
     }
   }
   ```
5. **Python Version Error**: Ensure you have Python 3.10 or higher installed

## Advanced Usage

### Batch Diagram Generation

You can ask your host (e.g. Claude Desktop) to generate multiple related diagrams:

```
Create a complete system design with:
1. A sequence diagram for the login flow
2. An ER diagram for the database schema
3. A cloud architecture diagram for the deployment
```

The host will call the tool multiple times with appropriate parameters for each diagram type.

### Custom Themes and Styling

Specify exact styling requirements:

```
Create a light-themed sequence diagram with background for a presentation about OAuth flow.
```

This will use `theme="light"` and `background=True` parameters.
