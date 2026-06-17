# HSRAI Production Roadmap

> From Research Prototype to Enterprise-Grade Reasoning Operating System

---

## Current State Assessment

| Metric | Status |
|--------|--------|
| Language | Python (100%) |
| Source Files | 91 .py files |
| Test Files | 14 (hsrai only) |
| Packages | 3 (hsrai, isre, urcm) |
| Test Coverage | hsrai partial, isre 0%, urcm 0% |
| Known Bugs | 9 critical |
| Duplicated Code | 15+ classes |
| Hardcoded Values | 20 locations |
| Missing `__init__.py` | 7 directories |
| Missing Dependencies | 3 (scipy, networkx, psutil) |

---

## Phase 1: Fix Breaking Bugs & Dependencies

**Effort: 2 days | Priority: P0**

### 1.1 Fix Missing Dependencies

- [ ] Add `scipy>=1.9.0` to `requirements.txt` (imported in `urcm/core/theory.py:12`)
- [ ] Add `networkx>=3.0` to `requirements.txt` (imported in `hsrai/graph/builder.py:3`)
- [ ] Add `psutil>=5.9.0` to `requirements.txt` (imported in `isre/utils/resources.py:2`)
- [ ] Remove unused `import networkx` from `hsrai/graph/builder.py:3`
- [ ] Remove unused `import uuid` from `hsrai/graph/builder.py:2`
- [ ] Remove unused `import uuid` from `hsrai/output/generator.py:2`
- [ ] Remove unused `import uuid` from `hsrai/knowledge/query.py:2`
- [ ] Remove unused `import uuid` from `hsrai/compression/multimodal.py:1`

### 1.2 Fix Crash-Level Bugs

- [ ] **`hsrai/tests/test_extensibility.py:29`** — `MockCompressionPlugin` returns `SemanticPrimitive` with wrong fields (`content=`, `type=`, `source_id=`). Fix to use `id=`, `concept=`, `type=SemanticType.CONCEPT`
- [ ] **`urcm/core/error_handling.py:129`** — bare `except:` → `except Exception:`
- [ ] **`urcm/core/error_handling.py:84-130`** — attractor recovery is dead code (`if attractor:` block does `pass`). Implement attractor-to-vector conversion
- [ ] **`urcm/core/error_handling.py:119-126, 143-146`** — dimension mismatch padding corrupts data. Normalize after padding
- [ ] **`hsrai/reasoning/hybrid_engine.py:150`** — `id(best_path)` uses memory address for convergence. Replace with `path.__hash__()` or content-based key
- [ ] **`isre/models/__init__.py:1-5`** — duplicate imports. Remove duplicates

### 1.3 Fix Silent Failures

- [ ] **`hsrai/core/models.py:52`** — `ResonanceState.__post_init__` does `pass` when `mu != rho/chi`. Raise `ValueError`
- [ ] **`urcm/core/data_models.py:66-67`** — same `pass` pattern. Fix identically

---

## Phase 2: Consolidate Duplicated Code

**Effort: 3 days | Priority: P0**

### 2.1 Create Shared Types Package

Create `hsrai/common/` with single source of truth:

```
hsrai/common/
    __init__.py
    types.py        # IntentType, EdgeType, SemanticType
    models.py       # SemanticPrimitive, ResonanceState, TrustCertificate
    graph.py        # IntentNode, IntentEdge, IntentGraph
    phoneme.py      # PhonemeFrequencyMapper, PhonemeSequence, FrequencyPath
```

- [ ] Create `hsrai/common/` package
- [ ] Move canonical type definitions to `hsrai/common/types.py`
- [ ] Move canonical model definitions to `hsrai/common/models.py`
- [ ] Move canonical graph models to `hsrai/common/graph.py`
- [ ] Move phoneme models to `hsrai/common/phoneme.py`
- [ ] Update `hsrai/` imports to use `hsrai.common`
- [ ] Update `isre/` imports to use `hsrai.common`
- [ ] Update `urcm/` imports to use `hsrai.common`
- [ ] Remove duplicate definitions from `isre/types.py`, `isre/models/`, `urcm/core/data_models.py`
- [ ] Verify no circular imports

### 2.2 Merge or Deprecate `isre/`

