# Configuration Guide

## MCP Server Configuration

This project uses **separate MCP configuration** from Claude Code's global settings.

---

## 🎯 Two Configuration Systems

### 1. Claude Code's Global MCP Servers

**Location:** `~/.claude.json` or project `.claude/config.json`

**Purpose:** MCP servers available to Claude Code during conversation

**Managed by:** Claude Code runtime

**Example:**
```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp/github"],
      "env": {"GITHUB_TOKEN": "..."}
    }
  }
}
```

### 2. This Project's MCP Servers

**Location:** `mcp_config.json` in project root

**Purpose:** MCP servers available to skills and scripts via this runtime

**Managed by:** mcp-execution runtime (this project)

**Example:**
```json
{
  "mcpServers": {
    "git": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "."]
    }
  }
}
```

---

## ⚠️ Potential Conflicts

### Issue: Overlapping Server Names

If both configurations have a server named "git":
- Claude Code uses its version during conversation
- This project uses its version when running scripts/scripts
- Can cause confusion about which server is being used

### Solution Options

**Option A: Separate Servers (Recommended)**

Use different MCP servers in each configuration:

```json
// Claude Code (~/.claude.json)
{
  "mcpServers": {
    "github": {...},
    "slack": {...}
  }
}

// This project (mcp_config.json)
{
  "mcpServers": {
    "git": {...},
    "fetch": {...}
  }
}
```

**Option B: Disable Claude Code Servers**

Temporarily disable or remove servers from `~/.claude.json`:

```json
// Claude Code (~/.claude.json) - empty or minimal
{
  "mcpServers": {}
}

// This project (mcp_config.json) - all servers here
{
  "mcpServers": {
    "git": {...},
    "fetch": {...},
    "your-other-servers": {...}
  }
}
```

**Option C: Different Names**

Use different names for the same server type:

```json
// Claude Code (~/.claude.json)
{
  "mcpServers": {
    "git-claude": {"command": "mcp-server-git", ...}
  }
}

// This project (mcp_config.json)
{
  "mcpServers": {
    "git": {"command": "uvx", "args": ["mcp-server-git"], ...}
  }
}
```

---

## 🔧 Managing Configurations

### Finding Claude Code's Config

```bash
# Global config
cat ~/.claude.json

# Project config (if exists)
cat .claude/config.json
```

### Disabling a Server in Claude Code

**Option 1: Comment out (JSON doesn't support comments, so remove):**
```json
{
  "mcpServers": {
    // Remove or comment out the server you want to disable
  }
}
```

**Option 2: Move to backup:**
```bash
# Backup current config
cp ~/.claude.json ~/.claude.json.backup

# Edit to remove servers
nano ~/.claude.json
```

**Option 3: Use project-specific config:**
```bash
# Claude Code can use project-specific config in .claude/
mkdir -p .claude
echo '{"mcpServers": {}}' > .claude/config.json
```

---

## 📖 Configuration Reference

### This Project's mcp_config.json Format

```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",           // or "sse" or "http"
      "command": "command",       // stdio only
      "args": ["arg1", "arg2"],   // stdio only
      "env": {"KEY": "value"},    // stdio only
      "url": "https://...",       // sse/http only
      "headers": {...},           // sse/http only
      "disabled": false           // optional
    }
  },
  "sandbox": {
    "enabled": false,
    "runtime": "auto",
    "image": "python:3.11-slim"
  }
}
```

See `mcp_config.example.json` for complete examples.

---

## 🎓 Best Practices

### When Using with Claude Code

1. **Document your configuration**
   - Keep track of which servers are where
   - Document why you separated them

2. **Test independently**
   - Test Claude Code servers with Claude Code
   - Test project servers with `uv run mcp-generate`

3. **Avoid duplication**
   - Don't configure same server in both places
   - Or use different names if you must

4. **Use project config for skills**
   - Skills need servers in `mcp_config.json`
   - Claude Code conversation uses `~/.claude.json`

---

## 🔍 Troubleshooting

### "Server not found" when running skill

**Cause:** Server not in project's `mcp_config.json`

**Solution:**
```bash
# Add server to mcp_config.json
# Then regenerate wrappers
uv run mcp-generate
```

### "Server already configured" message

**Cause:** Server exists in both Claude Code config and project config

**Solution:**
- Remove from one configuration
- Or use different server names

### Wrappers generated for wrong servers

**Cause:** `mcp-generate` reads project's `mcp_config.json` only

**Solution:**
- Ensure servers are in `mcp_config.json` (not `~/.claude.json`)
- Claude Code's servers are not used by this runtime

---

## 📝 Summary

**Key points:**
- Claude Code's config ≠ This project's config
- Skills use project's `mcp_config.json`
- Avoid overlapping server names
- Can use different servers in each
- Or disable Claude Code servers when using this project

**Configuration file locations:**
- Claude Code: `~/.claude.json` or `.claude/config.json`
- This project: `mcp_config.json` (in project root)
