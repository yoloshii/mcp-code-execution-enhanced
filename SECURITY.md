# Security Documentation

## Sandbox Security Model

The MCP Code Execution runtime provides optional container-based sandboxing for secure execution of AI-generated scripts.

## Threat Model

### What Sandbox Protects Against

✅ **Network Access**
- Malicious outbound connections
- Data exfiltration
- C2 communication
- DDoS participation

✅ **Filesystem Access**
- Unauthorized file reads outside allowed paths
- System configuration tampering
- Malware installation
- Persistence mechanisms

✅ **Privilege Escalation**
- Kernel exploits
- Container escapes
- Capability abuse
- Setuid binaries

✅ **Resource Exhaustion**
- Memory bombs
- Fork bombs
- CPU monopolization
- Disk space exhaustion

### What Sandbox Does NOT Protect Against

❌ **Logical Bugs**
- Scripts can still have business logic errors
- Incorrect data processing
- Algorithmic mistakes

❌ **MCP Server Vulnerabilities**
- Sandbox doesn't protect the MCP servers themselves
- Server-side vulnerabilities remain possible
- API misuse can still occur

❌ **Timing/Side-Channel Attacks**
- Resource usage patterns may leak information
- Timing attacks on cryptographic operations

## Security Features

### Container Isolation

**Default Configuration:**
```python
SecurityPolicy(
    # Resource limits
    memory_limit="512m",      # 512 MB RAM maximum
    cpu_limit=None,           # No CPU limit (optional)
    pids_limit=128,           # Maximum 128 processes
    timeout=30,               # 30 second execution timeout

    # Network
    network_mode="none",      # Complete network isolation

    # Filesystem
    tmpfs_size_tmp="64m",     # 64 MB /tmp tmpfs
    tmpfs_size_workspace="128m",  # 128 MB /workspace tmpfs

    # User/Permissions
    container_user="65534:65534",     # nobody:nogroup (rootless)
    drop_capabilities=["ALL"],        # No capabilities
)
```

### Rootless Execution

Scripts execute as UID 65534 (nobody) and GID 65534 (nogroup):
- Cannot access privileged operations
- Cannot modify system files
- Cannot interact with other users' processes
- Cannot bind to privileged ports (<1024)

### Network Isolation

**Default: Complete isolation** (`--network none`)

Network stack is completely disabled:
- No outbound connections
- No DNS resolution
- No socket creation
- No localhost access

**Alternative modes** (use with caution):
- `host`: Share host network (reduces isolation)
- `bridge`: Connect to bridge network
- `container:name`: Share another container's network

### Filesystem Restrictions

**Read-only root filesystem:**
- Immutable base system
- Cannot modify /etc, /usr, /bin, etc.
- Prevents malware installation

**Writable tmpfs mounts:**
- `/tmp` (64 MB, noexec, nosuid, nodev)
- `/workspace` (128 MB, noexec, nosuid, nodev)

**Restrictions:**
- `noexec`: Cannot execute binaries from tmpfs
- `nosuid`: Setuid/setgid bits ignored
- `nodev`: Device files disallowed

### Capability Dropping

**All capabilities dropped** (`--cap-drop ALL`):

Disabled operations include:
- `CAP_NET_ADMIN`: Network administration
- `CAP_SYS_ADMIN`: System administration
- `CAP_DAC_OVERRIDE`: Discretionary access control bypass
- `CAP_SETUID/SETGID`: Change user/group IDs
- `CAP_SYS_PTRACE`: Debug other processes
- `CAP_SYS_MODULE`: Load kernel modules
- [And 30+ more capabilities]

### Resource Limits

**Memory Limit** (default: 512 MB)
- Prevents memory exhaustion attacks
- OOM killer terminates on exceeded
- Configurable per use case

**PID Limit** (default: 128 processes)
- Prevents fork bombs
- Limits concurrent processes
- Container killed if exceeded

**CPU Limit** (optional)
- Limit CPU usage (e.g., "1.0" = 1 CPU)
- Prevents CPU monopolization
- Configurable per workload

**Timeout** (default: 30s, max: 120s)
- Enforced execution time limit
- Process killed on timeout (SIGKILL)
- Prevents infinite loops

### Additional Security Options

**no-new-privileges:**
- Prevents privilege escalation
- Disables setuid/setgid binaries
- Blocks capability gains

**Automatic cleanup:**
- Containers always removed (`--rm`)
- No persistent state between runs
- Prevents resource leaks

## Configuration

### Sandbox Configuration

**mcp_config.json:**
```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "."]
    }
  },
  "sandbox": {
    "enabled": true,
    "runtime": "podman",
    "image": "python:3.11-slim",
    "memory_limit": "512m",
    "cpu_limit": "1.0",
    "pids_limit": 128,
    "timeout": 30,
    "max_timeout": 120
  }
}
```

### Runtime Detection

**Automatic detection order:**
1. Explicit `--sandbox` flag
2. Configuration `sandbox.enabled: true`
3. Environment variable `MCP_SANDBOX_RUNTIME`

