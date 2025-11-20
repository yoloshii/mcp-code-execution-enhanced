# MCP Transport Types

**Version:** 3.0
**Last Updated:** 2025-11-19

---

## Overview

This runtime supports all three MCP transport types, enabling connection to any MCP server regardless of its communication protocol.

**Supported Transports:**
- **stdio** - Process-based (15 servers)
- **SSE** - Server-Sent Events (1 server - jina)
- **HTTP** - Streamable HTTP (2 servers - exa, ref)

**Total Coverage:** 100% of your configured servers (18/18)

---

## stdio Transport

### Overview

**Protocol:** JSON-RPC over stdin/stdout
**Connection:** Subprocess
**Servers using:** 15 (perplexity, tavily, context7, gitmcp, puppeteer, apify, bright_data, obsidian, nia, playwright, mcp_pandoc, visioncraft, semgrep, github, pdf_reader)

### Configuration

```json
{
  "server_name": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "package-name"],
    "env": {
      "API_KEY": "your-key-here"
    }
  }
}
```

### Connection Implementation

```python
# In mcp_client.py
async def _connect_stdio(self, name: str, config: ServerConfig):
    params = StdioServerParameters(
        command=config.command,
        args=config.args,
        env=config.env
    )

    stdio_ctx = stdio_client(params)
    read, write = await stdio_ctx.__aenter__()

    session = ClientSession(read, write)
    client = await session.__aenter__()
    await client.initialize()

    self._clients[name] = client
```

### Characteristics

**Advantages:**
- ✅ Universal (works with any subprocess)
- ✅ Mature (most common MCP transport)
- ✅ Stateless (restart on connection loss)
- ✅ Environment variable support

**Disadvantages:**
- ⚠️ Subprocess overhead
- ⚠️ Process management complexity
- ⚠️ Stderr conflicts (if server logs to stderr)

### Examples

**Perplexity (stdio):**
```json
{
  "perplexity": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@perplexity-ai/mcp-server"],
    "env": {
      "PERPLEXITY_API_KEY": "pplx-...",
      "PERPLEXITY_TIMEOUT_MS": "60000"
    }
  }
}
```

**Tavily (stdio):**
```json
{
  "tavily": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "tavily-mcp@0.2.4"],
    "env": {
      "TAVILY_API_KEY": "tvly-..."
    }
  }
}
```

---

## SSE Transport

### Overview

**Protocol:** Server-Sent Events over HTTPS
**Connection:** Long-lived HTTP
**Servers using:** 1 (jina - 16 tools)

### Configuration

```json
{
  "jina": {
    "type": "sse",
    "url": "https://mcp.jina.ai/sse",
    "headers": {
      "Authorization": "Bearer jina_..."
    }
  }
}
```

### Connection Implementation

```python
# In mcp_client.py
async def _connect_sse(self, name: str, config: ServerConfig):
    sse_ctx = sse_client(
        url=config.url,
        headers=config.headers or {}
    )

    read, write = await sse_ctx.__aenter__()

    session = ClientSession(read, write)
    client = await session.__aenter__()
    await client.initialize()

    self._clients[name] = client
```

### Characteristics

**Advantages:**
- ✅ No subprocess overhead
- ✅ Server push capability
- ✅ HTTP-based (firewall friendly)
- ✅ Header authentication

**Disadvantages:**
- ⚠️ Requires HTTPS endpoint
- ⚠️ Network dependency
- ⚠️ Connection timeout handling

### SSE Workflow

```
1. Client connects to SSE endpoint
2. Server sends "endpoint" event with session URL
3. Client validates endpoint (same origin)
4. Client receives "message" events (JSON-RPC)
5. Long-lived connection maintained
6. Server pushes notifications/responses
```

### Example Usage

```python
from servers.jina import search_web, SearchWebParams

# SSE connection established on first call
result = await search_web(
    SearchWebParams(query="quantum computing", num=10)
)

# Connection reused for subsequent calls
result2 = await search_web(SearchWebParams(query="AI trends"))
```

---

## HTTP Transport

### Overview

**Protocol:** Streamable HTTP (POST requests, GET/SSE responses)
**Connection:** Session-based HTTPS
**Servers using:** 2 (exa, ref - 5 tools total)

### Configuration

**Exa (HTTP):**
```json
{
  "exa": {
    "type": "http",
    "url": "https://mcp.exa.ai/mcp",
    "headers": {
      "x-api-key": "2fa5693d-ea7d-4207-82ad-98bd8d0e5e2b"
    }
  }
}
```

**Ref (HTTP with API key in URL):**
```json
{
  "ref": {
    "type": "http",
    "url": "https://api.ref.tools/mcp?apiKey=ref-46ea8107f150e2a9439e"
  }
}
```

### Connection Implementation

```python
# In mcp_client.py
async def _connect_http(self, name: str, config: ServerConfig):
    http_ctx = streamablehttp_client(
        url=config.url,
        headers=config.headers or {}
    )

    # HTTP returns (read, write, get_session_id)
    read, write, _get_session_id = await http_ctx.__aenter__()

    session = ClientSession(read, write)
    client = await session.__aenter__()
    await client.initialize()

    self._clients[name] = client
```

### Characteristics

**Advantages:**
- ✅ No subprocess overhead
- ✅ HTTP-based (firewall friendly)
- ✅ Session resumption support
- ✅ Flexible authentication (headers, query params)

