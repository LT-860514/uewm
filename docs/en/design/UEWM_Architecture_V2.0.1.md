# 🧠 UEWM core architecture design document

**Document version:** V2.0.1
**Document Number:** UEWM-ARCH-001
**Last update:** 2026-04-02
**Status:** Design completed (100% coverage of R01, R05, R07, R11, NFR-1~14 + MEM-AC-1~10 + GPU-AC-1~6 + EXT-AC-1~8 + LIC-AC-1~4 + GND-AC-1~10 + LeWM-AC-1~6)
**Change History:**
- deliver-v1.1: H-JEPA, 8 Z-Layers, EBM, orchestration module, TRL, long-term memory
- V1.0.1: GPU optimization, third-party Agent adaptation layer, independent API, license policy
- V2.0.0: Dual space architecture (G-Space + Z-Space), bridging function, Discovery Engine, dual space surprise, enhanced EBM output, verification priority construction strategy
- **V2.0.1: LeWorldModel integration - SIGReg replaces VICReg, projection head (MLP+BN), physical detection verification, expectation violation testing, adaptive latent dimension (256-d→2048-d), end-to-end encoder fine-tuning strategy**

---

## 1. Document purpose and scope

This document defines the core architectural design of UEWM V2.0. The core innovation of V2.0: **Dual-Space Architecture** — Z-Space (hidden space) is responsible for discovering unnamed patterns, G-Space (observable space) is responsible for verification and anchoring, and the two are coupled through the bridge function. Hidden space discovery, observable space verification, memory consolidation, and evolutionary sharpening.

Covers: dual space awareness architecture, H-JEPA hierarchical prediction engine (dual prediction), EBM enhanced arbitration (energy + risk decomposition), Discovery Engine, G-Space Engine, bridging function and consistency loss, Brain Core orchestration module, multi-project concurrency model and tenant sharding, GPU optimization strategy, third-party Agent adaptation layer, independent Brain Core API, license and distribution.

---

## 2. Architecture design principles

| # | Principle | Description |
|---|------|------|
| P1 | JEPA-First | All reasoning is completed in the latent space, no token-level generation is performed |
| P2 | Non-generative | Using Joint Embedding Predictive Architecture |
| P3 | Energy minimization | Global decision-making is optimized through EBM energy function |
| P4 | Hierarchical abstraction | H-JEPA multi-timescale multi-granularity prediction |
| P5 | Model-independent | The underlying sensing module is pluggable |
| P6 | Self-evolution | Surprise-driven continuous learning |
| P7 | Safe and controllable | Energy threshold + manual access control |
| P8 | Common to multiple teams | Base Model + independent LoRA + tenant sharding |
| P9 | Active introspection | Regular self-reflection (including grounded health) |
| P10 | Human-machine collaboration | Role engineers can intervene at any time |
| P11 | Uncertainty perception | Probability distribution representation under POMDP framework |
| P12 | Progressive Maturity | TRL drives system behavior |
| P13 | Orchestration is decision-making | Cross-Agent orchestration is the execution function of Brain Core |
| **P14** | **Dual space anchoring** | **Each prediction in the latent space must ultimately be verifiable against observables; the observable space learns new indicators from the latent space** |
| **P15** | **Verification first** | **Use PoC to prove scientific hypotheses first, and then build a complete platform** |
| **P16** | **Discovery is knowledge** | **Predictions that Z-Space is correct but G-Space cannot explain = new engineering knowledge** |

---

## 3. Overall system architecture (V2.0 five-layer bionic architecture)

### 3.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│Level 0: Observable World │
│ Code Warehouse / CI-CD / Monitoring Platform / Issue Tracker / Market Data / Logging System │
└──────────────────────────────────────────┬───────────────────────────────┘
                     │ Direct Measurements │ Raw Signals (for encoding)
┌─────────────────────▼──────────────────────▼───────────────────────────────┐
│ First layer: Dual Perception Layer │
│ │
│ ┌─ G-Space Engine ────────────────┐ ┌─ Z-Space Encoders ─────────────┐ │
│ │ ~80 named metrics per project │ │ 8 modal encoders → 2048-d │ │
│ │ No learning, direct measurement │ │ Discovers unnamed patterns │ │
│ │ Reality anchor for Z-Space │ │ Learned representations │ │
│ └──────────────┬─────────────────┘ └─────────────┬─────────────────┘ │
│ │ Bridging Functions (φ, ψ) │ │
│ └──────── Consistency Loss ────────────┘ │
│ AlignmentTrainer (cross-modal alignment, V1.0.1 reserved) │
└────────────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────────────┐
│ Second layer: H-JEPA Brain Core (V2.0 enhanced) │
│ │
│ Z-Buffer Manager ← Manage Z-Layer status + G-Space status simultaneously │
│ H-JEPA Predictor ──► Double prediction: Z(t+1) AND G(t+1) synchronous output │
│ EBM Arbiter (V2.0) ──► Energy score + Risk Decomposition │
│ unnamed_risk = energy not explained by G-Space → Discovery Signal │
│ Causal Graph Engine ← Z-Space Edge + G-Space Edge Unified Causal Graph │
│ Discovery Engine [New in V2.0] ← Detect and name unknown patterns │
│ Long-term memory subsystem (four layers: Procedural/Working/Episodic/Semantic) │
│ Episodes dual index: Z-snapshot + G-snapshot + discovery mark │
│ Orchestration module (7 capabilities, including asynchronous) │
│ TRL Maturity Evaluator │
│ Error budget engine (Burn-Rate/level 4 alarm) │
│ Self-evolution engine (Safety Envelope/Circuit Breaker/Pareto) — Dual Space Surprise Drive │
│ Self-reflective engine (6 dimensions, including grounded health) │
│ Cross-project knowledge engine (KSL/Privacy Budget/Federated Learning) │
└────────────────────────────────────────────────────────────────────────┘
                                │ EIP Protocol (gRPC + Kafka + Stream)
┌─────────────────────────────────────────────────────────────────────────┐
│The third layer: EIP Gateway + third-party Agent adaptation layer │
│ (RBAC/mTLS/DynamicPermission/REST↔gRPC Gateway) │
└────────────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────────────┐
│The fourth layer: Agent terminal array (three-ring layered) │
│ Outer ring: AG-PA │ AG-PD │ AG-BI │ AG-PR (Phase 2, LOA 3-5) │
│ Central: AG-SA │ AG-FD │ AG-AU (Phase 1, LOA 5-7) │
│ Inner ring: AG-CD │ AG-CT │ AG-DO │ AG-ST │ AG-MA (Phase 0B, LOA 7-9) │
│ + Third-party Agents via SDK (Apache 2.0) │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Brain Core internal component list (V2.0)

| # | Component | Responsibility | Source | Benchmarking Requirements |
|---|------|------|------|---------|
| 1 | Z-Buffer Manager | 8-layer hidden state + G-Space state reading and writing/snapshot/version | V1 + V2 enhancement | R01 |
| 2 | Perception Pipeline + AlignmentTrainer | Encoder Management/Projection/Cross-modal Alignment | V1 | R01, R12 |
| 3 | **G-Space Engine** | **~80 named indicator collection/normalization/storage** | **V2.0 new** | **GND** |
| 4 | **Bridging Functions (φ, ψ)** | **Z↔G coupling/consistency loss** | **New in V2.0** | **GND** |
| 5 | H-JEPA Predictor | Multi-time scale state prediction **(V2.0: dual prediction Z+G)** | V1 + V2 enhancement | R01 |
| 6 | Causal Graph Engine | Granger Causal Graph **(V2.0: Z edge + G edge)** | V1 + V2 enhancement | R01 |
| 7 | EBM Arbiter | Energy Arbitration **(V2.0: + Risk Decomposition)** | V1 + V2 Enhancement | R01 |
| 8 | **Discovery Engine** | **Detect Z-correct/G-unexplained events, extract new indicators** | **New in V2.0** | **GND** |
| 9 | Long Memory Subsystem | Four-layer memory **(V2.0: Dual Index Episodes)** | V1.1 + V2 enhancement | R01,R03,R06,R10 |
| 10 | Orchestration Module | Task sequencing/handover/arbitration/milestones/conflicts | V1 | R01 |
| 11 | TRL Evaluator | Z-Layer maturity automatic assessment/dynamic weight reduction | V1 | R01 |
| 12 | Evolution Engine | Security Envelope/Circuit Breaker/Pareto/LoRA **(V2.0: Dual Space Surprise)** | V1 + V2 Enhancement | R03 |
| 13 | Self-Reflection Engine | Regular introspection **(V2.0: 6 dimensions including grounded health)** | V1 + V2 enhancement | R06 |
| 14 | Knowledge Engine | KSL Distillation/Privacy Budget/Federated Learning | V1 | R08 |
| 15 | Error Budget Engine | Burn-Rate/Level 4 Alarm/Automatic Downgrade | V1 | R05 |
| 16 | Request Router | Request distribution/response aggregation | V1 | R11 |

### 3.3 Orchestration module — Same as V1.0.1 (7 capabilities, asynchronous, multi-project concurrency)

(For complete content, see V1.0.1 ARCH §3.3, no changes)

### 3.4 Multi-project orchestration concurrency model — Same as V1.0.1

(For complete content, see V1.0.1 ARCH §3.4, no changes)

### 3.5 Tenant Sharding Architecture - Same as V1.0.1

(For complete content, see V1.0.1 ARCH §3.6, no changes)

---

## 4. G-Space Engine (new in V2.0 core)

### 4.1 Design Goals

Provide a continuous "reality anchor" for Z-Space hidden space. Every Z-Space prediction is ultimately verifiable against G-Space observables. G-Space itself does not do learning, only collection and normalization.

### 4.2 G-Space indicator matrix

```python
class GSpaceEngine:
    """
    Capture and maintain ~80 directly measurable engineering metrics/items.
    No ML, pure observations and normalization. The "reality anchor" of the system.
    """
    
    METRICS = {
        "code": { # ~15 indicators, updated each commit
            "complexity_avg": {"unit": "cyclomatic", "source": "tree-sitter"},
            "complexity_max": {"unit": "cyclomatic", "source": "tree-sitter"},
            "coupling_score": {"unit": "ratio [0,1]", "source": "import graph"},
            "cohesion_score": {"unit": "ratio [0,1]", "source": "module analysis"},
            "churn_rate_7d": {"unit": "lines/day", "source": "git log"},
            "duplication_pct": {"unit": "%", "source": "jscpd/PMD"},
            "file_count": {"unit": "count", "source": "git ls-files"},
            "loc_total": {"unit": "lines", "source": "cloc"},
            "loc_delta": {"unit": "lines", "source": "git diff"},
            "files_changed": {"unit": "count", "source": "git diff"},
            "hotspot_concentration": {"unit": "gini [0,1]", "source": "churn analysis"},
            "dependency_count": {"unit": "count", "source": "go.mod/requirements.txt"},
            "outdated_deps_pct": {"unit": "%", "source": "pip-audit/npm-audit"},
            "lint_violations": {"unit": "count", "source": "golangci-lint/eslint"},
            "todo_count": {"unit": "count", "source": "grep TODO"},
        },
        "test": { # ~8 indicators, updated every CI run
            "pass_rate": {"unit": "%", "source": "CI results"},
            "coverage_pct": {"unit": "%", "source": "Cobertura/JaCoCo"},
            "coverage_delta": {"unit": "pp", "source": "diff with previous"},
            "flakiness_rate": {"unit": "%", "source": "CI reruns"},
            "test_count": {"unit": "count", "source": "test framework"},
            "test_duration_s": {"unit": "seconds", "source": "CI timing"},
            "test_duration_delta": {"unit": "seconds", "source": "diff"},
            "failed_test_count": {"unit": "count", "source": "CI report"},
        },
        "ops": { # ~11 metrics, updated every minute from Prometheus
            "p50_latency_ms": {"unit": "ms", "source": "Prometheus"},
            "p99_latency_ms": {"unit": "ms", "source": "Prometheus"},
            "error_rate_pct": {"unit": "%", "source": "Prometheus"},
            "cpu_usage_pct": {"unit": "%", "source": "Prometheus"},
            "memory_usage_pct": {"unit": "%", "source": "Prometheus"},
            "disk_usage_pct": {"unit": "%", "source": "Prometheus"},
            "request_rate_rps": {"unit": "req/s", "source": "Prometheus"},
            "uptime_pct_30d": {"unit": "%", "source": "Prometheus"},
            "incident_count_7d": {"unit": "count", "source": "PagerDuty"},
            "mttr_minutes": {"unit": "minutes", "source": "incident tracker"},
            "deploy_count_7d": {"unit": "count", "source": "CI/CD"},
        },
        "process": { # ~7 indicators, updated daily
            "pr_merge_time_hours": {"unit": "hours", "source": "GitHub API"},
            "review_turnaround_hours": {"unit": "hours", "source": "GitHub API"},
            "pr_size_lines_avg": {"unit": "lines", "source": "GitHub API"},
            "author_count_7d": {"unit": "count", "source": "git log"},
            "bus_factor": {"unit": "count", "source": "git fame"},
            "sprint_velocity": {"unit": "points", "source": "Jira/Linear"},
            "issue_close_rate_7d": {"unit": "count", "source": "issue tracker"},
        },
        "discovered": {} # V2.0: Dynamic growth, Discovery Engine adds new indicators
    }
    
    def observe(self, project_id: str) -> GSpaceState:
        """Collect the current G-Space status. No ML, pure measurement."""
        state = {}
        for domain, metrics in self.METRICS.items():
            for name, spec in metrics.items():
                state[f"{domain}.{name}"] = self.collectors[spec["source"]].collect(
                    project_id, name)
        return GSpaceState(project_id=project_id, values=state, timestamp=now())
    
    def add_discovered_metric(self, metric: ProposedGSpaceMetric):
        """New metrics proposed by Discovery Engine are added to G-Space after manual review."""
        self.METRICS["discovered"][metric.name] = {
            "unit": metric.unit, "source": metric.data_source,
            "discovered_by": "discovery_engine",
            "discovery_date": now(), "confidence": metric.confidence,
        }
```

