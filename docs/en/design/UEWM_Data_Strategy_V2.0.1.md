# 📊 UEWM training data strategy design document

**Document version:** V2.0.1
**Document number:** UEWM-DATA-008
**Last update:** 2026-04-03
**Status:** Design completed (100% coverage of R12 + Long Memory data life cycle + G-Space data management + GPU data pipeline)
**Change History:**
- V4.0/deliver-v1.0: Vector Quality, PII, License, Composition, Rollback, Phase 0
- V1.0.1: GPU optimized data pipeline (§10.5)
- V2.0.0: G-Space data collection/storage/life cycle, bridging training data requirements, PoC data collection plan
- **V2.0.1: (LeWM integration) 256-d Z-Space vector, VoE test set, probe training data; fully merge V1.0.1 content, eliminate all reference dependencies**
**Benchmarking requirements:** R12 (all), R01 (encoder data), R03 (evolution training data)

---

## 1. Overview

Define the training data sources, acquisition methods, quality requirements, annotation strategies and life cycle management of each encoder of the JEPA world model.

---

## 2. Z-Layer encoder data source matrix

### 2.1 MVLS three layers (Phase 0)

| Z-Layer | Data source | Data format | Pre-training base | Minimum sample size | Labeling method | Update frequency |
|---------|---------|---------|---------|---------|---------|---------|
| Z_impl | GitHub Top-10K repositories (Python/Go) | AST+CFG (Tree-sitter) | CodeBERT/StarCoder | 100K commit-level diff | Self-supervision (same repository, different commits) | Monthly increment |
| Z_quality | Same as above warehouse CI/CD log | Test pass rate + coverage rate (Cobertura/JaCoCo XML) + execution time | Training from scratch (structured table) | 50K CI pipeline records | Self-supervision (same project timing) | Synchronization with Z_impl |
| Z_phys | Public Prometheus dashboard + synthetic data | Prometheus time series format | TimesFM/Chronos | 10M time series data points | Self-supervision (time series prediction) + weak supervision (fault annotation) | Real-time collection |

### 2.2 Phase 1+ Extension Layer

| Z-Layer | Data source | Pre-trained base | Challenge |
|---------|---------|---------|------|
| Z_arch | Architecture document (README/ARCHITECTURE.md) + dependency graph (pom.xml/go.mod) | GraphSAGE+BERT | Document quality varies and requires manual screening |
| Z_logic | Requirements Document/User Story/Jira Issue (requires desensitization) | BERT/RoBERTa | Requires desensitization data of partner companies |
| Z_biz/Z_val/Z_market | Public financial reports + industry reports + product reviews | TabNet + FinBERT | Data is sparse and mainly relies on synthetic data |

---

## 3. Data quality requirements

Deduplication standard: Forks of the same repository only retain the original repository. Data freshness: Z_phys real-time; Z_impl/Z_quality monthly update; Z_arch+ quarterly update. Cleaning rules: Remove empty repositories, projects with test coverage of 0, and repositories with incompatible licenses.

### 3.1 Vector quality standards

| Metrics | Thresholds | Description |
|------|------|------|
| L2 norm | ∈ [0.5, 2.0] | Vectors outside the range may have coding anomalies |
| NaN ratio | = 0 | Zero tolerance |
| All-zero vector | < 1% | Encoder may not be loaded |
| Minimum variance per dimension | > 0.01 | Prevent dimension collapse |
| Average cosine similarity | < 0.7 | Ensure vector diversity |
| Minimum number of projects | Phase 0: 5, Phase 1+: 1000 | Data coverage |
| Minimum programming languages | Phase 0: 2, Phase 1+: 5 | Language diversity |
| Sample number ratio in each layer | > 0.5 | Inter-layer balance |

---

## 4. Synthetic data strategy

Phase 0 allows synthetic data to account for ≤ 30% (used for data enhancement, non-main training set). Z_phys layer special approval exception: allowed ≤ 60% (public Prometheus data is scarce), must be specially marked in the data version, and priority is given to seeking real data replacement from early customers.

