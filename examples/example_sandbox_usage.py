"""
Example demonstrating sandbox execution with MCP tools.

This script shows how to:
1. Use MCP tools in a sandboxed environment
2. Handle results safely
3. Benefit from security isolation

Run with:
    uv run mcp-exec examples/example_sandbox_usage.py --sandbox

Or configure sandbox in mcp_config.json and run:
    uv run mcp-exec examples/example_sandbox_usage.py
"""

import asyncio

# Import runtime functions
# These work identically in both direct and sandbox mode
from runtime.mcp_client import call_mcp_tool


async def main():
    """Demonstrate MCP tool usage in sandbox."""

    print("=== Sandbox Execution Example ===\n")

    # Example 1: Call a git tool (if configured)
    try:
        print("1. Fetching git status...")
        result = await call_mcp_tool("git__git_status", {"repo_path": "."})

        print(f"   Result type: {type(result)}")
        print(f"   Success: Git status retrieved\n")

    except Exception as e:
        print(f"   Note: {e} (ensure git server configured)\n")

    # Example 2: Demonstrate security isolation
    print("2. Testing security isolation...")

    try:
        import socket

        socket.create_connection(("example.com", 80), timeout=1)
        print("   WARNING: Network access available (not in sandbox?)")
    except Exception:
        print("   ✓ Network isolated (as expected in sandbox)")

    try:
        with open("/etc/test_write", "w") as f:
            f.write("test")
        print("   WARNING: Filesystem writable (not in sandbox?)")
    except (PermissionError, OSError):
        print("   ✓ Root filesystem read-only (as expected)")

    try:
        with open("/workspace/test.txt", "w") as f:
            f.write("workspace test")
        print("   ✓ Workspace tmpfs writable (as expected)")
    except Exception as e:
        print(f"   WARNING: Workspace not writable: {e}")

    # Example 3: Demonstrate resource limits
    print("\n3. Demonstrating resource awareness...")
    import os

    uid = os.getuid()
    gid = os.getgid()
    print(f"   Running as UID={uid}, GID={gid}")

    if uid == 65534:
        print("   ✓ Rootless execution (nobody user)")
    else:
        print(f"   Note: Running as UID {uid} (direct mode)")

    print("\n=== Sandbox Example Complete ===")
    print("This script executed safely in an isolated container!")


if __name__ == "__main__":
    asyncio.run(main())
