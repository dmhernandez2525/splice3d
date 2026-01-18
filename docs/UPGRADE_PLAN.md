# Splice3D Python Tooling Upgrade Plan

> Modernizing the Python development stack for better performance, maintainability, and developer experience.

## Current State

| Tool | Current Version | Purpose |
|------|-----------------|---------|
| Python | >=3.9 (supports 3.9-3.12) | Runtime |
| pytest | >=7.0 | Testing |
| pytest-cov | >=4.0 | Coverage |
| black | >=23.0 | Formatting |
| flake8 | >=6.0 | Linting |
| isort | >=5.12 | Import sorting |
| pyserial | >=3.5 | Serial communication |

---

## Upgrade Path Overview

Each upgrade should be implemented as a separate PR for easier review and rollback.

```
PR 1: Python 3.12/3.13 support
PR 2: Replace flake8 + isort with ruff
PR 3: Upgrade pytest to 8.x
PR 4: Upgrade black to 24.x
PR 5: Add mypy for type checking
PR 6: Add pre-commit hooks
PR 7: Modernize pyproject.toml configuration
```

---

## PR 1: Python LTS Upgrade Path

### Current Support
- Python 3.9 (EOL: October 2025)
- Python 3.10 (EOL: October 2026)
- Python 3.11 (EOL: October 2027)
- Python 3.12 (EOL: October 2028)

### Recommended Change
Add Python 3.13 support while maintaining 3.10+ compatibility.

**Why drop 3.9?**
- 3.9 reaches EOL in 2025
- 3.10+ has significantly better type hint syntax (PEP 604 union types `X | Y`)
- Match statement support (PEP 634)
- Better error messages

### Changes Required

**pyproject.toml:**
```toml
[project]
requires-python = ">=3.10"
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]

[tool.black]
target-version = ['py310', 'py311', 'py312', 'py313']
```

**GitHub Actions (.github/workflows/ci.yml):**
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12', '3.13']
```

### Testing Checklist
- [ ] Run full test suite on Python 3.13
- [ ] Verify pyserial compatibility with 3.13
- [ ] Test CLI tools on each Python version
- [ ] Update documentation with new requirements

---

## PR 2: Replace flake8 with Ruff

### Why Ruff?

| Feature | flake8 + isort | Ruff |
|---------|----------------|------|
| Speed | Slow (pure Python) | 10-100x faster (Rust) |
| Configuration | Multiple files | Single pyproject.toml |
| Rules | Requires plugins | 800+ built-in rules |
| Formatting | Separate tool | Built-in (ruff format) |
| Auto-fix | Limited | Extensive |

### Migration Steps

1. Remove flake8 and isort from dependencies
2. Add ruff to dev dependencies
3. Migrate configuration to pyproject.toml
4. Update CI workflow

**pyproject.toml:**
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "black>=24.0",
    "ruff>=0.4.0",
    "mypy>=1.10",
]

[tool.ruff]
target-version = "py310"
line-length = 100

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
]
ignore = [
    "E501",   # line too long (handled by formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["postprocessor", "cli"]
```

### CLI Commands
```bash
# Lint
ruff check .

# Lint with auto-fix
ruff check --fix .

# Format (alternative to black)
ruff format .
```

---

## PR 3: Upgrade pytest to 8.x

### New Features in pytest 8.x
- Improved assertion introspection
- Better collection performance
- Enhanced fixture scoping
- Deprecation warnings cleanup

**pyproject.toml:**
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    # ...
]

[tool.pytest.ini_options]
testpaths = ["postprocessor/tests", "cli/tests"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
    "--strict-config",
]
filterwarnings = [
    "error",
    "ignore::DeprecationWarning",
]
```

### Migration Checklist
- [ ] Update pytest version constraint
- [ ] Update pytest-cov to 5.x
- [ ] Review and fix any deprecation warnings
- [ ] Add cli/tests directory for CLI tool tests

---

## PR 4: Upgrade black to 24.x

### New Features in black 24.x
- Stable style (2024 style by default)
- Better string handling
- Improved magic trailing comma behavior
- Preview features stabilized

**pyproject.toml:**
```toml
[tool.black]
line-length = 100
target-version = ['py310', 'py311', 'py312', 'py313']
include = '\.pyi?$'
extend-exclude = '''
/(
    \.git
    | \.venv
    | venv
    | build
    | dist
)/
'''
```

### Migration Steps
1. Update black version constraint
2. Run `black .` to reformat all files
3. Review changes (may be significant from style updates)
4. Commit formatting changes separately

---

## PR 5: Add mypy for Type Checking

### Why mypy?
- Catch type errors before runtime
- Improve code documentation
- Enable IDE features (autocomplete, refactoring)
- Gradual adoption possible

**pyproject.toml:**
```toml
[project.optional-dependencies]
dev = [
    # ...
    "mypy>=1.10",
    "types-pyserial",  # Type stubs for pyserial
]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Start permissive
check_untyped_defs = true
ignore_missing_imports = true