Synthesis method: controlled perturbation of real data (code mutation, indicator noise injection). Synthetic data must be marked as synthetic and does not participate in the "real data" metrics evaluated by TRL.

### 4.1 Synthetic data markup Schema

```
Synthetic data markup in Parquet Schema:

  Field: is_synthetic (bool, required)
    true = synthetic data (code mutation/noise injection generation)
    false = real data (GitHub collection / customer project)

  Field: synthetic_method (string, nullable)
    "code_mutation" | "noise_injection" | "interpolation" | null (real data)

  Field: synthetic_source_id (string, nullable)
    Reference the original real sample ID that generated the synthetic sample (for traceability)

TRL evaluator filter rules:
  TRL Evaluator when calculating ARI/causality testing/forecasting MSE: WHERE is_synthetic = false
  Synthetic data only participates in encoder pre-training and does not participate in TRL compliance evaluation.

DVC metadata tags:
  Each data version's manifest.json contains:
    "synthetic_ratio": 0.28, "synthetic_count": 28000, "real_count": 72000,
    "z_phys_synthetic_ratio": 0.55 // Z_phys layer separate statistics
```

---

## 5. Data version management

The training data set is versioned (DVC). Each model version is associated with its training data version, supporting joint backtracking. When data is rolled back, the model version that depends on the data is automatically marked as "to be verified".

### 5.1 Data rollback cascade automation

```python
class DataRollbackCascade:
    """Automatically mark dependent model versions when data is rolled back"""
    
    async def on_data_rollback(self, data_version: str, layer: str):
        # 1. Query MLflow: which model versions use this data version
        dependent_models = await self.mlflow.search_runs(
            filter=f"params.training_data_version = '{data_version}' AND params.layer = '{layer}'"
        )
        # 2. Mark as "DATA_ROLLED_BACK_PENDING_VERIFICATION"
        for model in dependent_models:
            await self.mlflow.set_tag(run_id=model.run_id, key="data_integrity_status",
                                      value="DATA_ROLLED_BACK_PENDING_VERIFICATION")
        # 3. Notification DEVOPS + 4. Audit log
    # DVC post-checkout hook integration: .dvc/hooks/post-checkout → python -m uewm.data.rollback_cascade
```

---

## 6. Data Compliance

### 6.1 PII detection

Tool: Microsoft Presidio (open source, supports Chinese and English). Detection entities: PERSON, EMAIL, PHONE, IP, CREDIT_CARD, API_KEY, PASSWORD, etc. Custom regular rules: GitHub Token, AWS Key, Private Key Header, Chinese ID card, Chinese mobile phone number. Mark only if confidence level ≥ 70%. False positive whitelist: localhost, private IP range. DVC pre-commit hook automatic scanning.

### 6.2 License Scan

Tools: scancode-toolkit (supports 200+ licenses). Whitelist: Apache-2.0, MIT, BSD-2/3, ISC, Unlicense, CC0. Blacklist: GPL-2.0/3.0, AGPL-3.0, SSPL-1.0, BSL-1.1, CC-BY-NC. Gray list (requires manual review): LGPL, MPL-2.0, EPL-2.0. DVC pre-commit hook integration: Automatically checks all data source licenses before push.

---

## 7. Data retention and deletion policy

| Data Category | Retention Period | Deletion Trigger | Deletion Scope |
|---------|--------|---------|---------|
| Open source collection of training data | Permanent | License changed to incompatible | This warehouse data |
| Customer project training data | Contract period + 90 days | Contract termination/customer request (30 days)/KSL downgrade | Original data + encoding cache + DVC version |
| Customer-level LoRA | Contract period +90 days | Synchronized with training data | LoRA weights (the basic model is not affected) |
| Synthetic data | Consistent with the model version | 180 days after the model is abandoned | Corresponding to synthetic data |
| Federated learning gradient aggregation | Keep only the aggregation results | — | Do not keep the original gradients of single items |
| **G-Space indicator history** | **Real-time 30 days + 1 year history + archived forever** | **Never deleted (non-sensitive aggregated data)** | **V2.0** |
| **Discovery Proposal Record** | **Permanent** | **None (required for audit)** | **V2.0** |
| **Bridge function training data (Z,G pairing)** | **Consistent with model version** | **180 days after model abandonment** | **V2.0** |

