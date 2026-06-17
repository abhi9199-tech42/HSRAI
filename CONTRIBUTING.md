# Contributing to HSRAI

Thank you for your interest in contributing to HSRAI. This document covers the development workflow, code standards, and pull request process.

## Table of Contents

- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

---

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip (or conda/uv)
- Git

### Installation

1. Clone the repository:

```bash
git clone https://github.com/abhi9199-tech42/HSRAI.git
cd HSRAI
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

3. Install in editable mode with dev dependencies:

```bash
pip install -e ".[dev]"
```

This installs the `hsrai` package along with development tools: `pytest`, `hypothesis`, `psutil`, and `networkx`.

4. Verify the installation:

```bash
python verify_hsrai.py
```

### Project Layout

```
HSRAI/
├── hsrai/          # Main production system
├── urcm/           # Unified mu-Resonance Cognitive Mesh
├── isre/           # Research/earlier implementation
├── pyproject.toml  # Build config and dependencies
├── requirements.txt
└── verify_hsrai.py
```

---

## Running Tests

### Run All Tests

```bash
pytest
```

Test discovery paths are configured in `pyproject.toml`:

- `hsrai/tests/`
- `urcm/tests/`
- `isre/tests/`

### Run a Specific Test Module

```bash
pytest hsrai/tests/test_trust.py -v
```

### Run with Coverage

```bash
pytest --cov=hsrai --cov-report=html
```

Coverage reports are generated in `htmlcov/`.

### Run Property-Based Tests

HSRAI uses Hypothesis for property-based testing. Run them normally with pytest; Hypothesis tests are mixed into the standard test suite.

```bash
pytest -v
```

### Run the Verification Script

```bash
python verify_hsrai.py
```

This runs a structural check, the full test suite, and a quick functionality test.

---

## Code Style

### PEP 8

All Python code must follow [PEP 8](https://peps.python.org/pep-0008/). Key points:

- 4 spaces for indentation (no tabs).
- Maximum line length: 88 characters (Ruff default).
- Two blank lines before top-level definitions, one blank line between methods.
- Imports sorted: standard library, third-party, local — each group separated by a blank line.

### Type Hints

Every public function and method must include type annotations for parameters and return values:

```python
def calculate_stability(self, path: ReasoningPath) -> float:
    ...
```

Use `Optional[X]` instead of `X | None` for Python 3.10 compatibility. Import from `typing` for `Dict`, `List`, `Optional`, `Any`, etc.

### Docstrings

All public classes and functions require docstrings. Use the imperative mood for function docstrings:

```python
class TrustManager:
    """Manages cryptographic attestation and trust verification."""

    def generate_certificate(self, subject: Any, subject_id: str) -> TrustCertificate:
        """Generate a TrustCertificate for a given subject."""
        ...
```

Use multi-line docstrings for complex functions:

```python
def run_reasoning_loop(
    self,
    initial_state: ResonanceState,
    next_state_generator: Callable[[ResonanceState], List[ResonanceState]],
) -> List[ReasoningPath]:
    """
    Execute the main resonance loop.

    Args:
        initial_state: The starting resonance state (e.g. from encoded query).
        next_state_generator: Function that proposes candidate next states.

    Returns:
        List of converged ReasoningPath objects (best ones first).
    """
    ...
```

### Linting with Ruff

HSRAI uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Check for lint violations
ruff check .

# Auto-fix safe violations
ruff check --fix .

# Format code
ruff format .
```

Run `ruff check` before every commit. CI will reject PRs with lint errors.

---

## Pull Request Process

### Workflow

1. Create a feature branch from `main`:

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes, following the code style above.

3. Run the full test suite and lint check:

```bash
ruff check .
pytest
```

4. Commit with a descriptive message:

```bash
git commit -m "Add oscillatory gating convergence threshold config"
```

5. Push your branch and open a Pull Request against `main`.

### PR Requirements

- **Tests pass**: All existing tests must pass. Add new tests for new functionality.
- **Lint clean**: `ruff check .` must report zero violations.
- **Type-annotated**: All new public functions must have type hints.
- **Documented**: New public APIs must have docstrings.
- **Single responsibility**: Each PR should address one logical change. Split unrelated work into separate PRs.
- **No secrets**: Never commit API keys, passwords, or private keys. Use environment variables or the `ConfigurationManager`.

### Review Process

- A maintainer will review the PR within 5 business days.
- Address review comments by pushing additional commits to the same branch.
- Squash-merge will be used to keep the commit history clean.

---

## Issue Reporting

### Bug Reports

Open an issue with:

- **Title**: Concise description of the bug.
- **Environment**: Python version, OS, HSRAI version/commit.
- **Steps to reproduce**: Minimal code or commands that trigger the bug.
- **Expected behavior**: What should have happened.
- **Actual behavior**: What happened, including full traceback if applicable.

### Feature Requests

- **Title**: Describe the desired capability.
- **Use case**: Explain why the feature is needed.
- **Proposed API**: Show how the feature would be used (code example if possible).

### Security Issues

Do not open public issues for security vulnerabilities. Instead, email the maintainer directly or use GitHub's private vulnerability reporting.

---

## Project Structure Reference

| Module | Purpose |
|--------|---------|
| `hsrai/core/` | Types, models, deterministic ID utilities |
| `hsrai/compression/` | MultiModalProcessor, PhonemeFrequencyMapper |
| `hsrai/graph/` | IntentNode, IntentEdge, IntentGraph, IntentGraphBuilder |
| `hsrai/reasoning/` | HybridReasoningEngine, OscillatoryGating |
| `hsrai/knowledge/` | KnowledgeQueryEngine, gap detection |
| `hsrai/trust/` | TrustManager, BehavioralVerifier, ECDSA signing |
| `hsrai/output/` | Text/Code/ActionPlan output generation |
| `hsrai/plugins/` | Plugin interfaces and PluginManager |
| `hsrai/system/` | SystemController, SystemConfig, API |
| `urcm/core/` | Frequency-based reasoning, Kuramoto oscillators |
| `isre/` | Research implementation, Hopf dynamics |
