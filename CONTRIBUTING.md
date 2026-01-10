# Contributing to Splice3D

Thank you for your interest in contributing to Splice3D! This document provides guidelines for contributing.

## Ways to Contribute

### 1. Hardware Testing
- Build the machine and report results
- Document calibration procedures
- Test different filament materials
- Report splice quality findings

### 2. Software Development
- Fix bugs in post-processor or firmware
- Add support for other slicers (Cura, PrusaSlicer)
- Improve CLI tools
- Add unit tests

### 3. Documentation
- Improve existing guides
- Create video tutorials
- Translate to other languages
- Add diagrams and illustrations

### 4. CAD/Design
- Create printable parts (STL files)
- Design frame/enclosure
- Improve cutter mechanism
- Design multi-input selector

## Getting Started

### Prerequisites
- Python 3.9+ (for post-processor)
- PlatformIO (for firmware)
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/splice3d.git
cd splice3d

# Set up Python environment
cd postprocessor
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Docstrings for all public functions
- Maximum line length: 100 characters

### C++ (Firmware)
- Use camelCase for functions and variables
- PascalCase for classes and enums
- Prefix private members with underscore
- Comment complex logic

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** for your feature: `git checkout -b feature/my-feature`
3. **Make changes** with clear, atomic commits
4. **Run tests** to ensure nothing is broken
5. **Update documentation** if needed
6. **Submit PR** with description of changes

### Commit Messages

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding tests
- `refactor`: Code refactoring
- `chore`: Maintenance

Examples:
```
feat(parser): add support for M600 color changes
fix(firmware): correct thermistor reading formula
docs(wiring): add diagram for servo connection
```

## Reporting Issues

### Bug Reports
Include:
- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- G-code file (if applicable)
- Serial output log
- Hardware configuration

### Feature Requests
Include:
- Description of the feature
- Use case / motivation
- Possible implementation approach

## Testing

### Python Tests
```bash
cd postprocessor
python -m pytest tests/ -v
```

### Firmware Testing
```bash
# Use simulator for logic testing
cd cli
python simulator.py ../samples/test_multicolor_splice_recipe.json
```

### Hardware Testing
Document results in issues with:
- Material used
- Splice parameters (temp, time, compression)
- Success rate
- Photos of splices

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Open an issue with the `question` label or start a discussion.

---

Thank you for contributing to Splice3D! 🎉