### 4.3 G-Space data storage

| Storage Tiers | Technology | Retention Period | Query SLO |
|--------|------|--------|---------|
| Real time | PostgreSQL (time-series partitioned) | 30 days | < 100ms |
| History | PostgreSQL + Parquet (S3) | 1 year | < 5s |
| Archive | S3 (zstd) | Permanent | < 5min |

G-Space and Z-Buffer are in the same PostgreSQL instance, but have different schemas.

---

## 5. Bridging Functions — New in V2.0 core

### 5.1 Design Goals

Coupling Z-Space (hidden space, discovery) and G-Space (observable space, verification). φ: Z→G decoding (hidden space prediction observable). ψ: G→Z constraint (observable constraint latent space). Consistency loss ensures that the two spaces do not drift.

### 5.2 φ decoder (Z → G)

```python
class PhiDecoder(nn.Module):
    """φ: Predict G-Space metrics from Z-Space states.
    Each Z-Layer decodes the G-Space indicator of the corresponding field. """
    
    def __init__(self, z_dim=2048):
        super().__init__()
        self.layer_decoders = nn.ModuleDict({
            "Z_impl": nn.Sequential(nn.Linear(z_dim, 512), nn.ReLU(),
                                     nn.Linear(512, 15)), # → code.* indicator
            "Z_quality": nn.Sequential(nn.Linear(z_dim, 256), nn.ReLU(),
                                       nn.Linear(256, 8)), # → test.* indicator
            "Z_phys": nn.Sequential(nn.Linear(z_dim, 256), nn.ReLU(),
                                    nn.Linear(256, 11)), # → ops.* indicator
            "Z_arch": nn.Sequential(nn.Linear(z_dim, 128), nn.ReLU(),
                                    nn.Linear(128, 5)), # → coupling/cohesion
            "Z_logic": nn.Sequential(nn.Linear(z_dim, 128), nn.ReLU(),
                                     nn.Linear(128, 7)), # → process.* indicator
        })
    
    def forward(self, z_buffer):
        g_predicted = {}
        for layer_name, decoder in self.layer_decoders.items():
            if layer_name in z_buffer:
                g_predicted[layer_name] = decoder(z_buffer[layer_name])
        return g_predicted
    
    def per_dimension_r2(self, g_predicted, g_actual):
        """Dimension-wise R² — a grounded health metric for self-reflection."""
        r2_scores = {}
        for dim_name in g_actual:
            pred = g_predicted.get(dim_name)
            if pred is not None:
                ss_res = ((g_actual[dim_name] - pred) ** 2).sum()
                ss_tot = ((g_actual[dim_name] - g_actual[dim_name].mean()) ** 2).sum()
                r2_scores[dim_name] = 1 - ss_res / (ss_tot + 1e-8)
        return r2_scores
```

### 5.3 ψ anchor (G → Z)

```python
class PsiAnchor(nn.Module):
    """ψ: Constrain Z-Space state from G-Space observations.
    Ensure Z-Space does not drift into regions that contradict observable reality. """
    
    def __init__(self, g_dim=80, z_dim=2048):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(g_dim, 512), nn.ReLU(),
            nn.Linear(512, z_dim))
    
    def forward(self, g_state):
        return self.encoder(g_state)
```

### 5.4 Consistency loss and SIGReg unified training target [V2.0.1 rewrite]

```python
class UEWMTrainingObjective:
    """
    V2.0.1 Unified training target (integrated with LeWorldModel SIGReg):
    
    L_UEWM = L_pred + λ_sig · SIGReg(Z) + λ_con · L_consistency
    
    Term 1: L_pred — Next state prediction loss (JEPA Core, MSE)
    Term 2: SIGReg(Z) — Isotropic Gaussian regularization (replaces VICReg, from LeWM)
             Using the Cramér-Wold theorem: random projection + Epps-Pulley normality test
             Single hyperparameter λ_sig, optimized by bisection search O(log n)
    Term 3: L_consistency — G-Space consistency loss (original to UEWM V2.0)
             φ(Z_pred) ≈ G_actual + ψ(G_actual) ≈ Z_pred
    
    Total hyperparameters: 2 (λ_sig, λ_con)
    Compare V2.0.0: 4+ (VICReg’s var/inv/cov + consistency)
    Compare PLDM: 7 loss terms
    """
    
    def compute_loss(self, z_pred, z_target, g_actual, z_batch):
        # Term 1: Prediction loss
        l_pred = F.mse_loss(z_pred, z_target)
        
        # Term 2: SIGReg (replaces VICReg, from LeWorldModel)
        l_sigreg = self.sigreg(z_batch)
        
        # Term 3: G-Space consistency (original to UEWM V2.0)
        g_from_z = self.phi(z_pred)
        z_from_g = self.psi(g_actual)
        l_consistency = (
            0.5 * F.mse_loss(g_from_z, g_actual) +
            0.5 * F.cosine_embedding_loss(z_pred, z_from_g,
                                           torch.ones(z_pred.size(0)))
        )
        
        return l_pred + self.lambda_sig * l_sigreg + self.lambda_con * l_consistency
    
    def sigreg(self, z_batch, M=128):
        """SIGReg: Sketched-Isotropic-Gaussian Regularizer (LeWorldModel).
        
        Using the Cramér-Wold theorem: High-dimensional distribution matching objective iff matches all 1D projections.
        Project the latent vectors into M random directions, performing an Epps-Pulley normality test for each 1D projection.
        """
        # Generate M random projection directions (unit vectors)
        directions = torch.randn(z_batch.size(1), M, device=z_batch.device)
        directions = F.normalize(directions, dim=0)
        
        # Projection: (batch, z_dim) × (z_dim, M) → (batch, M)
        projections = z_batch@directions
        
        # Compute the Epps-Pulley normality test statistic for each projection
        ep_stats = []
        for i in range(M):
            proj_i = projections[:, i]
            # normalize
            proj_i = (proj_i - proj_i.mean()) / (proj_i.std() + 1e-8)
            # Epps-Pulley statistics (simplified version)
            n = proj_i.size(0)
            T = (1/n) * torch.sum(torch.exp(-proj_i**2 / 2)) - torch.sqrt(torch.tensor(2.0))
            ep_stats.append(T)
        
        return torch.stack(ep_stats).mean()
```

### 5.5 Encoder projection head [New in V2.0.1, LeWorldModel key discovery]

```python
class EncoderProjectionHead(nn.Module):
    """
    LeWM Key Finding: Projection Head Between Encoder Output and Z-Space
    Crucial for training stability.
    
    Architecture: 1-layer MLP + BatchNorm (per LeWM ablation)
    Without this projection head → End-to-end training is unstable
    With this projection head → training smooth convergence
    
    Additional benefits: The projection head realizes dimensional adaptation
    Encoder output (e.g. CodeBERT 768-d) → Z-Space (256-d PoC / 2048-d full scale)
    When expanding the Z-Space dimension, only the projection head needs to be retrained, and the encoder does not need to be retrained.
    """
    
    def __init__(self, encoder_dim, z_dim):
        super().__init__()
        self.projection = nn.Sequential(
            nn.Linear(encoder_dim, z_dim),
            nn.BatchNorm1d(z_dim),
        )
    
    def forward(self, encoder_output):
        return self.projection(encoder_output)

# Projection head configuration for each encoder
PROJECTION_CONFIGS = {
    "Z_impl": {"encoder_dim": 768, "z_dim": 256}, # CodeBERT → 256-d
    "Z_quality": {"encoder_dim": 128, "z_dim": 256}, # CI metrics → 256-d
    "Z_phys": {"encoder_dim": 512, "z_dim": 256}, # TimesFM → 256-d
    "Z_arch": {"encoder_dim": 768, "z_dim": 256}, # GraphSAGE+BERT → 256-d
    "Z_logic": {"encoder_dim": 768, "z_dim": 256}, # BERT/RoBERTa → 256-d
}

# Predictor also uses dropout (LeWM: dropout=0.1 is critical for stability)
PREDICTOR_DROPOUT = 0.1
```

### 5.6 Encoder end-to-end fine-tuning strategy [New in V2.0.1]

```
Phase 0A PoC: frozen pre-trained encoder + trainable projection head
  Reason: Quick verification to avoid instability in encoder training
  SIGReg only works on the projection head output (Z-Space)

Phase 0B: Unfreeze encoder, end-to-end fine-tuning
  Rationale: LeWM demonstrates that SIGReg prevents end-to-end training crashes
  Method: Encoder lr = 1e-5 (low), Projection head/predictor lr = 1e-3 (high)
  Monitor: SIGReg loss should decrease quickly and then level off (per LeWM training curve)
  If training is unstable: refreeze the encoder and only train the projection head

Phase 1+: Full end-to-end training or custom encoder training from scratch
  End-to-end fine-tuning effects dependent on Phase 0B
```

### 5.7 Training ensemble

Consistency loss + SIGReg is added during the following training process:
- Encoder pre-training: After encoding, the projection head output is checked by SIGReg regularization + φ(Z) ≈ G
- JEPA Predictor training: predict Z(t+1) and then check SIGReg(Z_batch) + φ(Z(t+1)) ≈ G(t+1)_actual
- LoRA evolution training: Check SIGReg normality without degradation + consistency without degradation after evolution
- Cross-modal alignment: check after alignment that φ R² has not dropped

Weights: λ_sig = 0.1 (initial, optimized by bisection search), λ_con = 0.3.
It is adjustable during Phase 0A PoC and fixed after entering Phase 0B.

---

## 6. H-JEPA hierarchical prediction engine (V2.0 dual prediction)

### 6.1 Essential differences with LLM/Transformer

