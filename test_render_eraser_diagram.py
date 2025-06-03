#!/usr/bin/env python3
"""
Test script for render_eraser_diagram.py

This script tests various functionalities of the render_eraser_diagram module.
Requires ERASER_API_TOKEN to be set in environment or .env file.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from render_eraser_diagram import check_undefined_icons, render_diagram

# Load environment variables
load_dotenv()

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test_header(test_name):
    """Print a formatted test header"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing: {test_name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_result(success, message):
    """Print test result with color"""
    if success:
        print(f"{GREEN}✓ {message}{RESET}")
    else:
        print(f"{RED}✗ {message}{RESET}")

def test_icon_validation():
    """Test the icon validation functionality"""
    print_test_header("Icon Validation")

    # Test with standard icons
    code_with_standard = "icon: user\nicon: database"
    undefined = check_undefined_icons(code_with_standard)
    print_result(len(undefined) == 0, f"Standard icons validation: {undefined}")

    # Test with undefined icons
    code_with_undefined = 'icon: custom-icon\nicon: another-custom'
    undefined = check_undefined_icons(code_with_undefined)
    print_result(len(undefined) == 2, f"Undefined icons detected: {undefined}")

    # Test with SKIP_ICON_CHECK
    os.environ["SKIP_ICON_CHECK"] = "true"
    undefined = check_undefined_icons(code_with_undefined)
    print_result(len(undefined) == 0, "Icon check skipped when SKIP_ICON_CHECK=true")
    os.environ.pop("SKIP_ICON_CHECK", None)


def test_render_diagram_function():
    """Test the render_diagram function directly"""
    print_test_header("render_diagram Function")

    if not os.getenv("ERASER_API_TOKEN"):
        print(f"{YELLOW}⚠ Skipping API tests - ERASER_API_TOKEN not set{RESET}")
        return

    # Test basic sequence diagram
    result = render_diagram(
        diagram_type="sequence-diagram",
        code="Alice -> Bob: Hello\\nBob -> Alice: Hi",
        return_file=False,
        background=False,
        theme="dark",
    )

    print_result(result.get("success", False), "Basic sequence diagram")
    if result.get("success"):
        print(f"  Image URL: {result.get('image_url', 'N/A')[:50]}...")
        print(f"  Edit URL: {result.get('create_eraser_file_url', 'N/A')[:50]}...")

    # Test with file return
    result_file = render_diagram(
        diagram_type="flowchart-diagram",
        code="Start -> Process -> End",
        return_file=True,
        background=True,
        theme="light",
    )

    print_result(
        result_file.get("success", False) and "image_blob" in result_file,
        "Diagram with file return"
    )

    # Test with string boolean parameters
    result_str_bool = render_diagram(
        diagram_type="sequence-diagram",
        code="A -> B: Test",
        return_file="false",
        background="True",
        theme="dark",
    )

    print_result(result_str_bool.get("success", False), "String boolean parameters")

    # Test with warning for undefined icons
    result_warning = render_diagram(
        diagram_type="flowchart",
        code="custom-icon: My Service",
        return_file=False,
        background=False,
        theme="dark",
    )

    has_warning = "warning" in result_warning
    print_result(has_warning, f"Warning for undefined icons: {has_warning}")

def test_cli_interface():
    """Test the CLI interface"""
    print_test_header("CLI Interface")

    script_path = Path(__file__).parent / "render_eraser_diagram.py"

    # Test help
    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        capture_output=True,
        text=True
    )
    print_result(result.returncode == 0, "Help command")

    if not os.getenv("ERASER_API_TOKEN"):
        print(f"{YELLOW}⚠ Skipping CLI API tests - ERASER_API_TOKEN not set{RESET}")
        return

    # Test basic CLI usage
    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--diagram-type",
            "sequence-diagram",
            "--code",
            "User -> API: Request\\nAPI -> User: Response",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        try:
            output = json.loads(result.stdout)
            print_result(output.get("success", False), "Basic CLI usage")
        except json.JSONDecodeError:
            print_result(False, f"CLI output is not valid JSON: {result.stdout}")
    else:
        print_result(False, f"CLI failed: {result.stderr}")

    # Test with all parameters
    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--diagram-type",
            "flowchart",
            "--code",
            "Start -> End",
            "--theme",
            "light",
            "--scale",
            "2",
            "--background",
            "--return-file",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        try:
            output = json.loads(result.stdout)
            success = output.get("success", False) and "image_blob" in output
            print_result(success, "CLI with all parameters")
        except json.JSONDecodeError:
            print_result(False, "CLI output is not valid JSON")
    else:
        print_result(False, f"CLI failed: {result.stderr}")


def test_edge_cases():
    """Test edge cases and error handling"""
    print_test_header("Edge Cases")

    # Test without API token
    original_token = os.environ.pop("ERASER_API_TOKEN", None)
    result = render_diagram(
        diagram_type="sequence-diagram", code="A -> B", return_file=False
    )
    print_result(
        not result.get("success") and "ERASER_API_TOKEN" in result.get("message", ""),
        "Error when API token missing",
    )
    if original_token:
        os.environ["ERASER_API_TOKEN"] = original_token

    # Test special characters in code
    if os.getenv("ERASER_API_TOKEN"):
        result = render_diagram(
            diagram_type="sequence-diagram",
            code='User -> API: {"data": "value"}\\nAPI -> User: Response with "quotes"',
            return_file=False,
        )
        print_result(result.get("success", False), "Special characters in diagram code")

    # Test theme with quotes
    if os.getenv("ERASER_API_TOKEN"):
        result = render_diagram(
            diagram_type="flowchart",
            code="A -> B",
            theme="dark",
        )
        print_result(result.get("success", False), "Theme with existing quotes")


def test_parameter_processing():
    """Test parameter processing logic"""
    print_test_header("Parameter Processing")

    # Test remove_quotes function
    from render_eraser_diagram import render_diagram

    # Create a test to verify quote removal
    test_values = [
        ('"true"', True, "Quoted true string"),
        ("false", False, "Unquoted false string"),
        ('"1"', True, "Quoted 1 string"),
        ("yes", True, "Yes string"),
        ("no", False, "No string"),
        (True, True, "Boolean True"),
        (False, False, "Boolean False"),
    ]

    print("Testing boolean parameter conversion:")
    for value, expected, desc in test_values:
        # We can't directly test the internal processing, but we can verify
        # the function doesn't crash with these inputs
        if os.getenv("ERASER_API_TOKEN"):
            try:
                result = render_diagram(
                    diagram_type="flowchart",
                    code="A -> B",
                    background=value,
                    return_file=False,
                )
                print_result(True, f"  {desc} - processed without error")
            except Exception as e:
                print_result(False, f"  {desc} - error: {str(e)}")


def main():
    """Run all tests"""
    print(f"{BLUE}Starting render_eraser_diagram.py tests{RESET}")

    # Check for API token
    if not os.getenv("ERASER_API_TOKEN"):
        print(
            f"\n{YELLOW}⚠ Warning: ERASER_API_TOKEN not set. Some tests will be skipped.{RESET}"
        )
        print(
            f"{YELLOW}To run all tests, set ERASER_API_TOKEN in your environment or .env file.{RESET}"
        )

    # Run tests
    test_icon_validation()
    test_render_diagram_function()
    test_cli_interface()
    test_edge_cases()
    test_parameter_processing()

    print(f"\n{BLUE}Tests completed!{RESET}")


if __name__ == "__main__":
    main()
