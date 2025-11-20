"""Security policy configuration for sandbox execution."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class SecurityPolicy:
    """
    Security policy for sandbox execution.

    Defines resource limits, filesystem access, network configuration,
    and other security constraints for containerized script execution.
    """

    # Resource limits
    memory_limit: str = "512m"
    """Memory limit for container (e.g., '512m', '1g')."""

    cpu_limit: Optional[str] = None
    """CPU limit (e.g., '1.0' for 1 CPU, '0.5' for half CPU)."""

    pids_limit: int = 128
    """Maximum number of processes allowed in container."""

    timeout: int = 30
    """Execution timeout in seconds."""

    max_timeout: int = 120
    """Maximum allowed timeout in seconds."""

    # Filesystem
    allow_host_paths: List[Path] = field(default_factory=list)
    """Host paths allowed to be mounted (empty = none allowed)."""

    tmpfs_size_tmp: str = "64m"
    """Size limit for /tmp tmpfs mount."""

    tmpfs_size_workspace: str = "128m"
    """Size limit for /workspace tmpfs mount."""

    # Network
    network_mode: str = "none"
    """Network mode: 'none' (isolated), 'host', or network name."""

    # User/permissions
    container_user: str = "65534:65534"
    """User:Group to run as in container (default: nobody:nogroup)."""

    drop_capabilities: List[str] = field(default_factory=lambda: ["ALL"])
    """Capabilities to drop (default: all capabilities)."""

    def validate(self) -> None:
        """
        Validate policy constraints.

        Raises:
            ValueError: If policy contains invalid values.
        """
        if self.timeout > self.max_timeout:
            raise ValueError(
                f"Timeout {self.timeout}s exceeds max {self.max_timeout}s"
            )

        if self.timeout <= 0:
            raise ValueError(f"Timeout must be positive, got {self.timeout}s")

        if self.pids_limit <= 0:
            raise ValueError(f"PIDs limit must be positive, got {self.pids_limit}")

        # Validate memory limit format
        if not self.memory_limit or not any(
            self.memory_limit.endswith(suffix) for suffix in ["k", "m", "g", "K", "M", "G"]
        ):
            raise ValueError(
                f"Invalid memory limit format: {self.memory_limit}. "
                "Expected format like '512m', '1g', '2G'"
            )

        # Validate network mode
        valid_network_modes = ["none", "host", "bridge"]
        if self.network_mode not in valid_network_modes and not self.network_mode.startswith(
            "container:"
        ):
            raise ValueError(
                f"Invalid network mode: {self.network_mode}. "
                f"Expected one of {valid_network_modes} or 'container:name'"
            )

    def to_docker_flags(self) -> List[str]:
        """
        Convert policy to Docker/Podman CLI flags.

        Returns:
            List of CLI flags for container execution.
        """
        flags = [
            "--rm",  # Auto-cleanup
            "--interactive",
            "--network",
            self.network_mode,
            "--read-only",  # Read-only root filesystem
            "--pids-limit",
            str(self.pids_limit),
            "--memory",
            self.memory_limit,
            "--tmpfs",
            f"/tmp:rw,noexec,nosuid,nodev,size={self.tmpfs_size_tmp}",
            "--tmpfs",
            f"/workspace:rw,noexec,nosuid,nodev,size={self.tmpfs_size_workspace}",
            "--workdir",
            "/workspace",
            "--security-opt",
            "no-new-privileges",
            "--user",
            self.container_user,
        ]

        # Add CPU limit if specified
        if self.cpu_limit:
            flags.extend(["--cpus", self.cpu_limit])

        # Add capability drops
        for cap in self.drop_capabilities:
            flags.extend(["--cap-drop", cap])

        # Add allowed host path mounts
        for host_path in self.allow_host_paths:
            # Mount as read-only by default
            flags.extend(["-v", f"{host_path}:/mnt/{host_path.name}:ro"])

        return flags
