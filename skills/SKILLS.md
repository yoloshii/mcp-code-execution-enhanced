# Skills Framework Documentation

**Anthropic's Vision:** Agents build a toolbox of reusable capabilities that evolve over time.

> **Claude Code Optimized:** This framework is designed for [Claude Code](https://docs.claude.com/en/docs/claude-code) (v2.0.20+). Claude Code's filesystem discovery and CLI-based execution enable the 99.6% token reduction. Other AI agents can use the core runtime but may not achieve the same efficiency.

## Philosophy

**DON'T:** Write scripts from scratch each time
**DON'T:** Edit skill files
**DO:** Discover and execute skills with CLI arguments

**Pattern:**
```
Discover (ls) → Read (cat) → Execute with CLI args (--query, --num-urls, etc.)
```

## Agent Operational Intelligence

**For simple tasks (1 tool call):**
- Use Direct Access (call MCP tool directly)

**For complex workflows (>2 tools, logic, processing):**
1. `ls ./skills/` - Discover available skills
2. `cat ./skills/{skill}.py` - Read skill documentation and CLI arguments
3. Execute with CLI args (IMMUTABLE - do NOT edit file):
   ```bash
   uv run python -m runtime.harness skills/simple_fetch.py \
       --url "https://example.com"
   ```

**For novel workflows:**
1. Explore `./servers/` to discover tools
2. Write NEW skill following CLI template
3. Save to `./skills/` for future reuse
4. Document CLI arguments in docstring

## Efficiency Benefits

**Token savings:**
- ❌ Writing from scratch: Load schemas + write code = ~5,000 tokens
- ❌ Editing skill file: Read skill + edit + write = ~800 tokens
- ✅ CLI execution: Read skill + command = ~110 tokens
- **Reduction: 98% (CLI approach)**

**Time savings:**
- ❌ Writing from scratch: ~2 min
- ❌ Editing skill: ~30 sec
- ✅ CLI execution: ~5 sec
- **Reduction: 96% (CLI approach)**

## Skill Template (CLI-Based)

```python
"""
SKILL: {Name}

DESCRIPTION: {What it does}

WHEN TO USE: {Use cases}

CLI ARGUMENTS:
    --param1    Description (required/optional, default: value)
    --param2    Description (type: int, default: 123)

USAGE:
    cd /home/khitomer/Projects/mcp-code-execution
    uv run python -m runtime.harness skills/{skill}.py \
        --param1 "value" \
        --param2 456
"""

import argparse
import asyncio
import sys

def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="{Skill description}")
    parser.add_argument("--param1", required=True, help="Description")
    parser.add_argument("--param2", type=int, default=123, help="Description")

    # Filter out script path from sys.argv (harness adds it)
    args_to_parse = [arg for arg in sys.argv[1:] if not arg.endswith(".py")]
    return parser.parse_args(args_to_parse)

async def main():
    """Main skill workflow."""
    args = parse_args()

    print(f"Executing with param1={args.param1}, param2={args.param2}")

    # Use args.param1, args.param2, etc.
    # ...implementation...

    return result

if __name__ == "__main__":
    asyncio.run(main())
```

## Current Skills Library

| Category | Skill | CLI Arguments |
|----------|-------|---------------|
| **Basic** | simple_fetch.py | `--url` (required) |
| **Pipeline** | multi_tool_pipeline.py | `--repo-path` (default: "."), `--max-commits` (default: 10) |

## Creating New Skills

**When to create:**
- Novel workflow not covered
- Found better pattern
- Specific use case needs

**How to create:**
1. Explore `./servers/` to find needed tools
2. Write skill following CLI template above
3. Add CLI argument parsing with argparse
4. Document in docstring (DESCRIPTION, WHEN TO USE, CLI ARGUMENTS, USAGE)
5. Test thoroughly
6. Save to `./skills/`

**Best practices:**
- Use argparse for all configurable values
- Document all CLI arguments in docstring with types and defaults
- Include USAGE section with concrete example
- Filter sys.argv to remove script path: `[arg for arg in sys.argv[1:] if not arg.endswith(".py")]`
- Keep workflow logic generic/reusable
- Include error handling and progress printing
- Return structured result

## Skills vs Writing Scripts

**Skills (PREFERRED):**
- ✅ Reusable workflow templates
- ✅ IMMUTABLE (no file editing)
- ✅ CLI arguments for flexibility
- ✅ Pre-tested and documented
- ✅ 110 tokens per use
- ✅ 5 seconds execution time
- ✅ Agent just reads and executes

**Writing Scripts (ALTERNATIVE):**
- ⚠️ Custom code each time
- ⚠️ Requires schema exploration
- ⚠️ More tokens (~2,000)
- ⚠️ More time (~2 min)
- ⚠️ Agent must write from scratch
- ✅ Good for: Novel workflows, learning, prototyping

## Example Usage

```bash
# Simple fetch example
uv run python -m runtime.harness skills/simple_fetch.py \
    --url "https://example.com"

# Multi-tool pipeline example
uv run python -m runtime.harness skills/multi_tool_pipeline.py \
    --repo-path "." \
    --max-commits 5
```

## Key Principles

1. **Immutability** - Skills are templates, never edit the file
2. **CLI Parameters** - All configuration via command-line arguments
3. **Reusability** - Write once, use many times with different args
4. **Documentation** - Every skill has USAGE section with example
5. **Type Safety** - argparse provides validation and help text
6. **Efficiency** - 98% token reduction, 96% time reduction vs writing scripts

## Help Text

Every skill supports `--help`:

```bash
python skills/simple_fetch.py --help

# Output:
usage: simple_fetch.py [-h] --url URL

Simple URL fetch skill

optional arguments:
  -h, --help  show this help message and exit
  --url URL   URL to fetch (required)
```

---

**Remember:** Skills are IMMUTABLE. Pass parameters via CLI, never edit files!
