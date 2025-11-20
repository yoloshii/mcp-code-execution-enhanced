# Usage Guide

**Version:** 3.0 with Sandbox Integration
**Last Updated:** 2025-11-19

---

## Quick Start

### 1. Install Dependencies

```bash
cd /home/khitomer/Projects/mcp-code-execution

# Sync environment
uv sync

# Verify installation
uv run python -c "from runtime.mcp_client import get_mcp_client_manager; print('✓ Ready')"
```

### 2. Review Configuration

Your mcp_config.json already has 18 servers configured:
```bash
cat mcp_config.json | jq '.mcpServers | keys'
```

### 3. Explore Available Tools (Anthropic's Pattern)

```bash
# List servers
ls servers/

# List jina's tools
ls servers/jina/

# Read a tool definition
cat servers/jina/search_web.py
```

### 4. Choose Your Approach

#### Option A: Skills (PREFERRED - 99.6% token reduction)

For multi-step workflows, use pre-written skills:

```bash
# Discover available skills
ls skills/

# Read skill documentation
cat skills/simple_fetch.py

# Execute with CLI arguments (IMMUTABLE - don't edit file)
uv run python -m runtime.harness skills/simple_fetch.py \
    --url "https://example.com"
```

**Available example skills:**
- `simple_fetch.py` - Basic single-tool execution
- `multi_tool_pipeline.py` - Multi-tool chaining pattern

See `skills/README.md` for complete documentation.

**Benefits:** 99.6% token reduction, 96% time reduction, battle-tested workflows.

#### Option B: Write Custom Script (ALTERNATIVE - 98.7% token reduction)

For simple tasks or novel workflows, write a custom script:

Create `workspace/my_first_script.py`:
```python
"""My first MCP script using filesystem discovery."""

import asyncio
from servers.jina import search_web, SearchWebParams


async def main():
    print("Searching web with Jina...")

    result = await search_web(
        SearchWebParams(
            query="Model Context Protocol 2025",
            num=5
        )
    )

    print(f"✓ Found {len(result)} results")
    return result


if __name__ == "__main__":
    asyncio.run(main())
```

### 5. Run Your Script

**Direct mode (fast):**
```bash
uv run python -m runtime.harness workspace/my_first_script.py
```

**Sandbox mode (secure):**
```bash
uv run python -m runtime.harness workspace/my_first_script.py --sandbox
```

---

## Execution Modes

### Direct Mode (Default)

**When to use:**
- Development and iteration
- Trusted scripts
- Performance-critical paths
- Local testing

**Characteristics:**
- Runs in current process
- Full host access
- Fast (~100ms startup)
- No container overhead

**Command:**
```bash
uv run python -m runtime.harness workspace/script.py
```

### Sandbox Mode (Secure)

**When to use:**
- Production deployments
- AI-generated code
- Untrusted scripts
- Security-critical operations

**Characteristics:**
- Runs in isolated container
- Security hardened
- Moderate startup (~500ms)
- Resource limited

**Command:**
```bash
# Via CLI flag
uv run python -m runtime.harness workspace/script.py --sandbox

# Or via config
{
  "sandbox": {"enabled": true}
}
uv run python -m runtime.harness workspace/script.py
```

---

## Working with MCP Tools

### Discovering Tools

**Step 1: Explore servers**
```bash
$ ls ./servers/
apify  bright_data  context7  exa  jina  perplexity  ref  tavily  ...
```

**Step 2: Explore server's tools**
```bash
$ ls ./servers/jina/
__init__.py              read_url.py              search_web.py
parallel_read_url.py     search_arxiv.py          ...
```

**Step 3: Read tool documentation**
```bash
$ cat ./servers/jina/README.md
```

### Using Tools (Type-Safe)

**Import pattern:**
```python
from servers.{server_name} import {tool_name}, {ToolName}Params
```

**Examples:**

```python
# Jina (SSE transport)
from servers.jina import search_web, SearchWebParams

result = await search_web(SearchWebParams(query="...", num=5))

# Exa (HTTP transport)
from servers.exa import web_search_exa, WebSearchExaParams

result = await web_search_exa(WebSearchExaParams(query="...", numResults=5))

# Perplexity (stdio transport)
from servers.perplexity import perplexity_search, PerplexitySearchParams

result = await perplexity_search(PerplexitySearchParams(query="..."))
```

### Multi-Server Workflows