```text
UEWM H-JEPA vs LLM/Transformer architecture comparison:

Core paradigm differences:
  ├── LLM/Transformer: Autoregressive generation in token space (next-token prediction)
  ├── UEWM H-JEPA: joint embedding prediction in latent space (latent state prediction)
  └── Fundamental difference: UEWM does not generate text/code, but predicts a vector representation of future system states

  Transformer-XL's role in UEWM (non-LLM usage):
  ├── Purpose: only as a temporal attention component within Predictor
  │ No token-level autoregressive generation
  │ No natural language understanding/generation
  │ Only model temporal dependencies on 2048-d Z vector sequences
  ├── Reason for selection:
  │ T-GCN captures the graph structure (causal topology) between Z-Layer
  │ Transformer-XL captures long-distance timing dependencies (segment-level recurrence) of the same Z-Layer
  │ The two are complementary: space (graph) + time (sequence) = space-time prediction
  ├── Evaluation of alternatives:
  │ LSTM: weak long-distance dependencies, and unable to utilize GPU parallelism → rejected
  │ Mamba/S4: State-space model, efficient for long sequences but weak in causal diagram interaction → Phase 2 candidate
  │ Standard Transformer: no segment recurrence, limited context window → rejected
  │ Transformer-XL: segment-level recurrence + relative position encoding → elected
  └── Key constraint: Transformer-XL component does not accept raw text input, only Z vector sequence
      Input: [Z_impl(t-n), ..., Z_impl(t)] (2048-d × n)
      Output: Z_impl(t+1) predicted (2048-d)
      It is essentially different from LLM's [token_1, ..., token_n] → token_n+1

  Relation to JEPA variant published by Yann LeCun:
  ├── I-JEPA (Image JEPA, 2023): Image domain, predicting latent representation of image patches
  │ UEWM reference: joint embedding + predicted latent representation (non-pixel/token)
  │ UEWM differences: multimodal (code + documentation + indicators + market), non-monomodal images
  ├── V-JEPA (Video JEPA, 2024): Video domain, spatiotemporal latent representation prediction
  │ UEWM reference: multi-time scale hierarchical forecasting
  │ UEWM Difference: 8-Layer Heterogeneous Z-Space for Engineering, Non-Video Frame Sequence
  └── UEWM innovations (beyond the published JEPA):
      (1) Granger causality — I/V-JEPA causal reasoning
      (2) EBM energy arbitration + security envelope - I/V-JEPA no decision-making layer
      (3) Surprise-driven self-evolution—I/V-JEPA without online learning
      (4) Multi-tenant Privacy Segregation (KSL) - I/V-JEPA without multi-tenancy
      (5) Long-term memory (Episodic+Semantic) — I/V-JEPA memoryless system
```

### 6.2 JEPA Core (V2.0 Enhanced: Dual Prediction)

Context Encoder → Target Encoder (EMA) → Predictor (T-GCN + Transformer-XL). Predict Z vectors instead of tokens. Micro/meso/macro three-layer calculation.

**V2.0 Enhancement:** Predictor also outputs:
- Z(t+1) prediction: future hidden space state (discovery mode)
- G(t+1) prediction: future observable indicators (verification mode)

```python
class DualPredictorHead(nn.Module):
    """V2.0: JEPA Predictor outputs Z and G predictions simultaneously."""
    
    def __init__(self, z_dim=2048, g_dim=80):
        super().__init__()
        self.z_head = nn.Linear(z_dim, z_dim) # Z(t+1) prediction
        self.g_head = nn.Sequential( # G(t+1) prediction
            nn.Linear(z_dim, 512), nn.ReLU(),
            nn.Linear(512, g_dim))
    
    def forward(self, predictor_output):
        return {
            "z_predicted": self.z_head(predictor_output),
            "g_predicted": self.g_head(predictor_output),
        }
```

### 6.3 POMDP uncertainty modeling

Z^(l) ~ N(μ^(l), Σ^(l)). Low tr(Σ)→Cognition is sufficient, high tr(Σ)→triggers information acquisition.

#### Information acquisition trigger mechanism

```python
class UncertaintyTriggeredActions:
    """Information acquisition strategy when Z-Layer uncertainty (tr(Σ)) exceeds the threshold."""
    
    UNCERTAINTY_THRESHOLDS = {
        # Layer: (moderate_threshold, high_threshold, critical_threshold)
        "Z_impl": (0.5, 1.0, 2.0),
        "Z_quality": (0.5, 1.0, 2.0),
        "Z_phys": (0.3, 0.8, 1.5), # The physical layer is more sensitive to uncertainty
        "Z_arch": (0.8, 1.5, 3.0),
        "Z_logic": (0.6, 1.2, 2.5),
        "Z_biz": (1.0, 2.0, 4.0),
        "Z_val": (1.0, 2.0, 4.0),
        "Z_market": (1.5, 3.0, 5.0), # The market level has the highest uncertainty
    }
```

MODERATE→Agent additional observation (LOA cap=7), HIGH→Request manual + LOA cap=5, CRITICAL→Delay decision + EBM weight temporarily reset to zero + orchestration blocking (LOA cap=3).

Uncertainty dashboard: real-time value of each layer tr(Σ) + threshold line, refreshed in 30s.

### 6.4 Cross-modal alignment training

AlignmentTrainer as a Perception Pipeline submodule. Three stages:

Stage 1 intra-domain comparison (InfoNCE, ARI≥0.3): Z_impl at different time points for the same project should be closer than those for different projects.
Stage 2 adjacent layer alignment (cross-modal comparison + causal prediction, MSE improvement >30%): Z_impl and Z_quality of the same project at the same time point should be closer than random pairing.
Stage 3 Global Union (VICReg regularization, causal graph efficiency >80%): All layers form a unified semantic space.

Each stage has convergence criteria and termination conditions. Only use the training GPU pool (NFR-9). Phase 0 timeline: Week 1-4 Stage 1 (3 layers), Week 5-8 Stage 2 (3 pairs), Week 9+ MVLS verification.
(V2.0 update: Added consistency loss check, requiring that φ R² cannot decrease after alignment)

### 6.5 JEPA Predictor Verification Protocol

```python
class PredictorValidationProtocol:
    """JEPA Predictor prediction accuracy verification solution"""
    
    VALIDATION_SPEC = {
        "validation_set_construction": {
            "method": "Held-out 20% projects (time-based split, not random)",
            "min_projects": 2, # Phase 0: At least 2/10 benchmark projects for verification
            "split_point": "The observations in the last 20% of the time period are used as the validation set",
            "rationale": "Time series data must be split by time, otherwise data will leak",
        },
        "evaluation_metrics": {
            "1_step_mse": {"threshold": 0.15, "layers": ["Z_impl", "Z_quality", "Z_phys"]},
            "3_step_mse": {"threshold": 0.30, "layers": ["Z_impl", "Z_quality", "Z_phys"]},
            "5_step_mse": {"threshold": 0.50, "layers": ["Z_impl", "Z_quality", "Z_phys"]},
        },
        "evaluation_cadence": "After each LoRA evolution + weekly timing",
        "reporting": "The results are written to MLflow metrics and can be viewed on the TRL Progress dashboard",
        "failure_action": "MSE exceeds the standard → TRL Evaluator may downgrade this layer TRL",
    }
```
*(V2.0 update: Add G-Space prediction accuracy as an additional verification dimension)*

---

## 7. Hidden space layered design (Z-Layers)

### 7.1 8-layer Z-Layer definition

8 layers: Z_market(week/month) → Z_val(quarter) → Z_biz(week) → Z_logic(day) → Z_arch(day) → Z_impl(hour) → Z_quality(hour) → Z_phys(minute). Each layer outputs 2048-d vectors.

Dynamic causal topology G=(V,E), Granger causality test (p<0.05) automatically discovers causal edges. Main chain: Z_market→Z_val→Z_biz→Z_logic→Z_arch→Z_impl→Z_quality, Z_impl→Z_phys. Feedback: Z_phys→Z_arch, Z_quality→Z_logic, Z_phys→Z_val, Z_quality→Z_val.

**[V2.0.1] Adaptive latent dimension strategy (LeWorldModel inspiration):**

```
LeWM achieves detection r > 0.99 in 192-d — proving that higher dimensions are unnecessary.

Adaptive latent dimension:
  Phase 0A PoC: 256-d per Z-Layer
    Reason: LeWM 192-d is sufficient for physics domain; engineering domain may require slightly more
    Benefits: Training speed 8×, GPU memory 8×, retrieval speed 8×
    
  Phase 0B: Determine whether to expand based on detection saturation testing
    If probing R² is saturated at 256-d → keep 256-d
    If probing R² is still boosting → expand to 512-d
    
  Phase 1+: Scale on demand (512-d to 2048-d)
    Expansion basis: Dimension-by-dimension probing R² + information theory analysis
    Each expansion needs to demonstrate: Marginal R² improvement in new dimensions > 0.01

  Backward compatibility: the projection head is responsible for dimension adaptation
    The encoder output dimension is fixed (such as CodeBERT 768-d)
    Projection head → Z-Space dim (256/512/1024/2048)
    When expanding, only the projection head is retrained, and the encoder does not need to be retrained.
```

### 7.2 Correspondence between Z-Layer and G-Space (new in V2.0)

| Z-Layer | G-Space Domain | Bridge Direction | Example |
|---------|-----------|---------|------|
| Z_impl | code.* | φ: Z_impl → complexity, churn, loc_delta | Code changes → Complexity changes |
| Z_quality | test.* | φ: Z_quality → pass_rate, coverage, duration | Quality status → Test indicator |
| Z_phys | ops.* | φ: Z_phys → p99_latency, error_rate, cpu | physical status → operating indicators |
| Z_arch | code.coupling, code.cohesion | φ: Z_arch → coupling, dependency_count | architecture status → coupling degree |
| Z_logic | process.* | φ: Z_logic → pr_merge_time, velocity | logic state → process indicator |
| Z_biz/Z_val/Z_market | (Phase 2+) | Requires commercial data sources | Phase 2+ |

### 7.3 TRL Maturity Assessment (V2.0 Enhanced)

```
TRL-0 (concept): The encoder architecture is determined, but there is no training data and the latent space is meaningless
TRL-1 (prototype): Encoder produces vectors, but semantic clustering ARI < 0.3
TRL-2 (validation): Semantic clustering ARI ≥ 0.3, but cross-layer causality not verified
TRL-3 (integrated): One-way causality can be detected (this layer → neighbor layer Granger p<0.05)
TRL-4 (Mature): Bidirectional causal transmission is reliable, predicted MSE < 0.1, and can support Agent decision-making
TRL-5 (self-optimization): Self-evolution closed-loop verification passed, surprise degree converged
```

TRL↔System behavior: Agent autonomy (TRL<3→not autonomous), EBM weight (TRL<3→0.1x), causal backtracking (TRL<3→one-way), evolutionary training (TRL<2→data collection only), manual intervention (TRL<3→must be approved). Evaluation frequency: Daily 02:00 UTC + immediately after evolution + cold start every 6h.

```
TRL Enhanced Assessment (V2.0):
  TRL original criterion (ARI, causality test) unchanged
  New auxiliary indicator: φ R² (Z→G decoding accuracy)
    When TRL < 2: φ R² does not participate in the evaluation (insufficient data)
    When TRL ≥ 2: φ R² ≥ 0.1 is an additional condition (Z-Space must have observable significance)
    When TRL ≥ 4: φ R² ≥ 0.3 is an additional condition (Z-Space high-precision decoding)
```

### 7.4 MVLS Minimum Feasible Hidden Space + G-Space

MVLS: Z_impl + Z_quality + Z_phys + corresponding to G-Space (code.* + test.* + ops.*).
Verification standard: V1.0.1 original standard + φ R² ≥ 0.2 for MVLS three layers.

---

## 8. EBM energy arbitration engine (V2.0 enhancement)

### 8.1 Global energy function

E_total = Σ w_l^eff · Ẽ_l + λ_cross · E_cross + λ_safe · E_safety. w_l^eff = w_l × TRL_weight(l). TRL<3→weight 0 or 0.1.

