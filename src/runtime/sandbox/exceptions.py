"""Sandbox-specific exceptions."""


class SandboxError(Exception):
    """Base exception for sandbox operations."""

    pass


class SandboxRuntimeError(SandboxError):
    """Container runtime not available or failed to start."""

    pass


class SandboxTimeout(SandboxError):
    """Script execution exceeded timeout limit."""

    pass


class SandboxResourceError(SandboxError):
    """Resource limit exceeded (memory, CPU, PIDs)."""

    pass


class SandboxSecurityError(SandboxError):
    """Security policy violation."""

    pass
