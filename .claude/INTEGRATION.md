# Claude Code Skills Integration Guide

**Version:** 1.0
**Date:** 2025-11-21
**Project:** mcp-code-execution-enhanced

---

## Overview

This project is fully integrated with Claude Code's native Scripts pattern, providing:

- **2 generic Skills** in proper Claude Code format
- **Auto-discovery** by Claude Code
- **CLI-based execution** for parameter flexibility
- **Template examples** for creating custom Skills

---

## Skills Directory Structure

```
.claude/scripts/
├── README.md                    # Integration documentation
├── simple-fetch/
│   ├── SKILL.md                # Basic single-tool pattern
│   └── workflow.py             # Fetch URL workflow
└── multi-tool-pipeline/
    ├── SKILL.md                # Advanced multi-tool pattern
    └── workflow.py             # Git analysis workflow
```

## SKILL.md Format

Each Skill follows Claude Code's official format:

```markdown
---
name: skill-name                    # Validation: lowercase-hyphens, max 64 chars
description: Brief description      # Validation: max 1024 chars, no XML
---

# Skill Title

## When to Use This Skill
Clear triggers and use cases

## What This Skill Does
Explanation of what the workflow accomplishes

## Instructions
Step-by-step instructions for Claude to execute:

```bash
cd /path/to/project
uv run python -m runtime.harness scripts/workflow.py \
    --param1 "value1" \
    --param2 value2
```

### Parameters
- --param1: Description
- --param2: Description

### Example Usage
Concrete examples with real values

## Expected Output
What results to expect

## MCP Servers Required
Configuration needed in mcp_config.json
```

## How Claude Code Discovers Skills

**Automatic scanning:**
1. Claude Code scans `.claude/scripts/` directory
2. Finds subdirectories containing SKILL.md
3. Validates YAML frontmatter
4. Makes Skills available to agents

**Validation:**
- name: lowercase, hyphens, numbers only
- description: non-empty, under 1024 chars
- No XML tags
- No reserved words

**Discovery confirmation:**
```bash
ls .claude/scripts/
# Shows: simple-fetch, multi-tool-pipeline
```

## How Agents Use Skills

**Workflow:**
1. **Discovery**: Agent sees Skills in `.claude/scripts/`
2. **Reading**: Reads SKILL.md for instructions
3. **Execution**: Follows bash commands in instructions
4. **Result**: Workflow returns structured output

**Example flow:**
```
Agent task: "Fetch content from https://example.com"
    ↓
Agent: bash: ls .claude/scripts/
    → Sees: simple-fetch
    ↓
Agent: bash: cat .claude/scripts/simple-fetch/SKILL.md
    → Reads: Instructions to execute workflow.py --url
    ↓
Agent: bash: cd /home/khitomer/Projects/mcp-code-execution-enhanced
Agent: bash: uv run python -m runtime.harness scripts/simple_fetch.py --url "https://example.com"
    ↓
Workflow executes, returns result
    ↓
Agent processes and presents to user
```

## Progressive Disclosure Model

**Claude Code's pattern:**
- SKILL.md loaded initially (via bash cat)
- Additional files loaded as referenced
- Scripts executed, output only in context
- Token efficient for complex Skills

**Our implementation:**
- SKILL.md references workflow.py
- workflow.py is CLI-based (immutable)
- Parameters passed via CLI (no file editing)
- Single execution, structured result

**Token cost:**
- Discovery: ls (10 tokens)
- Reading: cat SKILL.md (~500 tokens)
- Execution: bash command (0 tokens, output only)
- **Total: ~510 tokens** (99.6% reduction!)

## Creating Custom Skills

### Step 1: Write Python Workflow

Create in `scripts/` directory:

```python
"""
SKILL: your-workflow
DESCRIPTION: What it does
USAGE: uv run python -m runtime.harness scripts/your_workflow.py --args
"""

import argparse
import asyncio
from runtime.mcp_client import call_mcp_tool

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--your-param", required=True)
    args_to_parse = [arg for arg in sys.argv[1:] if not arg.endswith(".py")]
    return parser.parse_args(args_to_parse)

async def main():
    args = parse_args()
    result = await call_mcp_tool("server__tool", {"param": args.your_param})
    return result

asyncio.run(main())
```

### Step 2: Create Claude Code Skill

Create directory and SKILL.md:

```bash
mkdir .claude/scripts/your-skill-name/
```

