# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2025-11-20

### Added - Major Enhancements

- **Skills Framework**: CLI-based immutable workflow pattern achieving 99.6% token reduction
  - Framework documentation and template
  - 2 generic example skills (simple_fetch.py, multi_tool_pipeline.py)
  - Pattern for creating custom workflows

- **Multi-Transport Support**: Full implementation for all MCP transport types
  - stdio (subprocess-based)
  - SSE (Server-Sent Events)
  - HTTP (Streamable HTTP)
  - Automatic transport detection
  - Unified configuration format

- **Container Sandboxing**: Optional rootless isolation (merged from elusznik/mcp-server-code-execution-mode)
  - Rootless execution (UID 65534:65534)
  - Network isolation
  - Read-only filesystem
  - Resource limits (memory, CPU, PID)
  - Comprehensive security controls
  - Dual-mode execution (direct/sandbox)

- **Enhanced Documentation**:
  - Skills system guide (`skills/SKILLS.md`, `skills/README.md`)
  - Transport-specific guide (`docs/TRANSPORTS.md`)
  - Architecture documentation (`docs/ARCHITECTURE.md`)
  - Usage guide (`docs/USAGE.md`)
  - Security documentation (`SECURITY.md`)

### Changed

- **README.md**: Complete rewrite positioning Skills as PREFERRED approach
- **AGENTS.md**: Added Skills-first operational intelligence
- **Configuration**: Extended to support multi-transport and sandbox options
- **Token reduction**: Improved from 98.7% (scripts) to 99.6% (Skills)
- **Execution modes**: Added dual-mode support (direct/sandbox)

### Fixed

- Python 3.14 compatibility issues (using Python 3.11 for stability)
- SELinux volume mount permissions (added :Z flags)
- Import errors with direct tool imports vs package imports
- Test isolation issues in sandbox tests
- Argparse receiving script path from harness

### Improved

- Type safety throughout with enhanced Pydantic models
- Error handling for all transport types
- Test coverage (129 comprehensive tests)
- Documentation alignment with implementation
- CLI-based execution pattern (immutable templates)

---

## [2.0.0] - Original ipdelete/mcp-code-execution

### From ipdelete/mcp-code-execution

- Filesystem-based progressive disclosure (Anthropic's PRIMARY pattern)
- Type-safe Pydantic wrappers
- Lazy server connections
- Auto-generated tool wrappers
- Schema discovery system
- Field normalization for inconsistent APIs
- Defensive coding patterns

### From elusznik/mcp-server-code-execution-mode

- Container sandboxing architecture
- Security policy system
- Production deployment patterns
- Rootless execution model

---

## Version Comparison

| Version | Token Reduction | Approach | Key Feature |
|---------|----------------|----------|-------------|
| **v3.0.0 (Enhanced)** | 99.6% | Skills + Scripts | CLI-based Skills |
| v2.0.0 (Original) | 98.7% | Scripts only | Progressive disclosure |
| v1.0.0 (Bridge) | ~95% | Alternative pattern | Security sandboxing |

---

## Migration Guide

### From ipdelete/mcp-code-execution

No breaking changes - fully backward compatible:
- ✅ All existing scripts work as-is
- ✅ Configuration format unchanged (with optional additions)
- ✅ Tool wrapper generation identical
- ✅ Add Skills for enhanced efficiency (optional)
- ✅ Add multi-transport servers (optional)
- ✅ Enable sandboxing (optional)

### From elusznik/mcp-server-code-execution-mode

Major architecture change:
- ⚠️ Switch from ALTERNATIVE to PRIMARY pattern
- ⚠️ Use filesystem discovery instead of search_tools
- ⚠️ Configure servers in `mcp_config.json` (not as MCP server itself)
- ✅ Sandboxing architecture preserved
- ✅ Security controls maintained
- ✅ Can use Skills for better efficiency

See `docs/ARCHITECTURE.md` for detailed migration information.

---

## Roadmap

### Planned Features

- [ ] Additional skills for common workflows
- [ ] Performance benchmarking suite
- [ ] Type stub generation (.pyi files)
- [ ] Multi-stage Dockerfile optimization
- [ ] GitHub Actions CI/CD pipeline
- [ ] Plugin system for custom skills
- [ ] Web UI for skill management
- [ ] Skill marketplace

### Under Consideration

- [ ] Skill composition (chaining skills)
- [ ] Dynamic skill generation from prompts
- [ ] Skill versioning and updates
- [ ] Alternative container runtimes (nsjail, firejail)
- [ ] Windows native support
- [ ] Distributed execution

---

## Contributors

Thank you to all contributors who have helped improve this project!

### Original Authors
- **Ian Philpot** - ipdelete/mcp-code-execution
- **elusznik** - mcp-server-code-execution-mode

### Enhancement Contributors
- See GitHub contributors page

---

## Release Notes

### v3.0.0 - Enhanced Edition

**Major improvements:**
- Skills system with 99.6% token reduction
- Multi-transport support (stdio + SSE + HTTP)
- Optional container sandboxing
- Comprehensive documentation
- 129 passing tests

**Breaking changes:**
- None (fully backward compatible)

**Upgrade path:**
- Replace project directory with enhanced version
- Existing `mcp_config.json` works as-is
- Add `"type": "stdio"` to existing servers (optional, defaults to stdio)
- Optionally configure sandbox in config
- Start using Skills for better efficiency

---

For older versions, see the original projects:
- [ipdelete/mcp-code-execution](https://github.com/ipdelete/mcp-code-execution)
- [elusznik/mcp-server-code-execution-mode](https://github.com/elusznik/mcp-server-code-execution-mode)
