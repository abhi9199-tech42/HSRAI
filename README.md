# Hybrid Semantic Reasoning AI (HSRAI)

> A Deterministic, Auditable, Cryptographically Verifiable Reasoning Operating System for Enterprise AI

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-49%20passed-brightgreen)](VALIDATION_REPORT.md)
[![Status](https://img.shields.io/badge/status-validated-success)](VALIDATION_REPORT.md)

---

## The Problem

Current enterprise AI suffers from three critical flaws:

| Flaw | Impact | Example |
|------|--------|---------|
| **Non-Determinism** | Same input produces different outputs | AI denies a loan today, approves it tomorrow with identical data |
| **Unverifiable Reasoning** | No structural proof of decisions | "The model said so" fails regulatory compliance |
| **Infinite Loops** | Agents diverge or loop endlessly | Wasted compute, unpredictable latency |

**HSRAI solves these by replacing stochastic LLM reasoning with a deterministic, structurally auditable, cryptographically verifiable reasoning pipeline.**

---

## How It Works

### Core Architecture

```
Input (Text / Voice / Behavior / Sensor)
    │
    ▼
┌─────────────────────────────────────────────┐
│  1. SEMANTIC COMPRESSION                    │
│     MultiModalProcessor → SemanticPrimitive │
│     Content-Addressable Deterministic IDs   │
│     ID = SHA256(CanonicalJSON(Content))     │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  2. INTENT GRAPH CONSTRUCTION               │
│     IntentGraphBuilder → IntentGraph        │
│     Typed Nodes + Edges + Conflict Detection│
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  3. KNOWLEDGE INTEGRATION                   │
│     KnowledgeQueryEngine + Gap Detection    │
│     Trust-Rated Source Filtering            │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  4. HYBRID REASONING ENGINE                 │
│     Oscillatory Gating: ỹt = yt ⊙ σ(Wg·g(t)+b) │
│     μ-Stability: μ = ρ / χ                 │
│     Auto-convergence when Δμ → 0            │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  5. TRUSTED OUTPUT                          │
│     Text / Code / Action Plans              │
│     + ECDSA-signed TrustCertificate         │
└─────────────────────────────────────────────┘
```

### Key Mathematical Innovations

**Deterministic Identity**
```python
# Every concept gets a deterministic, reproducible ID
id = f"{'type'}_{sha256(canonical_json(content))[:8]}"
# Same input ALWAYS produces the same graph structure
```

**μ-Stability Convergence**
```python
μ = ρ / χ
# ρ (rho): Semantic Density = 1 - H(v)/H_max  (information purity)
# χ (chi): Transformation Cost = ||v_t - v_{t-1}||  (energy expenditure)
# System stops reasoning when Δμ approaches zero
```

**Oscillatory Gating**
```python
ỹt = yt ⊙ σ(Wg · g(t) + b)
# g(t) = [sin(phase), cos(phase)]  — biological rhythm modulation
# Gates semantic flow through attention windows
```

---

## Project Structure

```
HSRAI/
├── hsrai/                    # Main production system
│   ├── core/                 # Types, models, utils
│   ├── compression/          # MultiModalProcessor, PhonemeFrequencyMapper
│   ├── graph/                # IntentNode, IntentEdge, IntentGraph, Builder
│   ├── reasoning/            # HybridReasoningEngine, OscillatoryGating
│   ├── knowledge/            # KnowledgeQueryEngine, gap detection
│   ├── trust/                # ECDSA TrustManager, ComplianceReporter
│   ├── output/               # Text/Code/ActionPlan generator
│   ├── plugins/              # Plugin interfaces and manager
│   ├── system/               # SystemController, API, Config
│   └── tests/                # 14 test modules, 49 tests
│
├── urcm/                     # Unified mu-Resonance Cognitive Mesh
│   ├── core/                 # Frequency-based reasoning engine
│   │   ├── theory.py         # URCMTheory (rho, chi, mu math)
│   │   ├── phoneme_mapper.py # Text → Phoneme → Frequency vectors
│   │   ├── convergence_engine.py  # Beam search + delta-mu convergence
│   │   ├── attractor_network.py   # Kuramoto oscillator dynamics
│   │   ├── latent_space.py   # Semantic projection/reconstruction
│   │   └── mesh.py           # Decentralized cognitive mesh
│   └── integration/          # ISRE ↔ URCM bridge
│
├── isre/                     # Research/earlier implementation
│   ├── reasoning/            # Hopf oscillator dynamics
│   ├── knowledge/            # Physics rules, domain modules
│   ├── reconstruction/       # Multi-format output translators
│   └── pipeline/             # 5-layer orchestration
│
├── requirements.txt
├── verify_hsrai.py           # Standalone verification script
├── ROADMAP_PRODUCTION.md     # Production roadmap
├── VALIDATION_REPORT.md      # 49/49 tests passed
└── MARKET_ANALYSIS.md        # Market pain points and solutions
```

---

## Three Subsystems

| Subsystem | Purpose | Key Features |
|-----------|---------|--------------|
| **hsrai** | Production pipeline | Full async pipeline, plugin system, ECDSA trust chain |
| **urcm** | Frequency-based reasoning | Phoneme→Frequency→Resonance, Kuramoto oscillators, beam search |
| **isre** | Research implementation | Hopf dynamics, physics rules, architectural validation |

---

## Quick Start

### Installation

```bash
git clone https://github.com/abhi9199-tech42/HSRAI.git
cd HSRAI
pip install -r requirements.txt
```

### Verify Installation

```bash
python verify_hsrai.py
```

### Run Tests

```bash
pytest hsrai/tests/ -v
```

### Usage

```python
from hsrai.system.controller import SystemController
from hsrai.system.config import SystemConfig

# Initialize the system
config = SystemConfig()
controller = SystemController(config=config)

# Process a request (async)
import asyncio
output = asyncio.run(controller.process_request("Analyze the risk of this financial transaction"))

# Output includes:
# - content: Generated text/code/action plan
# - trust_certificate: ECDSA-signed proof of reasoning
print(output.content)
print(output.trust_certificate.signature)
```

---

## Features

### Deterministic Reasoning
- **Content-Addressable IDs**: `SHA256(CanonicalJSON(Content))` — same input always produces the same graph
- **Reproducible Paths**: Reasoning paths are structurally identical across runs
- **Regression Proof**: Code changes that alter reasoning are mathematically detectable

### Cryptographic Trust
- **ECDSA SECP256R1** signatures on every output
- **Behavioral Alignment Scoring** with tamper detection
- **Chain of Custody**: Trace outputs back to source data and knowledge entries

### Oscillatory Convergence
- **Biological Rhythm Gating**: `ỹt = yt ⊙ σ(Wg·g(t) + b)`
- **μ-Stability Metric**: Automatic termination when solution is stable
- **No Arbitrary Limits**: Stops based on informational convergence, not token counts

### Multi-Modal Input
- Text, Voice (phoneme sequences), Behavior (gaze/gesture), Sensor data
- Unified SemanticPrimitive representation across all modalities

### Plugin Architecture
```python
from hsrai.plugins.interfaces import CompressionPlugin

class MyPlugin:
    def initialize(self, config): ...
    def shutdown(self): ...
    def process(self, input_data, source_id) -> SemanticPrimitive: ...
```

### Observer Pattern
```python
from hsrai.system.api import GraphObserver

class MyObserver:
    def on_graph_built(self, graph): ...   # Inspect/modify graph
    def on_reasoning_complete(self, path): ...
```

---

## Testing

**49 tests across 14 modules** — all passing.

| Test Module | What It Tests |
|-------------|---------------|
| `test_trust.py` | ECDSA signing, verification, tamper detection |
| `test_reasoning.py` | Multi-path DFS, μ-stability, oscillatory convergence |
| `test_compression.py` | Phoneme mapping, determinism, smoothness |
| `test_graph.py` | Node/edge creation, conflict detection |
| `test_integration.py` | End-to-end pipeline, plugin integration, error recovery |
| `test_properties.py` | Property-based invariants (Hypothesis) |
| `test_system.py` | Concurrent isolation, graceful degradation |
| `test_knowledge.py` | Source verification, gap detection |
| `test_multimodal.py` | Text/voice/behavior/sensor processing |
| `test_output.py` | Text/code/action plan generation + trust certs |
| `test_api.py` | Public API, observer pattern |
| `test_extensibility.py` | Plugin registration, config management |
| `test_structure.py` | Component shape and structure |
| `test_system.py` | Performance and reliability |

Run with coverage:
```bash
pytest hsrai/tests/ --cov=hsrai --cov-report=html
```

---

## Mathematical Foundations

### 1. Inverse Entropy Density (ρ)
```
ρ = 1 - H(v) / H_max
# H(v) = Shannon entropy of frequency vector
# Higher ρ = purer, more focused semantic signal
```

### 2. Manifold Distance Cost (χ)
```
χ = ||v_t - v_{t-1}||₂
# Measures energy expenditure between reasoning steps
# Higher χ = more transformation cost
```

### 3. μ-Stability
```
μ = ρ / (χ + ε)
# ε = 1e-9 (numerical stability)
# High μ = high density, low cost = stable reasoning
```

### 4. Oscillatory Gating
```
ỹt = yt ⊙ σ(Wg · g(t) + b)
g(t) = [sin(ωt + φ), cos(ωt + φ)]
# Gates semantic flow through biological attention windows
```

### 5. Kuramoto Synchronization (URCM)
```
r = |1/N Σ e^{iθⱼ}|
# Order parameter measuring phase coherence
# r → 1 = fully synchronized, r → 0 = desynchronized
```

---

## Roadmap

See [ROADMAP_PRODUCTION.md](ROADMAP_PRODUCTION.md) for the full production roadmap.

**Current Phase**: Phase 1 — Fix Breaking Bugs & Dependencies

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | In Progress | Fix breaking bugs & dependencies |
| Phase 2 | Planned | Consolidate duplicated code |
| Phase 3 | Planned | Fix `__init__.py` & exports |
| Phase 4 | Planned | Configuration & hardcoded values |
| Phase 5 | Planned | Error handling & logging |
| Phase 6 | Planned | Refactor god classes |
| Phase 7 | Planned | URCM test suite (16 files) |
| Phase 8 | Planned | ISRE test suite (12 files) |
| Phase 9 | Planned | Fix hsrai test gaps |
| Phase 10 | Planned | Docs & REST API |
| Phase 11 | Planned | Security hardening |
| Phase 12 | Planned | CI/CD & packaging |
| Phase 13 | Planned | Performance & monitoring |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the **GNU General Public License v3.0** — see the [LICENSE](LICENSE) file for details.

Under GPL-3.0:
- You may study, modify, and distribute this software
- Any derivative work **must also be open-sourced** under GPL-3.0
- You may **not** use this software in proprietary/closed-source products
- All copies must include the original copyright notice and license

---

## Citation

```bibtex
@software{hsrai2026,
  title={HSRAI: Hybrid Semantic Reasoning AI},
  author={Kriti},
  year={2026},
  version={1.0.0},
  url={https://github.com/abhi9199-tech42/HSRAI}
}
```

---

## Contact

- **Author**: Kriti
- **GitHub**: [@abhi9199-tech42](https://github.com/abhi9199-tech42)
- **Issues**: [GitHub Issues](https://github.com/abhi9199-tech42/HSRAI/issues)
