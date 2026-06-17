# HSRAI Architecture

## System Overview

HSRAI is a deterministic, auditable, cryptographically verifiable reasoning operating system. It replaces stochastic LLM reasoning with a structurally auditable pipeline grounded in information theory and oscillatory dynamics.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HSRAI SYSTEM                                 │
│                                                                     │
│  Input (Text / Voice / Behavior / Sensor)                           │
│      │                                                              │
│      ▼                                                              │
│  ┌──────────────────────────────────────────┐                       │
│  │  1. SEMANTIC COMPRESSION                 │                       │
│  │     MultiModalProcessor                  │                       │
│  │     → SemanticPrimitive                  │                       │
│  │     ID = SHA256(CanonicalJSON(Content))  │                       │
│  └──────────────────────────────────────────┘                       │
│      │                                                              │
│      ▼                                                              │
│  ┌──────────────────────────────────────────┐                       │
│  │  2. INTENT GRAPH CONSTRUCTION            │                       │
│  │     IntentGraphBuilder                   │                       │
│  │     → IntentGraph (Typed Nodes + Edges)  │                       │
│  │     Conflict Detection + Optimization    │                       │
│  └──────────────────────────────────────────┘                       │
│      │                                                              │
│      ▼                                                              │
│  ┌──────────────────────────────────────────┐                       │
│  │  3. KNOWLEDGE INTEGRATION                │                       │
│  │     KnowledgeQueryEngine                 │                       │
│  │     Trust-Rated Source Filtering         │                       │
│  │     Gap Detection                        │                       │
│  └──────────────────────────────────────────┘                       │
│      │                                                              │
│      ▼                                                              │
│  ┌──────────────────────────────────────────┐                       │
│  │  4. HYBRID REASONING ENGINE              │                       │
│  │     DFS Path Finding                     │                       │
│  │     Oscillatory Gating: ỹt = yt ⊙ σ(...) │                       │
│  │     μ-Stability: μ = ρ / χ              │                       │
│  │     Auto-convergence when Δμ → 0         │                       │
│  └──────────────────────────────────────────┘                       │
│      │                                                              │
│      ▼                                                              │
│  ┌──────────────────────────────────────────┐                       │
│  │  5. TRUSTED OUTPUT                       │                       │
│  │     Text / Code / Action Plans           │                       │
│  │     + ECDSA-signed TrustCertificate      │                       │
│  └──────────────────────────────────────────┘                       │
│                                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │  Plugin System                           │                       │
│  │  CompressionPlugin | ReasoningPlugin     │                       │
│  │  OutputPlugin      | Observer Pattern    │                       │
│  └──────────────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Three Subsystems

HSRAI is organized into three subsystems with distinct responsibilities.

### 1. `hsrai` — Production Pipeline

The main production system. Provides the full async pipeline from input to signed output.

| Package | Responsibility |
|---------|---------------|
| `hsrai/core/` | Data types (`SemanticPrimitive`, `TrustCertificate`), enums (`IntentType`, `EdgeType`, `SemanticType`), deterministic ID generation |
| `hsrai/compression/` | `MultiModalProcessor` (text, voice, behavior, sensor → `SemanticPrimitive`), `PhonemeFrequencyMapper` |
| `hsrai/graph/` | `IntentNode`, `IntentEdge`, `IntentGraph`, `IntentGraphBuilder` (typed graph with conflict detection) |
| `hsrai/reasoning/` | `HybridReasoningEngine` (DFS + μ-stability), `OscillatoryGating` |
| `hsrai/knowledge/` | `KnowledgeQueryEngine`, `InMemoryKnowledgeBase`, knowledge gap detection |
| `hsrai/trust/` | `TrustManager` (ECDSA SECP256R1 signing), `BehavioralVerifier` |
| `hsrai/output/` | `OutputGenerator` (text, code, action plan generation with trust certificates) |
| `hsrai/plugins/` | `PluginManager`, protocol interfaces (`CompressionPlugin`, `ReasoningPlugin`, `OutputPlugin`) |
| `hsrai/system/` | `SystemController` (pipeline orchestration), `SystemConfig`, `ConfigurationManager` |
| `hsrai/api/` | FastAPI REST server |

### 2. `urcm` — Unified mu-Resonance Cognitive Mesh

A frequency-based reasoning engine. Converts text to phonemes, maps them to frequency vectors, and uses oscillator dynamics for convergence.

| Module | Purpose |
|--------|---------|
| `urcm/core/theory.py` | `URCMTheory` — mathematical foundations for ρ, χ, μ |
| `urcm/core/phoneme_mapper.py` | Text → Phoneme → Frequency vector conversion |
| `urcm/core/convergence_engine.py` | `MuConvergenceEngine` — beam search with Δμ convergence |
| `urcm/core/attractor_network.py` | `AttractorNetwork` — Kuramoto oscillator dynamics |
| `urcm/core/latent_space.py` | Semantic projection and reconstruction |
| `urcm/core/mesh.py` | Decentralized cognitive mesh |
| `urcm/integration/isre/` | Bridge between URCM and ISRE |

