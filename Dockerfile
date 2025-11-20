# Multi-stage Dockerfile for mcp-code-execution-enhanced
# Optimized for Skills framework and production deployment

# =============================================================================
# Stage 1: Builder - Install dependencies and build
# =============================================================================
FROM python:3.11-slim AS builder

# Install uv for fast package management
RUN pip install --no-cache-dir uv

WORKDIR /build

# Copy dependency files first (better layer caching)
COPY pyproject.toml uv.lock* ./

# Install dependencies to system Python
RUN uv pip install --system -e .

# =============================================================================
# Stage 2: Runtime - Minimal production image
# =============================================================================
FROM python:3.11-slim AS runtime

# Metadata
LABEL maintainer="mcp-code-execution-enhanced"
LABEL version="3.0.0"
LABEL description="Enhanced MCP code execution with Skills framework"
LABEL org.opencontainers.image.source="https://github.com/yoloshii/mcp-code-execution-enhanced"

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code
WORKDIR /app
COPY src/ ./src/
COPY skills/ ./skills/
COPY examples/ ./examples/

# Set Python path
ENV PYTHONPATH=/app/src

# Create workspace directory
RUN mkdir -p /app/workspace && \
    chmod 777 /app/workspace

# Run as non-root user (matches sandbox SecurityPolicy default)
USER 65534:65534

# Default entrypoint
ENTRYPOINT ["python3", "-m", "runtime.harness"]

# Default command (can be overridden)
CMD ["--help"]

# =============================================================================
# Stage 3: Development - Includes testing and dev tools
# =============================================================================
FROM runtime AS development

USER root

# Install uv and dev dependencies
RUN pip install --no-cache-dir uv && \
    uv pip install --system pytest pytest-asyncio mypy black ruff

# Copy tests
COPY tests/ ./tests/
COPY pyproject.toml ./

USER 65534:65534

# Override entrypoint for dev work
ENTRYPOINT ["/bin/bash"]

# =============================================================================
# Stage 4: Sandbox - For use as sandbox execution image
# =============================================================================
FROM runtime AS sandbox

# This image is used when running scripts in sandbox mode
# It includes runtime + mcp dependencies pre-installed

USER root

# Install common MCP server dependencies
RUN apt-get update && \
    apt-get install -y --no-recommends \
        curl \
        git \
        nodejs \
        npm && \
    npm install -g npx && \
    rm -rf /var/lib/apt/lists/*

# Pre-install common MCP servers (optional, commented out to keep image small)
# RUN npx -y @modelcontextprotocol/server-fetch
# RUN npx -y mcp-server-git

USER 65534:65534

# Volume for mounting mcp_config.json at runtime
VOLUME ["/app/config"]

# =============================================================================
# Usage Examples:
# =============================================================================
#
# Build all stages:
#   docker build --target runtime -t mcp-execution:latest .
#   docker build --target development -t mcp-execution:dev .
#   docker build --target sandbox -t mcp-execution:sandbox .
#
# Run a skill:
#   docker run --rm mcp-execution:latest skills/simple_fetch.py --url "https://example.com"
#
# Run in sandbox mode (using this image as the sandbox):
#   docker run --rm \
#     -v $(pwd)/workspace:/app/workspace:ro,Z \
#     -v $(pwd)/mcp_config.json:/app/config/mcp_config.json:ro,Z \
#     mcp-execution:sandbox \
#     skills/simple_fetch.py --url "https://example.com"
#
# Development mode:
#   docker run --rm -it \
#     -v $(pwd):/app \
#     mcp-execution:dev
#
# Run tests:
#   docker run --rm mcp-execution:dev -c "cd /app && pytest"
#