### 8.1.1 Dimension/risk mapping/sandbox preview/weight automatic tuning

Quantile normalization → [0,1]. LOW[0,0.3)/MEDIUM[0.3,0.5)/HIGH[0.5,0.7)/CRITICAL[0.7,1.0]. Multi-scheme GPU batch parallel simulation to compare trajectory stability. Meta-learning automatically adjusts weights every week/every 100 decisions.

### 8.2 V2.0 Enhancement: Energy + Risk Decomposition

```python
class EnhancedEBMArbiter:
    """V2.0: EBM output energy score (signal found) + risk decomposition (interpretable)."""
    
    def evaluate(self, candidates, context, z_buffer, g_state, memory_ctx):
        results = []
        for candidates in candidates:
            # 1. Latent space evaluation (UEWM original — discovery engine)
            z_trajectory = self.jepa.sandbox_predict(candidate, steps=3)
            energy = self.compute_energy(z_trajectory)
            
            # 2. Observable Prediction (V2.0 — Verification Engine)
            g_predicted = self.phi.decode(z_trajectory[-1])
            
            # 3. Risk decomposition (named components)
            risk = RiskDecomposition(
                test_risk=self.assess("test.coverage_delta", g_predicted, g_state, -2.0),
                perf_risk=self.assess("ops.p99_latency_ms", g_predicted, g_state, 1.2),
                complexity_risk=self.assess("code.complexity_avg", g_predicted, g_state, 1.15),
                cascade_risk=self.estimate_cascade(z_trajectory, context),
            )
            
            # 4. Unnamed risk = the part of energy that G-Space cannot explain
            explained = sum(r.contribution for r in risk.components)
            unnamed_risk = max(0, energy - explained)
            risk.unnamed_risk = unnamed_risk
            # unnamed_risk High → Discovery Engine Follow
            
            # 5. Memory impact (V1.0.1 retained)
            if memory_ctx:
                risk.apply_memory(memory_ctx)
            
            results.append(EvaluationResult(
                candidate_id=candidate.id,
                energy=energy,
                risk=risk,
                unnamed_risk_pct=unnamed_risk / energy if energy > 0 else 0,
                explanation=risk.generate_explanation(),
                memory_influence=memory_ctx,
            ))
        
        results.sort(key=lambda r: r.energy)
        return results
```

### 8.3 EBM Calibration Plan

**Calibration data set:** 200 pairs of paired comparison samples (5 types of decisions × 40-50 pairs each), 3-5 experts blind review, Dawid-Skene aggregation, minimum agreement rate 60%.

**Calibration process:** Step 1(Week 1-3): Build calibration set → Step 2(Week 4): Baseline τ measurement (expected ~0.2-0.3) → Step 3(Week 5-6): Bayesian optimization weights (Optuna+cross-validation) → Step 4(Week 7): Verify τ≥0.5 on 30% held-out → Step 5(Phase 1+): Supplement 50 samples + re-evaluation every quarter.

Calibration data version: DVC management, `datasets/calibration/v{X}/calibration_pairs.parquet`.

---

## 9. Discovery Engine (new in V2.0 core)

### 9.1 Design Goals

Detect events that Z-Space predicts correctly but cannot be explained by G-Space metrics. This is the system's mechanism for "generating new ideas."

### 9.2 Dual-space surprise matrix

```
S_z(t) = ||Z_observed - Z_predicted||² (hidden space surprise)
S_g(t) = ||G_observed - G_predicted||² (observable surprise)

Interpretation matrix:
┌───────────────────────────────────────────────────────────┐
│ S_z HIGH + S_g HIGH → Real surprise (the world has changed) │
│ Action: Create INCIDENT Episode, trigger evolution │
│ │
│ S_z HIGH + S_g LOW → Z-Space noise (implicit space drift) │
│ Action: Marker encoder needs to be retrained, evolution will not be triggered │
│ │
│ S_z LOW + S_g HIGH → Ground notch (needs new indicator) │
│ Action: Discovery Engine steps in — Z is correct but G is incomplete │
│ │
│ S_z LOW + S_g LOW → Normal (accurate prediction) │
│ Action: None, recorded as successful prediction │
└───────────────────────────────────────────────────────────┘
```

### 9.3 Discovery Engine Implementation

```python
class DiscoveryEngine:
    """Detecting Z-Space found patterns that G-Space could not explain."""
    
    def analyze(self, z_pred, g_pred, g_actual, energy):
        z_correct = self.was_z_correct(z_pred, g_actual) # via φ
        g_correct = self.was_g_correct(g_pred, g_actual)
        
        if z_correct and not g_correct:
            return self.handle_discovery(z_pred, g_actual, energy)
        elif not z_correct and g_correct:
            return self.handle_z_noise(z_pred, g_actual)
        elif not z_correct and not g_correct:
            return self.handle_blind_spot(z_pred, g_pred, g_actual)
        return DiscoveryResult.NORMAL
    
    def handle_discovery(self, z_pred, g_actual, energy):
        """The most exciting scenario: the Z prediction is correct but the G metric cannot explain it."""
        episode = Episode(
            trigger_type="DISCOVERY", z_snapshot=z_pred,
            g_snapshot=g_actual, importance_score=1.0)
        self.memory.store_episode(episode)
        
        # Attribution: Which Z dimensions contribute the most?
        attribution = self.attribute_z_to_outcome(z_pred, g_actual)
        
        # Find similar findings
        similar = self.memory.recall(z_snapshot=z_pred,
                                     filter={"trigger_type": "DISCOVERY"}, max=20)
        
        if len(similar) >= 3:
            pattern = self.extract_pattern(similar, attribution.top_k(10))
            proposed_metric = ProposedGSpaceMetric(
                name=pattern.suggested_name,
                formula=pattern.formula,
                data_source=pattern.data_sources,
                expected_correlate=pattern.predicted_outcome,
                confidence=pattern.confidence,
                requires_human_review=True)
            return DiscoveryResult("NEW_PATTERN", proposed_metric=proposed_metric)
        
        return DiscoveryResult("POTENTIAL_DISCOVERY", evidence_count=len(similar))
```

### 9.4 G-Space Dynamic Growth

```
Day 1: G-Space ≈ 80 manually defined indicators
Month 3: Discovery Engine proposed 5 new indicators, 2 were approved by manual review
Month 6: G-Space ≈ 90 indicators (10 discovered by the model)
Year 1: G-Space ≈ 120 indicators (40 discovered by the model)
Year 3: G-Space ≈ 200+ indicators, many that humans have never thought of measuring

Closed loop: Z-Space discovery → Discovery Engine identification → Semantic Memory storage →
      Manual review and approval → G-Space new indicators → Future G-Space prediction improvements →
      Z-Space released to discover the next unnamed pattern
```

---

## 10. Long-term memory subsystem (V2.0 dual index enhancement)

### 10.1 Four-layer memory model

```text
Layer 0: Procedural Memory — LoRA weights
  Storage: Implicit skills and decision-making patterns encoded through incremental training with LoRA
  Format: LoRA weight matrix (ΔW = BA, rank r)
  Mechanism: Self-evolution engine drives LoRA updates through surprise/drift/feedback
  Relationship to other layers:
    ├── Receive Layer 2 (Episodic) experience as training data
    ├── Accept Layer 3 (Semantic) ANTI_PATTERN Fact as a targeted training target
    ├── Output: Improve prediction accuracy of Layer 1 (Working) (reduce surprise)
    └── Versioning: MLflow management, rollback, associated with Z-Buffer snapshots
  Capacity: Independent LoRA per project (rank 8-64), approximately 2-16 MB/layer/project
  Index: MLflow run_id + layer_name + project_id
  Purpose: "The system has learned that when Z_impl changes beyond 0.5, Z_quality usually decreases within 24h"

Layer 1: Working Memory — Z-Buffer
  Stores the current Z-Layer vector, overwritten with each observation

Layer 2: Episodic Memory
  Storage: specific events (decision/accident/evolution/human intervention) and their Z-Layer snapshots and results
  Format: Episode = {trigger, Z-snapshot, decision, result, energy, surprise, timestamp, project}
  Capacity: 1K(Phase 0) → 5K(Phase 1) → 10K(Phase 2+) per project
  Index: time + Z vector similarity (pgvector ANN) + causal label + result label
  Purpose: "The last time a Z_impl-like pattern occurred, deployment caused a P99 spike"

Layer 3: Semantic Memory
  Storage: Stable facts (causality/patterns/anti-patterns/preferences) extracted from multiple episodes
  Format: Fact = {Topic, Relationship, Object, Confidence, Validity, SourceEpisode}
  Capacity: ~200(Phase 0) → ~1000(Phase 2+) per item
  Index: Neo4j Knowledge Graph (Entity-Relation-Entity)
  Purpose: "Increased code complexity on this project typically results in decreased test coverage within 72h"

Four layers of memory interactive closed loop:
  Observation → Layer 1 (Z-Buffer update) → Surprise calculation
  Surprise > θ → Layer 2 (Create Episode)
  ≥3 consistent Episode → Layer 3 (extract Fact)
  ANTI_PATTERN Fact → Layer 0 (Directed LoRA training)
  LoRA update → Layer 1 (prediction accuracy improved, surprise decreased)
  → Closed loop completed
```

### 10.2 V2.0 Episode Enhancement: Dual Index

```python
class EnhancedEpisode(Episode):
    """V2.0: Episode contains both Z-snapshot and G-snapshot."""
    
    # V1.0.1 reserved fields
    z_snapshot: Dict[str, bytes]
    trigger_type: str # DECISION/INCIDENT/EVOLUTION/HUMAN_INTERVENTION/REFLECTION
    
    # V2.0 new fields
    g_snapshot: Dict[str, float] # G-Space measurement value at decision time
    g_predicted: Dict[str, float] # G-Space predicted by the model (post-fill)
    g_actual: Dict[str, float] #actual G-Space (post-fill)
    prediction_accuracy: float # ||g_predicted - g_actual|| (post hoc calculation)
    was_discovery: bool # Discovery Engine whether to mark
    discovery_pattern_id: Optional[str] # Associated extracted pattern
    surprise_category: str # REAL/Z_NOISE/GROUNDING_GAP/NORMAL
```

### 10.3 Memory retrieval (V2.0 enhancement: 5 retrieval modes)

(4 types in V1.0.1 + added 5th type)

1. Z-Layer vector similarity (pgvector ANN)
2. Cause-and-effect graph traversal (Neo4j 2 hops)
3. Text semantic retrieval
4. Project Profile injection
5. **G-Space Conditional Search (V2.0):** "What happened the last time test.coverage_delta < -5%?"

### 10.4-10.8 Other memory subsections

#### Episode data structure

```python
class Episode:
    episode_id: str; project_id: str; tenant_id: str; timestamp: datetime
    trigger_type: str # DECISION / INCIDENT / EVOLUTION / HUMAN_INTERVENTION / REFLECTION
    z_snapshot: Dict[str, bytes] # Z-Buffer slice frozen at decision time
    decision_summary: str; decision_energy: float; outcome: str; outcome_energy: float
    surprise_score: float; was_human_overridden: bool; human_feedback: Optional[str]
    importance_score: float # [0,1] Multi-factor weighting
    decay_factor: float # Ebbinghaus decay [0,1]
    recall_count: int; last_recalled: datetime
    extracted_fact_ids: List[str]
    ksl_level: int # Inherit project KSL
```

#### Episode trigger rules

EVALUATE completed→create DECISION Episode, surprise exceeds threshold→INCIDENT Episode, LoRA evolution completed→EVOLUTION Episode (importance=1.0), manual intervention→HUMAN_INTERVENTION Episode, self-reflection exception→REFLECTION Episode.

#### Importance Rating

```python
importance = (surprise × 0.25) + (energy_delta × 0.20) + (human_override × 0.20)
           + (failure_value × 0.15) + (risk_level × 0.10) + (recall_boost × 0.10)
```

#### Ebbinghaus decay

