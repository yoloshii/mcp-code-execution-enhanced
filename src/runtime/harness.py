"""
Script execution harness for MCP-enabled Python scripts.

This harness:
1. Initializes MCP client manager
2. Executes user script with MCP tools available (direct or sandboxed)
3. Handles signals gracefully (SIGINT/SIGTERM)
4. Cleans up all connections on exit

Execution modes:
- Direct mode: Script runs in current process (default)
- Sandbox mode: Script runs in isolated container (--sandbox flag or config)
"""

import asyncio
import json
import logging
import runpy
import signal
import sys
from pathlib import Path
from typing import Any, NoReturn, Optional

from .config import McpConfig
from .exceptions import McpExecutionError
from .mcp_client import get_mcp_client_manager

# Configure logging to stderr
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s", stream=sys.stderr)

logger = logging.getLogger("mcp_execution.harness")


def _parse_arguments() -> tuple[Path, bool]:
    """
    Parse command-line arguments.

    Returns:
        Tuple of (script_path, use_sandbox)
    """
    if len(sys.argv) < 2:
        logger.error("Usage: python -m runtime.harness <script_path> [--sandbox]")
        sys.exit(1)

    script_path = Path(sys.argv[1]).resolve()
    use_sandbox = "--sandbox" in sys.argv

    return script_path, use_sandbox


def _load_config() -> Optional[McpConfig]:
    """
    Load MCP configuration if available.

    Returns:
        McpConfig if found, None otherwise
    """
    config_path = Path.cwd() / "mcp_config.json"

    if not config_path.exists():
        logger.debug("No mcp_config.json found, using defaults")
        return None

    try:
        with open(config_path) as f:
            config_dict = json.load(f)

        # Handle missing sandbox config (backward compatibility)
        if "sandbox" not in config_dict:
            config_dict["sandbox"] = {"enabled": False}

        return McpConfig.model_validate(config_dict)
    except Exception as e:
        logger.warning(f"Failed to load config: {e}, using defaults")
        return None


async def _execute_sandboxed(script_path: Path, config: McpConfig) -> int:
    """
    Execute script in sandbox mode.

    Args:
        script_path: Path to Python script
        config: MCP configuration

    Returns:
        Exit code
    """
    from .sandbox import ContainerSandbox, SandboxError, SandboxTimeout
    from .sandbox.security import SecurityPolicy

    logger.info("=== Sandbox Mode ===")
    logger.info(f"Runtime: {config.sandbox.runtime}")
    logger.info(f"Image: {config.sandbox.image}")
    logger.info(f"Memory: {config.sandbox.memory_limit}")
    logger.info(f"Timeout: {config.sandbox.timeout}s")

    # Create security policy from config
    policy = SecurityPolicy(
        memory_limit=config.sandbox.memory_limit,
        cpu_limit=config.sandbox.cpu_limit,
        pids_limit=config.sandbox.pids_limit,
        timeout=config.sandbox.timeout,
        max_timeout=config.sandbox.max_timeout,
    )

    # Create sandbox
    try:
        sandbox = ContainerSandbox(
            runtime=config.sandbox.runtime,
            image=config.sandbox.image,
            security_policy=policy,
        )
    except SandboxError as e:
        logger.error(f"Failed to initialize sandbox: {e}")
        return 1

    # Execute script in container
    try:
        config_path = Path.cwd() / "mcp_config.json"
        result = await sandbox.execute_script(
            script_path,
            config_path if config_path.exists() else None,
        )

        # Output results
        if result.stdout:
            sys.stdout.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)

        if result.timeout_occurred:
            logger.error(f"Execution timed out after {policy.timeout}s")
            return 124

        if not result.success:
            logger.error(f"Execution failed with exit code {result.exit_code}")
            return result.exit_code

        logger.info("Execution completed successfully")
        return 0

    except SandboxTimeout:
        logger.error("Execution timed out")
        return 124
    except SandboxError as e:
        logger.error(f"Sandbox error: {e}")
        return 1


def _execute_direct(script_path: Path) -> int:
    """
    Execute script in direct mode (current process, no sandbox).

    Args:
        script_path: Path to Python script

    Returns:
        Exit code
    """
    logger.info("=== Direct Mode ===")

    # Add project root and src/ to Python path for imports
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
        logger.debug(f"Added to sys.path: {src_path}")

    project_root = src_path.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        logger.debug(f"Added to sys.path: {project_root}")

    # Create persistent event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Initialize MCP client manager
    manager = get_mcp_client_manager()
    try:
        loop.run_until_complete(manager.initialize())
        logger.info("MCP client manager initialized")
    except McpExecutionError as e:
        logger.error(f"Failed to initialize MCP client: {e}")
        return 1

    # Set up signal handling
    def signal_handler(signum: int, frame: Any) -> None:
        """Handle shutdown signals."""
        signal_name = signal.Signals(signum).name
        logger.info(f"Received {signal_name}, shutting down...")
        sys.exit(130)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Execute script
    exit_code = 0
    try:
        logger.info(f"Executing script: {script_path}")
        runpy.run_path(str(script_path), run_name="__main__")
        logger.info("Script execution completed")

    except KeyboardInterrupt:
        logger.info("Execution interrupted by user")
        exit_code = 130

    except Exception as e:
        logger.error(f"Script execution failed: {e}", exc_info=True)
        exit_code = 1

    finally:
        # Cleanup
        logger.debug("Cleaning up MCP connections...")
        try:
            loop.run_until_complete(manager.cleanup())
            logger.info("Cleanup complete")
        except BaseException as e:
            # Suppress BaseExceptionGroup from async generators
            if type(e).__name__ == "BaseExceptionGroup":
                logger.debug("Suppressed BaseExceptionGroup during cleanup")
            else:
                logger.error(f"Cleanup failed: {e}", exc_info=True)
                if exit_code == 0:
                    exit_code = 1
        finally:
            loop.close()

    return exit_code


def main() -> NoReturn:
    """Entry point for the harness with sandbox support."""
    # 1. Parse CLI arguments
    script_path, use_sandbox_flag = _parse_arguments()

    # 2. Validate script exists
    if not script_path.exists():
        logger.error(f"Script not found: {script_path}")
        sys.exit(1)

    if not script_path.is_file():
        logger.error(f"Not a file: {script_path}")
        sys.exit(1)

    logger.info(f"Script: {script_path}")

    # 3. Load configuration
    config = _load_config()

    # 4. Determine execution mode
    use_sandbox = use_sandbox_flag or (config and config.sandbox.enabled)

    # 5. Route to appropriate execution mode
    if use_sandbox:
        if config is None:
            logger.error(
                "Sandbox mode requires mcp_config.json with sandbox configuration"
            )
            sys.exit(1)

        # Sandbox mode (async)
        exit_code = asyncio.run(_execute_sandboxed(script_path, config))
    else:
        # Direct mode (existing behavior)
        exit_code = _execute_direct(script_path)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