### 3. `isre` — Research Implementation

An earlier research implementation used for architectural validation and algorithm prototyping.

| Module | Purpose |
|--------|---------|
| `isre/reasoning/` | Hopf oscillator dynamics, reasoning selection |
| `isre/knowledge/` | Physics rules, domain modules, knowledge engine |
| `isre/reconstruction/` | Multi-format output translators (language, code, action) |
| `isre/graph/` | Graph builder |
| `isre/compression/` | Text, speech, and multimodal compression |
| `isre/pipeline/` | 5-layer orchestration |

---

## Data Flow

### Stage 1: Semantic Compression

Raw input is compressed into a `SemanticPrimitive` — a content-addressed, deterministic unit of meaning.

```python
# MultiModalProcessor.process_text()
id_data = {
    "type": "concept",
    "concept": text[:50],
    "modality": "text",
    "source_id": source_id,
    "source_length": len(text)
}
sem_id = f"text_{deterministic_id(id_data)[:8]}"
```

Every input modality (text, voice, behavior, sensor) produces the same `SemanticPrimitive` structure. The `id` field is a SHA-256 hash of the canonical JSON representation, guaranteeing determinism: the same input always produces the same primitive.

### Stage 2: Intent Graph Construction

Primitives are assembled into a typed `IntentGraph`:

- **Nodes** (`IntentNode`): Typed as `GOAL`, `CONTEXT`, `QUERY`, `CONSTRAINT`, `EMOTION`, or `BEHAVIORAL_PATTERN`. Each node carries a list of `SemanticPrimitive` payloads and a `behavioral_score`.
- **Edges** (`IntentEdge`): Typed as `CAUSAL`, `TEMPORAL`, `LOGICAL`, `PRIORITY`, or `TRUST_BASED`. Each edge has a `weight` and a `trust_verified` flag.

The `IntentGraphBuilder` also performs:
- **Conflict detection**: Identifies `CONSTRAINT → GOAL` edges connected by `PRIORITY`, marking resource conflicts.
- **Graph optimization**: Prunes isolated non-goal nodes and normalizes weights.

### Stage 3: Knowledge Integration

The `KnowledgeQueryEngine` queries registered knowledge sources and filters by trust rating.

- Sources implement the `KnowledgeSource` protocol (`query()`, `get_trust_rating()`).
- Results below the required trust threshold are discarded.
- **Gap detection**: If no results are found or all trust ratings are low, a `KnowledgeGap` is emitted with criticality and trust implications.

### Stage 4: Hybrid Reasoning

The `HybridReasoningEngine` finds and evaluates paths through the intent graph:

1. **DFS path finding** from a context node to a goal node (max depth 10).
2. **μ-stability calculation** for each path: `μ = ρ / (χ + ε)`.
3. **Oscillatory gating** modulates stability using biological rhythms.
4. **Convergence**: The engine tracks the best path across time steps. When the same path is selected for 5 consecutive steps, it converges and returns.

### Stage 5: Output Generation

The `OutputGenerator` produces the final output:

- **Text**: Natural language explanation of the reasoning path.
- **Code**: Executable code derived from action and concept nodes.
- **Action Plan**: Structured step-by-step plan.

Each output is accompanied by an ECDSA-signed `TrustCertificate`.

---

## Key Algorithms

### μ-Stability

The central convergence metric. It measures the ratio of information purity to transformation cost.

```
μ = ρ / (χ + ε)

where:
  ρ (rho) = Semantic Density = 1 - H(v) / H_max
            H(v) = Shannon entropy of the frequency vector
            Higher ρ = purer, more focused semantic signal

  χ (chi) = Transformation Cost = ||v_t - v_{t-1}||₂
            L2 norm of the displacement between successive states
            Higher χ = more energy expenditure

  ε = 1e-9 (numerical stability constant)
```

A high μ indicates high information purity achieved at low cost — stable reasoning. The system terminates when Δμ (the change in μ between steps) drops below a threshold, indicating the solution has stabilized.

### Oscillatory Gating

Biological rhythm modulation applied to semantic flow through attention windows.

```
ỹ_t = y_t ⊙ σ(W_g · g(t) + b)

where:
  g(t) = [sin(ωt + φ), cos(ωt + φ)]   — biological rhythm signal
  σ    = sigmoid activation function
  W_g  = gating weight matrix
  b    = bias vector
  ⊙    = element-wise multiplication
```

This gates which semantic activations are allowed to propagate at any given time, creating attention windows analogous to biological neural oscillations. The `OscillatoryGating` class manages phase advancement and attention window detection.

### Kuramoto Synchronization (URCM)

Used in the `AttractorNetwork` to achieve phase coherence across oscillators representing semantic concepts.

```
dθ_i/dt = ω_i + (K/N) Σ_j sin(θ_j - θ_i)

Order parameter: r = |(1/N) Σ_j e^(iθ_j)|

  r → 1: fully synchronized (semantic consensus)
  r → 0: desynchronized (no coherent interpretation)
```