decay = exp(-0.1 × days_since) × exp(-0.05 × days_since_recall) × (0.5 + 0.5 × importance). Episodes with importance > 0.8 are never archived (milestone events).

### 12.4 Semantic memory

#### Fact data structure

```python
class Fact:
    fact_id: str; project_id: str; tenant_id: str
    subject: str; relation: str; object: str # Knowledge triple
    confidence: float; valid_from: datetime; valid_until: Optional[datetime]
    is_invalidated: bool; invalidated_by: Optional[str]
    source_episode_ids: List[str]; min_episodes_required: int = 3
    fact_type: str # CAUSAL / CORRELATION / PREFERENCE / PATTERN / ANTI_PATTERN / TEMPORAL
    ksl_level: int
```

#### Fact extraction rules

3+ Consistent Episode Same Z-Layer change direction → Same result → CAUSAL Fact. 3+ Similar Z Snapshot → FAILURE → ANTI_PATTERN Fact. 3+ Manual overwriting of similar decisions → PREFERENCE Fact. 4+ Periodic Repeat → TEMPORAL Fact.

#### Conflict handling

When extracting new Facts, scan existing Facts with semantic similarity >0.8. When there is a contradiction: time priority (new overturns old) + frequency weighting (more support for Episode wins). Old Fact flag is_invalidated=true. When the confidence level is close (difference <0.1), upgrade to manual confirmation.

### 12.5 Memory Consolidation Engine

Runs daily at 03:00 UTC (synchronized with self-reflection). Stage 1(5min): Episode decay cleaning→archive cold storage. Stage 2 (10min): New Episode fact extraction → contradiction detection → confirmation writing. Stage 3(5min): Fact confidence has been updated (new support ↑, long-term no support ↓). Stage 4(2min): Project Profile generation.

Consolidation drives evolution: ANTI_PATTERN Fact → Inject evolution engine directed training. Conflict resolution → trigger LoRA fine-tuning. Evolution outputs consolidation material: Evolution Episode(importance=1.0) → Extract evolution effectiveness Fact.

### 12.6 Project Profile

```python
classProjectProfile:
    """Automatically generated from semantic memory, queryable in ~50ms, injected into every EBM/JEPA decision."""
    
    static_facts: List[str] # Stable features (changes slowly)
    # "Python/Go dual language, microservices, 12 services", "Test coverage is stable 78-82%"
    
    dynamic_context: List[str] # Recent activities (frequently updated)
    # "The payment service is being reconstructed (Z_impl changes frequently)", "The last deployment caused a spike in P99 and has been rolled back"
    
    risk_memories: List[str] # Extracted from FAILURE Episodes
    # "Large-scale DB migrations have historically resulted in downtime 2/3 times"
```

Profile injection: PREDICT→affects uncertainty estimation (risk→increase Σ), EVALUATE→affects energy weight (PREFERENCE→-5%, ANTI_PATTERN→+20%), ORCHESTRATE→affects task ordering (dynamic_context→priority). Cache Redis TTL=30s.

### 12.7 Memory retrieval engine

Four retrieval modes: (1) Z-Layer vector similarity (current state vs past episode snapshot, pgvector ANN), (2) causal graph traversal (changed_layers → 2-hop causal chain, Neo4j), (3) text semantic retrieval (natural language query), (4) Project Profile injection (always). Retrieval SLO: P99 < 200ms. Exposed via the EIP RECALL verb.

### 12.8 KSL Perceptual Memory Isolation

KSL-0: Episode/Fact completely isolated, cross-project retrieval returns zero, forgetting 100%. KSL-1: Shareable aggregate statistical level Fact (DP ε≤0.5). KSL-2: Desensitization Pattern/AntiPattern (reviewed). KSL-3: Federation + Desensitization Fact + Aggregation Episode Statistics. KSL-4: Fully shared memory with Tenant.

### 12.9 Storage architecture

Episode: Hot (30 days, PostgreSQL+pgvector, ~25MB/day Profile-M) → Warm (30-180 days, PG metadata + S3 snapshot, <5s) → Cold (180 days+, S3 archive, <5min). Semantic: Neo4j knowledge graph. Profile: Redis cache (TTL=30s).

---

## 11. Self-reflective engine (V2.0: 6 dimensions)

### 11.1 Six-dimensional self-reflection

| Dimensions | Sources | Health Standards |
|------|------|---------|
| 1. Prediction consistency | Z-Space | 1-step MSE < 0.15, 3-step MSE < 0.3 |
| 2. Causal Graph Health | Causal Graph | Effective Margin Rate > 80% |
| 3. Cross-layer alignment | AlignmentTrainer | ARI > 0.3 |
| 4. Decision diversity | EBM | Shannon entropy ≥ 0.6 |
| 5. Blind area detection | POMDP | High Σ area proportion < 20% |
| **6. Ground Health (V2.0)** | **Bridging** | **See below** |

### 11.2 Grounding Health — New in V2.0

```
Ground health sub-indicators:
  φ Accuracy: Z→G decoding R² (Target: mean > 0.3 across G-Space dimensions)
  ψ Consistency: G→Z constrained cosine similarity (target: > 0.5)
  Discovery rate: Z correct + G unexplained (Health: 5-15%)
    Too low (<2%): Z-Space may be redundant (not necessarily bad)
    Too high (>30%): Z-Space may drift, increase ψ weight
  G-Space coverage: indicator collection success rate (Target: > 95%)
  Dimension-wise health: Z dimension with R² < 0.05 → Mark as needing pruning or retraining
```

---

## 12. GPU optimization strategy

### 13.1 Design Goals

Maximize training efficiency and inference throughput under limited GPU resources, and reduce GPU memory usage and computing time through mixed precision, gradient checkpointing, model quantization, operator fusion, and intelligent scheduling.

### 13.2 Mixed precision training strategy

```python
class MixedPrecisionPolicy:
    """
    Global mixed precision strategy: training BF16, inference FP16/INT8, gradient accumulation FP32.
    Goal: Reduce training memory by ~40% and reduce inference latency by ~30%.
    """
    
    TRAINING_PRECISION = {
        "forward_pass": "bfloat16", # BF16: Large dynamic range, not easy to overflow
        "backward_pass": "bfloat16",
        "gradient_accumulation": "float32", # Gradient is accumulated under FP32 (to prevent accuracy loss)
        "optimizer_states": "float32", # Adam state remains FP32
        "loss_scaling": "dynamic", # PyTorch GradScaler (optional in BF16 mode)
    }
    
    INFERENCE_PRECISION = {
        "brain_core_jepa": "float16", # JEPA Predictor reasoning
        "brain_core_ebm": "float16", # EBM energy calculation
        "encoder_forward": "float16", # Encoder forward inference
        "memory_retrieval": "float32", # pgvector retrieval maintains FP32 precision
    }
    
    QUANTIZATION_PIPELINE = {
        "phase_0": "FP16 inference (baseline)",
        "phase_1": "INT8 dynamic quantization (torch.quantization.quantize_dynamic)",
        "phase_2": "INT8 static quantization (calibration data set 1000 samples)",
        "phase_3": "INT4 GPTQ/AWQ (native model within LLM adapter only)",
    }
```

### 13.3 Gradient Checkpointing

```python
classGradientCheckpointConfig:
    """
    Enable gradient checkpointing for large components: trade compute for video memory.
    Expected effect: video memory reduced by 60-70%, training time increased by ~20%.
    """
    
    CHECKPOINT_TARGETS = {
        "jepa_predictor": {
            "enabled": True,
            "strategy": "every_2_layers", # Checkpoint every 2 Transformer-XL layers
            "memory_saving": "~65%",
            "compute_overhead": "~20%",
        },
        "context_encoder": {
            "enabled": True,
            "strategy": "every_3_layers", # The encoder is shallower, every 3 layers
            "memory_saving": "~50%",
            "compute_overhead": "~15%",
        },
        "alignment_trainer": {
            "enabled": True,
            "strategy": "full_recompute", # Alignment training batch size is large, full batch recalculation
            "memory_saving": "~70%",
            "compute_overhead": "~25%",
        },
        "evolution_lora": {
            "enabled": False, # LoRA has few parameters and is not needed
            "reason": "LoRA rank 8-64, parameter size < 1M, memory usage can be ignored",
        },
    }
    
    # PyTorch implementation
    IMPLEMENTATION = """
    from torch.utils.checkpoint import checkpoint_sequential
    
    class CheckpointedJEPAPredictor(nn.Module):
        def forward(self, z_sequence):
            #Group Transformer-XL layers and do checkpoints for each group
            segments = [self.layers[i:i+2] for i in range(0, len(self.layers), 2)]
            x = z_sequence
            for segment in segments:
                x = checkpoint_sequential(segment, 1, x, use_reentrant=False)
            return x
    """
```

### 13.4 DeepSpeed ZeRO Configuration

```json
{
  "description": "DeepSpeed ZeRO Configuration — Select ZeRO Stage by Training Stage",
  "phase_0_mvls_training": {
    "stage": 1,
    "rationale": "Phase 0 single GPU training is mainly used, ZeRO-1 can split the optimizer state",
    "config": {
      "zero_optimization": {
        "stage": 1,
        "allgather_partitions": true,
        "reduce_scatter": true,
        "overlap_comm": true
      },
      "bf16": { "enabled": true },
      "gradient_clipping": 1.0
    }
  },
  "phase_1_alignment_training": {
    "stage": 2,
    "rationale": "Cross-modal alignment requires a larger batch, ZeRO-2 additional segmentation gradient",
    "config": {
      "zero_optimization": {
        "stage": 2,
        "contiguous_gradients": true,
        "overlap_comm": true,
        "reduce_bucket_size": 50000000
      },
      "bf16": { "enabled": true },
      "gradient_accumulation_steps": 4
    }
  },
  "phase_2_full_training": {
    "stage": 3,
    "rationale": "Full 8-layer joint training, ZeRO-3 segmentation model parameters",
    "config": {
      "zero_optimization": {
        "stage": 3,
        "offload_param": { "device": "cpu", "pin_memory": true },
        "offload_optimizer": { "device": "cpu", "pin_memory": true },
        "overlap_comm": true,
        "sub_group_size": 1000000000
      },
      "bf16": { "enabled": true },
      "gradient_accumulation_steps": 8
    }
  }
}
```

### 13.5 Inference Optimization (TensorRT / vLLM)

```
Inference optimization pipeline:

  JEPA Predictor inference optimization:
  ├── TensorRT conversion: torch.export → ONNX → TensorRT engine
  │ Optimization: Operator fusion (LayerNorm+Linear, Attention+Softmax)
  │ Dynamic batch size (1-32)
  │ FP16 accuracy
  │ Expectation: Inference latency reduced by 40-60%, throughput increased by 2-3x
  ├── CUDA Graph: Enable CUDA Graph capture for fixed shape inference paths
  │ Applicable to: PREDICT request (fixed 8 layers × 2048-d input)
  │ Expectation: 10-20% reduction in inference latency (reduce kernel launch overhead)
  └── Flash Attention v2: Replaces standard attention
      Applicable to: Transformer-XL self-attention layer
      Expected: memory O(N²) → O(N), speed increase 2-4x

  EBM sandbox preview optimization:
  ├── Batch preview: multiple candidate solutions GPU batch parallel (existing, ENG §2.3)
  ├── Early stop: If the energy of a candidate has exceeded the current optimal 2x, terminate the trajectory early
  └── Cache: Preview result cache in the same Z-Buffer state for 30s

LLM local model inference optimization (Agent execution engine):
  ├── vLLM deployment: PagedAttention + continuous batching
  │ Configuration: max_model_len=4096, gpu_memory_utilization=0.85
  │ Applicable: CodeLlama-7B local downgrade model
  ├── Quantization: GPTQ 4-bit (local LLM only, not JEPA)
  └── Dynamic batch processing: merge LLM requests from multiple agents
```

### 13.6 GPU memory budget (Per-Component)

