"""Pytest configuration for integration tests."""

import json
from pathlib import Path

import pytest

from runtime.mcp_client import get_mcp_client_manager


@pytest.fixture(scope="session", autouse=True)
def mcp_config_for_tests(tmp_path_factory):
    """Create a temporary mcp_config.json for integration tests.

    This fixture:
    1. Creates a temp directory for the test session
    2. Copies the example config to a real config file
    3. Makes it available at Path.cwd() / "mcp_config.json"

    This ensures tests can run even though mcp_config.json is in .gitignore.
    """
    # Read the example config
    example_config_path = Path(__file__).parent.parent.parent / "mcp_config.example.json"

    if not example_config_path.exists():
        pytest.skip("mcp_config.example.json not found")

    with open(example_config_path) as f:
        config = json.load(f)

    # Write it to the current working directory
    config_path = Path.cwd() / "mcp_config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    yield config_path

    # Cleanup after all tests
    if config_path.exists():
        config_path.unlink()


@pytest.fixture(autouse=True)
async def cleanup_mcp_manager():
    """Cleanup MCP client manager after each test.

    This fixture ensures that:
    1. Each test gets a fresh manager instance
    2. The singleton cache is cleared between tests
    3. All connections are properly closed

    This is critical because get_mcp_client_manager() uses @lru_cache
    which would otherwise share state across all tests.
    """
    # Yield to run the test
    yield

    # Cleanup after test
    try:
        manager = get_mcp_client_manager()
        # Only cleanup if manager was initialized
        if manager._state.value != "uninitialized":
            await manager.cleanup()
    except Exception as e:
        # Log but don't fail if cleanup has issues
        print(f"Warning: Manager cleanup failed: {e}")
    finally:
        # Clear the lru_cache to ensure next test gets fresh instance
        get_mcp_client_manager.cache_clear()