**Long term memory data retention:**

| Data categories | Hot (30 days) | Warm (180 days) | Cold (180 days+) | Delete rules |
|---------|---------|----------|----------|---------|
| Episode (Z snapshot + decision + result) | PG+pgvector | PG metadata + S3 snapshot | S3 archive (zstd) | importance×decay<0.05→Archive; customer exit→delete together with training data (90 days) |
| Fact (semantic knowledge) | Neo4j | Neo4j | Export JSON archive | Delete following the project; KSL-0→Delete all; invalidated Fact retained for 180 days for audit |
| Project Profile | Redis Cache | — | — | Real-time regeneration, not retained independently |

Episode deletion is linked to machine forgetting: When the KSL-0 project is forgotten, Episode+Fact is deleted together (100% complete). When the KSL-1/2 project is forgotten, the shared desensitized Fact is retained (DP protection, without original information), and the original Episode is deleted.

Delete audit: source + scope + confirmation + associated model tag + integrity statement + timestamp. Log retention ≥ 3 years.

---

## 8. Phase 0 data collection plan

### 8.1 Phase 0A: PoC Data Collection (Week 1-2)

```
PoC data collection plan (new in V2.0, takes precedence over encoder training data):

  Target repository: FastAPI, Gin, Prometheus (3)
  Requirements: >5K stars, active CI, with Prometheus/Grafana metrics

  G-Space data collection:
    GitHub API → code.* Metrics (per commit)
    GitHub Actions API → test.* metrics (per CI run)
    SonarQube/tree-sitter → complexity, coupling (per commit)
    local analysis → churn, hotspot, duplication (per commit)
    
    Target: ~2000 commits × ~80 G-Space metrics per repository
    Storage: SQLite (PoC stage)
    Format: Parquet (including timestamp, commit SHA, all indicators)

Z-Space data acquisition (synchronized with G-Space):
    per commit → Tree-sitter AST diff → CodeBERT embedding → projection header → 256-d Z_impl [V2.0.1: 256-d + projection header]
    per CI run → test metric normalization → encoding → projection header → 256-d Z_quality [V2.0.1]
    
    Key: Z-Space and G-Space data must be aligned by commit SHA
    In this way, the bridge function φ (Z → G) and the probe head (Z → single metric) can be trained [V2.0.1: + probe head]

  [New in V2.0.1] VoE test data generation:
    50 Normal scenario: Randomly sampled from real commit history
    50 Abnormal Scenarios: Generated from Controlled Mutation of Real Data
      - Indicator transfer (coverage mutation ±50pp)
      - Causal contradiction (complexity↑ but coverage↑)
      - Zero causal effect (zero commits but metric changes)
    Storage: voe_test_set.parquet

  Delivery:
    g_space_fastapi.parquet, g_space_gin.parquet, g_space_prometheus.parquet
    z_space_fastapi.parquet (256-d), z_space_gin.parquet, z_space_prometheus.parquet [V2.0.1: 256-d]
    aligned_pairs.parquet (Z,G pairs, used to train φ and probe)
    voe_test_set.parquet (100 scenarios) [V2.0.1]
```

### 8.2 Phase 0A: Bridging training data (Week 5-6)

```
Bridging function training data:
  Input: aligned_pairs.parquet (Z vector + G index at the same time)
  Training set: first 80% commits (time split)
  Validation set: last 20% commits
  
  φ training:
    Input: Z_impl (256-d, V2.0.1)
    Output: code.* indicators (~15-d)
    Loss: MSE
    
  ψ training:
    Input: G-Space (80-d)
    Output: Z constraint vector (256-d, V2.0.1)
    Loss: Cosine similarity
    
  Consistency loss training:
    Input: Z(t), G(t), Z(t+1)_predicted
    Loss: α * MSE(φ(Z_pred), G_actual) + (1-α) * cosine(Z_pred, ψ(G_actual))
```

### 8.3 Phase 0B: Production data collection (original V1.0.1 weekly plan)