| Components | Profile-S (2×A100 80GB) | Profile-M (4×A100) | Phase | Remarks |
|------|------------------------|---------------------|-------|------|
| JEPA Predictor (FP16) | 8 GB | 8 GB | 0 | Fixed, does not grow with the number of projects |
| 8× Encoders (FP16) | 12 GB | 12 GB | 0-2 | Phase 0 3 encoders only ~5GB |
| EBM Arbiter | 2 GB | 2 GB | 0 | Lightweight MLP |
| Z-Buffer (Active Project) | 2 GB | 10 GB | 0-2 | ~200MB/project |
| AlignmentTrainer (while training) | 16 GB | 16 GB | 0 | Training GPU pool only, after gradient checkpoint |
| LoRA Evolution (while training) | 4 GB | 4 GB | 0 | rank 8-64, very lightweight |
| CodeLlama-7B (INT4, optional) | 4 GB | 4 GB | 1+ | Local LLM downgrade |
| Memory Retrieval (pgvector) | 1 GB | 2 GB | 0 | Vector Index Cache |
| **Total Inference GPU** | **~25 GB/GPU** | **~25 GB/GPU** | | **Leave 55 GB headroom** |
| **Total Training GPU** | **~36 GB/GPU** | **~36 GB/GPU** | | **Leave 44 GB headroom** |

### 13.7 GPU utilization monitoring and benchmarking

```
GPU Profiling Methodology:

  Tools: nvidia-smi + PyTorch Profiler + Nsight Systems

  Key indicators:
    gpu_utilization_pct target: inference > 60%, training > 80%
    gpu_memory_used_bytes target: < 85% peak (leave headroom)
    gpu_memory_high_water_mark records the maximum video memory per component
    sm_efficiency_pct Streaming Multiprocessor efficiency
    tensor_core_utilization_pct Tensor Core utilization (when BF16/FP16)

  Benchmark plan:
    Phase 0 Week 2: Single encoder GPU profiling (memory + latency)
    Phase 0 Week 6: MVLS three-encoder joint profiling
    Phase 0 Week 10: JEPA Predictor + EBM inference profiling
    Phase 1 Month 1: Comparison before and after TensorRT conversion
    Quarterly: Full-system GPU benchmark regression testing

  Prometheus Exporter:
    uewm_gpu_memory_used_bytes{component, device}
    uewm_gpu_utilization_pct{device}
    uewm_inference_throughput_rps{component}
    uewm_training_throughput_samples_per_sec{component}

  Alert rules:
    GPU memory > 85%: warning → trigger garbage collection
    GPU memory > 95%: critical → Pause training, keep only inference
    GPU utilization < 20% for 30min: warning → waste of resources
```

### 13.8 Cross-platform GPU optimization (Mac M-series / RTX 3060 / A100)

```
Development environment GPU strategy (benchmarked UEWM-PREP-015):

  Mac M5 Max (main development machine):
    Backend: MPS (Metal Performance Shaders)
    Accuracy: FP32 (MPS has limited support for BF16)
    Purpose: Function development + unit testing + small batch verification
    Limitations: No CUDA, No TensorRT, No DeepSpeed
    Strategy: get_device() abstraction layer automatically selects MPS

  RTX 3060 (CUDA validator, 12GB VRAM):
    Precision: FP16 (no BF16 native support)
    Purpose: CUDA function verification + small-scale training verification
    Limitation: 12GB VRAM, strict memory budget required
    Strategy:
      Gradient checkpoints: force all enabled
      batch size: automatically scaled down to RTX 3060 adaptation
      LoRA rank: limit ≤ 16

  Cloud A100 (training/CI):
    Accuracy: BF16 training + FP16 inference
    Purpose: Full training + alignment + load testing
    Strategy: DeepSpeed ZeRO + Flash Attention + TensorRT

  get_device() enhancement:
    In addition to device selection, return device capabilities (DeviceCapabilities):
      max_vram, supports_bf16, supports_flash_attention,
      supports_tensorrt, recommended_batch_size, precision_policy
```

---

## 13. Third-party Agent adaptation layer architecture

### 14.1 Design Goals

Allows third-party developers to build custom Agents and access the world model capabilities of UEWM Brain Core while ensuring safe isolation and resource fairness.

### 14.2 Adaptation layer architecture

```
Third-party Agent access architecture:

┌─────────────────────────────────────────────────────┐
  │Third-party Agents │
  │ Custom Agent A │ Custom Agent B │ Custom Agent C │
  │ (Python SDK) (REST Adapter) (gRPC native) │
  └───────────┬──────────┬─────────────┬─────────────────┘
              │ │ │
  ┌────────────▼───────────▼──────────────▼─────────────────┐
  │Third-party Adaptation Layer │
  │ ┌────────────────────────────────────────────────┐ │
  │ │ REST↔gRPC Gateway (protocol conversion) │ │
  │ │ Agent Registry (Registration/Discovery/Health Check) │ │
  │ │ Capability Negotiator │ │
  │ │ Sandbox Enforcer (resource isolation/quota) │ │
  │ │ Schema Validator (load verification) │ │
  │ └─────────────────────────────────────────────────┘ │
  └──────────────────────┬──────────────────────────────────────────────────────────────────────────────────
                          │
  ┌───────────────────────▼───────────────────────────────┐
  │ EIP Gateway (RBAC / mTLS) │
  │ (Existing, add THIRD_PARTY role) │
  └──────────────────────┬──────────────────────────────────────────────────────────────────────────────────
                          │
  ┌───────────────────────▼───────────────────────────────┐
  │ Brain Core │
  └──────────────────────────────────────────────────────┘
```

### 14.3 Agent Registration Agreement

```python
classAgentRegistration:
    """The protocol for third-party Agent to register to the UEWM system."""
    
    class RegistrationRequest:
        agent_type: str # Custom type name (e.g., "custom-nlp-reviewer")
        agent_version: str # Semantic version number
        supported_verbs: List[str] # Supported EIP verbs ["PREDICT", "EVALUATE", "RECALL"]
        z_layer_read: List[str] # Z-Layer to be read ["Z_impl", "Z_quality"]
        z_layer_write: List[str] # Z-Layer to be written (via REPORT_STATUS)
        ring_classification: str # "inner" / "middle" / "outer" (self-declaration, system verification)
        required_loa_range: Tuple[int, int] # Desired LOA range (e.g., (3, 6))
        health_check_endpoint: str # Health check URL
        metadata: Dict[str, str] # Description, contact person, document link
    
    class RegistrationResponse:
        agent_id: str # Unique ID assigned by the system: "EXT-{type}-{uuid}"
        api_key: str # API Key generated by Vault (used for mTLS certificate application)
        granted_verbs: List[str] # Actual granted verbs (may be less than requested)
        granted_z_layers: List[str] #actually authorized Z-Layer
        assigned_loa: int # Initial LOA (usually = required_loa_range[0])
        resource_quota: ResourceQuota # allocated resource quota
        sdk_config: SDKConfig # Recommended timeout/retry/circuit breaker configuration
    
    #Registration life cycle
    LIFECYCLE = """
      PENDING → (Approved) → REGISTERED → (Health check OK) → ACTIVE
      ACTIVE → (consecutive health check failures) → SUSPENDED → (recovery) → ACTIVE
      ACTIVE → (manual logout/violation) → DEREGISTERED
      
      Audit requirements:
        inner ring third-party Agent: SECURITY + ARCHITECT double review
        middle ring: ARCHITECT review
        outer ring: automatic review (Schema verification is required)
    """
```

### 14.4 Capability Negotiation

```python
class CapabilityNegotiation:
    """
    The third-party Agent declares capabilities, and the system determines the authorization scope based on the capabilities.
    """
    
    classAgentCapability:
        # EIP Verb Capabilities
        can_predict: bool = False # Requires Z-Layer read permission
        can_evaluate: bool = False #Requires EBM calling permission
        can_report_status: bool = True # All Agents must support
        can_submit_artifact: bool = False
        can_recall: bool = False # Long Memory read permission is required
        can_orchestrate: bool = False # Generally do not authorize third parties
        
        # Z-Layer capabilities
        encoders_provided: List[str] = [] # Comes with its own encoder (extended Z-Space)
        custom_z_layers: List[str] = [] # Custom Z-Layer (Phase 3+)
    
    # Capability→Permission Mapping
    CAPABILITY_TO_PERMISSION = {
        "can_predict": ["READ:Z-Buffer:{granted_layers}"],
        "can_evaluate": ["READ:Z-Buffer:*", "INVOKE:EBM:evaluate"],
        "can_report_status": ["WRITE:Z-Buffer:{granted_layers}"],
        "can_submit_artifact": ["WRITE:Artifact:own"],
        "can_recall": ["READ:Memory:{project_scope}"],
    }
    
    # Custom Z-Layer extension (Phase 3+)
    CUSTOM_Z_LAYER_SPEC = """
      Third-party Agent can register custom Z-Layer:
        Conditions: Provide a compatible Encoder (outputs 2048-d vectors)
        Registration: declare z_layer_name, encoder_type, pre-training base
        Validation: VectorQualityValidator passes (L2 norm, NaN, variance)
        Integration: Automatically included in Z-Buffer, but TRL is initially 0
        Limitations: Do not participate in core causal diagrams (until TRL ≥ 2)
    """
```

### 14.5 REST↔gRPC Gateway

```
REST adaptation layer (lower third-party access threshold):

  POST /api/v1/ext/predict → converted to EipRequest(verb=PREDICT)
  POST /api/v1/ext/evaluate → converted to EipRequest(verb=EVALUATE)
  POST /api/v1/ext/report → converted to EipRequest(verb=REPORT_STATUS)
  POST /api/v1/ext/artifact → converted to EipRequest(verb=SUBMIT_ARTIFACT)
  POST /api/v1/ext/recall → converted to EipRequest(verb=RECALL)
  GET /api/v1/ext/health → Agent health status
  GET /api/v1/ext/schema → Get supported Protobuf Schema (JSON Schema format)
  
  Certification: Bearer Token (Issued by Vault, rotated every 24h)
  Current limit: read 50/min, write 10/min (third-party default, upgradeable)
  Format: JSON request body, automatically converted to Protobuf
  Version: URL path version (/api/v1/, /api/v2/)
  Documentation: OpenAPI 3.0 automatically generated
```

### 14.6 Third-party Agent resource isolation

```python
classThirdPartyResourceQuota:
    """Third-party Agent resource quota (independent of built-in Agent)."""
    
    QUOTA_TIERS = {
        "free": {
            "max_concurrent_requests": 5,
            "max_requests_per_minute": 30,
            "max_z_buffer_read_layers": 3,
            "max_z_buffer_write_layers": 1,
            "memory_recall_enabled": False,
            "evolution_participation": False,
            "max_artifact_size_mb": 10,
        },
        "standard": {
            "max_concurrent_requests": 20,
            "max_requests_per_minute": 120,
            "max_z_buffer_read_layers": 5,
            "max_z_buffer_write_layers": 2,
            "memory_recall_enabled": True,
            "evolution_participation": False,
            "max_artifact_size_mb": 100,
        },
        "premium": {
            "max_concurrent_requests": 50,
            "max_requests_per_minute": 300,
            "max_z_buffer_read_layers": 8, # all
            "max_z_buffer_write_layers": 4,
            "memory_recall_enabled": True,
            "evolution_participation": True, # Can contribute training data
            "max_artifact_size_mb": 500,
        },
    }
    
    # Resource isolation mechanism
    ISOLATION = """
      Network: Standalone K8s namespace (uewm-ext-agents)
      CPU/Memory: ResourceQuota per Agent registration
      GPU: No direct access to GPU (indirectly used through Brain Core API)
      Storage: independent PV, not shared with built-in Agent
      Kafka: independent consumer group, independent topic prefix (uewm.ext.*)
    """
```

### 14.7 Agent Development Standards and Compliance