# Gradually enable stricter checking
[[tool.mypy.overrides]]
module = "postprocessor.*"
disallow_untyped_defs = true

[[tool.mypy.overrides]]
module = "cli.*"
disallow_untyped_defs = false  # Enable later
```

### Gradual Adoption Strategy
1. Add mypy with permissive settings
2. Fix obvious type errors
3. Add type hints to new code
4. Gradually enable stricter settings per module
5. Target full strict mode eventually

### CLI Commands
```bash
# Run type checking
mypy postprocessor/ cli/

# Generate type coverage report
mypy --html-report mypy-report postprocessor/
```

---

## PR 6: Add Pre-commit Hooks

### Benefits
- Automated code quality checks before commit
- Consistent formatting across contributors
- Catch issues early

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-pyserial
```

**pyproject.toml:**
```toml
[project.optional-dependencies]
dev = [
    # ...
    "pre-commit>=3.7",
]
```

### Setup Commands
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files (first time)
pre-commit run --all-files
```

---

## PR 7: Modernize pyproject.toml

### Final pyproject.toml Structure

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "splice3d"
version = "0.2.0"
description = "Multi-color filament pre-splicer for FDM 3D printing"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
authors = [
    {name = "Splice3D Contributors"}
]
keywords = ["3d-printing", "filament", "splicer", "multi-color", "gcode"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Manufacturing",
    "Topic :: Printing",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Typing :: Typed",
]
dependencies = [
    "pyserial>=3.5",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "black>=24.0",
    "ruff>=0.4.0",
    "mypy>=1.10",
    "types-pyserial",
    "pre-commit>=3.7",
]

[project.scripts]
splice3d = "postprocessor.splice3d_postprocessor:main"
splice3d-analyze = "cli.analyze_gcode:main"
splice3d-simulate = "cli.simulator:main"

[project.urls]
Homepage = "https://github.com/dmhernandez2525/splice3d"
Documentation = "https://github.com/dmhernandez2525/splice3d#readme"
Repository = "https://github.com/dmhernandez2525/splice3d.git"
Issues = "https://github.com/dmhernandez2525/splice3d/issues"
Changelog = "https://github.com/dmhernandez2525/splice3d/blob/main/CHANGELOG.md"

[tool.setuptools.packages.find]
include = ["postprocessor*", "cli*"]

[tool.setuptools.package-data]
"*" = ["py.typed"]

# Ruff configuration
[tool.ruff]
target-version = "py310"
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM"]
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["postprocessor", "cli"]

# Black configuration
[tool.black]
line-length = 100
target-version = ['py310', 'py311', 'py312', 'py313']
include = '\.pyi?$'

# Mypy configuration
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
check_untyped_defs = true

# Pytest configuration
[tool.pytest.ini_options]
testpaths = ["postprocessor/tests", "cli/tests"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = ["-v", "--tb=short", "--strict-markers"]

# Coverage configuration
[tool.coverage.run]
source = ["postprocessor", "cli"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

---

## Implementation Timeline

| Week | PR | Description |
|------|-----|-------------|
| 1 | PR 2 | Replace flake8 with ruff (minimal disruption) |
| 1 | PR 4 | Upgrade black to 24.x |
| 2 | PR 3 | Upgrade pytest to 8.x |
| 2 | PR 6 | Add pre-commit hooks |
| 3 | PR 5 | Add mypy (gradual adoption) |
| 4 | PR 1 | Python 3.13 support / drop 3.9 |
| 4 | PR 7 | Final pyproject.toml cleanup |

---

## CI/CD Updates

**.github/workflows/ci.yml:**
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install ruff black mypy types-pyserial
      - name: Ruff check
        run: ruff check .
      - name: Black check
        run: black --check .
      - name: Mypy check
        run: mypy postprocessor/ cli/

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12', '3.13']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: pytest --cov --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.12'
```

---

## Rollback Plan

If any upgrade causes issues:

1. Each PR is independent - revert the specific PR
2. Version constraints allow flexibility (e.g., `>=8.0` not `==8.0`)
3. Pre-commit hooks can be temporarily disabled: `SKIP=mypy git commit`
4. CI failures block merge - issues caught before production

---

## Success Criteria

- [ ] All tests pass on Python 3.10-3.13
- [ ] Lint (ruff) passes with zero warnings
- [ ] Format (black) produces no changes
- [ ] Type check (mypy) passes with configured strictness
- [ ] Pre-commit hooks work for all contributors
- [ ] CI pipeline completes in under 5 minutes
- [ ] Documentation updated with new development setup
