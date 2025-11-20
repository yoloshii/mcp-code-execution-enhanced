# Using with Other AI Frameworks

This project is **optimized for Claude Code** but the core runtime can be used with other AI frameworks.

---

## 🎯 Compatibility Overview

| Feature | Claude Code | Other AI Frameworks |
|---------|-------------|---------------------|
| **Skills Framework** | ✅ 99.6% reduction | ⚠️ Limited (manual adaptation needed) |
| **Script Writing** | ✅ 98.7% reduction | ✅ 98.7% reduction |
| **Multi-Transport** | ✅ Full support | ✅ Full support |
| **Container Sandboxing** | ✅ Full support | ✅ Full support |
| **Type Safety** | ✅ Full support | ✅ Full support |

---

## 📖 For Other AI Frameworks

### Using the Core Runtime (Recommended)

**Focus on script writing approach (98.7% reduction):**

1. **Configure MCP servers** in `mcp_config.json`
2. **Generate wrappers**: `uv run mcp-generate`
3. **Your agent writes scripts** using the generated tool imports
4. **Execute via harness**: `uv run python -m runtime.harness workspace/script.py`

**This approach works with any AI agent** that can:
- Read documentation
- Write Python code
- Execute commands

### Creating Framework-Specific Guide

1. **Copy template**: `cp AGENTS.md.template AGENTS.md`
2. **Customize** for your framework's capabilities
3. **Remove Skills references** if not supported
4. **Add framework-specific** instructions
5. **Document** what works and what doesn't

---

## ⚠️ Skills Framework Limitations

The Skills framework requires these capabilities:

**Claude Code has (99.6% reduction):**
- ✅ Filesystem discovery (`ls ./skills/`)
- ✅ CLI argument parsing from docstrings
- ✅ USAGE section interpretation
- ✅ Immutable template execution

**Your framework may need:**
- ⚠️ Explicit skill discovery instructions
- ⚠️ Manual CLI argument documentation
- ⚠️ Custom execution patterns
- ⚠️ May not achieve same efficiency

**Recommendation:** Use script writing (98.7%) unless your framework supports filesystem-based skill discovery.

---

## 📝 Example AGENTS.md for Generic Framework

```markdown
# AGENTS.md

**MCP Code Execution**: Progressive disclosure pattern (98.7% token reduction)

## Quick Start

1. Configure servers: Edit mcp_config.json
2. Generate wrappers: uv run mcp-generate
3. Write script: Create workspace/script.py
4. Execute: uv run python -m runtime.harness workspace/script.py

## Script Pattern

```python
import asyncio
from runtime.mcp_client import call_mcp_tool

async def main():
    result = await call_mcp_tool("server__tool", {"param": "value"})
    return result

asyncio.run(main())
```

## Multi-Transport

Supports stdio, SSE, and HTTP MCP servers via mcp_config.json.

## Sandboxing

Optional: Add --sandbox flag for container isolation.

## Documentation

- README.md - Overview
- docs/ - Technical guides
- examples/ - Script examples (ignore examples/skills/)
```

---

## 🛠️ Framework-Specific Adaptations

### If Your Framework Supports Filesystem Discovery

You may be able to adapt the Skills pattern:

1. Test if your framework can `ls ./skills/`
2. Test if it can parse docstrings
3. Test if it can execute with CLI arguments
4. If yes, use `CLAUDE.md` as base
5. If no, use script writing approach

### If Your Framework Uses Different Patterns

Focus on the core runtime:

**What you get:**
- Type-safe MCP tool wrappers
- Multi-transport support
- Progressive disclosure
- Container sandboxing

**What you adapt:**
- How your agent discovers tools
- How your agent writes scripts
- How your agent orchestrates workflows

---

## 💡 Recommendations by Framework Type

### Agent Frameworks with Filesystem Access

**Examples:** Aider, Cursor, other code-aware agents

**Approach:** May be able to adapt Skills pattern
- Try the filesystem discovery workflow
- Test CLI execution capabilities
- Adapt CLAUDE.md for your framework

### Agent Frameworks without Filesystem

**Examples:** API-only agents, web-based tools

**Approach:** Use script writing approach
- Provide tool schemas directly
- Agent writes scripts
- Execute via harness
- 98.7% reduction still achievable

### Custom Agent Systems

**Examples:** Your own agent implementation

**Approach:** Full flexibility
- Use any features you want
- Adapt Skills pattern if capable
- Fall back to scripts if needed
- Document your approach

---

## 📊 Expected Performance

| Framework Type | Token Reduction | Approach |
|----------------|-----------------|----------|
| **Claude Code** | 99.6% | Skills framework |
| **Filesystem-aware** | 95-99% | Adapted Skills or scripts |
| **Script-capable** | 98.7% | Script writing |
| **API-only** | 90-95% | Direct tool wrappers |

---

## 🤝 Contributing Framework Adaptations

If you successfully adapt this for another framework:

1. Create your `AGENTS.md` guide
2. Document what works and limitations
3. Share via Pull Request or Discussion
4. Help others use with your framework

**We welcome framework-specific guides!**

---

## 📖 See Also

- `CLAUDE.md` - Claude Code operational guide (reference implementation)
- `AGENTS.md.template` - Template for other frameworks
- `docs/CLAUDE_CODE.md` - Detailed Claude Code integration
- `examples/` - Script examples (universal approach)

---

**Summary:** Core runtime works everywhere (98.7%). Skills framework optimized for Claude Code (99.6%). Adapt as needed for your framework.
