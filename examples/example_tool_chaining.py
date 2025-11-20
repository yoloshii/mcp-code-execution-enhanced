"""
Example: Tool Chaining with LLM Data Reshaping

Demonstrates the pattern where:
1. Script calls tool A and returns raw output
2. LLM processes/reshapes the output
3. LLM uses reshaped data as input to tool B
4. Repeat as needed

This example shows a multi-step git workflow:
- Get recent commits via git_log
- Return raw data to LLM
- LLM identifies commits of interest
- Script uses commit hashes to get detailed diffs via git_show
- Return detailed analysis to LLM for final processing

Key insight: Not all processing happens in-script. The LLM orchestrates
the workflow and reshapes data between tool calls.
"""

import asyncio
import sys
from runtime.mcp_client import call_mcp_tool


async def step1_get_recent_commits():
    """
    Step 1: Get recent commits.

    Returns raw commit log to LLM, who will then:
    - Identify commits of interest
    - Extract commit hashes
    - Request detailed diffs for specific commits
    """
    print("📝 Step 1: Fetching recent commits...")

    commits = await call_mcp_tool(
        "git__git_log",
        {
            "repo_path": ".",
            "max_count": 10
        }
    )

    print(f"\n{'='*60}")
    print("COMMITS FETCHED - Returning to LLM for analysis")
    print(f"{'='*60}")
    print(f"\nData type: {type(commits)}")
    print(f"Data length: {len(str(commits))} chars")
    print(f"\nFirst 500 chars of output:")
    print(str(commits)[:500])
    print("...\n")

    # Return raw data - LLM will process this and extract commit hashes
    return commits


async def step2_get_commit_details(commit_hash: str):
    """
    Step 2: Get detailed diff for a specific commit.

    The LLM has processed step1 output and identified a commit hash.
    Now fetch full details including diff.

    Args:
        commit_hash: Commit hash identified by LLM from step1 output
    """
    print(f"\n📊 Step 2: Fetching detailed diff for commit {commit_hash[:8]}...")

    details = await call_mcp_tool(
        "git__git_show",
        {
            "repo_path": ".",
            "revision": commit_hash
        }
    )

    print(f"\n{'='*60}")
    print(f"COMMIT DETAILS FETCHED - Returning to LLM for analysis")
    print(f"{'='*60}")
    print(f"\nData type: {type(details)}")
    print(f"Data length: {len(str(details))} chars")
    print(f"\nFirst 500 chars of output:")
    print(str(details)[:500])
    print("...\n")

    # Return raw diff - LLM will analyze changes
    return details


async def step3_compare_branches():
    """
    Step 3: Compare current branch with master.

    After analyzing individual commits, LLM might want to see
    the overall diff between branches.
    """
    print("\n🔍 Step 3: Comparing current branch with master...")

    diff = await call_mcp_tool(
        "git__git_diff",
        {
            "repo_path": ".",
            "target": "master"
        }
    )

    print(f"\n{'='*60}")
    print("BRANCH DIFF FETCHED - Returning to LLM for final analysis")
    print(f"{'='*60}")
    print(f"\nData type: {type(diff)}")
    print(f"Data length: {len(str(diff))} chars")
    print(f"\nFirst 500 chars of output:")
    print(str(diff)[:500])
    print("...\n")

    # Return raw diff - LLM will summarize changes
    return diff


async def main():
    """
    Orchestrate the multi-step workflow.

    In practice, each step would be a separate script execution:
    1. LLM runs step1 script, sees output
    2. LLM identifies interesting commit hash from output
    3. LLM runs step2 script with that hash
    4. LLM analyzes changes
    5. LLM decides to compare branches
    6. LLM runs step3 script
    7. LLM provides final summary

    For this demo, we'll simulate all steps in sequence.
    """

    # Check which step to run (simulating separate executions)
    # Note: harness passes script path twice, so actual args start at index 2
    step = sys.argv[2] if len(sys.argv) > 2 else "all"

    if step == "1" or step == "all":
        print("\n" + "="*60, flush=True)
        print("STEP 1: Get Recent Commits", flush=True)
        print("="*60, flush=True)
        result = await step1_get_recent_commits()

        if step == "1":
            return result

        print("\n[LLM would process this output and extract commit hash...]", flush=True)
        print("[For demo, using HEAD as example commit hash]", flush=True)
        await asyncio.sleep(1)

    if step == "2" or step == "all":
        print("\n" + "="*60, flush=True)
        print("STEP 2: Get Commit Details", flush=True)
        print("="*60, flush=True)
        result = await step2_get_commit_details("HEAD")

        if step == "2":
            return result

        print("\n[LLM would analyze the changes and decide next step...]", flush=True)
        await asyncio.sleep(1)

    if step == "3" or step == "all":
        print("\n" + "="*60, flush=True)
        print("STEP 3: Compare Branches", flush=True)
        print("="*60, flush=True)
        result = await step3_compare_branches()

        return result

    return {"error": f"Unknown step: {step}"}


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║           TOOL CHAINING WITH LLM ORCHESTRATION             ║
    ╚════════════════════════════════════════════════════════════╝

    This demonstrates the pattern:
    - Script fetches data from tools
    - Returns raw output to LLM
    - LLM processes and reshapes data
    - LLM calls next tool with reshaped data

    Usage:
      uv run mcp-exec examples/example_tool_chaining.py [step]

    Where step is:
      1   - Get recent commits only
      2   - Get commit details (requires commit hash)
      3   - Compare branches
      all - Run all steps (demo mode)
    """, flush=True)

    # Use existing event loop from harness (don't create new one with asyncio.run)
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main())

    print("\n" + "="*60)
    print("FINAL OUTPUT")
    print("="*60)
    print(f"\nReturned data length: {len(str(result))} chars")
    print("\nIn a real workflow, the LLM would now:")
    print("  1. Read this output")
    print("  2. Summarize the findings")
    print("  3. Answer the user's original question")
    print("  4. Or decide to call more tools if needed")
