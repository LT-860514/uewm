# 📊 UEWM training data strategy design document

**Document version:** deliver-v1.1
**Document number:** UEWM-DATA-008
**Last update:** 2026-03-24
**Status:** Design completed (100% coverage of R12 + Long Memory data life cycle)
**Merge source:** Data Strategy V1.0 + V2.0 (Vector Quality) + V3.0 (PII/License) + V4.0 (Synthetic Tag/Rollback Cascade/Phase0 Plan) — Full Merge
**Benchmarking requirements:** R12 (all), R01 (encoder data), R03 (evolution training data)

---

## 1. Overview

Define the training data sources, acquisition methods, quality requirements, annotation strategies and life cycle management of each encoder of the JEPA world model.

---

## 2. Z-Layer encoder data source matrix

### 2.1 MVLS three layers (Phase 0)

| Z-Layer | Data source | Data format | Pre-training base | Minimum sample size | Labeling method | Update frequency |
|---------|----------|----------|-----------|-----------|----------|----------|
| Z_impl | GitHub Top-10K repositories (Python/Go) | AST+CFG (Tree-sitter) | CodeBERT/StarCoder | 100K commit-level diff | Self-supervision (same repository, different commits) | Monthly increment |
| Z_quality | Same as above warehouse CI/CD log | Test pass rate + coverage rate (Cobertura/JaCoCo XML) + execution time | Training from scratch (structured table) | 50K CI pipeline records | Self-supervision (same project timing) | Synchronization with Z_impl |
| Z_phys | Public Prometheus dashboard + synthetic data | Prometheus time series format | TimesFM/Chronos | 10M time series data points | Self-supervision (time series prediction) + weak supervision (fault annotation) | Real-time collection |

### 2.2 Phase 1+ Extension Layer

| Z-Layer | Data source | Pre-trained base | Challenge |
|---------|---------|-----------|------|
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

### 4.1 Synthetic data markup Schema```
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
```---

## 5. Data version management

The training data set is versioned (DVC). Each model version is associated with its training data version, supporting joint backtracking. When data is rolled back, the model version that depends on the data is automatically marked as "to be verified".

### 5.1 Data rollback cascade automation```python
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
```---

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

**[deliver-v1.1] Long-term memory data retention (Architecture §12):**

| Data categories | Hot (30 days) | Warm (180 days) | Cold (180 days+) | Delete rules |
|---------|---------|----------|----------|---------|
| Episode (Z snapshot + decision + result) | PG+pgvector | PG metadata + S3 snapshot | S3 archive (zstd) | importance×decay<0.05→Archive; customer exit→delete together with training data (90 days) |
| Fact (semantic knowledge) | Neo4j | Neo4j | Export JSON archive | Delete following the project; KSL-0→Delete all; invalidated Fact retained for 180 days for audit |
| Project Profile | Redis Cache | — | — | Real-time regeneration, not retained independently |

Episode deletion is linked to machine forgetting: When the KSL-0 project is forgotten, Episode+Fact is deleted together (100% complete). When the KSL-1/2 project is forgotten, the shared desensitized Fact is retained (DP protection, without original information), and the original Episode is deleted.

Delete audit: source + scope + confirmation + associated model tag + integrity statement + timestamp. Log retention ≥ 3 years.

---

## 8. Phase 0 data collection plan

### 8.1 Week-by-week planning```
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
```---

## 9. Training data stage planning

| Phase | Z-Layer | Data source | Target |
|-------|----------|----------|------|
| Phase 0 (M1-M4) | Z_impl, Z_quality, Z_phys | Open source GitHub + public Prometheus + synthesis | MVLS three-layer TRL-3 |
| Phase 1 (M5-M7) | +Z_arch, Z_logic | Architecture document + desensitization requirement data | Core five layers TRL-3+ |
| Phase 2 (M8-M10) | +Z_biz, Z_val, Z_market | Financial report + industry report + synthesis + customer data | Extended seven layers TRL-2+ |
| Phase 3 (M11+) | Full 8 layers | Accumulate real customer data | Full layer TRL-4+ |

---

## 10. Vector quality automated verification pipeline

### 10.1 Validation Rule Engine```python
class VectorQualityValidator:
    """Automated vector quality verification. Triggers: Post-encoder training/incremental import/synthetic generation/LoRA evolution/manual audit."""
    
    class QualityRules:
        L2_NORM_MIN = 0.5;  L2_NORM_MAX = 2.0
        NAN_RATIO_MAX = 0.0;  ZERO_VECTOR_RATIO_MAX = 0.01
        MIN_VARIANCE_PER_DIM = 0.01;  MAX_AVG_COSINE_SIMILARITY = 0.7
        MIN_PROJECTS = 1000;  MIN_LANGUAGES = 5;  MIN_LAYER_SAMPLE_RATIO = 0.5
    
    def validate_batch(self, vectors, metadata, layer_name) -> ValidationReport:
        # Rule 1: NaN detection (zero tolerance) → Rule 2: L2 norm range → Rule 3: All zero vectors
        # → Rule 4: Variance per dimension → Rule 5: Average cosine similarity (sampling 1000)
    
    def validate_dataset_coverage(self, dataset_manifest) -> ValidationReport:
        # Number of projects → Programming language coverage → Ratio of samples in each layer
```### 10.2 Verification pipeline integration

Trigger source: DVC push hook → MLflow callback → LoRA post-check → manual CLI. Result: PASSED → Storage | WARNING → Storage + Alarm | FAILED → Blocking (NaN hard blocking, L2 abnormal soft blocking, cosine too high → increase VICReg).

### 10.3 Verification report format```json
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
```---

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