The coupling strength `K` controls the synchronization threshold. When `K > K_c` (critical coupling), oscillators spontaneously synchronize, indicating semantic convergence.

### Resonant Hebbian Learning (URCM)

Attractor weights are updated proportionally to achieved resonance:

```
ΔW = η · μ · (state - attractor)

where:
  η = learning rate
  μ = resonance achieved during the current cycle
```

This reinforces paths that lead to high-resonance outcomes, allowing the system to learn and stabilize over repeated processing.

---

## Trust Chain

### ECDSA Signing

Every output is signed using ECDSA with the SECP256R1 curve (NIST P-256).

**Certificate generation**:

1. Compute a behavioral alignment score via `BehavioralVerifier`.
2. Create a payload: `"{subject_id}:{trust_score}:{timestamp}"`.
3. Sign the payload with the ECDSA private key.
4. Encode the signature as Base64.
5. Generate a deterministic certificate ID from the signed payload.

**Certificate verification**:

1. Check trust score is in [0.0, 1.0].
2. Reconstruct the payload from certificate fields.
3. Verify the ECDSA signature against the public key.
4. Return validity.

Key management:

- `TrustManager.__init__()` generates a new key pair if no key file exists.
- `TrustManager.save_keys()` persists the private key to PEM.
- `TrustManager.rotate_keys()` generates a fresh key pair.

### Behavioral Scoring

`BehavioralVerifier.calculate_alignment_score()` checks:

- Emotional intensity anomalies (penalizes intensity > 0.95).
- Hyper-intense actions (penalizes action weight > 1.0).
- Non-human semantic types in behavioral contexts.

Scores range from 0.0 (anomalous) to 1.0 (fully aligned). The score is embedded in the trust certificate and used to filter knowledge sources.

---

## Plugin System

HSRAI supports runtime extension through three plugin interfaces.

### Plugin Interfaces

```python
class CompressionPlugin(Protocol):
    def initialize(self, config: Dict[str, Any]) -> None: ...
    def shutdown(self) -> None: ...
    def process(self, input_data: Any, source_id: str) -> SemanticPrimitive: ...

class ReasoningPlugin(Protocol):
    def initialize(self, config: Dict[str, Any]) -> None: ...
    def shutdown(self) -> None: ...
    def reason(self, graph: IntentGraph) -> Optional[ReasoningPath]: ...

class OutputPlugin(Protocol):
    def initialize(self, config: Dict[str, Any]) -> None: ...
    def shutdown(self) -> None: ...
    def generate(self, path: ReasoningPath) -> GeneratedOutput: ...
```

### Registration

```python
from hsrai.plugins.manager import PluginManager

manager = PluginManager()
manager.register_compression("my_compressor", my_plugin)
manager.register_reasoning("my_reasoner", my_plugin)
manager.register_output("my_outputter", my_plugin)

# Initialize all with config
manager.initialize_all(config_dict)

# Shutdown all on exit
manager.shutdown_all()
```

### Observer Pattern

The `SystemController` supports observers that receive events during pipeline execution:

```python
from hsrai.system.api import GraphObserver

class MyObserver:
    def on_graph_built(self, graph: IntentGraph, request_id: str) -> None:
        """Called after the intent graph is constructed."""

    def on_path_found(self, path: ReasoningPath, request_id: str) -> None:
        """Called when a reasoning path is found."""

controller.add_observer(MyObserver())
```

---

## Configuration

### SystemConfig

The `SystemConfig` dataclass holds runtime parameters:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `environment` | `str` | `"development"` | Runtime environment (`development`, `production`, `testing`) |
| `debug` | `bool` | `False` | Enable debug logging |
| `max_concurrent_requests` | `int` | `10` | Maximum concurrent pipeline executions (async semaphore) |
| `timeout_ms` | `int` | `5000` | Request timeout in milliseconds |
| `plugins` | `Dict[str, Dict[str, Any]]` | `{}` | Per-plugin configuration dictionaries |

### ConfigurationManager

Loads and validates configuration from a JSON file:

```python
from hsrai.system.config import ConfigurationManager

cm = ConfigurationManager("config.json")
cm.load()

# Access raw values
debug = cm.get("debug", False)

# Subscribe to config changes
cm.subscribe(lambda config: print(f"Config updated: {config.environment}"))

# Reload from disk
cm.reload()
```

Validation rules:

- `environment` must be one of `development`, `production`, or `testing`.
- `max_concurrent_requests` must be positive.

### Configuration File Example

```json
{
  "environment": "production",
  "debug": false,
  "max_concurrent_requests": 50,
  "timeout_ms": 10000,
  "plugins": {
    "compression": {
      "nlp_compressor": {
        "model": "en_core_web_sm"
      }
    },
    "reasoning": {
      "custom_reasoner": {
        "beam_width": 5,
        "convergence_epsilon": 1e-4
      }
    }
  }
}
```