```
Third-party Agent Development Standard (ADS):

  ADS-1 Protocol Compliance:
    □ Implement EipService gRPC interface (or use REST gateway)
    □ All requests carry valid agent_id + api_key
    □ Support REPORT_STATUS heartbeat (≤ 60s interval)
    □ Correctly handle EipStatus error codes (retry/fuse)

  ADS-2 Safety Compliance:
    □ No hardcoding credentials (use Vault SDK or environment variables)
    □ No attempt to access Z-Buffer directly (via EIP only)
    □ Do not attempt cross-tenant requests
    □ Follow assigned LOA behavioral boundaries
    □ Do not output the original value of the Z-Layer vector in the log

  ADS-3 Quality Compliance:
    □ Provide health check endpoint (HTTP 200 / gRPC HealthCheck)
    □ The submitted artifact contains the version number and checksum
    □ The reported status data complies with the Z-Layer encoding specification (2048-d, L2∈[0.5,2.0])
    □ The response timeout does not exceed the SLO declared during registration

ADS-4 文档合规:
    □ Provide README describing Agent functions and applicable scenarios
    □ Provide Z-Layer mapping instructions (which layers to read/write, meaning)
    □ Provide description of fault degradation behavior

  合规验证工具:
    uewm-agent-lint: statically checks code compliance (ADS-2)
    uewm-agent-test: Integration test suite (ADS-1, ADS-3)
    uewm-agent-certify: Certification process (all ADS)
```

### 14.8 Python SDK

```python
# uewm-agent-sdk (PyPI package)
from uewm_sdk import UEWMAgent, ZLayerData

class MyCustomAgent(UEWMAgent):
    """Third-party Agent development example."""
    
    def __init__(self):
        super().__init__(
            agent_type="custom-code-reviewer",
            supported_verbs=["PREDICT", "EVALUATE", "REPORT_STATUS", "RECALL"],
            z_layers_read=["Z_impl", "Z_quality"],
            z_layers_write=["Z_quality"],
        )
    
    async def on_directive(self, directive):
        """Receive Brain Core orchestration instructions."""
        if directive.action == "REVIEW_CODE":
            result = await self.do_code_review(directive.context)
            # Report the results to Z_quality
            await self.report_status(
                layer="Z_quality",
                data=ZLayerData.from_metrics(result.quality_scores)
            )
    
    async def do_code_review(self, context):
        # 先检索历史经验
        memories = await self.recall(
            changed_layers=["Z_impl"],
            max_episodes=5
        )
        # Request Brain Core predictions
        prediction = await self.predict(
            target_layers=["Z_quality"],
            steps=1
        )
        # Custom business logic...
        return ReviewResult(...)

# SDK 内置功能:
# - mTLS certificate automatic application and rotation
# - EIP message serialization/deserialization
# - 心跳自动上报
# - Fuse (Hystrix-style)
# - Retry (exponential backoff)
# - Indicator reporting (Prometheus exporter)
# - Log specification (structured JSON)
```

V2.0 enhancement: Third-party Agents can access the G-Space query API (read-only) through the REST gateway to obtain interpretable project indicators.

---

## 14. Independent Brain Core API

### 15.1 设计目标

Brain Core can run as a standalone "World Model as a Service" (WMaaS) without deploying any Agent, querying Z-Layer status, predictions and evaluations directly through the API.

### 15.2 Standalone API endpoints

```
Brain Core Standalone API (no Agent required):

POST /api/v1/brain/ingest
    Description: Inject observation data directly into Z-Buffer (replaces Agent REPORT_STATUS)
    Input: { "layer": "Z_impl", "data": <base64 encoded 2048-d vector>,
            "project_id": "...", "source": "external" }
    Purpose: Users can code their own data and directly inject it into the world model.

  POST /api/v1/brain/predict
    Description: Request JEPA predictions directly (replaces Agent PREDICT)
    Input: { "target_layers": ["Z_quality"], "steps": 3 }
    Output: { "predictions": [...], "confidence": 0.85 }

  POST /api/v1/brain/evaluate
    Description: Request EBM evaluation directly (replaces Agent EVALUATE)
    Input: { "candidates": [...], "context": "..." }
    Output: { "scores": [...], "recommended_index": 1 }

  GET /api/v1/brain/z-buffer/{project_id}
    Description: Read the current Z-Buffer status
    Output: { "layers": { "Z_impl": { "trl": 3, "energy": 0.15 }, ... } }

  GET /api/v1/brain/causal-graph/{project_id}
    Description: Query the cause and effect diagram
    Output: { "edges": [{"from": "Z_impl", "to": "Z_quality", "strength": 0.72}] }

  [New in V2.0.1] GET /api/v1/brain/g-space-query
    Description: Decode Z vector into G space observation prediction through Discovery Engine
    Output: { "g_state_predictions": { "code.complexity": ..., "test.coverage": ... } }

  Authentication: API Key (Vault) or OAuth 2.0
  Documentation: OpenAPI 3.0 + Swagger UI
  Current limit: based on Tenant quota
```

### 15.3 Independent deployment mode

```
Brain Core standalone deployment (no Agent):

  Helm values-standalone.yaml:
    agents.enabled: false
    portal.enabled: false # optional
    brain.standalone_api.enabled: true
    brain.observation_source: "api" # Not obtained from Agent, obtained from API

  Minimal dependencies: PostgreSQL + Redis + (optional Neo4j)
  GPU: 1× A100 (or RTX 3060 development mode)

  Purpose:
    (1) Researchers directly experiment with world models
    (2) Users use their own Agent framework (non-UEWM Agent)
    (3) Integrate into existing CI/CD systems as a "prediction engine"
    (4) Quick trial in the open source community (no need to deploy 12 Agent)
```

```
V2.0 new endpoints:

  GET /api/v1/brain/g-space/{project_id}
    Description: Read the current G-Space status (all observable indicators)
    Output: { "code": { "complexity_avg": 12.4, ... }, "test": {...}, ... }
  
  GET /api/v1/brain/g-space/{project_id}/history?from=&to=
    Description: Read G-Space historical trends
    
  GET /api/v1/brain/discoveries/{project_id}
    Description: Read new patterns discovered by Discovery Engine
    Output: [{ "pattern_id": "...", "description": "...", "confidence": 0.85 }]
```

---

## 15. Licensing and distribution architecture

### 16.1 Dual License Model

```
License structure:

  Open source version (AGPL v3):
  ├── Brain Core (H-JEPA + EBM + Z-Buffer + Evolution + Memory)
  ├── EIP Protocol (Protobuf IDL + gRPC Gateway)
  ├──Agent Framework (Universal Framework + EIP Client SDK)
  ├── Inner Ring 5 Agent (AG-CD/CT/DO/ST/MA)
  ├── Third-party Agent SDK
  ├── Standalone Brain Core API
  └── Limitations: Single Tenant, Profile-S, no federated learning

  Commercial License:
  ├── All contents of the open source version +
  ├── Middle/Outer Ring 7 Agent (AG-SA/FD/AU/PA/PD/BI/PR)
  ├──Multi-tenant support (Profile-M/L)
  ├── Federated Learning Engine
  ├── Enterprise-grade security (SOC 2, penetration testing report)
  ├── Priority Support + SLA
  ├── LLM Cost Optimization Tool
  └── Advanced monitoring dashboard

  CLA (Contributor License Agreement):
    All external contributors must sign a CLA
    Contributors retain copyright and grant Anthropic a perpetual license
    CLA Bot: Automatically checks the CLA signing status of a PR
```

### 16.2 Component licensing boundaries

| Components | License | AGPL Trigger Analysis |
|------|--------|-------------|
| Brain Core Binary | AGPL v3 | Open source modification required when provided as a service |
| EIP Protocol (.proto) | Apache 2.0 | Protocol definition does not trigger AGPL (Interoperability) |
| Third-party Agent SDK | Apache 2.0 | SDK does not trigger AGPL (independent process, network call) |
| Agent Framework | AGPL v3 | Built-in Agent is based on this framework |
| Helm Charts | AGPL v3 | Deployment configuration comes with the main project |
| Documentation | CC BY-SA 4.0 | Documentation Independent License |

### 16.3 Community Edition vs Enterprise Edition Feature Flag

| Features | Community Edition (Open Source) | Enterprise Edition (Commercial) |
|------|-------------|-------------|
| Brain Core | ✅ | ✅ |
| EIP Protocol | ✅ | ✅ |
| Inner Ring 5 Agent | ✅ | ✅ |
| Long-term memory | ✅ | ✅ |
| Self-evolution engine | ✅ | ✅ |
| Third-party Agent SDK | ✅ | ✅ |
| Standalone API | ✅ | ✅ |
| Middle Ring/Outer Ring Agent | ❌ (FF_MIDDLE/OUTER_RING) | ✅ |
| Multi-tenant | ❌ (Single Tenant) | ✅ |
| Profile-M/L | ❌ (Profile-S only) | ✅ |
| Federated Learning | ❌ | ✅ |
| SOC 2 Report | ❌ | ✅ |
| Enterprise SSO/SAML | ❌ | ✅ |
| Priority Support | Community Forum | Dedicated Engineer |

### 16.4 Contributor Workflow

```
External contribution process:

  1. Fork → Branch → Develop → Test
  2. Submit PR → CLA Bot check → CI passed
  3. Code Review (Module Owner):
     brain-core/: ARCHITECT level reviewer
     agents/: domain expert corresponding to Agent
     eip/: Protocol team reviewer
     sdk/: SDK team reviewer
  4. Merge → Release Notes automatically generated
  
  Module Ownership:
    CODEOWNERS files define reviewers for each directory
    External contributions cannot be modified: security envelope parameters, RBAC matrix, KSL hierarchical logic
    External contributions can modify: Agent adapters, coders, SDK extensions, documentation, tests
```

---

## 16. Verification first build strategy (new in V2.0 core)

### 16.1 Phase 0A: PoC Verification (Weeks 1-8)

```
Week 1-2: G-Space Engine
  3 warehouses (FastAPI, Gin, Prometheus) collect ~80 indicators
  Storage: SQLite (PoC stage)
  Delivery: G-Space time series, ≥2000 commits/repo

Week 3-4: Z-Space Baseline + Projection Head
  CodeBERT → Projection head (MLP+BN) → Z_impl (256-d) [V2.0.1: 256-d, including projection head]
  CI result encoding → projection head → Z_quality (256-d)
  SIGReg regularization training (replaces VICReg) [V2.0.1: SIGReg]
  Verification: SIGReg loss curve converges smoothly (per LeWM training feature)
  Delivery: Training curve + Epps-Pulley normality test passed

Week 5-6: Bridge verification + physical detection [V2.0.1: Using LeWM detection methodology]
  Training φ decoder: Z_impl → code.* metrics
  Training φ decoder: Z_quality → test.* metric
  
  [New in V2.0.1] Physical Probing Test (Physical Probing, from LeWM):
    Train lightweight probes for each Z-Layer:
      Linear probe: Z → W·Z + b → single G-metric
      MLP probe: Z → Linear(512) → ReLU → Linear(1) → single G-metric
    
    Detection target:
      Z_impl → code.complexity_avg, code.coupling_score, code.churn_rate_7d
      Z_quality → test.pass_rate, test.coverage_pct, test.test_duration_s
    
    Success criteria:
      Linear probe Pearson r > 0.6 for ≥3 G-Space metrics per Z-Layer
      MLP probe Pearson r > 0.85 for ≥5 G-Space metrics per Z-Layer
    
    [V2.0.1] This is stronger than the ARI clustering check:
      ARI > 0.2 → Supplementary metric (clustering quality)
      Probing r > 0.6 → Main indicator (structural coding verification)
  
  Key test: Z_impl predicts whether test.coverage_delta is better than
            code.* indicator alone forecast?
  YES → Z-Space has value beyond measurement → Continue
  NO → Z-Space Redundancy → Investigate Encoder/Projection Head Architecture
  Delivery: B5 vs B6 vs B7 comparison table + dimension-by-dimension R² report

Week 7-8: Found Signal PoC + Violation of Expected Testing
  Training JEPA predictor on 3-layer Z-Space
  Run prediction → Collect dual space surprise
  Check the Surprise Matrix: How many "Z correct + G wrong" (discoveries) were there?
  Manual inspection of top-20 potential findings

  [New in V2.0.1] Violation-of-Expectation, from LeWM:
    Generate 50 normal scenes + 50 abnormal scenes:
    
    Normal scenario (deserves low surprise):
      Normal commit → normal test result
      Standard deployment → Stability indicator
      Progressive Refactoring → Progressive Complexity Reduction
    
    Unusual scenes (deserving of high surprise):
      "Transfer": test.coverage jumps from 40% to 95% (single commit)
      "Impossible Physics": p99 latency dropped by 90% without any code changes
      "Cause-and-effect contradiction": doubled complexity but increased coverage (violating learned causal relationships)
      "Appeared out of thin air": zero commits but 50% more tests
      "Strange rollback": Rolling back to the old version but the indicators are not restored
    
    Metric: ROC-AUC (normal vs abnormal surprise score)
    Target: AUC > 0.80
    
    Significance: This directly demonstrates whether the model "understands" software engineering causality
  
  Delivery: Discovery rate, Noise rate, VoE ROC-AUC, Qualitative evaluation

Gate Review [V2.0.1 Update]:
  PASS: Probing r > 0.6 (linear) AND φ R² > 0.2 AND VoE AUC > 0.80 AND Z beyond G
  PARTIAL: Probing r > 0.4 OR φ R² > 0.1 OR VoE AUC > 0.65 → Continue but adjust
  FAIL: Probing r < 0.3 AND φ R² < 0.05 AND VoE AUC < 0.55 → Fundamental Rethink

  [V2.0.1] Additional checks:
    □ SIGReg normality test passed (Epps-Pulley p > 0.05)
    □ Smooth monotonic convergence of training curve (non-noise/non-monotone)
    □ Projection head ablation: Comparison of training stability with and without projection head
    □ Temporal straightening: Continuous velocity vector cosine similarity > 0.5
```