- [ ] Audit unique modules in `isre/` (physics.py, domain.py, architectural_validator.py, resources.py)
- [ ] Move unique modules to `hsrai/` subpackages
- [ ] Mark `isre/` as deprecated with `warnings.warn`
- [ ] Update `urcm/integration/isre/bridge.py` to import from `hsrai`

### 2.3 Extract `OscillatoryGating` to Single Implementation

- [ ] Keep `hsrai/reasoning/oscillatory.py` as canonical
- [ ] Update `urcm/core/oscillatory_gating.py` to import from `hsrai`
- [ ] Delete duplicate implementation

---

## Phase 3: Fix All `__init__.py` & Exports

**Effort: 1 day | Priority: P1**

### 3.1 Add Missing `__init__.py` Files

- [ ] `hsrai/knowledge/__init__.py`
- [ ] `hsrai/plugins/__init__.py`
- [ ] `hsrai/output/__init__.py`
- [ ] `hsrai/system/__init__.py`
- [ ] `isre/utils/__init__.py`
- [ ] `urcm/integration/__init__.py`
- [ ] `urcm/integration/isre/__init__.py`

### 3.2 Add `__all__` to All Public Modules

Every public `.py` file needs `__all__`:

- [ ] `hsrai/core/types.py`
- [ ] `hsrai/core/models.py`
- [ ] `hsrai/core/utils.py`
- [ ] `hsrai/compression/mapper.py`
- [ ] `hsrai/compression/multimodal.py`
- [ ] `hsrai/graph/models.py`
- [ ] `hsrai/graph/builder.py`
- [ ] `hsrai/reasoning/hybrid_engine.py`
- [ ] `hsrai/reasoning/oscillatory.py`
- [ ] `hsrai/knowledge/models.py`
- [ ] `hsrai/knowledge/query.py`
- [ ] `hsrai/trust/verifier.py`
- [ ] `hsrai/trust/reporting.py`
- [ ] `hsrai/output/models.py`
- [ ] `hsrai/output/generator.py`
- [ ] `hsrai/plugins/interfaces.py`
- [ ] `hsrai/plugins/manager.py`
- [ ] `hsrai/system/config.py`
- [ ] `hsrai/system/controller.py`
- [ ] `hsrai/system/api.py`
- [ ] All `urcm/` and `isre/` modules

---

## Phase 4: Configuration & Hardcoded Values

**Effort: 2 days | Priority: P1**

### 4.1 Replace Global `np.random.seed(42)`

Use `np.random.default_rng(42)` as instance attributes instead:

- [ ] `hsrai/reasoning/oscillatory.py:16`
- [ ] `urcm/core/oscillatory_gating.py:21`
- [ ] `urcm/core/resonance_encoder.py:59,79`
- [ ] `urcm/core/latent_space.py:28`

### 4.2 Move Hardcoded Values to Config

| Value | File | Config Key |
|-------|------|------------|
| `stability_counter >= 5` | `hybrid_engine.py:159` | `SystemConfig.convergence_threshold` |
| `emotion_intensity_limit = 0.95` | `verifier.py:26` | `TrustConfig.emotion_limit` |
| `collapse threshold 0.1` | `error_handling.py:44` | `ErrorConfig.collapse_threshold` |
| `desync threshold 0.3` | `error_handling.py:75` | `ErrorConfig.desync_threshold` |
| `future tolerance 5.0s` | `error_handling.py:138` | `ErrorConfig.future_tolerance` |
| `staleness tolerance 30.0s` | `error_handling.py:143` | `ErrorConfig.staleness_tolerance` |
| `error log cap 100` | `error_handling.py:157` | `ErrorConfig.max_log_size` |
| Selection weights `0.4,0.4,0.2` | `selection.py:34` | `ReasoningConfig.scoring_weights` |
| `knowledge_base` dicts | `engine.py:24`, `context_loader.py:40` | External JSON files |

- [ ] Add config fields to `SystemConfig`
- [ ] Update `ConfigurationManager` to load from YAML/JSON
- [ ] Update all 20 hardcoded locations

### 4.3 Type Hint Cleanup

Replace `param: Type = None` with `Optional[Type] = None`:

- [ ] `hsrai/compression/multimodal.py:17,87`
- [ ] `hsrai/reasoning/hybrid_engine.py:26`
- [ ] `hsrai/knowledge/query.py:50`
- [ ] `hsrai/output/generator.py:17`
- [ ] `hsrai/graph/builder.py:22`
- [ ] `hsrai/system/controller.py:26`

