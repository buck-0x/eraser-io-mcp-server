#!/usr/bin/env python3
"""
Eraser.io Diagram Renderer

This script renders diagrams using the Eraser.io API and returns either an image URL or file content.

Usage:
    python render_eraser_diagram.py --diagramType sequence-diagram --code "Alice -> Bob: Hello"
"""

import argparse
import base64
import csv
import json
import os
import re
import sys

import requests
from dotenv import load_dotenv

from .server import mcp

# Load environment variables
load_dotenv()

# Load standard icons from CSV
STANDARD_ICONS = set()
icon_csv_path = os.path.join(os.path.dirname(__file__), "eraser-standard-icons.csv")
if os.path.exists(icon_csv_path):
    try:
        with open(icon_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "icon_name" in row:
                    STANDARD_ICONS.add(row["icon_name"])
    except (OSError, csv.Error) as e:
        # Log warning but continue without icon checking
        if os.getenv("DEBUG"):
            print(f"Warning: Could not load icon CSV file: {e}")


def check_undefined_icons(code):
    """
    Check for icon references in the code that are not in the standard icons list.

    Args:
        code (str): The diagram code to check

    Returns:
        list: List of undefined icon names found in the code
    """
    if os.getenv("SKIP_ICON_CHECK") == "true":
        return []

    # Pattern to match icon references
    # Icons can be referenced as icon: icon-name or "icon: icon-name"
    icon_pattern = r'(?:"icon:\s*([^"]+)"|icon:\s*([^\s\],]+))'

    # Find all icon references in the code
    icon_matches = re.findall(icon_pattern, code, re.IGNORECASE)

    # Clean up icon names and check against standard list
    undefined_icons = []
    for match in icon_matches:
        # Handle tuple from regex groups (quoted, unquoted)
        icon_name = (match[0] or match[1]).strip()
        if icon_name and icon_name not in STANDARD_ICONS:
            undefined_icons.append(icon_name)

    return list(set(undefined_icons))  # Remove duplicates


@mcp.tool()
def render_diagram(
    diagram_type,
    code,
    return_file=False,
    background=True,
    theme="light",
    scale="1",
):
    """
    Render a diagram using the Eraser.io API.

    Args:
        diagram_type (str): Type of diagram (e.g., 'sequence-diagram', 'cloud-architecture-diagram')
        code (str): Diagram code in Eraser.io syntax (with proper line breaks and escaping)
        return_file (bool): Whether to return the file content (defaults to False)
        background (bool): Whether to include background (defaults to True)
        theme (str): Theme to use - "light" or "dark" (defaults to "light")
        scale (str): Scale factor for the diagram - "1", "2", or "3" (defaults to "1")

    Returns:
        dict: Response containing success status, image data/URL, and message
    """

    # Get API token from environment
    api_token = os.getenv("ERASER_API_TOKEN")
    if not api_token:
        return {
            "success": False,
            "message": "Error: ERASER_API_TOKEN not found in environment",
        }

    # Validate scale parameter
    if str(scale) not in ["1", "2", "3"]:
        return {
            "success": False,
            "message": f"Error: Invalid scale value '{scale}'. Must be '1', '2', or '3'",
        }

    # Process the code to handle escape sequences using unicode_escape decoding
    try:
        processed_code = code.encode('utf-8').decode('unicode_escape')
    except Exception as e:
        return {
            "success": False,
            "message": f"Error decoding escape sequences: {e}",
        }

    # Debug output to show processed code
    if os.getenv("DEBUG"):
        print(f"Processed code:\n{processed_code}")
        print(f"Code length: {len(processed_code)} characters")

    # Check for undefined icons
    undefined_icons = check_undefined_icons(processed_code)
    warning_message = None
    if undefined_icons:
        warning_message = (
            f"Warning: The following icons are not defined in the standard Eraser icons list: "
            f"{', '.join(undefined_icons)}. These icons may not render correctly. "
            f"You can disable this warning by setting SKIP_ICON_CHECK=true."
        )

    # Prepare API request
    url = "https://app.eraser.io/api/render/elements"

    # Helper function to remove quotes from string parameters
    def remove_quotes(value):
        value = str(value).lower()
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        return value

    # Process parameters - remove quotes if present
    # Convert string booleans to actual booleans
    if isinstance(background, str):
        background_str = remove_quotes(background).lower()
        background = background_str in ["true", "1", "yes"]
    else:
        background = bool(background)

    if isinstance(return_file, str):
        return_file_str = remove_quotes(return_file).lower()
        return_file = return_file_str in ["true", "1", "yes"]
    else:
        return_file = bool(return_file)

    payload = {
        "elements": [
            {"type": "diagram", "diagramType": diagram_type, "code": processed_code}
        ],
        "background": background,
        "theme": theme,
        "scale": scale,
        "returnFile": return_file,
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_token}",
    }

    try:
        # Make API request
        response = requests.post(url, json=payload, headers=headers)

        # Check response status
        if response.status_code != 200:
            return {
                "success": False,
                "message": f"API request failed with status code {response.status_code}: {response.text}",
            }

        # Handle response based on returnFile parameter
        if return_file:
            # Return the binary image data
            image_blob = base64.b64encode(response.content).decode("utf-8")
            result = {
                "success": True,
                "image_blob": image_blob,
                "message": f"Successfully rendered {diagram_type} diagram",
            }
            if warning_message:
                result["warning"] = warning_message
            return result
        else:
            # Parse JSON response to get image URL
            response_data = response.json()
            image_url = response_data.get("imageUrl", "")
            create_eraser_file_url = response_data.get("createEraserFileUrl", "")
            if not image_url:
                return {"success": False, "message": "No image URL returned from API"}
            result = {
                "success": True,
                "image_url": image_url,
                "create_eraser_file_url": create_eraser_file_url,
                "message": f"Successfully rendered {diagram_type} diagram",
            }
            if warning_message:
                result["warning"] = warning_message
            return result

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"Failed to connect to Eraser.io API: {str(e)}",
        }
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Render diagrams using the Eraser.io API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple sequence diagram (returns URL)
  python render_eraser_diagram.py --diagram-type sequence-diagram --code "Alice -> Bob: Hello"

  # Return file content as base64
  python render_eraser_diagram.py --diagram-type sequence-diagram --code "Alice -> Bob: Hello" --return-file

  # Multi-line sequence diagram (use \\n for line breaks)
  python render_eraser_diagram.py --diagram-type sequence-diagram --code "Alice -> Bob: Hello\\nBob -> Alice: Hi there\\nAlice -> Bob: How are you?"

  # Cloud architecture with light theme and background
  python render_eraser_diagram.py --diagram-type cloud-architecture-diagram --code "AWS S3 Bucket\\n|\\nAWS Lambda" --theme light

  # Enable debug mode to see processed code
  DEBUG=1 python render_eraser_diagram.py --diagram-type sequence-diagram --code "A -> B: Test\\nB -> C: Response"
        """,
    )

    parser.add_argument(
        "--diagram-type",
        required=True,
        help="Type of diagram (e.g., sequence-diagram, cloud-architecture-diagram)",
    )
    parser.add_argument(
        "--code",
        required=True,
        help="Diagram code in Eraser.io syntax (use \\n for line breaks)",
    )
    parser.add_argument(
        "--no-background",
        action="store_true",
        default=False,
        help="Disable background in the diagram (background is enabled by default)",
    )
    parser.add_argument(
        "--theme",
        choices=["light", "dark"],
        default="light",
        help="Theme for the diagram (defaults to light)",
    )
    parser.add_argument(
        "--scale",
        choices=["1", "2", "3"],
        default="1",
        help="Scale factor for the diagram: 1, 2, or 3 (defaults to 1)",
    )
    parser.add_argument(
        "--return-file",
        action="store_true",
        default=False,
        help="Return the file content as base64 instead of URL (defaults to False)",
    )

    args = parser.parse_args()

    # Render the diagram
    result = render_diagram(
        diagram_type=args.diagram_type,
        code=args.code,
        return_file=args.return_file,
        background=not args.no_background,
        theme=args.theme,
        scale=args.scale,
    )

    # Output the result as JSON
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
