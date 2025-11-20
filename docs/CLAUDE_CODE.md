# Claude Code Integration

This project is **optimized for Claude Code** with native support for the Skills framework pattern.

---

## 🤖 What Is Claude Code?

[Claude Code](https://docs.claude.com/en/docs/claude-code) is Anthropic's official CLI tool that enables Claude to work directly with codebases through filesystem operations, command execution, and MCP tool integration.

**Key features:**
- Filesystem-based tool discovery
- Progressive disclosure pattern
- MCP server integration
- Skills framework support (as of v2.0.20)

---

## 🎯 Why Claude Code?

### Skills Framework Integration

The Skills framework in this project is designed for Claude Code's operational intelligence:

**Claude Code understands:**
1. `ls ./skills/` → Discover available workflows
2. `cat ./skills/skill.py` → Read CLI arguments from docstring
3. Execute with `--param` arguments → Immutable templates
4. Parse USAGE sections → Self-documenting

**Other agents would need:**
- Custom training on Skills pattern
- Different discovery mechanisms
- May not achieve 99.6% efficiency

### Progressive Disclosure

**Claude Code's workflow:**
```
1. Claude explores codebase with filesystem tools
2. Claude discovers ./skills/ directory
3. Claude reads skill documentation
4. Claude executes skill with CLI arguments
5. Skill orchestrates MCP tools
6. Results returned to Claude for processing
```

This achieves **99.6% token reduction** through:
- Minimal tool schema loading (only what's needed)
- Filesystem-based discovery (cheap operations)
- CLI-based execution (no code generation)
- Skills handle complexity (agent just orchestrates)

---

## 🔌 Compatibility

### Full Support (Claude Code)

**Skills Framework (99.6% reduction):**
- ✅ Automatic skill discovery via `ls`
- ✅ CLI argument parsing from docstrings
- ✅ USAGE section interpretation
- ✅ Immutable template execution
- ✅ Full operational intelligence

**Core Runtime (98.7% reduction):**
- ✅ Tool wrapper generation
- ✅ Script writing and execution
- ✅ Progressive disclosure
- ✅ Type-safe operations

### Partial Support (Other AI Agents)

**Core Runtime (98.7% reduction):**
- ✅ Can use generated tool wrappers
- ✅ Can write and execute scripts
- ✅ Progressive disclosure works
- ⚠️ May need custom prompts

**Skills Framework (limited):**
- ⚠️ May not understand filesystem discovery
- ⚠️ May not parse CLI arguments from docs
- ⚠️ May try to edit files instead of using CLI
- ⚠️ May not achieve 99.6% efficiency

---

## 📖 Using With Claude Code

### Prerequisites

1. Install Claude Code:
   ```bash
   npm install -g @anthropic-ai/claude-code
   # or
   brew install claude-code
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/mcp-code-execution-enhanced.git
   cd mcp-code-execution-enhanced
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

### Configuration

> **Important:** This project manages MCP servers through its own `mcp_config.json` file, **separate from Claude Code's global MCP configuration**.

**Two configuration systems:**

1. **Claude Code's MCP servers** (`~/.claude.json`, `.claude/config.json`)
   - Used by Claude Code directly
   - Available during conversation
   - Discovered at runtime by Claude Code

2. **This project's MCP servers** (`mcp_config.json` in project root)
   - Used by the mcp-execution runtime only
   - Available when running skills or scripts via harness
   - Isolated from Claude Code's servers

**Recommendation:** To avoid conflicts or confusion, you can:

**Option A:** Use separate servers (recommended)
- Configure different MCP servers in each
- Claude Code servers for conversation
- Project servers for skills/scripts

**Option B:** Disable Claude Code servers
- Comment out or remove servers from `~/.claude.json`
- Use only project's `mcp_config.json`
- Cleaner separation

**Example Claude Code configuration (optional):**

```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "."]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

### Using Skills with Claude Code

**Natural language prompts that work:**

```
"Fetch the content from example.com"
→ Claude discovers skills/
→ Reads simple_fetch.py
→ Executes with --url "https://example.com"

"Create a custom skill for analyzing git repositories"
→ Claude reads skills/SKILLS.md
→ Creates new skill following template
→ Saves to skills/

"Run the multi tool pipeline skill on this repo"
→ Claude reads multi_tool_pipeline.py
→ Executes with appropriate arguments
→ Returns results
```

---

## 🎓 Skills Framework with Claude Code

### How It Works

**Claude Code's operational intelligence:**

1. **Discovery Phase:**
   ```
   User: "I need to research X"
   Claude: Uses `ls ./skills/` to discover available workflows
   Claude: Finds skills matching the need
   ```

2. **Understanding Phase:**
   ```
   Claude: Uses `cat ./skills/skill.py` to read documentation
   Claude: Parses DESCRIPTION, CLI ARGUMENTS, USAGE sections
   Claude: Understands what the skill does and how to execute it
   ```

3. **Execution Phase:**
   ```
   Claude: Executes with CLI arguments
   Command: uv run python -m runtime.harness skills/skill.py --param "value"
   Skill: Orchestrates multiple MCP tools
   Results: Returned to Claude for processing
   ```

4. **Processing Phase:**
   ```
   Claude: Receives structured results
   Claude: Summarizes, analyzes, or presents to user
   User: Gets answer without seeing complexity
   ```

### Token Efficiency

**Traditional approach (without Skills):**
- Load all MCP tool schemas: ~27,300 tokens
- Agent processes everything in context
- High latency, high cost

**Script writing (98.7% reduction):**
- Discover needed tools: ~500 tokens
- Write script: ~1,500 tokens
- Total: ~2,000 tokens

**Skills framework (99.6% reduction - Claude Code):**
- Discover skills: ~50 tokens
- Read skill docs: ~60 tokens
- Execute command: ~0 tokens (just shell)
- Total: ~110 tokens

---

## 🛠️ Creating Skills for Claude Code

### Design Principles

**1. Self-Documenting**

Claude Code reads your skill's docstring:
```python
"""
SKILL: Your Skill Name

DESCRIPTION: What it does (Claude reads this)

CLI ARGUMENTS:
    --param1    Description (Claude parses this)

USAGE:
    uv run python -m runtime.harness skills/your_skill.py \
        --param1 "value"
    (Claude executes this pattern)
"""
```

**2. CLI-Based**

No file editing - Claude passes arguments:
```bash
# Claude doesn't edit the file, just executes:
uv run python -m runtime.harness skills/skill.py --query "user's query"
```

**3. Filesystem Discoverable**

Claude uses standard filesystem tools:
```bash
ls ./skills/           # Discovery
cat skills/skill.py    # Understanding
# Execution via harness
```

**4. Structured Output**

Return data Claude can process:
```python
async def main():
    # ... workflow logic
    return {
        "results": data,
        "summary": "Claude can summarize this",
        "metadata": {"source": "skill_name"}
    }
```

---

## ⚠️ Limitations with Other Agents

### Without Claude Code

If using with other AI agents:

**Core Runtime (✅ Works):**
- Tool wrapper generation
- Script writing and execution
- Progressive disclosure (98.7% reduction)

**Skills Framework (⚠️ Limited):**
- May not discover skills automatically
- May not parse CLI arguments from docstrings
- May try to edit files instead of using CLI
- May not achieve 99.6% efficiency

**Workaround:**
- Provide explicit instructions for skill discovery
- Document CLI arguments separately
- May need custom operational prompts
- Efficiency may be reduced

---

## 📚 Claude Code Resources

### Official Documentation

- [Claude Code Docs](https://docs.claude.com/en/docs/claude-code)
- [Claude Code Skills](https://docs.claude.com/en/docs/claude-code/skills)
- [MCP Integration](https://docs.claude.com/en/docs/claude-code/mcp)
- [Progressive Disclosure](https://www.anthropic.com/engineering/code-execution-with-mcp)

---

## 🎯 Recommendations

### For Claude Code Users

✅ **Recommended:** Use Skills framework for maximum efficiency (99.6%)
- Discover skills with `ls ./skills/`
- Execute with CLI arguments
- Create custom skills for your workflows

### For Other AI Agent Users

⚠️ **Alternative:** Use script writing approach (98.7%)
- Explore `./servers/` for tools
- Write custom scripts
- May not benefit from Skills framework

### For Framework Developers

🔧 **Contribution opportunity:** Adapt Skills pattern for other agents
- Document discovery patterns
- Create agent-specific guides
- Share integration approaches

---

## 💡 Future Directions

### Potential Enhancements

- **Multi-Agent Support:** Adapt Skills for other AI agents
- **Skills Marketplace:** Share skills across community
- **Visual Editor:** GUI for creating skills
- **Auto-Documentation:** Generate USAGE from code

### Community Feedback

We welcome feedback on:
- Using Skills with other agents
- Integration patterns
- Documentation improvements
- Framework enhancements

---

## 🎉 Summary

**Claude Code Integration:**
- ✅ Skills framework optimized for Claude Code
- ✅ Core runtime works with any agent
- ✅ Documentation clarifies compatibility
- ✅ Best practices for Claude Code users

**This project provides:**
- Maximum efficiency with Claude Code (99.6%)
- Good efficiency with other agents (98.7%)
- Flexibility to adapt and extend

---

**For best results:** Use with Claude Code! 🚀
