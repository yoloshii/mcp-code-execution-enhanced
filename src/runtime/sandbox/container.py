"""Container-based sandbox for secure script execution."""

import asyncio
import logging
import os
import shutil
from asyncio import subprocess as aio_subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .exceptions import SandboxError, SandboxRuntimeError, SandboxTimeout
from .security import SecurityPolicy

logger = logging.getLogger("mcp_execution.sandbox")


@dataclass
class SandboxResult:
    """Result of sandbox execution."""

    success: bool
    exit_code: int
    stdout: str
    stderr: str
    timeout_occurred: bool = False


class ContainerSandbox:
    """
    Secure container-based sandbox for script execution.

    Provides isolated execution environment with:
    - Rootless containers (nobody:nogroup 65534:65534)
    - Network isolation (--network none)
    - Read-only filesystem + tmpfs workspaces
    - Resource limits (memory, CPU, PIDs)
    - Capability dropping (--cap-drop ALL)
    - Timeout enforcement
    """

    def __init__(
        self,
        runtime: str = "auto",
        image: str = "python:3.11-slim",
        security_policy: Optional[SecurityPolicy] = None,
    ):
        """
        Initialize container sandbox.

        Args:
            runtime: Container runtime ('docker', 'podman', or 'auto')
            image: Container image to use
            security_policy: Security constraints (default: SecurityPolicy())
        """
        self.runtime = self._detect_runtime(runtime)
        self.image = image
        self.security_policy = security_policy or SecurityPolicy()
        self.security_policy.validate()

        logger.info(f"Initialized sandbox: runtime={self.runtime}, image={self.image}")

    def _detect_runtime(self, preferred: str) -> str:
        """
        Detect and validate container runtime.

        Args:
            preferred: Preferred runtime ('docker', 'podman', or 'auto')

        Returns:
            Path to runtime binary

        Raises:
            SandboxRuntimeError: If no runtime found
        """
        if preferred != "auto":
            # Try explicit preference
            runtime_path = shutil.which(preferred)
            if not runtime_path:
                raise SandboxRuntimeError(
                    f"Requested runtime '{preferred}' not found in PATH"
                )
            return runtime_path

        # Auto-detection: prefer podman > docker
        for runtime in ["podman", "docker"]:
            runtime_path = shutil.which(runtime)
            if runtime_path:
                logger.debug(f"Auto-detected container runtime: {runtime}")
                return runtime_path

        raise SandboxRuntimeError(
            "No container runtime found. Please install Docker or Podman."
        )

    async def _ensure_runtime_ready(self) -> None:
        """
        Ensure container runtime is ready.

        For Podman on macOS/Windows, this auto-starts the Podman machine if needed.
        """
        runtime_name = os.path.basename(self.runtime)
        if "podman" not in runtime_name:
            # Docker doesn't need machine management
            return

        # Check if Podman is accessible
        for attempt in range(3):
            proc = await asyncio.create_subprocess_exec(
                self.runtime,
                "info",
                "--format",
                "{{json .}}",
                stdout=aio_subprocess.PIPE,
                stderr=aio_subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            code = proc.returncode

            if code == 0:
                logger.debug("Podman runtime ready")
                return

            # Check if issue is missing/stopped machine
            combined = f"{stdout.decode()}\n{stderr.decode()}".lower()
            needs_machine = any(
                phrase in combined
                for phrase in (
                    "cannot connect to podman",
                    "podman machine",
                    "run the podman machine",
                    "socket: connect",
                )
            )

            if not needs_machine:
                raise SandboxRuntimeError(
                    f"Podman runtime unavailable: {stderr.decode()}"
                )

            # Try to start machine
            logger.info("Starting Podman machine...")
            start_proc = await asyncio.create_subprocess_exec(
                self.runtime,
                "machine",
                "start",
                stdout=aio_subprocess.PIPE,
                stderr=aio_subprocess.PIPE,
            )
            start_stdout, start_stderr = await start_proc.communicate()
            start_code = start_proc.returncode

            if start_code == 0:
                continue  # Retry info check

            # Check if machine doesn't exist
            start_combined = f"{start_stdout.decode()}\n{start_stderr.decode()}".lower()
            if "does not exist" in start_combined or "no such machine" in start_combined:
                # Initialize machine
                logger.info("Initializing Podman machine...")
                init_proc = await asyncio.create_subprocess_exec(
                    self.runtime,
                    "machine",
                    "init",
                    stdout=aio_subprocess.PIPE,
                    stderr=aio_subprocess.PIPE,
                )
                init_stdout, init_stderr = await init_proc.communicate()
                init_code = init_proc.returncode

                if init_code != 0:
                    raise SandboxRuntimeError(
                        f"Failed to initialize Podman machine: {init_stderr.decode()}"
                    )
                continue  # Retry info/start sequence

            raise SandboxRuntimeError(
                f"Failed to start Podman machine: {start_stderr.decode()}"
            )

        raise SandboxRuntimeError(
            "Unable to prepare Podman runtime after 3 attempts"
        )

    async def _ensure_image_available(self) -> None:
        """
        Ensure container image is available locally.

        Pulls image if not found.
        """
        # Check if image exists
        proc = await asyncio.create_subprocess_exec(
            self.runtime,
            "image",
            "inspect",
            self.image,
            stdout=aio_subprocess.DEVNULL,
            stderr=aio_subprocess.DEVNULL,
        )
        code = await proc.wait()

        if code == 0:
            logger.debug(f"Image {self.image} available")
            return

        # Pull image
        logger.info(f"Pulling image {self.image}...")
        proc = await asyncio.create_subprocess_exec(
            self.runtime,
            "pull",
            self.image,
            stdout=aio_subprocess.PIPE,
            stderr=aio_subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        code = proc.returncode

        if code != 0:
            raise SandboxError(
                f"Failed to pull image {self.image}: {stderr.decode()}"
            )

        logger.info(f"Successfully pulled {self.image}")

    def _build_command(
        self,
        script_path: Path,
        config_path: Optional[Path] = None,
    ) -> list[str]:
        """
        Build container execution command.

        Args:
            script_path: Path to Python script to execute
            config_path: Optional path to mcp_config.json

        Returns:
            Complete command as list of arguments
        """
        # Get base security flags from policy
        cmd = [self.runtime, "run"] + self.security_policy.to_docker_flags()

        # Add environment variables
        cmd.extend([
            "--env", "HOME=/workspace",
            "--env", "PYTHONUNBUFFERED=1",
            "--env", "PYTHONIOENCODING=utf-8",
            "--env", "PYTHONDONTWRITEBYTECODE=1",
        ])

        # Mount src/runtime so scripts can import runtime modules
        # Find the runtime package directory (src/)
        runtime_src = Path(__file__).parent.parent.parent
        cmd.extend([
            "-v", f"{runtime_src.absolute()}:/workspace/src:ro,Z",
        ])

        # Add src to PYTHONPATH so imports work
        cmd.extend([
            "--env", "PYTHONPATH=/workspace/src",
        ])

        # Mount script as read-only with Z flag for SELinux contexts
        # Use :ro,Z to ensure proper labeling for rootless containers
        cmd.extend([
            "-v", f"{script_path.absolute()}:/workspace/{script_path.name}:ro,Z",
        ])

        # Mount config if provided
        if config_path and config_path.exists():
            cmd.extend([
                "-v", f"{config_path.absolute()}:/workspace/mcp_config.json:ro,Z",
            ])

        # Add image and execution command
        cmd.extend([
            self.image,
            "python3",
            "-u",  # Unbuffered output
            f"/workspace/{script_path.name}",
        ])

        return cmd

    async def execute_script(
        self,
        script_path: Path,
        config_path: Optional[Path] = None,
        timeout: Optional[int] = None,
    ) -> SandboxResult:
        """
        Execute Python script in isolated container.

        Args:
            script_path: Path to Python script to execute
            config_path: Optional path to mcp_config.json
            timeout: Execution timeout in seconds (default: policy timeout)

        Returns:
            SandboxResult with execution outcome

        Raises:
            SandboxError: If execution fails
            SandboxTimeout: If execution exceeds timeout
        """
        if not script_path.exists():
            raise SandboxError(f"Script not found: {script_path}")

        if timeout is None:
            timeout = self.security_policy.timeout

        # Ensure runtime is ready
        await self._ensure_runtime_ready()

        # Ensure image is available
        await self._ensure_image_available()

        # Build execution command
        cmd = self._build_command(script_path, config_path)

        logger.info(f"Executing script: {script_path.name}")
        logger.debug(f"Container command: {' '.join(cmd)}")

        # Execute container
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=aio_subprocess.DEVNULL,
            stdout=aio_subprocess.PIPE,
            stderr=aio_subprocess.PIPE,
        )

        # Wait with timeout
        timeout_occurred = False
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
            exit_code = process.returncode or 0
        except asyncio.TimeoutError:
            # Kill process on timeout
            logger.warning(f"Execution timed out after {timeout}s, killing container")
            process.kill()
            await process.communicate()
            timeout_occurred = True
            exit_code = 124  # Timeout exit code
            stdout = b""
            stderr = f"Execution exceeded timeout of {timeout}s\n".encode()

        stdout_text = stdout.decode("utf-8", errors="replace")
        stderr_text = stderr.decode("utf-8", errors="replace")

        success = exit_code == 0 and not timeout_occurred

        if not success:
            logger.error(
                f"Execution failed: exit_code={exit_code}, "
                f"timeout={timeout_occurred}"
            )
            if stderr_text:
                logger.debug(f"Stderr: {stderr_text[:500]}")

        return SandboxResult(
            success=success,
            exit_code=exit_code,
            stdout=stdout_text,
            stderr=stderr_text,
            timeout_occurred=timeout_occurred,
        )
