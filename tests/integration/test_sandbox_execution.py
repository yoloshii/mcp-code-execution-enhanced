"""Integration tests for sandbox execution."""

import asyncio
from pathlib import Path

import pytest

from runtime.sandbox import ContainerSandbox, SandboxError, SandboxTimeout
from runtime.sandbox.security import SecurityPolicy


@pytest.fixture
def tmp_script(tmp_path):
    """Create a temporary script file."""

    def _create_script(content: str) -> Path:
        script = tmp_path / "test_script.py"
        script.write_text(content)
        return script

    return _create_script


@pytest.mark.asyncio
async def test_execute_simple_script(tmp_script):
    """Test executing a simple script in sandbox."""
    script = tmp_script("print('hello from sandbox')")

    sandbox = ContainerSandbox()
    result = await sandbox.execute_script(script)

    assert result.success
    assert result.exit_code == 0
    assert "hello from sandbox" in result.stdout
    assert not result.timeout_occurred


@pytest.mark.asyncio
async def test_execute_script_with_error(tmp_script):
    """Test executing a script that raises an error."""
    script = tmp_script("""
raise ValueError("test error")
""")

    sandbox = ContainerSandbox()
    result = await sandbox.execute_script(script)

    assert not result.success
    assert result.exit_code != 0
    assert "ValueError: test error" in result.stderr


@pytest.mark.asyncio
async def test_execute_script_timeout(tmp_script):
    """Test timeout enforcement."""
    script = tmp_script("""
import time
time.sleep(60)  # Sleep longer than timeout
print("should not reach here")
""")

    policy = SecurityPolicy(timeout=2)
    sandbox = ContainerSandbox(security_policy=policy)

    result = await sandbox.execute_script(script, timeout=2)

    assert not result.success
    assert result.exit_code == 124
    assert result.timeout_occurred
    assert "should not reach here" not in result.stdout


@pytest.mark.asyncio
async def test_network_isolation(tmp_script):
    """Test that network is isolated."""
    script = tmp_script("""
import socket
try:
    sock = socket.create_connection(("example.com", 80), timeout=2)
    print("FAIL: network accessible")
except Exception as e:
    print(f"PASS: network blocked ({type(e).__name__})")
""")

    sandbox = ContainerSandbox()
    result = await sandbox.execute_script(script)

    assert result.success
    assert "PASS: network blocked" in result.stdout


@pytest.mark.asyncio
async def test_filesystem_readonly(tmp_script):
    """Test that root filesystem is read-only."""
    script = tmp_script("""
import os
try:
    with open("/etc/test_write", "w") as f:
        f.write("test")
    print("FAIL: filesystem writable")
except (PermissionError, OSError) as e:
    print(f"PASS: filesystem readonly ({type(e).__name__})")
""")

    sandbox = ContainerSandbox()
    result = await sandbox.execute_script(script)

    assert result.success
    assert "PASS: filesystem readonly" in result.stdout


@pytest.mark.asyncio
async def test_tmpfs_workspace_writable(tmp_script):
    """Test that /workspace tmpfs is writable."""
    script = tmp_script("""
import os
try:
    with open("/workspace/test.txt", "w") as f:
        f.write("test data")
    with open("/workspace/test.txt", "r") as f:
        content = f.read()
    print(f"PASS: workspace writable, content={content}")
except Exception as e:
    print(f"FAIL: workspace not writable ({e})")
""")

    sandbox = ContainerSandbox()
    result = await sandbox.execute_script(script)

    assert result.success
    assert "PASS: workspace writable" in result.stdout
    assert "content=test data" in result.stdout


@pytest.mark.asyncio
async def test_tmpfs_noexec(tmp_script):
    """Test that tmpfs mounts have noexec."""
    script = tmp_script("""
import os
import stat
try:
    # Write a script to tmp
    with open("/tmp/test.sh", "w") as f:
        f.write("#!/bin/sh\\necho 'test'")
    os.chmod("/tmp/test.sh", 0o755)

    # Try to execute it
    import subprocess
    result = subprocess.run(["/tmp/test.sh"], capture_output=True)
    print(f"FAIL: executed binary in tmpfs (code={result.returncode})")
except (PermissionError, OSError) as e:
    print(f"PASS: tmpfs noexec enforced ({type(e).__name__})")
""")

    sandbox = ContainerSandbox()
    result = await sandbox.execute_script(script)

    assert result.success
    assert "PASS: tmpfs noexec" in result.stdout


@pytest.mark.asyncio
async def test_resource_limits_memory(tmp_script):
    """Test memory limit enforcement."""
    script = tmp_script("""
import sys
data = []
try:
    # Try to allocate more than limit
    for i in range(100):
        data.append(bytearray(10 * 1024 * 1024))  # 10MB chunks
        print(f"Allocated {(i+1)*10}MB")
except MemoryError:
    print("PASS: memory limit enforced")
except Exception as e:
    print(f"FAIL: unexpected error {type(e).__name__}: {e}")
""")

    # Use very low memory limit for faster test
    policy = SecurityPolicy(memory_limit="64m", timeout=10)
    sandbox = ContainerSandbox(security_policy=policy)

    result = await sandbox.execute_script(script)

    # Container should be killed by OOM or hit MemoryError
    # Either way, it shouldn't allocate all 1000MB
    assert "Allocated 1000MB" not in result.stdout


@pytest.mark.asyncio
async def test_script_not_found():
    """Test error handling for missing script."""
    sandbox = ContainerSandbox()

    with pytest.raises(SandboxError, match="Script not found"):
        await sandbox.execute_script(Path("/nonexistent/script.py"))


@pytest.mark.asyncio
async def test_user_isolation(tmp_script):
    """Test that script runs as nobody (UID 65534)."""
    script = tmp_script("""
import os
uid = os.getuid()
gid = os.getgid()
print(f"UID={uid}, GID={gid}")
if uid == 65534 and gid == 65534:
    print("PASS: running as nobody")
else:
    print("FAIL: not running as nobody")
""")

    sandbox = ContainerSandbox()
    result = await sandbox.execute_script(script)

    assert result.success
    assert "PASS: running as nobody" in result.stdout
    assert "UID=65534, GID=65534" in result.stdout


@pytest.mark.asyncio
async def test_multiple_executions(tmp_path):
    """Test that sandbox can be reused for multiple executions."""
    # Create two separate script files
    script1 = tmp_path / "script1.py"
    script1.write_text("print('execution 1')")

    script2 = tmp_path / "script2.py"
    script2.write_text("print('execution 2')")

    sandbox = ContainerSandbox()

    # Execute first script
    result1 = await sandbox.execute_script(script1)
    assert result1.success
    assert "execution 1" in result1.stdout

    # Execute second script (reuse sandbox instance)
    result2 = await sandbox.execute_script(script2)
    assert result2.success
    assert "execution 2" in result2.stdout