```python
"""Complex workflow using multiple MCP tools."""

import asyncio
from runtime.mcp_client import call_mcp_tool


async def analyze_repository(repo_path: str):
    """Multi-tool git repository analysis workflow."""

    print(f"Analyzing: {repo_path}")

    # Step 1: Get repository status
    print("1. Checking status...")
    status = await call_mcp_tool("git__git_status", {"repo_path": repo_path})
    print(f"   Status: {len(status)} files")

    # Step 2: Get recent commits
    print("2. Fetching commits...")
    commits = await call_mcp_tool(
        "git__git_log", {"repo_path": repo_path, "max_count": 10}
    )
    print(f"   Found {len(commits)} commits")

    # Step 3: Analyze branches
    print("3. Analyzing branches...")
    branches = await call_mcp_tool(
        "git__git_branch", {"repo_path": repo_path, "branch_type": "all"}
    )

    return {
        "status": status,
        "commits": commits,
        "branches": branches,
        "summary": {
            "total_commits": len(commits),
            "total_branches": len(branches)
        }
    }


if __name__ == "__main__":
    result = asyncio.run(analyze_repository("."))
    print(f"\n✓ Complete! Analyzed {result['summary']['total_commits']} commits")
```

**Run:**
```bash
# Development (fast)
uv run python -m runtime.harness workspace/research.py

# Production (secure)
uv run python -m runtime.harness workspace/research.py --sandbox
```

---

## Configuration

### Server Configuration

**stdio example:**
```json
{
  "perplexity": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@perplexity-ai/mcp-server"],
    "env": {
      "PERPLEXITY_API_KEY": "pplx-..."
    }
  }
}
```

**SSE example:**
```json
{
  "jina": {
    "type": "sse",
    "url": "https://mcp.jina.ai/sse",
    "headers": {
      "Authorization": "Bearer jina_..."
    }
  }
}
```

**HTTP example:**
```json
{
  "exa": {
    "type": "http",
    "url": "https://mcp.exa.ai/mcp",
    "headers": {
      "x-api-key": "..."
    }
  }
}
```

### Sandbox Configuration

**Minimal:**
```json
{
  "sandbox": {
    "enabled": true
  }
}
```

**Full:**
```json
{
  "sandbox": {
    "enabled": true,
    "runtime": "podman",
    "image": "mcp-execution:latest",
    "memory_limit": "512m",
    "cpu_limit": "1.0",
    "pids_limit": 128,
    "timeout": 30,
    "max_timeout": 120
  }
}
```

---

## Common Tasks

### Task: Web Search and Analysis

```python
from servers.jina import search_web, SearchWebParams

async def analyze_topic(topic: str):
    results = await search_web(
        SearchWebParams(query=topic, num=10)
    )

    # Process results
    for result in results:
        print(f"- {result.get('title')}: {result.get('url')}")

    return results

asyncio.run(analyze_topic("Quantum computing 2025"))
```

### Task: Code Search

```python
from servers.exa import get_code_context_exa, GetCodeContextExaParams

async def find_examples(library: str, pattern: str):
    result = await get_code_context_exa(
        GetCodeContextExaParams(
            query=f"{library} {pattern} examples"
        )
    )

    print(f"Found code examples for {library}")
    return result

asyncio.run(find_examples("fastapi", "websocket"))
```

### Task: Documentation Lookup

```python
from servers.ref import ref_search_documentation, RefSearchDocumentationParams

async def lookup_docs(library: str):
    result = await ref_search_documentation(
        RefSearchDocumentationParams(
            query=f"{library} API reference"
        )
    )

    print(f"Found documentation for {library}")
    return result

asyncio.run(lookup_docs("pydantic"))
```

### Task: Multi-Step Research

```python
from runtime.mcp_client import call_mcp_tool

async def analyze_codebase(repo_path: str):
    """Comprehensive repository analysis."""
    # Get status
    status = await call_mcp_tool("git__git_status", {"repo_path": repo_path})

    # Get commits
    commits = await call_mcp_tool(
        "git__git_log", {"repo_path": repo_path, "max_count": 20}
    )

    # Get branches
    branches = await call_mcp_tool("git__git_branch", {"repo_path": repo_path})

    return {"status": status, "commits": commits, "branches": branches}

asyncio.run(analyze_codebase("."))
```

---

## Debugging

### Enable Verbose Logging

```bash
# Set log level
export MCP_LOG_LEVEL=DEBUG

# Run with verbose output
uv run python -m runtime.harness workspace/script.py 2>&1 | tee execution.log
```

### Check MCP Connections