**Disadvantages:**
- ⚠️ Requires HTTPS endpoint
- ⚠️ More complex than stdio
- ⚠️ Session management overhead

### HTTP Workflow

```
1. Client initiates session (POST to /mcp)
2. Server returns session endpoint
3. Client opens GET/SSE stream for responses
4. Client POSTs requests to session endpoint
5. Server pushes responses via SSE
6. Session maintained until closed
```

### Example Usage

```python
from servers.exa import web_search_exa, WebSearchExaParams

# HTTP session established on first call
result = await web_search_exa(
    WebSearchExaParams(query="MCP examples", numResults=5)
)

# Session reused
result2 = await web_search_exa(WebSearchExaParams(query="code patterns"))
```

---

## Transport Comparison

| Feature | stdio | SSE | HTTP |
|---------|-------|-----|------|
| **Setup Complexity** | Medium | Low | Medium |
| **Network Required** | No | Yes | Yes |
| **Subprocess Overhead** | Yes | No | No |
| **Firewall Friendly** | N/A | Yes | Yes |
| **Authentication** | Env vars | Headers | Headers/URL |
| **Server Push** | No | Yes | Yes |
| **Session Management** | Per-call | Long-lived | Session-based |
| **Connection Reuse** | Process stays alive | Connection persists | Session persists |
| **Your Servers** | 15 | 1 | 2 |

---

## Adding New Servers

### stdio Server

```json
{
  "my_new_server": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "my-mcp-package"],
    "env": {
      "MY_API_KEY": "key123"
    }
  }
}
```

Then regenerate:
```bash
uv run mcp-generate
```

### SSE Server

```json
{
  "my_sse_server": {
    "type": "sse",
    "url": "https://api.example.com/mcp/sse",
    "headers": {
      "Authorization": "Bearer token123"
    }
  }
}
```

### HTTP Server

```json
{
  "my_http_server": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "x-api-key": "key123"
    }
  }
}
```

---

## Transport Selection Guide

### Choose stdio when:

- ✅ Server is Node.js/Python package
- ✅ Running locally
- ✅ No network access needed
- ✅ Environment variable configuration

**Example:** Local git server, filesystem server

### Choose SSE when:

- ✅ Server is remote HTTP service
- ✅ Server push needed
- ✅ Long-lived connections preferred
- ✅ Simpler than HTTP (no session management)

**Example:** jina AI services

### Choose HTTP when:

- ✅ Server is remote HTTP service
- ✅ Session resumption needed
- ✅ Complex request/response patterns
- ✅ RESTful API style

**Example:** exa search API, ref documentation API

---

## Troubleshooting Transports

### stdio Issues

**Problem:** "Command not found"
```bash
# Check command available
which npx
which python3

# Use full path if needed
{
  "command": "/usr/bin/npx",
  ...
}
```

**Problem:** "Process exit code 1"
```bash
# Test command manually
npx -y @perplexity-ai/mcp-server

# Check environment variables
env | grep PERPLEXITY
```

### SSE Issues

**Problem:** "Connection timeout"
```bash
# Test endpoint manually
curl -H "Authorization: Bearer ..." https://mcp.jina.ai/sse

# Check network connectivity
ping mcp.jina.ai
```

**Problem:** "Invalid endpoint URL"
- Ensure URL is HTTPS
- Verify endpoint path (/sse)
- Check Authorization header format

### HTTP Issues

**Problem:** "Session creation failed"
```bash
# Test endpoint
curl -X POST https://mcp.exa.ai/mcp \
  -H "x-api-key: ..."

# Verify API key
echo $EXA_API_KEY
```

**Problem:** "Headers not sent"
- Verify header format (dict[str, str])
- Check header names (case-sensitive)
- Ensure API key is valid

---

## Transport-Specific Features

### stdio: Environment Variables

```json
{
  "env": {
    "API_KEY": "...",
    "TIMEOUT_MS": "60000",
    "LOG_LEVEL": "info",
    "CUSTOM_VAR": "value"
  }
}
```

All env vars passed to subprocess.

### SSE: Custom Timeouts

```python
# In mcp_client.py
sse_ctx = sse_client(
    url=config.url,
    headers=config.headers,
    timeout=5.0,           # HTTP timeout
    sse_read_timeout=300   # SSE read timeout (5 minutes)
)
```

### HTTP: Session Management

```python
# HTTP client returns session ID callback
read, write, get_session_id = await http_ctx.__aenter__()

# Can retrieve current session
current_session = get_session_id()
```

---

## Best Practices

### 1. Use Appropriate Transport

```python
# ✅ stdio for local services
from servers.obsidian import ...  # Local Obsidian vault

# ✅ SSE for remote services with push
from servers.jina import ...      # Remote AI services

# ✅ HTTP for remote RESTful services
from servers.exa import ...       # Remote search API
```

### 2. Handle Connection Failures

```python
from runtime.exceptions import ServerConnectionError

try:
    result = await search_web(params)
except ServerConnectionError as e:
    logger.error(f"Connection failed: {e}")
    # Fallback to alternative server
```

### 3. Configure Timeouts Appropriately

```json
{
  "perplexity": {
    "env": {
      "PERPLEXITY_TIMEOUT_MS": "60000"  // 60s for slow operations
    }
  }
}
```

---

**Status:** All transports validated and working
**Your Configuration:** 15 stdio, 1 SSE, 2 HTTP = 18 servers total
