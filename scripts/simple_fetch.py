"""
SKILL: Simple Fetch

DESCRIPTION: Demonstrates basic CLI-based skill pattern - fetches a URL and returns content

WHEN TO USE:
- Learning how to create skills
- Simple data fetching tasks
- As a template for custom skills

CLI ARGUMENTS:
    --url    URL to fetch (required)

USAGE:
    uv run python -m runtime.harness skills/simple_fetch.py \
        --url "https://example.com"

REQUIREMENTS:
    MCP server with fetch capability (e.g., mcp-server-fetch)
"""

import argparse
import asyncio
import sys


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Simple URL fetch skill")
    parser.add_argument("--url", required=True, help="URL to fetch")

    # Filter out script path from sys.argv (harness adds it)
    args_to_parse = [arg for arg in sys.argv[1:] if not arg.endswith(".py")]
    return parser.parse_args(args_to_parse)


async def main():
    """Main skill workflow."""
    from runtime.mcp_client import call_mcp_tool

    args = parse_args()

    print(f"Fetching: {args.url}")

    try:
        # Call fetch tool (adjust server name based on your config)
        result = await call_mcp_tool("fetch__fetch", {"url": args.url})

        print(f"✓ Successfully fetched {len(str(result))} bytes")
        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    asyncio.run(main())