Add to your script:
```python
from runtime.mcp_client import get_mcp_client_manager

manager = get_mcp_client_manager()
await manager.initialize()

# Check what's configured
config = manager._config
print(f"Configured servers: {list(config.mcpServers.keys())}")

# Check what's connected
print(f"Connected servers: {list(manager._clients.keys())}")
```

### Validate Configuration

```bash
# Check JSON syntax
jq . mcp_config.json

# Validate with Python
uv run python -c "
from runtime.config import McpConfig
import json

with open('mcp_config.json') as f:
    config = McpConfig.model_validate_json(f.read())

print(f'✓ Valid config: {len(config.mcpServers)} servers')
"
```

### Test Sandbox

```bash
# Run simple security test
uv run python -m runtime.harness examples/example_sandbox_simple.py --sandbox

# Should show:
# ✓ Rootless execution (UID 65534)
# ✓ Network isolated
# ✓ Filesystem read-only
# ✓ Workspace writable
```

---

## Troubleshooting

### "Server not found in configuration"

**Cause:** Server name mismatch

**Solution:**
```bash
# Check configured servers
jq '.mcpServers | keys' mcp_config.json

# Use exact name in tool identifier
await call_mcp_tool("jina__search_web", ...)  # Correct
await call_mcp_tool("Jina__search_web", ...)  # Wrong (case sensitive)
```

### "Container runtime not found"

**Cause:** Docker/Podman not installed

**Solution:**
```bash
# Install Podman
sudo apt-get install -y podman

# Or Docker
curl -fsSL https://get.docker.com | sh

# Verify
podman --version
```

### "Permission denied" in sandbox

**Cause:** Script not readable by container user (65534)

**Solution:**
```bash
# Make script world-readable
chmod +r workspace/script.py

# Or check file permissions
ls -la workspace/script.py
```

### "Module not found" in sandbox

**Cause:** Runtime modules not available in container

**Solution:**
Use the custom mcp-execution:latest image:
```json
{
  "sandbox": {
    "image": "mcp-execution:latest"  // Has runtime pre-installed
  }
}
```

### "Tool not found on server"

**Cause:** Tool doesn't exist or wrappers not generated

**Solution:**
```bash
# Regenerate wrappers
uv run mcp-generate

# Check generated tools
ls servers/{server_name}/
```

---

## Best Practices

### 1. Use Type Hints

```python
# ✅ Good: Type-safe
from servers.jina import search_web, SearchWebParams

async def research(topic: str) -> Dict[str, Any]:
    result = await search_web(SearchWebParams(query=topic))
    return result

# ❌ Bad: Untyped
async def research(topic):
    result = await search_web({"query": topic})
    return result
```

### 2. Handle Errors Gracefully

```python
from runtime.exceptions import ToolExecutionError

try:
    result = await search_web(params)
except ToolExecutionError as e:
    logger.error(f"Search failed: {e}")
    # Fallback logic
    result = await backup_search(params)
```

### 3. Use Sandbox for Untrusted Code

```bash
# AI-generated or user-submitted code
uv run python -m runtime.harness user_code.py --sandbox

# Your own trusted code
uv run python -m runtime.harness trusted_code.py
```

### 4. Batch Operations

```python
# Use parallel operations when available
from servers.jina import parallel_read_url, ParallelReadUrlParams

# Read 5 URLs in parallel (much faster than sequential)
urls = ["url1", "url2", "url3", "url4", "url5"]
results = await parallel_read_url(ParallelReadUrlParams(urls=urls, timeout=60000))
```

### 5. Resource Management

```python
# Always use context managers or cleanup
from runtime.mcp_client import get_mcp_client_manager

manager = get_mcp_client_manager()
try:
    await manager.initialize()
    # Use manager...
finally:
    await manager.cleanup()  # Always cleanup
```

---

## Examples by Use Case

### Research & Analysis

```python
from servers.jina import search_web, SearchWebParams
from servers.exa import web_search_exa, WebSearchExaParams

# Compare search engines
jina_results = await search_web(SearchWebParams(query="..."))
exa_results = await web_search_exa(WebSearchExaParams(query="..."))
```

### Documentation Lookup

```python
from servers.ref import ref_search_documentation, RefSearchDocumentationParams

docs = await ref_search_documentation(
    RefSearchDocumentationParams(query="fastapi websockets")
)
```

### Code Discovery

```python
from servers.exa import get_code_context_exa, GetCodeContextExaParams
from servers.gitmcp import search_code  # If available

code = await get_code_context_exa(
    GetCodeContextExaParams(query="async error handling patterns")
)
```

### Content Extraction

