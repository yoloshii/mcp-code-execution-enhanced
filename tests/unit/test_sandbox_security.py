"""Unit tests for sandbox security policy."""

import pytest
from runtime.sandbox.security import SecurityPolicy


def test_security_policy_defaults():
    """Test default security policy values."""
    policy = SecurityPolicy()

    assert policy.memory_limit == "512m"
    assert policy.cpu_limit is None
    assert policy.pids_limit == 128
    assert policy.timeout == 30
    assert policy.max_timeout == 120
    assert policy.network_mode == "none"
    assert policy.container_user == "65534:65534"
    assert policy.drop_capabilities == ["ALL"]


def test_security_policy_validation_valid():
    """Test validation passes for valid policy."""
    policy = SecurityPolicy(
        memory_limit="1g",
        timeout=60,
        max_timeout=120,
        pids_limit=256,
    )

    # Should not raise
    policy.validate()


def test_security_policy_validation_timeout_exceeds_max():
    """Test validation fails when timeout exceeds max."""
    policy = SecurityPolicy(timeout=150, max_timeout=120)

    with pytest.raises(ValueError, match="exceeds max"):
        policy.validate()


def test_security_policy_validation_negative_timeout():
    """Test validation fails for negative timeout."""
    policy = SecurityPolicy(timeout=-5)

    with pytest.raises(ValueError, match="must be positive"):
        policy.validate()


def test_security_policy_validation_invalid_memory_format():
    """Test validation fails for invalid memory format."""
    policy = SecurityPolicy(memory_limit="invalid")

    with pytest.raises(ValueError, match="Invalid memory limit format"):
        policy.validate()


def test_security_policy_validation_invalid_network_mode():
    """Test validation fails for invalid network mode."""
    policy = SecurityPolicy(network_mode="invalid")

    with pytest.raises(ValueError, match="Invalid network mode"):
        policy.validate()


def test_security_policy_to_docker_flags():
    """Test conversion to Docker CLI flags."""
    policy = SecurityPolicy(
        memory_limit="1g",
        cpu_limit="2.0",
        pids_limit=256,
        network_mode="none",
    )

    flags = policy.to_docker_flags()

    # Check essential security flags
    assert "--rm" in flags
    assert "--interactive" in flags
    assert "--network" in flags
    assert "none" in flags
    assert "--read-only" in flags
    assert "--pids-limit" in flags
    assert "256" in flags
    assert "--memory" in flags
    assert "1g" in flags
    assert "--cpus" in flags
    assert "2.0" in flags
    assert "--cap-drop" in flags
    assert "ALL" in flags
    assert "--user" in flags
    assert "65534:65534" in flags
    assert "--security-opt" in flags
    assert "no-new-privileges" in flags


def test_security_policy_tmpfs_mounts():
    """Test tmpfs mount generation."""
    policy = SecurityPolicy(
        tmpfs_size_tmp="128m",
        tmpfs_size_workspace="256m",
    )

    flags = policy.to_docker_flags()

    # Find tmpfs flags
    tmpfs_flags = [flags[i + 1] for i, f in enumerate(flags) if f == "--tmpfs"]

    assert len(tmpfs_flags) == 2
    assert any("/tmp:" in f and "size=128m" in f for f in tmpfs_flags)
    assert any("/workspace:" in f and "size=256m" in f for f in tmpfs_flags)


def test_security_policy_no_cpu_limit():
    """Test that CPU limit is optional."""
    policy = SecurityPolicy(cpu_limit=None)

    flags = policy.to_docker_flags()

    assert "--cpus" not in flags
