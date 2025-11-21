# MCP Code Execution Examples

This directory contains example scripts demonstrating different patterns for using MCP tools with progressive disclosure.

## ⭐ Recommended: Skills-Based Execution

**For most workflows**, use pre-written skills from `../scripts/` directory instead of writing scripts from scratch.

**Why Skills?**
- ✅ 99.6% token reduction (110 tokens vs 2,000 for script writing)
- ✅ 96% time reduction (5 sec vs 2 min)
- ✅ Immutable templates with CLI arguments
- ✅ No file editing required
- ✅ Battle-tested workflows

**Example:**
```bash
# Instead of writing a custom research script
cd /home/khitomer/Projects/mcp-code-execution
uv run python -m runtime.harness scripts/simple_fetch.py \
    --url "https://example.com"
```

**Available skills:** See `../scripts/README.md` for complete list (8 workflows).

**When to use these example scripts:**
- ⚠️ Novel workflows not covered by skills
- ⚠️ Learning how MCP tools work
- ⚠️ Prototyping before creating new skill

---

## Direct Script Writing Examples

### 1. Progressive Disclosure Pattern (`example_progressive_disclosure.py`)

**Pattern**: Script processes data locally and returns only a summary.

Demonstrates the classic token reduction pattern where:
- Script fetches data from MCP tools (git commits)
- Processes data locally (counts authors, analyzes commits)
- Returns only summary statistics (NOT full data)
- Agent receives minimal tokens (~100 bytes vs 50KB)

**Use case**: When you want to aggregate/analyze data and only show summary metrics to the LLM.

**Run it**:
```bash
uv run mcp-exec examples/example_progressive_disclosure.py
```

**What it does**:
- Fetches 50 recent git commits
- Counts commits by author
- Returns summary: total commits, unique authors, top contributor

---

### 2. Tool Chaining with LLM Orchestration (`example_tool_chaining.py`)

**Pattern**: Script returns raw data; LLM processes and orchestrates next steps.

Demonstrates the flexible pattern where:
- Script fetches data from MCP tools
- Returns raw data to LLM
- LLM processes/reshapes the data
- LLM decides what to do next (summarize, chain to another tool, etc.)

**Use case**: When the LLM needs to analyze data and decide on follow-up actions, or when data needs to be reshaped as input to other tools.

**Run it**:
```bash
# Run individual steps
uv run mcp-exec examples/example_tool_chaining.py 1   # Get recent commits
uv run mcp-exec examples/example_tool_chaining.py 2   # Get commit details for HEAD
uv run mcp-exec examples/example_tool_chaining.py 3   # Compare with master branch

# Run all steps in sequence (demo mode)
uv run mcp-exec examples/example_tool_chaining.py all
```

**What it does**:
- **Step 1**: Fetches recent commits → Returns raw log → LLM identifies interesting commits
- **Step 2**: Fetches detailed diff for specific commit → Returns raw diff → LLM analyzes changes
- **Step 3**: Compares current branch with master → Returns 22KB diff → LLM summarizes or uses as input

**Multi-step workflow**:
In practice, each step would be a separate script execution:
1. LLM runs step 1, analyzes output
2. LLM extracts commit hash from output
3. LLM runs step 2 with that hash
4. LLM analyzes the changes
5. LLM decides to compare branches
6. LLM runs step 3
7. LLM provides final summary to user

---

## Key Insights

### Processing Flexibility

**Not all processing needs to happen in-script.** Choose the right pattern:

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **In-script processing** | Need to aggregate/reduce large datasets | Count 1000 commits → return count |
| **Return raw data** | LLM needs to analyze/make decisions | Return 10 commits → LLM picks interesting ones |
| **Hybrid** | Some reduction + LLM analysis | Filter to 50 items → LLM analyzes each |

### Token Reduction Math

Both patterns achieve ~98.7% token reduction compared to traditional approaches:

**Traditional** (150K tokens):
```
Agent → MCP tool definitions in context → Call tool → Process in context
```

**Progressive Disclosure** (2K tokens):
```
Agent → Explores ./servers/ → Reads only needed tools → Writes script → Script executes
```

The difference is **what comes back**:
- `example_progressive_disclosure.py`: 100 bytes (summary only)
- `example_tool_chaining.py`: 22KB (raw data for LLM to process)

Both are efficient - the LLM still gets far less data than loading all tool definitions upfront!

---

## Writing Your Own Scripts

### Pattern 1: Local Processing (Summary Only)

```python
import asyncio
from runtime.mcp_client import call_mcp_tool

async def main():
    # Fetch data
    data = await call_mcp_tool("server__tool", params)

    # Process locally
    summary = process_data(data)

    # Return only summary
    return summary

asyncio.run(main())
```

### Pattern 2: Return Raw Data (LLM Orchestration)

```python
import asyncio
from runtime.mcp_client import call_mcp_tool

async def main():
    # Fetch data
    data = await call_mcp_tool("server__tool", params)

    # Return raw data for LLM to process
    # LLM can then:
    # - Summarize it
    # - Extract specific fields
    # - Use as input to another tool
    return data

# Use existing event loop from harness
loop = asyncio.get_event_loop()
result = loop.run_until_complete(main())
```

**Important**: Use `loop.get_event_loop()` + `run_until_complete()` instead of `asyncio.run()` to avoid event loop conflicts with the harness.

---

## Running Examples

All examples should be run via the `mcp-exec` harness:

```bash
# General format
uv run mcp-exec examples/<script_name>.py [args]

# The harness:
# 1. Initializes MCP client manager
# 2. Executes your script with MCP tools available
# 3. Cleans up connections on exit
```

**Note**: User scripts should go in `workspace/` (gitignored). The `examples/` directory is for reference implementations.

---

## See Also

- **Main README**: [`../README.md`](../README.md) - Full project documentation
- **Agent Guide**: [`../AGENTS.md`](../AGENTS.md) - Quick reference for LLMs
- **Integration Tests**: [`../tests/integration/`](../tests/integration/) - More usage examples