---

## Phase 5: Error Handling & Logging

**Effort: 1 day | Priority: P1**

### 5.1 Replace All `print()` with `logging`

- [ ] `hsrai/system/controller.py:105,144` — observer errors
- [ ] `hsrai/knowledge/query.py:76` — query errors
- [ ] Add `import logging` and `logger = logging.getLogger(__name__)` to each file

### 5.2 Fix Bare/Catching-All Exceptions

- [ ] `urcm/core/error_handling.py:129` — `except:` → `except Exception as e:`
- [ ] `urcm/core/validation.py` (7 locations) — add logging before `return False`
- [ ] `urcm/core/phoneme_mapper.py:430` — add logging
- [ ] `hsrai/trust/verifier.py:136` — remove redundant `Exception` in `except (InvalidSignature, Exception)`

### 5.3 Add Input Validation

- [ ] `SystemController.process_request()` — validate `input_text` not empty/None
- [ ] `URCMSystem.process_query()` — validate `text` not empty/None
- [ ] `ConfigurationManager.__init__` — validate `config_path` exists

---

## Phase 6: Refactor God Classes & Long Functions

**Effort: 3 days | Priority: P2**

### 6.1 Break Down `SystemController` (165 lines, 10 deps)

Split into:
- [ ] `PipelineOrchestrator` — compression → graph → reasoning → output
- [ ] `PluginLoader` — plugin registration and lifecycle
- [ ] `ObserverManager` — observer notification
- [ ] Keep `SystemController` as thin facade

### 6.2 Break Down `URCMSystem` (200+ lines, 8 deps)

Split into:
- [ ] `URCMPipeline` — orchestrates the sequence
- [ ] `URCMState` — manages reasoning state
- [ ] `URCMMetrics` — tracks performance metrics

### 6.3 Shorten Long Functions

- [ ] `_process_pipeline` (92 lines) → extract `_compress()`, `_build_graph()`, `_reason()`, `_generate_output()`
- [ ] `run_reasoning_loop` (106 lines) → extract `_propose_candidate()`, `_validate_candidate()`, `_check_convergence()`
- [ ] `_initialize_articulatory_features` (57 lines) → extract helper
- [ ] `process` in ISRE orchestrator (74 lines) → extract layer methods

---

## Phase 7: URCM Test Suite

**Effort: 5 days | Priority: P2**

Create `urcm/tests/` directory with 16 test files:

### 7.1 Unit Tests

- [ ] `test_data_models.py` — `PhonemeSequence`, `FrequencyPath`, `ResonanceState`, `AttractorState`, `ReasoningPath`, `MeshSignal` construction and validation
- [ ] `test_theory.py` — `URCMTheory` (rho, chi, mu math), `ResonantLearning` (Hebbian updates)
- [ ] `test_phoneme_mapper.py` — `PhonemeFrequencyMapper`, `TextToPhonemeConverter`, `PhonemeFrequencyPipeline`
- [ ] `test_resonance_encoder.py` — `ResonancePathEncoder` output shape, state transitions
- [ ] `test_oscillatory_gating.py` — `OscillatoryGating` sigmoid range, rhythm periodicity
- [ ] `test_convergence_engine.py` — `MuConvergenceEngine` delta-mu convergence, beam search
- [ ] `test_attractor_network.py` — `AttractorNetwork` Kuramoto order parameter, phase dynamics
- [ ] `test_latent_space.py` — `SemanticLatentSpace` round-trip projection
- [ ] `test_mesh.py` — `MeshNode` signal exchange, `MeshNetwork` broadcast
- [ ] `test_error_handling.py` — `ErrorRecoverySystem` collapse/drift/desync recovery
- [ ] `test_validation.py` — `DataValidation` all 7 validators
- [ ] `test_performance.py` — `OptimizedPhonemeSet` caching, benchmarks
- [ ] `test_context_loader.py` — `ContextLoader` knowledge-to-resonance conversion

### 7.2 Integration Tests

- [ ] `test_system.py` — `URCMSystem.process_query()` end-to-end
- [ ] `test_bridge.py` — `IntentResonanceBridge` ISRE→URCM integration
- [ ] `test_intent_models.py` — `IntentNode`, `GoalHierarchy` construction

### 7.3 Property-Based Tests (Hypothesis)