```
Week 1-2: Benchmark project selection and infrastructure
  Select 5-10 benchmark open source projects (>5K stars, active CI, Python/Go)
  Candidates: FastAPI, Gin, Django, Hugo, Terraform, Prometheus, Grafana
  DVC warehouse initialization + Parquet schema definition + GitHub API collection script + Tree-sitter parsing pipeline

Week 3-4: Z_impl data collection
  Goal: 100K commit-level diffs. ~15K commits per project. AST+CFG parsing → Parquet storage.
  VectorQualityValidator first round of verification. Delivery: Z_impl data meets standard, synthetic_ratio < 30%.

Week 5-6: Z_quality data collection
  Goal: 50K CI pipeline records. Data source: GitHub Actions log API.
  Parsing: test pass rate + Cobertura/JaCoCo XML. Cleaning: filter coverage=0 items.

Week 7-8: Z_phys data acquisition + synthetic data
  Target: 10M time series data points. Real: Public Prometheus + Grafana demo.
  Synthetic: Noise injection (Gaussian/mutant/periodic anomalies), is_synthetic=true. Z_phys synthetic_ratio ≤ 60%.

Week 9-10: Quality verification + data version release
  VectorQualityValidator full verification (3 layers). License scanning (scancode) + PII detection (Presidio).
  DVC v1.0 released. Manifest.json is complete (including synthetic_ratio).
  Delivery: R12 AC-1 (minimum sample size) + AC-3 (synthetic proportion) + AC-4 (compliance).

Person in charge: Data Engineer × 2
Blocking risk: GitHub API current limit → apply for higher rate limit
Blocking risk: Insufficient public data in Prometheus → synthetic data placeholder, Phase 1 replacement
```

---

## 9. Training data stage planning

| Phase | Z-Layer | G-Space Domain | Data Source | Target |
|-------|----------|-----------|----------|------|
| Phase 0A | Z_impl, Z_quality | code.*, test.* | 3 open source warehouse | PoC verification |
| Phase 0B | + Z_phys | + ops.* | + Prometheus | MVLS TRL-3 + φ R² > 0.2 |
| Phase 1 | + Z_arch, Z_logic | + process.* | + Architecture documentation + Jira | Core five layers |
| Phase 2 | + Z_biz, Z_val, Z_market | (requires business data) | + financial report + customer data | All eight layers |

---

## 10. Vector quality automated verification pipeline

### 10.1 Validation Rule Engine

```python
class VectorQualityValidator:
    """Automated vector quality verification. Triggers: Post-encoder training/incremental import/synthetic generation/LoRA evolution/manual audit."""
    
    class QualityRules:
        L2_NORM_MIN = 0.5; L2_NORM_MAX = 2.0
        NAN_RATIO_MAX = 0.0; ZERO_VECTOR_RATIO_MAX = 0.01
        MIN_VARIANCE_PER_DIM = 0.01; MAX_AVG_COSINE_SIMILARITY = 0.7
        MIN_PROJECTS = 1000; MIN_LANGUAGES = 5; MIN_LAYER_SAMPLE_RATIO = 0.5
    
    def validate_batch(self, vectors, metadata, layer_name) -> ValidationReport:
        # Rule 1: NaN detection (zero tolerance) → Rule 2: L2 norm range → Rule 3: All zero vectors
        # → Rule 4: Variance per dimension → Rule 5: Average cosine similarity (sampling 1000)
    
    def validate_dataset_coverage(self, dataset_manifest) -> ValidationReport:
        # Number of projects → Programming language coverage → Ratio of samples in each layer
```

### 10.2 Verification pipeline integration

Trigger source: DVC push hook → MLflow callback → LoRA post-check → manual CLI. Result: PASSED → Storage | WARNING → Storage + Alarm | FAILED → Blocking (NaN hard blocking, L2 abnormal soft blocking, cosine too high → increase SIGReg).

### 10.3 Verification report format

