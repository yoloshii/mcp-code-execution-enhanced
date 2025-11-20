"""
Example: Progressive Disclosure Pattern

Demonstrates the 98.7% token reduction pattern:
1. Agent explores ./servers/ to discover available tools
2. Agent reads only needed tool definitions
3. Agent writes and executes this script
4. Script processes data locally
5. Only summary returned to agent

This example:
- Lists recent git commits
- Counts commits by author
- Returns summary statistics (NOT full commit data)
"""

import asyncio
from collections import Counter
from runtime.mcp_client import get_mcp_client_manager, call_mcp_tool


async def main():
    """Analyze git commit history and return summary."""
    # Get the MCP client manager (already initialized by the harness)
    manager = get_mcp_client_manager()

    print("🔍 Analyzing git commit history...")

    # Get recent commits (progressive disclosure: fetch data once)
    commits_result = await call_mcp_tool(
        "git__git_log",
        {
            "repo_path": ".",
            "max_count": 50,  # Limit to recent commits
        },
    )

    # Process data locally (agent doesn't see raw commits)
    print("📊 Processing commits locally...")

    # Parse commit data (structure varies by server)
    if isinstance(commits_result, str):
        # Parse text format from git server
        commit_lines = [
            line for line in commits_result.split("\n") if line.strip()
        ]
        # Count commits (git server uses "Commit:" prefix)
        total_commits = len([l for l in commit_lines if l.startswith("Commit:")])

        # Extract authors (format: 'Author: <git.Actor "Name <email>">')
        authors = []
        for line in commit_lines:
            if line.startswith("Author:"):
                author_str = line.split("Author:")[1].strip()
                # Extract name from '<git.Actor "Name <email>">' format
                if '"' in author_str:
                    author = author_str.split('"')[1].split('<')[0].strip()
                else:
                    author = author_str
                authors.append(author)
    elif isinstance(commits_result, list):
        # Parse list format
        total_commits = len(commits_result)
        authors = [
            commit.get("author", "Unknown")
            for commit in commits_result
            if isinstance(commit, dict)
        ]
    else:
        total_commits = 1
        authors = ["Unknown"]

    # Calculate statistics
    author_counts = Counter(authors)
    unique_authors = len(author_counts)
    top_author = author_counts.most_common(1)[0] if author_counts else ("None", 0)

    # Return SUMMARY only (not raw data)
    summary = {
        "total_commits_analyzed": total_commits,
        "unique_authors": unique_authors,
        "top_contributor": {
            "name": top_author[0],
            "commits": top_author[1],
        },
        "authors_list": list(author_counts.keys())[:5],  # Top 5 only
    }

    print("\n✅ Analysis complete!")
    print("\n📈 Summary:")
    print(f"  Total commits analyzed: {summary['total_commits_analyzed']}")
    print(f"  Unique authors: {summary['unique_authors']}")
    print(f"  Top contributor: {summary['top_contributor']['name']} "
          f"({summary['top_contributor']['commits']} commits)")

    return summary


# Execute the analysis
result = asyncio.run(main())
print(f"\n📤 Summary output: {result}")