- [ ] μ convergence: `assert delta_mu decreases over iterations`
- [ ] Kuramoto order: `assert 0 <= r <= 1`
- [ ] Latent space: `assert round_trip_error < epsilon`
- [ ] Phoneme smoothness: `assert ‖f(pi)-f(pj)‖² satisfies constraint`
- [ ] `mu = rho / (chi + epsilon)` invariant
- [ ] `rho = 1 - H(v)/H_max` bounds
- [ ] `chi = ‖v_t - v_{t-1}‖` non-negativity

---

## Phase 8: ISRE Test Suite

**Effort: 3 days | Priority: P2**

Create `isre/tests/` directory with 12 test files:

- [ ] `test_types.py` — `IntentType`, `EdgeType`, `SemanticType` enums
- [ ] `test_primitives.py` — `SemanticPrimitive` construction
- [ ] `test_intent.py` — `IntentNode`, `IntentEdge`, `IntentGraph` (cycles, priority inversion)
- [ ] `test_reasoning.py` — `ReasoningPath`, `ReasoningDecision`
- [ ] `test_dynamics.py` — `OscillatoryGate` Hopf oscillator dynamics
- [ ] `test_generator.py` — `ReasoningPathGenerator.generate_paths()`
- [ ] `test_selection.py` — `CompetitiveSelector.select()`
- [ ] `test_text.py` — `ConceptMapper.compress()` fuzzy matching
- [ ] `test_speech.py` — `PhonemeExtractor.compress()`
- [ ] `test_translator.py` — `MultiFormatTranslator.translate()`
- [ ] `test_orchestrator.py` — `ISREPipeline.process()` end-to-end
- [ ] `test_architectural_validator.py` — Layer separation enforcement

---

## Phase 9: Fix hsrai Test Gaps

**Effort: 2 days | Priority: P2**

### 9.1 Add Missing Tests

- [ ] `test_core_utils.py` — `deterministic_id()` determinism and collision resistance
- [ ] `test_trust_reporting.py` — `ComplianceReporter` markdown generation
- [ ] `test_config_manager.py` — `ConfigurationManager.load()` file-not-found, subscribe/notify

### 9.2 Fix Superficial Tests

- [ ] `test_structure.py` — expand smoke tests to verify behavior
- [ ] `test_graph.py:25-34` — test node creation with edge cases
- [ ] `test_multimodal.py` — test deterministic ID logic

### 9.3 Fix Over-Mocked Tests

- [ ] `test_api.py` — verify observer doesn't break downstream reasoning
- [ ] `test_integration.py` — verify plugin output is used by pipeline
- [ ] `test_extensibility.py` — fix `MockCompressionPlugin` fields

---

## Phase 10: Documentation & API

**Effort: 4 days | Priority: P3**

### 10.1 Add Docstrings to All Public APIs

~20 public classes and ~30 public methods need docstrings with Args/Returns:

- [ ] `hsrai/core/types.py` — all 3 enums
- [ ] `hsrai/core/models.py` — all 3 dataclasses
- [ ] `hsrai/reasoning/hybrid_engine.py` — `ReasoningPath`, `HybridReasoningEngine`
- [ ] `hsrai/output/models.py` — `GeneratedOutput`
- [ ] `hsrai/knowledge/models.py` — `KnowledgeEntry`, `KnowledgeGap`
- [ ] `hsrai/system/config.py` — `SystemConfig`, `ConfigurationManager`
- [ ] `isre/types.py` — all 3 enums
- [ ] All URCM public classes

### 10.2 Create REST API Server

Add `hsrai/api/` with FastAPI:

- [ ] `POST /process` — run full pipeline
- [ ] `GET /health` — health check
- [ ] `POST /plugins` — register plugin
- [ ] `GET /trust/{id}` — verify certificate
- [ ] `GET /graph/{id}` — inspect reasoning graph
- [ ] WebSocket `/stream` — real-time reasoning updates

### 10.3 Create CLI

Add `hsrai/cli.py` with argparse:

```
hsrai process "your query here"
hsrai verify --cert trust_cert.json
hsrai config --set convergence_threshold=10
hsrai serve --port 8000
hsrai test --suite all
```

---

## Phase 11: Security Hardening

**Effort: 2 days | Priority: P3**

### 11.1 Key Management

