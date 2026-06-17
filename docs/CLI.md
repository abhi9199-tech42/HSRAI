# HSRAI CLI Reference

HSRAI provides several command-line entry points for development, testing, verification, and serving the API.

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python verify_hsrai.py` | Run the full verification suite |
| `python run_api.py` | Start the REST API server |
| `pytest` | Run the test suite |
| `ruff check .` | Lint the codebase |
| `ruff format .` | Format the codebase |
| `pip install -e ".[dev]"` | Install in editable mode with dev dependencies |

---

## `verify_hsrai.py`

The standalone verification script. Checks project structure, runs tests, and validates basic functionality.

```bash
python verify_hsrai.py
```

### What It Does

1. **Finds the project root** by looking for `hsrai/__init__.py` in the current or parent directory.
2. **Checks project structure** — verifies that `hsrai/`, `hsrai/tests/`, `hsrai/core/`, `hsrai/reasoning/`, and `MARKET_ANALYSIS.md` exist.
3. **Runs pytest** on `hsrai/tests/` with verbose output and short tracebacks.
4. **Tests basic functionality** — imports core components and runs a compression test on a sample input.

### Output

```
======================================================================
HSRAI VERIFICATION TEST
======================================================================

[1/4] Finding HSRAI...
✅ Found: /path/to/HSRAI

[2/4] Checking structure...
Found: hsrai/, hsrai/tests/, hsrai/core/, hsrai/reasoning/, MARKET_ANALYSIS.md

[3/4] Running tests...
----------------------------------------------------------------------
<pytest output>
----------------------------------------------------------------------
✅ ALL TESTS PASSED

[4/4] Testing functionality...
✅ Compressed to primitive: text_a1b2c3d4

======================================================================
SUMMARY
======================================================================
Project: HSRAI
Structure: Complete
Tests: PASS
Functionality: PASS

🎉 VERDICT: HSRAI IS WORKING
======================================================================
```

---

## `run_api.py`

Starts the HSRAI REST API server using Uvicorn.

```bash
python run_api.py
```

### Options

The script runs Uvicorn with these defaults:

| Parameter | Value |
|-----------|-------|
| `host` | `0.0.0.0` |
| `port` | `8000` |

To change these, edit `run_api.py` or run Uvicorn directly:

```bash
uvicorn hsrai.api.server:app --host 127.0.0.1 --port 9000 --reload
```

The `--reload` flag enables auto-reload during development.

---

## `pytest`

HSRAI uses pytest as its test framework. The test discovery paths are configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["hsrai/tests", "urcm/tests", "isre/tests"]
```

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run a Specific Test File

```bash
pytest hsrai/tests/test_trust.py -v
```

### Run a Specific Test Function

```bash
pytest hsrai/tests/test_trust.py::test_ecdsa_signing -v
```

### Run with Coverage

```bash
pytest --cov=hsrai --cov-report=html
```

Generates an HTML coverage report in `htmlcov/`.

### Run with Short Tracebacks

```bash
pytest --tb=short
```

### Property-Based Tests

Hypothesis-based tests are included in the standard suite. They run automatically with `pytest`. To control Hypothesis settings (e.g., reduce examples for faster iteration):

```bash
pytest --hypothesis-seed=0
```

---

## `ruff`

HSRAI uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

### Lint Check

```bash
ruff check .
```

Reports style violations, unused imports, and potential bugs.

### Auto-Fix

```bash
ruff check --fix .
```

Automatically fixes safe violations (unused imports, formatting issues).

### Format Code

```bash
ruff format .
```

Formats all Python files to match the configured style.

### Lint a Specific File

```bash
ruff check hsrai/system/controller.py
```

---

## `pip install -e ".[dev]"`

Installs the HSRAI package in editable (development) mode with all dev dependencies.

```bash
pip install -e ".[dev]"
```

This installs:

| Package | Purpose |
|---------|---------|
| `numpy>=1.21` | Numerical operations |
| `scipy>=1.9` | Scientific computing |
| `pydantic>=2.0` | Data validation |
| `cryptography>=41.0` | ECDSA signing |
| `pytest>=7.0` | Test framework |
| `hypothesis>=6.0` | Property-based testing |
| `psutil>=5.9` | System monitoring |
| `networkx>=3.0` | Graph operations |

---

## `requirements.txt`

For installing production dependencies only (without dev tools):

```bash
pip install -r requirements.txt
```

---

## Configuration

HSRAI reads configuration from JSON files via the `ConfigurationManager`. While there is no dedicated CLI config command, you can create and manage config files directly.

### Create a Configuration File

```json
{
  "environment": "production",
  "debug": false,
  "max_concurrent_requests": 50,
  "timeout_ms": 10000,
  "plugins": {}
}
```

### Load in Python

```python
from hsrai.system.config import ConfigurationManager

cm = ConfigurationManager("config.json")
cm.load()
config = cm.config  # SystemConfig instance
```

### Set via Environment Variables

Currently, HSRAI reads configuration from JSON files only. To use environment variables, set them before starting the API server:

```bash
# Windows PowerShell
$env:HSRAI_ENV="production"
$env:HSRAI_DEBUG="false"

python run_api.py
```

Then read them in your configuration file or custom startup code.

---

## Docker (Planned)

Docker support is planned for Phase 12 of the production roadmap. Once available:

```bash
docker build -t hsrai .
docker run -p 8000:8000 hsrai
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'hsrai'` | Run `pip install -e ".[dev]"` from the project root |
| `pytest: command not found` | Install dev deps: `pip install -e ".[dev]"` |
| `ruff: command not found` | Install ruff: `pip install ruff` |
| `verify_hsrai.py` fails structure check | Ensure you're running from the HSRAI project root |
| API server won't start on port 8000 | Another process is using port 8000; change the port in `run_api.py` |
| Tests fail with web3 errors | Run with exclusions: `pytest -p no:ethereum -p no:web3` |
