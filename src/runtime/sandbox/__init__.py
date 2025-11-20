"""
Sandbox module for secure script execution in isolated containers.

This module provides container-based isolation for executing user scripts,
implementing comprehensive security controls including:
- Rootless container execution
- Network isolation
- Filesystem restrictions
- Resource limits
- Capability dropping
"""

from .container import ContainerSandbox, SandboxResult
from .exceptions import (
    SandboxError,
    SandboxRuntimeError,
    SandboxTimeout,
    SandboxResourceError,
)
from .security import SecurityPolicy

__all__ = [
    "ContainerSandbox",
    "SandboxResult",
    "SandboxError",
    "SandboxRuntimeError",
    "SandboxTimeout",
    "SandboxResourceError",
    "SecurityPolicy",
]