- [ ] `TrustManager` — add `key_path` parameter for persistent keys
- [ ] Implement key rotation with `rotate_keys()` method
- [ ] Zero key material on shutdown

### 11.2 Path Sanitization

- [ ] `ConfigurationManager` — validate `config_path` is within allowed directories
- [ ] Add `allowed_paths` config option

### 11.3 Remove Info Leaks

- [ ] Replace all `print()` error handling with structured `logging`
- [ ] Sanitize error messages in production mode

### 11.4 Add Security Audit

- [ ] Run `bandit` security scanner
- [ ] Fix any flagged issues
- [ ] Add to CI pipeline

---

## Phase 12: CI/CD & Packaging

**Effort: 2 days | Priority: P3**

### 12.1 Add `pyproject.toml`

```toml
[project]
name = "hsrai"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = [
    "numpy>=1.21",
    "scipy>=1.9",
    "networkx>=3.0",
    "pydantic>=2.0",
    "cryptography>=41.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "hypothesis>=6.0", "psutil>=5.9", "ruff", "mypy", "bandit"]
api = ["fastapi>=0.100", "uvicorn>=0.23"]
```

- [ ] Create `pyproject.toml`
- [ ] Remove `requirements.txt` (or keep for backwards compat)
- [ ] Add package build configuration

### 12.2 GitHub Actions CI

```yaml
name: CI
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ruff && ruff check .
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install mypy && mypy hsrai/
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -e ".[dev]" && pytest --cov=hsrai --cov-report=xml
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install bandit && bandit -r hsrai/
```

- [ ] Create `.github/workflows/ci.yml`
- [ ] Add coverage reporting (codecov)

### 12.3 Add Standard Files

- [ ] `.gitignore` — Python standard
- [ ] `.editorconfig` — consistent formatting
- [ ] `LICENSE` — choose license
- [ ] `CONTRIBUTING.md` — contribution guidelines

---

## Phase 13: Performance & Monitoring

**Effort: 2 days | Priority: P3**

### 13.1 Add Metrics Collection

- [ ] Timing for each pipeline stage
- [ ] Memory usage tracking
- [ ] Convergence iteration counts
- [ ] Error recovery statistics

### 13.2 Add Caching

- [ ] `PhonemeFrequencyMapper` — cache phoneme→vector lookups
- [ ] `KnowledgeQueryEngine` — cache query results with TTL
- [ ] `deterministic_id()` — cache recent hashes

### 13.3 Async Support

- [ ] Make `URCMSystem` async-compatible (currently sync only)
- [ ] Add `async process_query()` method
- [ ] Support `asyncio.gather()` for concurrent requests

---

## Execution Timeline

| Week | Phase | Tasks | Deliverable |
|------|-------|-------|-------------|
| 1 | Phase 1 | Fix breaking bugs | All crashers fixed, deps correct |
| 1 | Phase 2 | Consolidate duplicates | Single source of truth |
| 2 | Phase 3 | `__init__.py` & exports | Clean package structure |
| 2 | Phase 4 | Configuration | No hardcoded values |
| 2 | Phase 5 | Error handling | Proper logging everywhere |
| 3 | Phase 6 | Refactor god classes | Maintainable architecture |
| 3-4 | Phase 7 | URCM tests | 16 test files, 100% coverage |
| 4-5 | Phase 8 | ISRE tests | 12 test files, 100% coverage |
| 5 | Phase 9 | Fix hsrai tests | All tests comprehensive |
| 5-6 | Phase 10 | Docs & API | CLI + REST API + docstrings |
| 6 | Phase 11 | Security | Hardened, audited |
| 6-7 | Phase 12 | CI/CD | Automated pipeline |
| 7-8 | Phase 13 | Performance | Metrics, caching, async |

**Total: 8 weeks to production**

---

## Success Criteria

- [ ] All 49 existing tests pass
- [ ] New tests bring total to 200+
- [ ] Test coverage >90% across all packages
- [ ] Zero bare `except` clauses
- [ ] Zero `print()` for error handling
- [ ] Zero hardcoded magic numbers
- [ ] All public APIs have docstrings
- [ ] CI pipeline green on main
- [ ] `pip install hsrai` works
- [ ] `hsrai process "test"` works
- [ ] REST API responds to `/process`
- [ ] Security audit passes (bandit)
- [ ] No type errors (mypy strict)
- [ ] No lint errors (ruff)
