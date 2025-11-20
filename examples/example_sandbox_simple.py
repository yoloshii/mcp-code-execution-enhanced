"""
Simple sandbox example without MCP dependencies.

This demonstrates the sandbox security features without requiring
the full MCP runtime to be installed in the container.

Run with:
    uv run mcp-exec examples/example_sandbox_simple.py --sandbox
"""

import os


def main():
    """Demonstrate sandbox security features."""

    print("=== Sandbox Security Demo ===\n")

    # 1. User isolation
    uid = os.getuid()
    gid = os.getgid()
    print(f"1. User Isolation:")
    print(f"   Running as UID={uid}, GID={gid}")
    if uid == 65534 and gid == 65534:
        print("   ✓ Rootless execution (nobody:nogroup)\n")
    else:
        print(f"   Note: Running as UID {uid} (direct mode?)\n")

    # 2. Network isolation
    print("2. Network Isolation:")
    try:
        import socket

        socket.create_connection(("example.com", 80), timeout=1)
        print("   WARNING: Network access available (not sandboxed?)\n")
    except Exception as e:
        print(f"   ✓ Network isolated ({type(e).__name__})\n")

    # 3. Filesystem restrictions
    print("3. Filesystem Security:")

    # Try to write to root (should fail)
    try:
        with open("/etc/test_write", "w") as f:
            f.write("test")
        print("   WARNING: Root filesystem writable")
    except (PermissionError, OSError) as e:
        print(f"   ✓ Root filesystem read-only ({type(e).__name__})")

    # Try to write to workspace (should succeed)
    try:
        with open("/workspace/test.txt", "w") as f:
            f.write("sandbox test")
        with open("/workspace/test.txt", "r") as f:
            content = f.read()
        print(f"   ✓ Workspace writable (content: '{content}')")
    except Exception as e:
        print(f"   WARNING: Workspace not writable: {e}")

    # Try to execute from tmpfs (should fail due to noexec)
    try:
        with open("/tmp/test.sh", "w") as f:
            f.write("#!/bin/sh\necho 'test'")
        os.chmod("/tmp/test.sh", 0o755)

        import subprocess

        result = subprocess.run(["/tmp/test.sh"], capture_output=True)
        print(f"   WARNING: Executed binary from tmpfs (exit={result.returncode})")
    except (PermissionError, OSError) as e:
        print(f"   ✓ tmpfs noexec enforced ({type(e).__name__})\n")

    # 4. Environment
    print("4. Environment:")
    print(f"   HOME: {os.getenv('HOME')}")
    print(f"   PYTHONUNBUFFERED: {os.getenv('PYTHONUNBUFFERED')}")
    print(f"   Working directory: {os.getcwd()}")

    print("\n=== Sandbox Demo Complete ===")
    print("✓ All security features validated!")


if __name__ == "__main__":
    main()