**Container runtime priority:**
1. Explicit configuration (`runtime: "podman"`)
2. Auto-detection: podman > docker

### Security Levels

**Level 1: Direct Mode** (default)
- No container isolation
- Fastest execution
- Use for: Trusted scripts, development

**Level 2: Sandbox Mode** (--sandbox)
- Complete isolation
- Resource limits
- Use for: Untrusted scripts, production

## Operational Security

### Prerequisites

**For Podman (recommended):**
```bash
# Linux
sudo apt-get install -y podman

# macOS
brew install podman
podman machine init
podman machine start

# Verify
podman info
```

**For Docker:**
```bash
# Linux
curl -fsSL https://get.docker.com | sh

# macOS
brew install --cask docker

# Verify
docker info
```

### Image Preparation

**Pull image before first use:**
```bash
# Podman
podman pull python:3.11-slim

# Docker
docker pull python:3.11-slim
```

**Verify image:**
```bash
podman image inspect python:3.11-slim
```

### Monitoring

**Execution logs:**
- Stdout/stderr captured automatically
- Security events logged to stderr
- Timeout events logged

**Example log output:**
```
[INFO] === Sandbox Mode ===
[INFO] Runtime: /usr/bin/podman
[INFO] Image: python:3.11-slim
[INFO] Memory: 512m
[INFO] Timeout: 30s
[INFO] Executing script: test_script.py
[INFO] Execution completed successfully
```

## Best Practices

### When to Use Sandbox Mode

✅ **Always use for:**
- AI-generated code
- Untrusted scripts
- Production deployments
- Multi-tenant environments
- Scripts handling sensitive data

⚠️ **Consider using for:**
- Development (slower but safer)
- Automated workflows
- Scheduled tasks

❌ **Avoid for:**
- Rapid iteration (use direct mode)
- Known safe operations
- Performance-critical paths

### Configuration Recommendations

**Production:**
```json
{
  "sandbox": {
    "enabled": true,
    "runtime": "podman",
    "image": "python:3.11-slim",
    "memory_limit": "512m",
    "timeout": 30
  }
}
```

**Development:**
```json
{
  "sandbox": {
    "enabled": false  // Use direct mode for speed
  }
}
```

**High-security:**
```json
{
  "sandbox": {
    "enabled": true,
    "memory_limit": "256m",  // Reduced limit
    "cpu_limit": "0.5",      // Half CPU
    "pids_limit": 64,        // Fewer processes
    "timeout": 15            // Shorter timeout
  }
}
```

## Limitations

### Known Limitations

1. **No nested containers**
   - Cannot run Docker/Podman inside sandbox
   - Container runtime not available to scripts

2. **Limited filesystem access**
   - Only /tmp and /workspace writable
   - No persistent storage between runs
   - Host paths require explicit configuration

3. **No network access by default**
   - Cannot fetch external resources
   - Cannot make API calls outside MCP
   - Configure `network_mode` if needed (reduces security)

4. **Performance overhead**
   - Container startup: ~200-500ms
   - Memory overhead: ~50MB
   - Not suitable for sub-second executions

### Compatibility

**Container Runtimes:**
- ✅ Podman 4.0+ (recommended)
- ✅ Docker 20.10+
- ❌ Windows native containers (use WSL2)

**Operating Systems:**
- ✅ Linux (native)
- ✅ macOS (via Podman machine)
- ✅ Windows (WSL2 + Podman/Docker)

**Python Versions:**
- ✅ Python 3.11 (recommended)
- ✅ Python 3.12
- ✅ Python 3.13
- ⚠️ Python 3.14 (avoid due to anyio issues)

## Security Hardening

### Additional Hardening Options

**Custom seccomp profile:**
```json
{
  "sandbox": {
    "runtime": "podman",
    "seccomp_profile": "/path/to/seccomp.json"
  }
}
```

**AppArmor/SELinux:**
```json
{
  "sandbox": {
    "runtime": "podman",
    "security_opts": [
      "apparmor=mcp-sandbox",
      "label=type:mcp_sandbox_t"
    ]
  }
}
```

## Incident Response

### If Compromise Suspected

1. **Immediate actions:**
   - Stop all running containers
   - Review execution logs
   - Check for persistent changes

2. **Investigation:**
   ```bash
   # List recent containers
   podman ps -a --filter "ancestor=python:3.11-slim"

   # Review logs
   podman logs <container-id>

   # Inspect container state
   podman inspect <container-id>
   ```

3. **Mitigation:**
   - Rotate MCP server credentials
   - Review scripts for malicious code
   - Strengthen security policy
   - Consider additional monitoring

## References

- [Anthropic: Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Anthropic: Claude Code Sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [MCP Security Best Practices](https://modelcontextprotocol.io/docs/security)
- [Podman Security Features](https://docs.podman.io/en/latest/markdown/podman-run.1.html#security-options)
- [Docker Security](https://docs.docker.com/engine/security/)
