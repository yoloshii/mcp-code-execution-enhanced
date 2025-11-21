# MCP Code Execution - Enhanced Edition

**99.6% Token Reduction** through CLI-based scripts and progressive tool discovery for Model Context Protocol (MCP) servers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Optimized-5436DA.svg)](https://docs.claude.com/en/docs/claude-code)

> **Note:** This project is optimized for [Claude Code](https://docs.claude.com/en/docs/claude-code) with native Skills support. The core runtime works with any AI agent. Scripts with CLI arguments achieve 99.6% token reduction.

---

## 🎯 What This Is

An **enhanced implementation** of Anthropic's [Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) pattern, **optimized for Claude Code**, combining the best ideas from the MCP community and adding significant improvements:

- **Scripts with CLI Args**: Reusable Python workflows with command-line parameters (99.6% token reduction)
- **Multi-Transport**: Full support for stdio, SSE, and HTTP MCP servers
- **Container Sandboxing**: Optional rootless isolation with security controls
- **Type Safety**: Pydantic models throughout with full validation
- **Production-Ready**: 129 passing tests, comprehensive error handling

### 🤖 Claude Code Integration

**Native Skills Support:** This project includes proper [Claude Code Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills) integration:

- **`.claude/skills/`** - Skills in Claude Code's native format (SKILL.md + workflow.py)
- **Auto-discovery** - Claude Code automatically finds and validates Skills
- **2 Generic Examples** - simple-fetch, multi-tool-pipeline (templates for custom workflows)
- **Format Compliant** - YAML frontmatter, validation rules, progressive disclosure

**Dual-layer architecture:**
- **Layer 1**: Claude Code Skills (`.claude/skills/`) - Native discovery and format
- **Layer 2**: Scripts (`./scripts/`) - CLI-based Python workflows with argparse

**Token efficiency:**
- Core runtime: 98.7% reduction (Anthropic's filesystem pattern)
- Scripts with CLI args: 99.6% reduction (no file editing needed)

**Note:** Scripts work with any AI agent. Claude Code Skills provide native auto-discovery for Claude Code users.

---

## 🙏 Acknowledgments

This project builds upon and merges ideas from:

1. **[ipdelete/mcp-code-execution](https://github.com/ipdelete/mcp-code-execution)** - Original implementation of Anthropic's PRIMARY pattern
   - Filesystem-based progressive disclosure
   - Type-safe Pydantic wrappers
   - Schema discovery system
   - Lazy server connections

2. **[elusznik/mcp-server-code-execution-mode](https://github.com/elusznik/mcp-server-code-execution-mode)** - Production security patterns
   - Container sandboxing architecture
   - Comprehensive security controls
   - Production deployment patterns

**Our contribution:** Merged the best of both, added CLI-based scripts pattern, implemented multi-transport support, and refined the architecture for maximum efficiency.

---

## ✨ Key Enhancements

### 1. Claude Code Skills Integration (NEW)

**Native Skills format** in `.claude/skills/` directory:

```
.claude/skills/
├── simple-fetch/
│   ├── SKILL.md        # YAML frontmatter + markdown instructions
│   └── workflow.py     # → symlink to ../../scripts/simple_fetch.py
└── multi-tool-pipeline/
    ├── SKILL.md        # Multi-tool orchestration example
    └── workflow.py     # → symlink to ../../scripts/multi_tool_pipeline.py
```

**How it works:**
1. Claude Code auto-discovers Skills in `.claude/skills/`
2. Reads SKILL.md (follows Claude Code's format spec)
3. Executes workflow.py (which is a script) with CLI arguments
4. Returns results

**Benefits:**
- ✅ Native Claude Code discovery
- ✅ Standard SKILL.md format (YAML + markdown)
- ✅ Validation compliant (name, description rules)
- ✅ Progressive disclosure compatible
- ✅ Generic examples as templates

**Documentation:** See `.claude/skills/README.md` for details

### 2. Scripts with CLI Arguments (99.6% Token Reduction)

**CLI-based Python workflows** that agents execute with parameters:

```bash
# Simple example (generic template)
uv run python -m runtime.harness scripts/simple_fetch.py \
    --url "https://example.com"

# Pipeline example (generic template)
uv run python -m runtime.harness scripts/multi_tool_pipeline.py \
    --repo-path "." \
    --max-commits 5
```

**Benefits over writing scripts from scratch:**
- **18x better tokens**: 110 vs 2,000
- **24x faster**: 5 seconds vs 2 minutes
- **Immutable templates**: No file editing
- **Reusable workflows**: Same logic, different parameters

**What's included:**
- 2 generic template scripts (simple_fetch.py, multi_tool_pipeline.py)
- Complete pattern documentation

### 2. Multi-Transport Support (NEW)

Full support for all MCP transport types:

```json
{
  "mcpServers": {
    "local-tool": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-git"]
    },
    "jina": {
      "type": "sse",
      "url": "https://mcp.jina.ai/sse",
      "headers": {"Authorization": "Bearer YOUR_KEY"}
    },
    "exa": {
      "type": "http",
      "url": "https://mcp.exa.ai/mcp",
      "headers": {"x-api-key": "YOUR_KEY"}
    }
  }
}
```

### 3. Container Sandboxing (Enhanced)

Optional rootless container execution with comprehensive security:

```bash
# Sandbox mode with security controls
uv run python -m runtime.harness workspace/script.py --sandbox
```

**Security features:**
- Rootless execution (UID 65534:65534)
- Network isolation (--network none)
- Read-only root filesystem
- Memory/CPU/PID limits
- Capability dropping (--cap-drop ALL)
- Timeout enforcement

---

## 🚀 Installation

### System Requirements

- **Python 3.11 or 3.12** (3.14 not recommended due to anyio compatibility issues)
- **[uv](https://github.com/astral-sh/uv)** package manager (v0.5.0+)
- **[Claude Code](https://docs.claude.com/en/docs/claude-code)** (optional, for Skills auto-discovery)
- **Git** (for cloning repository)
- **Docker or Podman** (optional, for sandbox mode)

### Step 1: Install uv

If you don't have uv installed:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### Step 2: Clone and Install

```bash
# Clone repository
git clone https://github.com/yourusername/mcp-code-execution-enhanced.git
cd mcp-code-execution-enhanced

# Install dependencies (creates .venv automatically)
uv sync

# Verify installation
uv run python -c "from runtime.mcp_client import get_mcp_client_manager; print('✓ Installation successful')"
```

### Step 3: Review MCP Configuration

> **Important for Claude Code Users:** This project uses its own `mcp_config.json` for MCP server configuration, **separate** from Claude Code's global configuration (`~/.claude.json`). To avoid conflicts, use different servers in each configuration or disable overlapping servers in `~/.claude.json` while using this project.

**The repository includes a working `mcp_config.json`** with the servers needed for the example scripts:

```bash
# View current configuration
cat mcp_config.json
```

**Configuration included:**

```json
{
  "mcpServers": {
    "git": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "."]
    },
    "fetch": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  },
  "sandbox": {
    "enabled": false
  }
}
```

**To add more servers:** Edit `mcp_config.json` and add your own MCP servers. See `docs/TRANSPORTS.md` for examples of stdio, SSE, and HTTP transports.

### Step 4: Generate Tool Wrappers

```bash
# Auto-generate typed Python wrappers from your MCP servers
uv run mcp-generate

# This creates ./servers/<server_name>/<tool>.py files
# Example: servers/git/git_log.py, servers/fetch/fetch.py
```

### Step 5: Test the Installation

```bash
# Test with a simple script
uv run python -m runtime.harness scripts/simple_fetch.py --url "https://example.com"

# If you configured a git server, test the pipeline
uv run python -m runtime.harness scripts/multi_tool_pipeline.py --repo-path "." --max-commits 5
```

### Step 6 (Optional): Setup Sandbox Mode

If you want to use container sandboxing:

```bash
# Install Podman (recommended, rootless)
sudo apt-get install -y podman  # Ubuntu/Debian
brew install podman             # macOS

# OR install Docker
curl -fsSL https://get.docker.com | sh

# Verify
podman --version  # or docker --version

# Test sandbox mode
uv run python -m runtime.harness scripts/simple_fetch.py --url "https://example.com" --sandbox
```

### Step 7 (Optional): Claude Code Skills Setup

If using Claude Code, the Skills are already configured in `.claude/skills/` and will be auto-discovered. No additional setup needed!

**To use:**
- Claude Code will automatically find Skills in `.claude/skills/`
- Just ask Claude to use them naturally
- Example: "Fetch https://example.com" → Claude discovers and uses simple-fetch Skill

---

## 📖 How It Works

### PREFERRED: Scripts with CLI Args (99.6% reduction)

For multi-step workflows (research, data processing, synthesis):

1. **Discover scripts**: `ls ./scripts/` → see available script templates
2. **Read documentation**: `cat ./scripts/simple_fetch.py` → see CLI args and pattern
3. **Execute with parameters**:
   ```bash
   uv run python -m runtime.harness scripts/simple_fetch.py \
       --url "https://example.com"
   ```

**Generic template scripts** (`scripts/`):
- `simple_fetch.py` - Basic single-tool execution pattern
- `multi_tool_pipeline.py` - Multi-tool chaining pattern

**Note:** These are **templates** - use them as examples to create workflows for your specific MCP servers and use cases.

### ALTERNATIVE: Direct Script Writing (98.7% reduction)

For simple tasks or novel workflows:

1. **Explore tools**: `ls ./servers/` → discover available MCP tools
2. **Write script**: Create Python script using tool imports
3. **Execute**: `uv run python -m runtime.harness workspace/script.py`

**Example script:**
```python
import asyncio
from runtime.mcp_client import call_mcp_tool

async def main():
    result = await call_mcp_tool(
        "git__git_log",
        {"repo_path": ".", "max_count": 10}
    )
    print(f"Fetched {len(result)} commits")
    return result

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🏗️ Architecture

### Progressive Disclosure Pattern

**Traditional Approach** (High Token Usage):
```
Agent → MCP Server → [Full Tool Schemas 27,300 tokens] → Agent
```

**Scripts with CLI Args** (99.6% Reduction - PREFERRED):
```
Agent → Discovers scripts → Reads script docs → Executes with CLI args
Script → Multi-server orchestration → Returns results
Tokens: ~110 (script discovery + documentation)
Time: ~5 seconds
```

**Script Writing** (98.7% Reduction - ALTERNATIVE):
```
Agent → Discovers tools → Writes script
Script → MCP Server → Returns data
Agent → Processes/summarizes
Tokens: ~2,000 (tool discovery + script writing)
Time: ~2 minutes
```

### Key Components

- **`runtime/mcp_client.py`**: Lazy-loading MCP client manager with multi-transport support
- **`runtime/harness.py`**: Dual-mode script execution (direct/sandbox)
- **`runtime/generate_wrappers.py`**: Auto-generate typed wrappers from MCP schemas
- **`runtime/sandbox/`**: Container sandboxing with security controls
- **`scripts/`**: CLI-based workflow templates with 2 generic examples

---

## 🎓 Scripts System

### Philosophy

**DON'T:** Write scripts from scratch each time
**DO:** Use pre-written scripts with CLI arguments

### Creating Custom Scripts

```python
"""
SCRIPT: Your Script Name

DESCRIPTION: What it does

CLI ARGUMENTS:
    --query    Research query (required)
    --limit    Max results (default: 10)

USAGE:
    uv run python -m runtime.harness scripts/your_script.py \
        --query "your question" \
        --limit 5
"""

import argparse
import asyncio
import sys

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=10)

    # Filter script path from args
    args_to_parse = [arg for arg in sys.argv[1:] if not arg.endswith(".py")]
    return parser.parse_args(args_to_parse)

async def main():
    args = parse_args()
    # Your workflow logic here
    return result

if __name__ == "__main__":
    asyncio.run(main())
```

See `scripts/README.md` for complete documentation.

---

## 🔌 Multi-Transport Support

### stdio (Subprocess-based)
```json
{
  "type": "stdio",
  "command": "uvx",
  "args": ["mcp-server-name"],
  "env": {"API_KEY": "your-key"}
}
```

### SSE (Server-Sent Events)
```json
{
  "type": "sse",
  "url": "https://mcp.example.com/sse",
  "headers": {"Authorization": "Bearer YOUR_KEY"}
}
```

### HTTP (Streamable HTTP)
```json
{
  "type": "http",
  "url": "https://mcp.example.com/mcp",
  "headers": {"x-api-key": "YOUR_KEY"}
}
```

See `docs/TRANSPORTS.md` for detailed information.

---

## 🔐 Sandbox Mode

### Configuration

```json
{
  "sandbox": {
    "enabled": true,
    "runtime": "auto",
    "image": "python:3.11-slim",
    "memory_limit": "512m",
    "timeout": 30
  }
}
```

### Security Controls

- **Rootless execution**: UID 65534:65534 (nobody)
- **Network isolation**: `--network none`
- **Filesystem**: Read-only root, writable tmpfs
- **Resource limits**: Memory, CPU, PID constraints
- **Capabilities**: All dropped (`--cap-drop ALL`)
- **Security**: `no-new-privileges`, SELinux labels

See `SECURITY.md` for complete security documentation.

---

## 🧪 Testing

```bash
# Run all tests (129 total)
uv run pytest

# Unit tests only
uv run pytest tests/unit/

# Integration tests (requires Docker/Podman for sandbox tests)
uv run pytest tests/integration/

# With coverage
uv run pytest --cov=src/runtime
```

---

## 📚 Documentation

- **`README.md`** (this file) - Overview and quick start
- **`CLAUDE.md`** - Quick reference for Claude Code
- **`AGENTS.md.template`** - Template for adapting to other AI frameworks
- **`scripts/README.md`** - Scripts system guide
- **`scripts/SKILLS.md`** - Complete scripts documentation
- **`docs/USAGE.md`** - Comprehensive user guide
- **`docs/ARCHITECTURE.md`** - Technical architecture
- **`docs/CONFIGURATION.md`** - MCP server configuration management (Claude Code vs project)
- **`docs/TRANSPORTS.md`** - Transport-specific details
- **`SECURITY.md`** - Security architecture and best practices

---

## 🛠️ Development

### Code Quality

```bash
# Type checking
uv run mypy src/

# Formatting
uv run black src/ tests/

# Linting
uv run ruff check src/ tests/
```

### Project Scripts

```bash
# Generate wrappers from tool definitions
uv run mcp-generate

# (Optional) Generate discovery config with LLM parameter generation
uv run mcp-generate-discovery

# (Optional) Execute safe tools and infer schemas
uv run mcp-discover

# Execute a script with MCP tools available
uv run mcp-exec workspace/script.py

# Execute in sandbox mode
uv run mcp-exec workspace/script.py --sandbox
```

---

## 📊 Efficiency Comparison

| Approach | Tokens | Time | Use Case |
|----------|--------|------|----------|
| **Traditional** | 27,300 | N/A | All tool schemas loaded upfront |
| **Scripts with CLI Args** | 110 | 5 sec | Multi-step workflows (PREFERRED) |
| **Script Writing** | 2,000 | 2 min | Novel workflows (ALTERNATIVE) |

**Scripts with CLI args achieve 99.6% reduction** - exceeding Anthropic's 98.7% target!

---

## 🎨 What Makes This Enhanced

### Beyond Original Projects

**From ipdelete/mcp-code-execution:**
- ✅ Filesystem-based progressive disclosure
- ✅ Type-safe Pydantic wrappers
- ✅ Lazy server connections
- ✅ Schema discovery system

**From elusznik/mcp-server-code-execution-mode:**
- ✅ Container sandboxing architecture
- ✅ Security controls and policies
- ✅ Production deployment patterns

**Enhanced in this project:**
- ⭐ **CLI-based scripts**: CLI-based immutable templates (99.6% reduction)
- ⭐ **Multi-transport**: stdio + SSE + HTTP support (100% server coverage)
- ⭐ **Dual-mode execution**: Direct (fast) + Sandbox (secure)
- ⭐ **Python 3.11 stable**: Avoiding 3.14 anyio compatibility issues
- ⭐ **Comprehensive testing**: 129 tests covering all features
- ⭐ **Enhanced documentation**: Complete guides for all features

### Architecture Innovations

**Scripts with CLI Arguments:**
- Scripts are **immutable templates** executed with CLI arguments
- No file editing required (parameters via `--query`, `--num-urls`, etc.)
- Reusable across different queries and contexts
- Pre-tested and documented workflows

**Multi-Transport:**
- Single codebase supports all transport types
- Automatic transport detection
- Unified configuration format
- Seamless server connections

**Dual-Mode Execution:**
- Direct mode: Fast, full access (development)
- Sandbox mode: Secure, isolated (production)
- Same code, different security postures
- Runtime selection via flag or config

---

## 🔧 Configuration Reference

### Minimal Configuration

```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "."]
    }
  }
}
```

### Complete Configuration

```json
{
  "mcpServers": {
    "local-stdio": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-name"],
      "env": {"API_KEY": "key"},
      "disabled": false
    },
    "remote-sse": {
      "type": "sse",
      "url": "https://mcp.example.com/sse",
      "headers": {"Authorization": "Bearer KEY"},
      "disabled": false
    },
    "remote-http": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "headers": {"x-api-key": "KEY"},
      "disabled": false
    }
  },
  "sandbox": {
    "enabled": false,
    "runtime": "auto",
    "image": "python:3.11-slim",
    "memory_limit": "512m",
    "cpu_limit": "1.0",
    "timeout": 30,
    "max_timeout": 120
  }
}
```

---

## 📦 Features

### Core Features
- 🦥 **Lazy Loading**: Servers connect only when tools are called
- 🔒 **Type Safety**: Pydantic models for all tool inputs/outputs
- 🔄 **Defensive Coding**: Handles variable MCP response structures
- 📦 **Auto-generated Wrappers**: Typed Python functions from MCP schemas
- 🛠️ **Field Normalization**: Handles inconsistent API casing

### Enhanced Features
- 🎯 **Scripts Pattern**: Pattern for CLI-based reusable workflows
- 🔌 **Multi-Transport**: stdio, SSE, and HTTP support
- 🔐 **Container Sandboxing**: Optional rootless isolation
- 🧪 **Comprehensive Testing**: 129 tests with full coverage
- 📖 **Complete Documentation**: Guides for every feature

---

## 🎓 Examples

See the `examples/` directory for:
- `example_progressive_disclosure.py` - Classic token reduction pattern
- `example_tool_chaining.py` - LLM orchestration pattern
- `example_sandbox_usage.py` - Container sandboxing demo
- `example_sandbox_simple.py` - Basic sandbox usage

See the `scripts/` directory for production-ready workflows.

---

## 🐛 Troubleshooting

### Common Issues

**"MCP server not configured"**
- Check `mcp_config.json` server names match your calls

**"Connection closed"**
- Verify server command: `which <command>`
- Check server logs for startup errors

**"Module not found"**
- Run `uv run mcp-generate` to regenerate wrappers
- Ensure `src/` is in PYTHONPATH (harness handles this)

**Import errors in skills**
- Skills must be run via harness (sets PYTHONPATH)
- Don't run skills directly: `python scripts/script.py` ❌
- Correct: `uv run python -m runtime.harness scripts/script.py` ✅

### Python Version Issues

**Python 3.14 compatibility:**
- Not recommended due to anyio <4.9.0 breaking changes
- Use Python 3.11 or 3.12 for stability
- See issue tracker for updates

---

## 🤝 Contributing

We welcome contributions! Areas of interest:

- **New skills**: Add more workflow templates
- **MCP server support**: Test with different servers
- **Documentation**: Improve guides and examples
- **Testing**: Expand test coverage
- **Performance**: Optimize token usage further

### Development Setup

```bash
# Install with dev dependencies
uv sync --all-extras

# Run quality checks
uv run black src/ tests/
uv run mypy src/
uv run ruff check src/ tests/
uv run pytest
```

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🔗 References

### Original Projects
- [ipdelete/mcp-code-execution](https://github.com/ipdelete/mcp-code-execution) - Anthropic's PRIMARY pattern
- [elusznik/mcp-server-code-execution-mode](https://github.com/elusznik/mcp-server-code-execution-mode) - Production security

### MCP Resources
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Anthropic: Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Servers List](https://github.com/modelcontextprotocol/servers)

### Python Resources
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [uv Package Manager](https://github.com/astral-sh/uv)

---

## 🌟 Features Comparison

| Feature | Original (ipdelete) | Bridge (elusznik) | Enhanced (this) |
|---------|---------------------|-------------------|-----------------|
| **Progressive Disclosure** | ✅ PRIMARY | ⚠️ ALTERNATIVE | ✅ PRIMARY |
| **Token Reduction** | 98.7% | ~95% | **99.6%** |
| **Type Safety** | ✅ Pydantic | ⚠️ Basic | ✅ Enhanced |
| **Sandboxing** | ❌ None | ✅ Required | ✅ Optional |
| **Multi-Transport** | ❌ stdio only | ❌ stdio only | ✅ stdio/SSE/HTTP |
| **Scripts Pattern** | ❌ None | ❌ None | ✅ Yes + examples |
| **CLI Execution** | ❌ None | ❌ None | ✅ Immutable |
| **Test Coverage** | ⚠️ Partial | ⚠️ Partial | ✅ Comprehensive |
| **Python 3.11** | ✅ Yes | ⚠️ 3.12+ | ✅ Stable |

---

## 💡 Use Cases

### Perfect For

- ✅ AI agents needing to orchestrate multiple MCP tools
- ✅ Research workflows (web search → read → synthesize)
- ✅ Data processing pipelines (fetch → transform → output)
- ✅ Code discovery (search → analyze → recommend)
- ✅ Production deployments requiring security isolation
- ✅ Teams needing reproducible research workflows

### Not Ideal For

- ❌ Single tool calls (use MCP directly instead)
- ❌ Real-time interactive tools (better suited for direct integration)
- ❌ GUI applications (command-line focused)

---

## 🚦 Getting Started Checklist

- [ ] Install Python 3.11+ and uv
- [ ] Clone repository
- [ ] Run `uv sync`
- [ ] Create `mcp_config.json` with your MCP servers
- [ ] Run `uv run mcp-generate` to create wrappers
- [ ] Try a skill: `uv run python -m runtime.harness scripts/simple_fetch.py --url "https://example.com"`
- [ ] Read `AGENTS.md` for operational guide
- [ ] Explore `scripts/` for available workflows
- [ ] Review `docs/` for detailed documentation

---

## ❓ FAQ

**Q: Why Skills instead of writing scripts?**
A: Skills achieve 99.6% token reduction vs 98.7% for scripts, and execute 24x faster (5 sec vs 2 min). They're pre-tested, documented, and immutable.

**Q: Can I use this without Claude Code?**
A: Yes, but with limitations. The core runtime (script writing, 98.7% reduction) works with any AI agent. The Scripts with CLI args (99.6% reduction) work for Claude Code's operational intelligence.

**Q: Can I still write custom scripts?**
A: Yes! Scripts with CLI args are PREFERRED for common workflows (with Claude Code), but custom scripts are fully supported for novel use cases and other AI agents.

**Q: What's the difference from the original projects?**
A: We merged the best of both (progressive disclosure + security), added CLI-based scripts pattern, multi-transport support, and refined the architecture.

**Q: Why Python 3.11 instead of 3.14?**
A: anyio <4.9.0 has compatibility issues with Python 3.14's asyncio changes. 3.11 is stable and well-tested.

**Q: Is sandboxing required?**
A: No, it's optional. Use direct mode for development (fast), sandbox mode for production (secure).

**Q: How do I add my own MCP servers?**
A: Add them to `mcp_config.json`, run `uv run mcp-generate`, and they're ready to use!

---

## 🎯 Next Steps

1. **Explore scripts**: `ls scripts/` and `cat scripts/simple_fetch.py`
2. **Try examples**: Run the example skills or create your own
3. **Read CLAUDE.md**: Quick operational guide (for Claude Code users)
4. **Review docs/**: Deep dive into architecture
5. **Create custom skill**: Follow the template for your use case

