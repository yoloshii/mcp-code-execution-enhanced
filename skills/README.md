# Skills Framework

**Anthropic's Vision:** "Agents can persist their own code as reusable functions. Once an agent develops working code for a task, it can save that implementation for future use."

> **Claude Code Optimized:** This Skills framework is designed for [Claude Code's](https://docs.claude.com/en/docs/claude-code) operational intelligence (v2.0.20+). While the core runtime works with any AI agent, Skills achieve 99.6% token reduction specifically with Claude Code.

---

## 🎯 What Is This?

The Skills framework provides a **pattern** for creating reusable, CLI-based workflow templates that agents can discover and execute.

**This directory contains:**
- ✅ Framework documentation (this file, SKILLS.md)
- ✅ Simple generic examples (2 skills demonstrating the pattern)
- ✅ Template for creating your own skills

**This directory does NOT contain:**
- ❌ Opinionated workflows for specific MCP servers
- ❌ Pre-configured research pipelines
- ❌ Production-ready workflows

**Create your own advanced workflows** using the template in SKILLS.md

---

## 🚀 Quick Start

### 1. Review Example Skills

**Simple fetch** (basic pattern):
```bash
uv run python -m runtime.harness skills/simple_fetch.py \
    --url "https://example.com"
```

**Multi-tool pipeline** (chaining pattern):
```bash
uv run python -m runtime.harness skills/multi_tool_pipeline.py \
    --repo-path "." \
    --max-commits 5
```

### 2. Create Your Own Skill

Copy the template from `SKILLS.md` and customize:

```python
"""
SKILL: Your Workflow Name

DESCRIPTION: What it does

CLI ARGUMENTS:
    --param1    Description (required)
    --param2    Description (default: value)

USAGE:
    uv run python -m runtime.harness skills/your_skill.py \
        --param1 "value"
"""

import argparse
import asyncio
import sys

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--param1", required=True)
    args_to_parse = [arg for arg in sys.argv[1:] if not arg.endswith(".py")]
    return parser.parse_args(args_to_parse)

async def main():
    args = parse_args()
    # Your workflow logic here
    return result

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📖 How Skills Work

### Agent Workflow

1. **Discover:** `ls ./skills/` → see available workflows
2. **Read:** `cat ./skills/your_skill.py` → understand CLI arguments
3. **Execute:** Run with parameters (don't edit to change parameters)

```bash
uv run python -m runtime.harness skills/your_skill.py \
    --param1 "value" \
    --param2 123
```

### Key Principles

- **Parameter Immutability**: Change parameters via CLI args, not by editing files
- **Logic Mutability**: Edit skills freely to fix bugs or improve logic
- **CLI Parameters**: All configuration via command-line arguments
- **Reusability**: Write once, use many times with different args
- **Documentation**: Every skill has USAGE section
- **Type Safety**: argparse provides validation

---

## 🎨 Skills vs Scripts

### Use Skills When

✅ Workflow is reusable (same logic, different data)
✅ Multiple tools need orchestration
✅ You'll use the same pattern multiple times
✅ Maximum efficiency needed (110 tokens, 5 sec)

### Write Scripts When

⚠️ One-off task
⚠️ Prototyping new patterns
⚠️ Learning how tools work
⚠️ Workflow is truly unique

---

## 📚 Framework Documentation

- **SKILLS.md** - Complete framework documentation
  - Skill template with argparse
  - Best practices and patterns
  - CLI-based approach
  - Creating custom skills

- **This README** - Quick start guide
  - Framework overview
  - Example skills
  - Usage patterns

- **../examples/skills/README.md** - Advanced examples
  - 8 complex workflow demonstrations
  - Multi-server orchestration
  - Real-world patterns

---

## 🛠️ Creating Custom Skills

### Step-by-Step

1. **Identify workflow**: What steps need automation?
2. **Choose tools**: Which MCP tools are needed?
3. **Copy template**: Use template from SKILLS.md
4. **Add CLI args**: Use argparse for all parameters
5. **Implement logic**: Write the workflow
6. **Document**: Add DESCRIPTION, CLI ARGUMENTS, USAGE
7. **Test**: Verify with different arguments
8. **Save**: Store in your skills/ directory

### Best Practices

- ✅ Use descriptive skill names
- ✅ Document all CLI arguments with types and defaults
- ✅ Include comprehensive USAGE section
- ✅ Handle errors gracefully
- ✅ Print progress for user feedback
- ✅ Return structured results
- ✅ Support `--help` (automatic with argparse)

---

## 💡 Examples Included

### skills/simple_fetch.py

**Purpose:** Demonstrate basic CLI-based skill pattern
**Requirements:** Any MCP server with fetch capability
**Pattern:** Simple single-tool execution

```bash
uv run python -m runtime.harness skills/simple_fetch.py \
    --url "https://example.com"
```

### skills/multi_tool_pipeline.py

**Purpose:** Demonstrate tool chaining and orchestration
**Requirements:** MCP server with git capabilities
**Pattern:** Multi-step workflow with data aggregation

```bash
uv run python -m runtime.harness skills/multi_tool_pipeline.py \
    --repo-path "." \
    --max-commits 5
```

---

## 🎓 Advanced Examples

See `../examples/skills/` for 8 advanced workflow examples demonstrating:
- Multi-server orchestration
- Research pipelines
- Data processing
- Complex tool chaining

**Note:** These require specific MCP servers and are provided as examples, not core features.

---

## 📊 Efficiency

**Skills Framework Benefits:**
- **99.6% token reduction** vs traditional approach (27,300 → 110 tokens)
- **96% time reduction** vs writing scripts (2 min → 5 sec)
- **CLI parameters** mean no file editing for parameter changes
- **Reusable workflows** across different queries
- **Edit-friendly** for bug fixes and logic improvements

---

## 🔑 Key Concepts

### Parameter Immutability
Change parameters via CLI arguments, not by editing files. Edit skills freely to fix bugs or improve logic.

### CLI-Based
Parameter changes via CLI arguments. Execute with `--param1 value --param2 value`.

### Discoverable
Agents find skills via filesystem (`ls ./skills/`).

### Self-Documenting
Every skill has USAGE section showing how to execute it.

### Type-Safe
argparse provides validation, defaults, and help text.

---

## 🎯 Getting Started

1. **Read SKILLS.md** - Complete framework documentation
2. **Try examples** - Run simple_fetch.py and multi_tool_pipeline.py
3. **Review advanced** - Check ../examples/skills/ for complex patterns
4. **Create your own** - Use template for your workflows
5. **Share** - Contribute useful patterns back to community

---

**Remember:** Skills are a **framework**, not a library of specific workflows. Build what you need! 🚀