### 16.2 Phase 0B: Minimum Viable Brain (Months 3-6)

```
Pass PoC Gate → Build a real Brain Core:
  Z-Buffer Manager (V1 design)
  G-Space Engine (production level: Prometheus + GitHub API + CI API)
  H-JEPA Predictor (double prediction: Z + G)
  EBM Arbiter (enhanced: energy + risk decomposition)
  Bridging Functions (φ, ψ, consistency loss)
  Discovery Engine (Pattern Detection)
  Causal Graph Engine (Z side + G side)
  Long Memory (four levels, double index)
  TRL Evaluator, Safety Envelope, Circuit Breaker
  EIP Gateway (simplified: gRPC, Kafka optional)

First product: "Engineering Oracle" GitHub App
  PR → predict test/performance/complexity impact
  Deploy → predict accident probability
  Weekly → Project Health Report + Cause and Effect Explanation
  Discovery log → What the model sees but the metric cannot explain

Hardware: 1-2× A100 (or RTX 3060 for development)
Team: 2-3 engineers
```

### 16.3 Phase 1: Agents + Memory (Months 7-12)

```
Add Agent layer:
  Inner Ring 5 Agent (AG-CD/CT/DO/ST/MA)
  Complete EIP Protocol (gRPC + Kafka)
  ALFA framework (LOA control)
  memory consolidation engine
  Self-evolution (LoRA + dual space surprise drive)
  Third-party Agent SDK
  Standalone Brain Core API
```

### 16.4 Phase 2-3: Full UEWM (Year 2+)

```
V1.0.1 All design content:
  Middle/outer ring Agents, multi-tenancy (KSL), federated learning,
  SOC 2 compliance, enterprise features, full 8 Z-Layer coverage
```

---

## 17. Acceptance criteria mapping

### R01 — JEPA Base World Model (11 ACs)

| AC | Design Support | Verification Methods |
|----|---------|---------|
| AC-1: 8-layer 2048-d | §7.1 | Unit test: shape==(batch,2048) |
| AC-2: Kendall τ≥0.5 | §8.3 | Calibration data set +5-fold |
| AC-3: 1-step MSE<0.15 | §6.5 | Held-out 20%, time-split |
| AC-4: MVLS TRL-3 | §7.3+§7.4 | ARI≥0.3+Granger p<0.05 |
| AC-5: Causal p<0.05 | §6.4 | Granger test |
| AC-6: TRL dynamic weight reduction | §7.3 | Inject low ARI → EBM weight reduction |
| AC-7: Orchestration output sorting | §3.3 | Integration testing |
| AC-8: Selection Justification | §7.1 Encoder Matrix | Documentation Review |
| AC-9: Multi-project without starvation | §3.4 | Load testing |
| AC-10: Quota Queuing | §3.4 | Integration Testing |
| AC-11: Transformer-XL Non-LLM Demonstration | §6.1 | Documentation Review |

### MEM — Long Term Memory (10 ACs)

| AC | Design Support | Verification Methods |
|----|---------|---------|
| MEM-AC-1: Scenario retrieval | §12 | Z-Layer similarity retrieval accuracy >80% |
| MEM-AC-2: Ebbinghaus | §12 | High importance Episodes are never archived |
| MEM-AC-3: Fact Extraction | §12 | ≥3 Consistent Episode → Fact |
| MEM-AC-4: Anti-Pattern Feedback | §12 | Consolidation engine can inject anti-patterns into LoRA |
| MEM-AC-5: Profile injection | §12 | PREDICT and EVALUATE contain profile speedup |
| MEM-AC-6: Retrieval Delay | §12 | P99 < 200ms |
| MEM-AC-7: Tenant Isolation | §12 | KSL-0 cannot be retrieved across projects |
| MEM-AC-8: Archiving process | §12 | From hot storage (PgSql)->cold storage (S3) < 5min |
| MEM-AC-9: Federated Aggregation | §12 | KSL-3 Statistical Analysis DP ε≤0.5 |
| MEM-AC-10: Conflict Mediation | §12 | Time Priority Mechanism to Handle Old Fact Conflicts |

### GPU — GPU Optimized (6 ACs)

| AC | Design Support | Verification Methods |
|----|---------|---------|
| GPU-AC-1: mixed precision training BF16 | §13.2 | Training throughput: BF16 vs FP32, video memory reduction ≥35% |
| GPU-AC-2: Gradient checkpoint memory reduction ≥50% | §13.3 | Profiling: Comparison of memory with/without checkpoints |
| GPU-AC-3: TensorRT inference latency reduced by ≥30% | §13.5 | Benchmark: PyTorch vs TensorRT P99 |
| GPU-AC-4: The video memory of each component does not exceed the budget | §13.6 | nvidia-smi peak monitoring |
| GPU-AC-5: GPU utilization inference > 60% training > 80% | §13.7 | Prometheus GPU exporter 30min sampling |
| GPU-AC-6: Cross-platform get_device() function verification | §13.8 | Mac/RTX/A100 three-platform unit test |

### EXT — Third-party Agent (8 ACs)

| AC | Design Support | Verification Methods |
|----|---------|---------|
| EXT-AC-1: Third-party Agent registration process is available | §14.3 | Registration → Review → Activation → Health Check |
| EXT-AC-2: REST gateway function closed loop | §14.5 | REST→gRPC conversion 5 verbs |
| EXT-AC-3: Resource isolation is valid | §14.6 | Exceeding quota → current limiting + isolation verification |
| EXT-AC-4: SDK integration test passed | §14.8 | Python SDK completed registration+PREDICT+EVALUATE |
| EXT-AC-5: ADS compliance tools available | §14.7 | uewm-agent-lint/test/certify three tools |
| EXT-AC-6: Custom Z-Layer registration | §14.4 | Register custom encoder→VQV verification→Enter Z-Buffer |
| EXT-AC-7: Third-party RBAC interception | §14.3 | 100% interception of unauthorized requests |
| EXT-AC-8: Standalone API function verification | §15.2 | Agent-less deployment → direct predict/evaluate |

### LIC — License (4 ACs)

| AC | Design Support | Verification Methods |
|----|---------|---------|
| LIC-AC-1: AGPL/Apache boundaries clear | §16.2 | License scan: per-component licensing correct |
| LIC-AC-2: Community Edition features are fully available | §16.3 | Community Edition Profile-S Independent Deployment Verification |
| LIC-AC-3: CLA Workflow Automation | §16.4 | PR→CLA Bot→Sign→Merge |
| LIC-AC-4: Feature Flag isolation verification | §16.3 | The community version functions normally after disabling the commercial flag |

### GND — Dual Space Anchoring (10 ACs, new in V2.0)

| AC | Design Support | Verification Methods |
|----|---------|---------|
| GND-AC-1: G-Space ≥80 indicators/items, >95% collection rate | §4.2 | Indicator collection health dashboard |
| GND-AC-2: φ decoder R² > 0.2 for ≥3 G-Space Metric Group | §5.2 | Dimension-wise R² reporting |
| GND-AC-3: Consistency loss convergence | §5.4 | Training curve: loss < threshold |
| GND-AC-4: Dual-space surprise degree correct classification ≥80% events | §9.2 | 100 surprise events manual inspection |
| GND-AC-5: Discovery Engine identifies ≥1 valid unnamed pattern within 90 days | §9.3 | Manual review of proposed metrics |
| GND-AC-6: Z-Space outperforms G-Space independent predictions (p < 0.05) | §9, §16.1 | A/B: Z+G vs G-only |
| GND-AC-7: Self-reflective ground health 6 sub-indicators are functioning normally | §11.2 | All sub-indicators calculation + report |
| GND-AC-8: Risk decomposition coverage ≥70% EBM energy | §8.2 | explained/total ratio |
| GND-AC-9: G-Space Phase 1 Growth ≥5 Discovery Indicators | §9.4 | Discovery Log + Manual Review |
| GND-AC-10: PoC Gate Review All passed | §16.1 | ARI, φ R², Z-value-add |

### LeWM — LeWorldModel integration (6 ACs, new in V2.0.1)

| AC | Design Support | Verification Methods |
|----|---------|---------|
| LeWM-AC-1: SIGReg prevents collapse (normality test passed) | §5.4 | Epps-Pulley p > 0.05 on 100 random projections |
| LeWM-AC-2: Detection recovery G-Space metric (linear r > 0.6) | §16.1 | Dimension-wise detection report |
| LeWM-AC-3: VoE detection of abnormal engineering events (AUC > 0.80) | §16.1 | Normal vs abnormal ROC curve |
| LeWM-AC-4: Projection head improves training stability | §5.5 | Comparison of ablation with vs without projection head |
| LeWM-AC-5: Binary loss converges to smooth monotonicity | §5.4 | Training curve inspection |
| LeWM-AC-6: Natural emergence of time straightening | §16.1 | Continuous velocity vector cosine similarity > 0.5 |

### NFR (14 items)

| AC | Design Support | Verification Methods |
|----|---------|---------|
| NFR-1: Brain P99 | Load Planning | Load Testing Profile-S/M/L |
| NFR-2: Availability | Highly available architecture | 48-72h unattended operation |
| NFR-3: S→L | §3.6 | Extended test: add resources only |
| NFR-8: Decision Audit | Log Specification | Decision → Audit Log → Multidimensional Query |
| NFR-9: GPU contention | Resource allocation | GPU contention load testing |
| NFR-11: Log layering | Monitoring system | Hot/Warm/Cold query SLO verification |
| NFR-12: GPU memory budget compliance | §13.6 | Each component’s VRAM is not over-allocated |
| NFR-13: Third-party Agent Registration SLO | §14.3 | Registration→Activation < 5min (automatic review) |
| NFR-14: Standalone API P99 | §15.2 | Standalone deployment P99 < 300ms |

**Total: 154 ACs (107 R Extended + 10 MEM + 6 GPU + 8 EXT + 4 LIC + 10 GND + 6 LeWM + 3 NFR added)**