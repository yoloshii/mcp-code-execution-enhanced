# Contributing to mcp-code-execution-enhanced

Thank you for considering contributing! This project welcomes contributions from the community.

## 🎯 Areas of Interest

We're particularly interested in contributions in these areas:

### 1. Skills Library
- Add new workflow templates to `skills/`
- Document CLI arguments clearly
- Follow the immutable template pattern
- Include USAGE section with examples

### 2. MCP Server Support
- Test with different MCP servers
- Report compatibility issues
- Add transport-specific examples

### 3. Documentation
- Improve existing guides
- Add tutorials and examples
- Fix typos and clarify concepts

### 4. Testing
- Expand test coverage
- Add integration tests for new features
- Test on different platforms

### 5. Performance
- Optimize token usage further
- Improve execution speed
- Reduce memory footprint

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/mcp-code-execution-enhanced.git`
3. Install dependencies: `uv sync --all-extras`
4. Create a branch: `git checkout -b feature/your-feature`
5. Make your changes
6. Run tests: `uv run pytest`
7. Run quality checks: `uv run black src/ tests/ && uv run mypy src/ && uv run ruff check src/ tests/`
8. Commit and push
9. Create a Pull Request

## 📝 Development Guidelines

### Code Style

- **Formatting**: Use `black` with 100 character line length
- **Type hints**: Required for all functions (mypy strict mode)
- **Docstrings**: Use Google-style docstrings
- **Imports**: Sorted with `ruff`

### Testing

- Write tests for all new features
- Maintain 100% test pass rate
- Add integration tests where appropriate
- Use pytest fixtures for common setup

### Documentation

- Update relevant docs when changing features
- Add docstrings to all public functions
- Include examples in documentation
- Keep README.md up to date

### Skills Guidelines

When contributing new skills:

1. **Use CLI arguments** (not in-file parameters)
2. **Include comprehensive docstring**:
   - SKILL name
   - DESCRIPTION
   - WHEN TO USE
   - CLI ARGUMENTS (with types and defaults)
   - USAGE (concrete example)
3. **Use argparse** for argument parsing
4. **Filter sys.argv**: `[arg for arg in sys.argv[1:] if not arg.endswith(".py")]`
5. **Error handling**: Print progress, handle errors gracefully
6. **Return structured data**: JSON-serializable results

### Commit Messages

Use conventional commits format:

- `feat: add new data processing skill`
- `fix: resolve SSE transport connection issue`
- `docs: update ARCHITECTURE.md with Skills system`
- `test: add integration tests for sandbox mode`
- `refactor: improve MCP client connection handling`

## 🧪 Testing Your Changes

```bash
# Run all tests
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_mcp_client.py -v

# Run with coverage
uv run pytest --cov=src/runtime --cov-report=html

# Type checking
uv run mypy src/

# Formatting check
uv run black --check src/ tests/

# Linting
uv run ruff check src/ tests/
```

## 📋 Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Run all quality checks** (black, mypy, ruff, pytest)
4. **Update CHANGELOG.md** with your changes
5. **Reference issues** if applicable
6. **Describe your changes** clearly in PR description

## 🔒 Security

If you discover a security vulnerability:

1. **Do NOT** open a public issue
2. Email the maintainers directly
3. Provide detailed information about the vulnerability
4. Wait for response before disclosing publicly

See `SECURITY.md` for security architecture details.

## 📜 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Assume good intentions
- Respect different viewpoints and experiences

### Unacceptable Behavior

- Harassment, discrimination, or hate speech
- Trolling, insulting comments, or personal attacks
- Public or private harassment
- Publishing others' private information
- Other conduct inappropriate in a professional setting

## 🎨 Style Guide

### Python Code

```python
"""Module docstring describing purpose."""

from typing import Optional
import asyncio


class ExampleClass:
    """Class docstring.

    Args:
        param: Description of parameter

    Returns:
        Description of return value
    """

    def __init__(self, param: str) -> None:
        self.param = param

    async def async_method(self, value: int) -> Optional[str]:
        """Method docstring."""
        # Implementation
        return result
```

### Skills Template

```python
"""
SKILL: Skill Name

DESCRIPTION: Clear description of what this skill does

WHEN TO USE:
- Use case 1
- Use case 2

CLI ARGUMENTS:
    --param1    Description (required)
    --param2    Description (default: value)

USAGE:
    uv run python -m runtime.harness skills/skill_name.py \
        --param1 "value" \
        --param2 123
"""

import argparse
import asyncio
import sys


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Skill description")
    parser.add_argument("--param1", required=True, help="Description")
    parser.add_argument("--param2", type=int, default=100, help="Description")

    args_to_parse = [arg for arg in sys.argv[1:] if not arg.endswith(".py")]
    return parser.parse_args(args_to_parse)


async def main():
    """Main skill workflow."""
    args = parse_args()
    # Implementation
    return result


if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 Review Criteria

Pull requests will be reviewed for:

- ✅ **Functionality**: Does it work as intended?
- ✅ **Tests**: Are there tests? Do they pass?
- ✅ **Documentation**: Is it documented?
- ✅ **Code quality**: Does it follow style guidelines?
- ✅ **Performance**: Does it maintain or improve efficiency?
- ✅ **Compatibility**: Does it work with existing features?

## 🎓 Learning Resources

- Read `AGENTS.md` for quick operational guide
- Review `docs/ARCHITECTURE.md` for system design
- Study existing skills in `skills/` directory
- Check `examples/` for usage patterns
- Review tests in `tests/` for implementation details

## 💬 Questions?

- Check documentation first (`docs/` directory)
- Search existing issues and discussions
- Ask in GitHub discussions
- Tag maintainers if urgent

---

Thank you for contributing to making MCP code execution more efficient! 🚀
