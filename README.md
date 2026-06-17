# HSRAI — Hybrid Semantic Reasoning AI

> **Auditable AI that holds up in court.**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-408%20passed-brightgreen)]()
[![Status](https://img.shields.io/badge/status-production%20ready-success)]()

---

## The Problem

Your AI denied a loan today. It approved the same loan yesterday. With the same data.

Now a regulator is asking **"why?"**

You can't answer. Your model is a black box. Your logs are useless. Your legal team is panicking.

**This is happening right now.** The EU AI Act (2026) fines up to €35M for unauditable AI decisions. GDPR's "right to explanation" is being enforced. Financial regulators are demanding mathematical proof of reasoning chains.

---

## What HSRAI Does

HSRAI replaces black-box AI with a **Reasoning Operating System** that:

| Feature | What It Means |
|---------|---------------|
| **Deterministic** | Same input always produces the same reasoning path |
| **Auditable** | Every decision traces back to source data with cryptographic proof |
| **Trust-Certified** | Every output gets an ECDSA-signed certificate |
| **Convergent** | Stops reasoning when the answer is stable (no infinite loops) |
| **Real NLP** | 384-dimensional semantic embeddings, not text truncation |
| **Graph-Based** | Reasoning happens over structured graphs, not hidden tensors |

---

## See It Working

### Fraud Detection (Live Demo)

```
$ python -m usecases.fraud_detection.demo

Transaction: TX_DEMO_001  $250.00     LOW    (0.133)  Approve
Transaction: TX_DEMO_002  $15,000.00  MEDIUM (0.717)  Flag for review
  Risk Factors:
    * High-value transaction (>$10,000)
    * Foreign merchant in high-risk country
  Recommendations:
    > Send alert to compliance team
  Trust Certificate: cert_d92fce80
  Processing Time:   1.38s
```

Every assessment comes with:
- **Mathematical risk score** (0.0 - 1.0)
- **Traceable risk factors** (weighted, explainable)
- **ECDSA trust certificate** (cryptographically signed)
- **Reasoning path** (auditable graph traversal)

### Medical Diagnosis (Live Demo)

```
$ python -m usecases.medical_diagnosis.demo

Patient: PAT002 (68yo F)
Symptoms: cough, fever, dyspnea, sputum production, chest pain

  RISK LEVEL:    CRITICAL
  URGENCY:       EMERGENT
  CONFIDENCE:    94%

  Differential Diagnoses:
    1. Community-Acquired Pneumonia (J18.9)
       Probability: 93.9%

  Recommendations:
    > EMERGENT: Initiate immediate medical intervention
    > Activate rapid response team
  Trust Certificate: cert_26470ef9
```

Features:
- **10 conditions** in knowledge base (diabetes, pneumonia, MI, sepsis, UTI, etc.)
- **8 drugs** with interaction/contraindication checks
- **Differential diagnoses** ranked by probability
- **Drug safety warnings** (interactions + contraindications)

### REST API

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Analyze the risk of this $15,000 transaction from Nigeria"}'

# Response includes: content, trust_certificate_id, metadata
```

### CLI

```bash
hsrai process "Your query here"
hsrai verify --cert cert_d92fce80
hsrai config --show
```

---

## Architecture

```
Input (Text / Transaction / Sensor)
    |
    v
+-------------------------------+
|  NLP COMPRESSION              |
|  sentence-transformers        |
|  384-dim embeddings           |
|  Intent classification        |
|  Entity extraction            |
+-------------------------------+
    |
    v
+-------------------------------+
|  KNOWLEDGE GRAPH              |
|  Neo4j (or in-memory fallback)|
|  Entity relationships         |
|  Risk factor lookup           |
|  Pattern matching             |
+-------------------------------+
    |
    v
+-------------------------------+
|  INTENT GRAPH                 |
|  Typed nodes (Goal/Context/   |
|  Constraint/Emotion)          |
|  Conflict detection           |
|  Priority inversion check     |
+-------------------------------+
    |
    v
+-------------------------------+
|  HYBRID REASONING             |
|  Oscillatory gating           |
|  mu = rho / chi               |
|  Auto-convergence (delta-mu)  |
|  Multi-path exploration       |
+-------------------------------+
    |
    v
+-------------------------------+
|  TRUSTED OUTPUT               |
|  Text / Risk Score / Action   |
|  + ECDSA-signed certificate   |
|  + Reasoning path             |
+-------------------------------+
```

---

## Key Math

**Mu-Stability** — When to stop reasoning:
```
mu = rho / chi
rho = 1 - H(v)/H_max    (semantic purity)
chi = ||v_t - v_{t-1}||  (transformation cost)
```
System stops when delta-mu approaches zero. No arbitrary token limits.

**Oscillatory Gating** — Biological attention:
```
y_tilde = y * sigmoid(W_g * g(t) + b)
g(t) = [sin(phase), cos(phase)]
```

**Kuramoto Synchronization** — Network coherence:
```
r = |1/N * sum(e^(i*theta_j))|
r -> 1 = synchronized, r -> 0 = chaotic
```

---

## Performance

```
Benchmark                      Mean (ms)
--------------------------------------------------
compression (NLP)              27.0
graph_construction             0.053
reasoning (20 steps)           0.152
trust_generation               0.193
trust_verification             0.299
phoneme_mapping                0.048
oscillatory_gating (1000x)     0.042
```

Full pipeline: **~30ms** (with NLP model loaded)

---

## Installation

```bash
git clone https://github.com/abhi9199-tech42/HSRAI.git
cd HSRAI

# Core only
pip install -e .

# With NLP
pip install -e ".[nlp]"

# With Neo4j
pip install -e ".[neo4j]"

# With API server
pip install -e ".[api]"

# Everything
pip install -e ".[all]"
```

---

## Quick Start

### Python

```python
from usecases.fraud_detection.analyzer import FraudDetector, Transaction

detector = FraudDetector()

result = detector.analyze(Transaction(
    tx_id="TX001",
    amount=15000,
    merchant="OnlineShopX",
    merchant_category="electronics",
    country="NG",
    account_id="ACC001",
    timestamp="2026-01-16T02:15:00",
))

print(result.risk_level)    # "medium"
print(result.risk_score)    # 0.717
print(result.risk_factors)  # [("High-value...", 0.3), ("Foreign...", 0.2)]
```

### API

```bash
python run_api.py
# Server starts on http://localhost:8000
# Docs at http://localhost:8000/docs
```

### CLI

```bash
hsrai process "Your query"
hsrai serve --port 8000
hsrai test
```

---

## Who Uses This

| Industry | Use Case | Why HSRAI |
|----------|----------|-----------|
| **Banking** | Fraud detection | Regulatory audit trail |
| **Healthcare** | Diagnostic support | Explainable AI requirements |
| **Defense** | Decision support | Deterministic, classified-safe |
| **Legal** | Compliance checking | Cryptographic proof of reasoning |
| **Insurance** | Claims processing | Auditable risk assessment |
| **FinTech** | KYC/AML | GDPR right to explanation |

---

## We Build It For You

**Need HSRAI for your specific use case? We'll build a custom deployment in under a week.**

### What You Get

- **Custom risk rules** for your domain (fraud, compliance, diagnostics, etc.)
- **Your knowledge graph** connected (Neo4j, PostgreSQL, your existing DB)
- **REST API** ready for your infrastructure
- **Dashboard** for monitoring reasoning paths and trust scores
- **Integration** with your existing systems
- **Documentation** and training for your team

### How It Works

1. **Day 1-2**: We analyze your use case, data, and compliance requirements
2. **Day 3-4**: Custom risk rules, knowledge graph, and API endpoints
3. **Day 5-6**: Testing, integration, and documentation
4. **Day 7**: Deployment and handoff

### Pricing

- **Open Source**: Free (GPL-3.0) — use it yourself
- **Custom Build**: Contact us for a quote — we handle everything
- **Enterprise Support**: Ongoing maintenance and updates

**Contact**: Open an issue at [github.com/abhi9199-tech42/HSRAI/issues](https://github.com/abhi9199-tech42/HSRAI/issues)

---

## Project Structure

```
HSRAI/
├── hsrai/                    # Core reasoning engine
│   ├── compression/          # NLP + phoneme mapping
│   ├── graph/                # Intent graph construction
│   ├── reasoning/            # Hybrid reasoning engine
│   ├── knowledge/            # Knowledge graph (Neo4j)
│   ├── trust/                # ECDSA trust chain
│   ├── api/                  # REST API (FastAPI)
│   ├── cli.py                # CLI tool
│   └── tests/                # 56 tests
├── urcm/                     # Frequency-based reasoning
│   ├── core/                 # Theory, attractors, convergence
│   └── tests/                # 246 tests
├── isre/                     # Research implementation
│   └── tests/                # 82 tests
├── usecases/fraud_detection/ # Real-world use case
├── usecases/medical_diagnosis/ # Medical diagnosis use case
├── benchmarks/               # Performance benchmarks
├── docs/                     # API + CLI documentation
└── .github/workflows/        # CI/CD
```

---

## Testing

```bash
# Run all 408 tests
pytest

# Run with coverage
pytest --cov=hsrai --cov-report=html

# Run benchmarks
python -m benchmarks.benchmarks

# Run fraud demo
python -m usecases.fraud_detection.demo

# Run medical diagnosis demo
python -m usecases.medical_diagnosis.demo
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style, and PR process.

---

## License

GPL-3.0 — Free to use, modify, and distribute. Derivative works must also be open source.

See [LICENSE](LICENSE) for details.

---

## Built By

**Kriti** — [github.com/abhi9199-tech42](https://github.com/abhi9199-tech42)

If you need a custom HSRAI deployment, open an issue and we'll build it for you in under a week.