```json
{
  "report_id": "vqv-2026-03-22-Z_impl-v1.2",
  "layer": "Z_impl", "data_version": "v1.2", "model_version": "codbert-ft-v3",
  "timestamp": "2026-03-22T10:00:00Z", "total_vectors": 105000, "overall_passed": true,
  "checks": [
    {"name": "nan_ratio", "value": 0.0, "threshold": 0.0, "passed": true},
    {"name": "l2_norm_out_of_range", "value": 0.012, "threshold": 0.05, "passed": true},
    {"name": "zero_vector_ratio", "value": 0.002, "threshold": 0.01, "passed": true},
    {"name": "low_variance_dims", "value": 0.03, "threshold": 0.10, "passed": true},
    {"name": "avg_cosine_similarity", "value": 0.52, "threshold": 0.70, "passed": true}
  ]
}
```

### 10.5 GPU optimized data pipeline

```
Training data GPU optimization:

  Data loading optimization:
    PyTorch DataLoader: num_workers=4, pin_memory=True, prefetch_factor=2
    Parquet column-based reading: load only the columns required for training (avoid full loading)
    Memory mapping: Use mmap for large files to reduce memory copies
    
  Batch processing optimization:
    Dynamic batch size: automatically adjusted based on available GPU memory
    Gradient accumulation: Small memory devices (RTX 3060) use 4-8 steps of gradient accumulation to simulate large batches
    Mixed precision data: input data remains FP32, encoder internally converts to BF16
    
  Encoder output buffer:
    Cache Z vector after first encoding (256-d, ~1KB/sample, V2.0.1)
    Reuse cache during alignment training to avoid repeated encoding
    Cache invalidation: Automatically invalidate after the encoder weight is updated
    Estimated savings: ~60% reduction in alignment training GPU time

  Distributed data parallelism (Phase 2+, multiple GPUs):
    DeepSpeed data parallelism
    Data sharding: DistributedSampler shards by GPU
    Communication optimization: gradient all-reduce overlap with backward
```

### 10.6 G-Space data quality (new in V2.0)

```
G-Space data quality rules:

  Collection completeness:
    At least 12/15 code.* indicators for each commit are valuable (80%)
    At least 6/8 test.* metrics have values (75%) per CI run
    At least 9/11 ops.* metrics have value per minute (82%)
    
  Anomaly detection:
    Each indicator maintains μ and σ over a 30-day sliding window.
    New value exceeds μ ± 3σ → marked as suspicious (not discarded immediately)
    The suspicious value does not participate in the consistency loss calculation (to prevent T6 attacks)
    Suspicious values are retained in G-Space for manual review
    
  Data alignment:
    Z-Space and G-Space must be aligned by commit SHA + timestamp
    Data with failed alignment does not participate in φ/ψ training
    Alignment rate < 90% → Alarm (collector timing problem)
```

---

## 11. Acceptance criteria mapping

| AC | Design Support | Verification Methods |
|----|---------|---------|
| R12 AC-1: MVLS three-tier minimum sample size | §2.1 + §10.1 validate_dataset_coverage | Data statistics report |
| R12 AC-2: Model-data version traceability | §5 DVC+MLflow | DVC backtesting |
| R12 AC-3: Synthetic data ≤30% (Z_phys ≤60%) | §4 + §4.1 + §10.2 | Data label statistics |
| R12 AC-4: Compliance Review Passed | §6 PII+ License | Scan Report |
| R12 AC-5: Documentation of encoder pre-training selection | ARCH §9.2 | Document review |
| R12 AC-6: Customer data deleted within 90 days | §7 | Deletion process testing |
| R12 AC-7: KSL-0 Forgetting 100% (30 days) | EVO §10 | Forgetting Test: Delete → Zero Residue |
| R12 AC-8: Machine Forgetting Policy Document Review | EVO §10 | Document Review Passed |
| **R12 AC-9: Encoder cache reduces alignment training GPU time ≥50%** | **§10.5** | **A/B: With cache vs without cache** |
| **R12 AC-10: G-Space acquisition integrity ≥80%** | **§10.6** | **Acquisition rate monitoring** |
| **R12 AC-11: Z-G data alignment rate ≥90%** | **§10.6** | **Alignment check** |
| **R12 AC-12: PoC Dataset Delivery (3 Warehouses × Z+G)** | **§8.1** | **Data Integrity Check** |