```python
from servers.jina import read_url, ReadUrlParams

content = await read_url(
    ReadUrlParams(
        url="https://example.com/article",
        withAllLinks=True
    )
)
```

---

## Advanced Usage

### Custom Timeout

```bash
# Configure per script
{
  "sandbox": {
    "timeout": 60  // 60 seconds for long-running scripts
  }
}
```

### Custom Resource Limits

```json
{
  "sandbox": {
    "memory_limit": "1g",   // 1GB for data-intensive scripts
    "cpu_limit": "2.0",     // 2 CPUs for parallel processing
    "pids_limit": 256       // More processes for complex workflows
  }
}
```

### Disable Specific Servers

```json
{
  "mcpServers": {
    "slow_server": {
      "type": "stdio",
      "command": "...",
      "disabled": true  // Skip this server
    }
  }
}
```

---

## Performance Tips

### 1. Use Caching

Connections are cached automatically:
```python
# First call: connects to jina
result1 = await search_web(params1)  # ~1s (connection + call)

# Second call: reuses connection
result2 = await search_web(params2)  # ~100ms (call only)
```

### 2. Parallel Operations

```python
# Sequential (slow)
r1 = await search_web(params1)
r2 = await search_web(params2)

# Parallel (fast)
r1, r2 = await asyncio.gather(
    search_web(params1),
    search_web(params2)
)
```

### 3. Minimize Container Restarts

In sandbox mode, each script execution spawns a new container. Batch operations in single script:

```python
# ✅ Good: One container for multiple operations
async def main():
    result1 = await search_web(params1)
    result2 = await read_url(params2)
    result3 = await perplexity_search(params3)
    return [result1, result2, result3]

# ❌ Bad: Three containers for three scripts
# (Don't split into 3 separate scripts if sandbox mode)
```

---

## Security Guidelines

### When to Use Sandbox

**Always sandbox:**
- ✅ AI-generated code
- ✅ User-submitted scripts
- ✅ Production deployments
- ✅ Multi-tenant environments

**Consider sandboxing:**
- ⚠️ Scripts handling sensitive data
- ⚠️ Scripts from untrusted sources
- ⚠️ Automated workflows

**Direct mode OK:**
- ✅ Development iteration
- ✅ Your own trusted code
- ✅ Local testing

### Security Checklist

Before running untrusted code:

- [ ] Sandbox mode enabled (`--sandbox`)
- [ ] Resource limits configured (memory, timeout)
- [ ] Network isolation verified (`network_mode: "none"`)
- [ ] Reviewed script for obvious malicious code
- [ ] Logs monitored for suspicious activity

---

## Integration with Claude Code

### Pattern 1: Standalone Scripts

**Use mcp-code-execution for complex workflows:**

```
Claude Code (conversation)
    ↓
User: "Do deep research on X"
    ↓
Agent writes: workspace/research_x.py
    ↓
Agent runs: uv run python -m runtime.harness workspace/research_x.py
    ↓
Results returned to conversation
```

### Pattern 2: Filesystem Discovery

**Agent explores tools before writing script:**

```
Agent: ls ./servers/
       → Sees available servers

Agent: ls ./servers/jina/
       → Sees available tools

Agent: cat ./servers/jina/search_web.py
       → Learns tool signature

Agent: Writes script with correct imports
Agent: Executes script
```

**Token savings:** Load only needed definitions (~2k vs ~27k)

---

## Maintenance

### Regenerate Wrappers

When servers change or new servers added:

```bash
# Update mcp_config.json
# Then regenerate
uv run mcp-generate
```

### Update Custom Image

When runtime changes:

```bash
# Rebuild image
podman build -t mcp-execution:latest .

# Test
uv run python -m runtime.harness examples/example_sandbox_usage.py --sandbox
```

### Run Tests

```bash
# All tests
uv run pytest tests/ -v

# Specific category
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v

# With coverage
uv run pytest --cov=src/runtime tests/
```

---

## Next Steps

### For Development

1. Write scripts in `workspace/`
2. Use direct mode for speed
3. Import from `servers.{name}`
4. Iterate quickly

### For Production

1. Enable sandbox in config
2. Set appropriate resource limits
3. Test security isolation
4. Monitor execution logs
5. Deploy with confidence

### For Learning

1. Explore `./servers/` structure
2. Read example scripts in `examples/`
3. Review `docs/pydantic-usage.md`
4. Check `docs/type-safety.md`
5. Read `SECURITY.md`

---

**Status:** Ready for production use
**Support:** See documentation in /docs/ and SECURITY.md