**SKILL.md:**
```markdown
---
name: your-skill-name
description: Brief description under 1024 chars
---

# Your Skill Title

## When to Use This Skill
Clear use cases

## Instructions
```bash
uv run python -m runtime.harness scripts/your_workflow.py \
    --your-param "value"
```

## MCP Servers Required
List required servers
```

### Step 3: Link Workflow

```bash
cp scripts/your_workflow.py .claude/scripts/your-skill-name/workflow.py
```

### Step 4: Test

```bash
# Verify discovery
ls .claude/scripts/
# Should show: your-skill-name

# Verify format
cat .claude/scripts/your-skill-name/SKILL.md
# Should show: Valid YAML + markdown

# Test execution
uv run python -m runtime.harness scripts/your_workflow.py --your-param "test"
```

## Best Practices

### Skill Naming

**Do:**
- ✅ Use lowercase letters
- ✅ Use hyphens for word separation
- ✅ Keep under 64 characters
- ✅ Be descriptive

**Don't:**
- ❌ Use underscores (use hyphens)
- ❌ Use spaces or special characters
- ❌ Use uppercase letters
- ❌ Use reserved words

### Description Writing

**Do:**
- ✅ Be concise (under 1024 chars)
- ✅ Describe what the Skill does
- ✅ Mention key MCP servers used

**Don't:**
- ❌ Include XML tags
- ❌ Leave empty
- ❌ Write implementation details

### Instructions

**Do:**
- ✅ Provide complete bash commands
- ✅ Show all parameters
- ✅ Include concrete examples
- ✅ Explain expected output

**Don't:**
- ❌ Assume agent knows parameters
- ❌ Skip error handling guidance
- ❌ Omit MCP server requirements

## Integration Architecture

```
┌────────────────────────────────────────────────┐
│         Claude Code (Native)                    │
├────────────────────────────────────────────────┤
│  Skills Discovery:                              │
│  - Scans .claude/scripts/                        │
│  - Validates SKILL.md format                    │
│  - Makes available to agents                    │
└─────────────────┬──────────────────────────────┘
                  ↓
┌────────────────────────────────────────────────┐
│    .claude/scripts/ (Claude Code Format)        │
├────────────────────────────────────────────────┤
│  SKILL.md (YAML + markdown)                    │
│  - Discovery interface                          │
│  - Instructions for Claude                      │
│  - References workflow.py                       │
└─────────────────┬──────────────────────────────┘
                  ↓
┌────────────────────────────────────────────────┐
│    scripts/ (Python CLI Workflows)              │
├────────────────────────────────────────────────┤
│  workflow.py (Python with argparse)            │
│  - CLI argument parsing                         │
│  - MCP tool orchestration                       │
│  - Type-safe execution                          │
│  - Returns structured results                   │
└─────────────────┬──────────────────────────────┘
                  ↓
┌────────────────────────────────────────────────┐
│    MCP Servers (Multi-Transport)               │
├────────────────────────────────────────────────┤
│  - stdio (process-based)                        │
│  - SSE (server-sent events)                     │
│  - HTTP (streamable HTTP)                       │
└────────────────────────────────────────────────┘
```

## Validation Checklist

**Before committing a new Skill:**

- [ ] SKILL.md exists
- [ ] YAML frontmatter present
- [ ] name: lowercase-hyphens, <64 chars
- [ ] description: non-empty, <1024 chars
- [ ] No XML tags
- [ ] Instructions include complete bash commands
- [ ] Parameters documented
- [ ] Example usage provided
- [ ] workflow.py linked or copied
- [ ] Tested locally

## Troubleshooting

**Skill not discovered:**
- Check directory is in `.claude/scripts/`
- Verify SKILL.md exists
- Check YAML frontmatter format
- Validate name follows rules

**Skill execution fails:**
- Check bash command in SKILL.md
- Verify workflow.py path
- Test workflow.py independently
- Check MCP servers configured

**Validation errors:**
- Review name format (lowercase-hyphens)
- Check description length (<1024)
- Remove any XML tags
- Avoid reserved words

## References

- [Claude Code Skills Documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills)
- [Skills Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-scripts/best-practices)
- [Skills Quickstart](https://docs.claude.com/en/docs/agents-and-tools/agent-scripts/quickstart)
- [Anthropic: Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)

---

**Status:** Integration complete and ready for Claude Code discovery
