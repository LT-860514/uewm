# 🚀 UEWM deployment and operation design document

**Document version:** V2.0.1
**Document Number:** UEWM-DEPLOY-009
**Last update:** 2026-04-03
**Status:** Design completed (100% coverage of R05, NFR-1/2/6/9/12 + G-Space operation and maintenance + GPU optimized deployment + community version deployment)
**Change History:**
- V4.0/deliver-v1.0: SLO, error budget, GPU isolation, shadow mode, HA, chaos
- V1.0.1: GPU optimized Helm configuration (§15), Community Edition/Enterprise Edition deployment (§15.2), GPU monitoring alarms (§16)
- V2.0.0: G-Space operation and maintenance (collector monitoring/storage/capacity), Discovery operation and maintenance, bridge health monitoring, PoC deployment specifications
- **V2.0.1: (LeWM integration) PoC directory contains probes/voe/sigreg subdirectory; SIGReg monitoring alarm; fully merge V1.0.1 content and eliminate all reference dependencies**
**Benchmarking requirements:** R05 (all), NFR-1/2/3/6/9/11

---

## 1. Overview

Define UEWM's containerized deployment architecture, CI/CD pipeline, full-link observability, high-availability design, hierarchical SLO system, error budget and automatic degradation, GPU resource isolation and operation and maintenance operation manual.

---

## 2. Technology selection

Kubernetes (container orchestration), Helm (deployment template), Prometheus+Grafana+OTel (observable), Patroni/PostgreSQL (data), Redis Cluster (cache), Kafka (message), Harbor (mirror warehouse), ArgoCD (GitOps).

---

## 3. Deployment architecture

### 3.1 Kubernetes namespace

uewm-system (Brain Core + **G-Space Engine** + **Discovery Engine** + EIP Gateway), uewm-agents (12 Agent Deployments), uewm-data (PostgreSQL + Redis + Kafka + Milvus + Neo4j), uewm-monitoring (Prometheus + Grafana + OTel), uewm-vault (HashiCorp Vault), **uewm-ext-agents** (Third-party Agent independent namespace).

**[deliver-v1.1]** Neo4j New: Used for long-term memory semantic memory knowledge graph. Profile-S single instance, Profile-M 3-node causally consistent cluster, Profile-L independently deployed by shards.

### 3.2 Resource Baseline

| Components | Profile-S | Profile-M | Profile-L |
|------|-----------|-----------|----------|
| GPU | 2× A100 | 4× A100 | 8× A100 |
| CPU | 32 cores | 96 cores | 256 cores |
| RAM | 128 GB | 384 GB | 1 TB |
| Storage | 100 GB SSD | 1 TB SSD | 10 TB SSD |

### 3.3 GPU resource isolation

```
GPU resource allocation strategy:
  Inference GPU pool: always prioritize training
  Training GPU Pool: LoRA Evolution uses only remaining computing power or independent training GPUs
  
  Profile-M example (4× A100):
    GPU 0-1: Dedicated to inference (Brain Core decision-making)
    GPU 2: Inference overflow + training sharing (inference priority preemption)
    GPU 3: Training only (LoRA Evolution)
    
  Constraint: Evolutionary training cannot make inference P99 exceed 600ms
         600ms = Tier-1 SLO Baseline 500ms (Profile-M) + 100ms Evolutionary Training Degradation Tolerance [NFR-9]
         Exceeding 600ms → It is considered that evolution affects reasoning, and evolution must be suspended immediately
         Pause delay SLO: < 30s (Based on R05 AC-7)
```

---

## 4. Hierarchical SLO system

### 4.1 Tier 1 SLO (Core Path — Brain Inference)

| Profile | P50 | P99 | P99.9 | Measuring points |
|---------|-----|-----|-------|--------|
| Profile-S | < 100ms | < 300ms | < 1s | EIP Gateway→Brain Return |
| Profile-M | < 200ms | < 500ms | < 2s | Same as above |
| Profile-L | < 300ms | < 1000ms | < 3s | Same as above |

### 4.2 Tier 2 SLO (Agent end-to-end)

Simple tasks (code formatting/unit testing): P99 < 30s. Medium tasks (code review/functional teardown): P99 < 5min. Complex tasks (architecture evaluation/full testing): P99 < 30min. Tasks requiring manual approval: SLA < 4h.

### 4.3 Tier 3 SLO Monitoring Rules

```yaml
- alert: Tier3_SelfReflection_Slow
  expr: uewm_reflection_duration_seconds > 300 # > 5min
  labels: {severity: warning, tier: "3"}

- alert: Tier3_KnowledgeAggregation_Slow
  expr: uewm_knowledge_aggregation_duration_seconds > 3600 # > 1h
  labels: {severity: warning, tier: "3"}

- alert: Tier3_Evolution_Slow
  expr: uewm_evolution_iteration_duration_seconds > 900 # > 15min (Profile-S)
  labels: {severity: warning, tier: "3"}

- alert: Tier3_ModelRollback_Slow
  expr: uewm_model_rollback_duration_seconds > 120 # > 2min
  labels: {severity: critical, tier: "3"}
```

### 4.4 Availability SLO

Brain Core 99.95% (≤ 22 min/month), EIP Gateway 99.99% (≤ 4 min), Agent 99.9% each (≤ 44 min), end-to-end 99.5%, data layer 99.99%.

---

## 5. Error budget and SLO breach response

### 5.1 Error Budget Dashboard

Display: monthly remaining budget of each component (percentage + minutes), 24h/7d/30d burn-rate trend, current alarm level (L0-L4), automatically triggered protective action list, predicted exhaustion date.

### 5.2 Burn-Rate Level 4 Alarm

| Level | Trigger Condition | Automatic Response | Response SLA |
|------|---------|---------|---------|
| L1 Observation | 1h burn-rate > 2x | None (Grafana→Slack) | 1h |
| L2 warning | 6h burn-rate > 5x | Pause evolution + reduce outer ring priority + HPA expansion | 30min |
| L3 critical | Monthly budget <20% or 1h>14x | L2 all + freeze new projects + outer ring suspension + LOA downgraded by 1-2 levels | 15min |
| L4 exhausted | Monthly budget = 0% | Change freeze (evolution/deployment prohibited, only fault repair requires two-person approval) | Instant |

### 5.3 Shadow mode implementation

During Phase 0, Error Budget operates in shadow mode: recording "actions that should be triggered" but not actually performing freezes or degradations. Generate calibration report (30 days trigger statistics, L4 trigger rate needs to be <1%). Phase 1 activated access control: ≥30 days of shadow data, ≥100 events, calibration report approved by DEVOPS+SECURITY.

### 5.4 Alarm channel configuration

| Level | Notification Channel | Receiving Role |
|------|---------|---------|
| L1 | Slack #uewm-alerts | DEVOPS |
| L2 | PagerDuty (P2) + Slack | DEVOPS + SECURITY |
| L3 | PagerDuty (P1) + Slack + Email + Portal Banner | Full Channel |
| L4 | PagerDuty (P1) + Slack + Email + Portal + SMS | SYSTEM_ADMIN |

Portal banner: L3 orange warning (outer loop suspended, project frozen), L4 red critical (change frozen, only fault repair).

---

## 6. LLM Cost Management

Monthly budget: Profile-S ≤$500, Profile-M ≤$5,000, Profile-L ≤$25,000. Per-Task ceiling: Simple ≤ $0.01, Medium ≤ $0.10, Complex ≤ $1.00. 80% budget warning, 100% downgrade to small model/rule engine. LLM cost per Agent is available in real time. Daily report (Agent × Project × Tenant 3D). Cost anomaly: Single Agent single day > 3x historical average → alarm.

---

## 7. CI/CD pipeline

CI: Lint+Tests → Protobuf compilation + Schema compatibility → Integration testing (EIP closed loop) → Security scanning (Trivy+Semgrep) → Container building (multi-arch) → Push Harbor. CD: Staging deployment → 1h soak test → canary 10%/30min → full release → Post-deploy health check for 5 minutes.

---

## 8. High availability and disaster recovery

### 8.1 Self-healing mechanism

Brain Core: Active-Standby, <30s switching. EIP Gateway: 3 replicas Active-Active. Agent: HPA + readiness probe. Data layer: Patroni(PG)/Sentinel(Redis)/ISR(Kafka).

### 8.2 Model version rollback

MLflow version management. Rollback SLO < 2min. Rollback range: single-layer LoRA / full model / Z-Buffer snapshot.

---

## 9. Brain Core Decision Audit

Record of each decision: input Z-Layer signal + EBM energy score + arrangement suggestion + final decision + delay. Supports multi-dimensional query by time/Agent/project/energy value. Write to Kafka audit topic → Elasticsearch/ClickHouse.

---

## 10. Scalability

S→M→L only needs to add resources without changing the architecture: the number of Brain GPUs/Agent HPA max/the number of data layer replicas/SLO thresholds are switched through Helm values. See Architecture §3.6 for tenant sharding.

---

## 11. Monitoring alarm rule matrix

Brain P99, Gateway error rate, Agent task completion rate, GPU utilization, Kafka lag, PG replication lag, Redis memory, Disk usage. Each item contains warning/critical thresholds and notification channels.

### 11.2 Long-term memory monitoring rules

```yaml
- alert: Memory_Consolidation_Slow
  expr: uewm_memory_consolidation_duration_seconds > 1800 # > 30min
  labels: {severity: warning}
  annotations: {summary: "Memory consolidation took {{ $value }}s (SLO: < 1800s)"}

- alert: Memory_Retrieval_Slow
  expr: histogram_quantile(0.99, uewm_memory_recall_duration_seconds_bucket) > 0.2 # P99 > 200ms
  labels: {severity: warning}
  annotations: {summary: "Memory RECALL P99 {{ $value }}s (SLO: < 200ms)"}

- alert: Memory_Episode_Storage_High
  expr: uewm_episode_count_total > 8000 # Close to the 10K upper limit
  labels: {severity: warning}
  annotations: {summary: "Episode count {{ $value }} approaching 10K limit"}

- alert: Memory_Fact_Contradiction_Spike
  expr: rate(uewm_fact_contradictions_total[1h]) > 5
  labels: {severity: warning}
  annotations: {summary: "{{ $value }} fact contradictions/hour — possible model drift"}
```

### 11.3 Long-term memory storage capacity

| Profile | Episodes/day | Hot storage (30 days) | Warm storage (180 days) | Fact number/project | Total increment |
|---------|------------|------------|------------|------------|--------|
| Profile-S | ~100 | ~150 MB | ~900 MB | ~200 | +~1 GB |
| Profile-M | ~500 | ~750 MB | ~4.5 GB | ~500 | +~5 GB |
| Profile-L | ~2,000 | ~3 GB | ~18 GB | ~1,000 | +~21 GB |

Storage: Episode hot tier uses PostgreSQL + pgvector (shared with existing PG instance), warm/cold tier uses S3. Semantic Memory uses Neo4j (new component). Profile cache uses existing Redis.

### 11.4 G-Space collection monitoring (new in V2.0)

```yaml
- alert: GSpace_Collection_Failure
  expr: uewm_gspace_collection_success_rate < 0.90
  for: 10m
  labels: {severity: warning}
  annotations: {summary: "G-Space collection rate {{ $value }} < 90%"}

- alert: GSpace_Suspicious_Value
  expr: uewm_gspace_suspicious_values_total > 10
  for: 1h
  labels: {severity: warning}
  annotations: {summary: "{{ $value }} suspicious G-Space values in last hour"}

- alert: GSpace_ZG_Alignment_Low
  expr: uewm_gspace_alignment_rate < 0.90
  labels: {severity: warning}
  annotations: {summary: "Z-G data alignment rate {{ $value }} < 90%"}
```

### 11.5 Bridge health monitoring (new in V2.0)

```yaml
- alert: Bridging_Phi_R2_Low
  expr: uewm_bridging_phi_r2_avg < 0.15
  for: 24h
  labels: {severity: warning}
  annotations: {summary: "φ decoder R² {{ $value }} < 0.15 — bridging degraded"}

- alert: Bridging_Consistency_Loss_High
  expr: uewm_bridging_consistency_loss > 2.0
  for: 6h
  labels: {severity: warning}
  annotations: {summary: "Consistency loss {{ $value }} > 2.0 — Z/G drift"}

- alert: Discovery_Rate_High
  expr: uewm_discovery_rate > 0.30
  for: 24h
  labels: {severity: warning}
  annotations: {summary: "Discovery rate {{ $value }} > 30% — Z-Space may be drifting"}

- alert: Discovery_Rate_Zero
  expr: uewm_discovery_rate == 0
  for: 168h # 7 days
  labels: {severity: info}
  annotations: {summary: "No discoveries in 7 days — Z-Space may be redundant or stable"}
```

### 11.6 G-Space storage capacity (new in V2.0)

| Profile | G-Space metrics/day | Real-time storage (30 days) | History (1 year) | Yearly increments |
|---------|---------------|-------------|---------|--------|
| Profile-S | ~50K data points | ~50 MB | ~600 MB | ~600 MB |
| Profile-M | ~500K data points | ~500 MB | ~6 GB | ~6 GB |
| Profile-L | ~2M data points | ~2 GB | ~24 GB | ~24 GB |

G-Space is shared with an existing PostgreSQL instance, independent of the schema `gspace`.

---

## 12. SLO Validation Load Test Plan

### 12.1 Testing Methodology

Test tool: k6 (HTTP/gRPC) + custom EIP client (Protobuf). Independent performance testing cluster. The hardware is consistent with each Profile baseline. Preload MVLS Z-Buffer, warm up cache. Prometheus+Grafana real-time monitoring, OTel trace.

### 12.2 Profile-S Load Test

| Test items | Load parameters | SLO target | Duration |
|--------|---------|---------|---------|
| Brain P99 | 5 concurrent EIPs | P50<100ms, P99<300ms | 30min |
| Peak | 10 concurrency (2x) | P99<500ms | 5min |
| Agent end-to-end | 1 simple + 1 medium parallelism | <30s / <5min | 3 rounds |
| Availability | 24h unattended | Brain 99.95%, GW 99.99% | 24h |
| Fault recovery | Kill Brain pod | <30s self-healing | Single shot |

### 12.3 Profile-M Load Test

| Test items | Load parameters | SLO targets | Duration |
|--------|---------|---------|---------|
| Brain P99 | 50 concurrency | P50<200ms, P99<500ms | 60min |
| Peak | 100 concurrency (2x) | P99<800ms | 10min |
| Multi-Agent parallelism | 10 projects × 5 Agents | Fair distribution, no hunger | 30min |
| GPU contention | Inference full load + evolution | Inference P99<600ms (NFR-9) | 30min |
| Evolution pause | L2 injection | Pause <30s | Single |
| L3 downgrade | L3 injection | All actions <60s | Single |
| Model rollback | Trigger rollback | <2min | Single |
| Availability | 48h unattended | Brain 99.95% | 48h |
| LLM Cost | 30 Days Simulation | ≤$5,000 | 30 Days Simulation |

### 12.4 Profile-L Load Test

200 concurrency, P99<1000ms, multi-tenant isolation (20 Tenant), scalability (S→L only adds resources), 72h availability.

### 12.5 Chaos test matrix

| Fault Injection | Desired Behavior | Profile |
|---------|---------|---------|
| Kill Brain pod | <30s self-healing (Active-Standby) | S,M,L |
| Kill EIP Gateway pod | Load balancing elimination, no awareness | M, L |
| Kill Agent pod | HPA restarts, tasks are not lost | M, L |
| Redis master node failure | <10s Sentinel switchover | M,L |
| PostgreSQL Primary failure | Patroni switchover <15s | M,L |
| Kafka Broker failure (1/3) | ISR, no message loss | M, L |
| Network Partition (Brain↔Agent) | Agent Rule Engine Mode | M |
| GPU driver abnormality | Increased latency → L2 alarm → Evolution pause | M |
| Disk full (audit log) | Hot→Warm accelerated cooling + alarm | M |

### 12.6 Test Timeline

Phase 0 M3: Profile-S full volume + Profile-M Tier-1 (1 week). Phase 0 M4: Full Profile-M + Chaos (2 weeks). Phase 1 M7: Multi-Agent and multi-project (1 week). Phase 2 M10: Profile-L full volume + multi-tenant (2 weeks). Phase 3+: Quarterly return (1 week).

### 12.7 Test passing criteria

AC-1→P99<500ms@50 concurrent 60min, AC-2→Chaos recovery<30s, AC-4→S/M/L each passed, AC-5→S→L only added resources, AC-7→L2 pause<30s, AC-8→L3 action<60s, AC-9→30 days LLM≤$5K.

### 12.8 G-Space + bridge performance test (new in V2.0)

| Test items | Load parameters | SLO targets | Duration |
|--------|---------|---------|---------|
| G-Space acquisition P99 | 10 projects in parallel | < 500ms/acquisition cycle | 1h |
| φ decoding P99 | 50 concurrent requests | < 50ms | 30min |
| G-Space query P99 | 100 query/min | < 200ms (real-time), < 5s (history) | 30min |
| Discovery event processing | 10 events/min | < 2s | 30min |

---

## 13. Profile upgrade operation manual

```
Pre-requisite: Hardware in place + Helm values review + Level-0 + backup (Z-Buffer+LoRA+configuration)

Steps (Zero Downtime):
  1. Data layer expansion: PG Replica (Patroni) → Redis Cluster expansion node → Kafka Broker+rebalancing
  2. Brain Core expansion: Helm upgrade → Old Pod terminates after new Pod readiness → P99 verification
  3. Agent expansion: Update HPA max_replicas → CPU automatic expansion
  4. Configuration switching: SLO threshold + error budget reset + LLM budget update + orchestration quota update
  5. Verification: 1h soak test → All SLOs meet the standards
  
Rollback: Helm rollback < 10min
```

---

## 14. Phase Transition Operation Manual

```
Phase 0A→0B Access Control (PoC → Minimum Viable Brain):
  □ ARI > 0.2 (Z-Space meaningful clustering)
  □ φ R² > 0.2 (Z→G decoding is valid)
  □ Z exceeds G independently predicted (p < 0.05)
  □ Noise rate < 30% (Z_NOISE does not exceed the standard)
  □ PoC code review passed
  □ Complete data set (3 warehouses × Z+G alignment)

Phase 0→1 access control:
  □ MVLS three-layer TRL≥3 □ Inner ring 5 Agent LOA≥7 □ EIP 12 Agent integration test passed
  □ Error budget shadow calibration report approval □ Penetration test T1/T4/T5 passed □ Profile-M load test passed
  Feature Flags: FF_MIDDLE_RING_AGENTS→true, FF_ERROR_BUDGET_ENFORCE→true

Phase 1→2 Access Control:
  □ Z_arch/Z_logic TRL≥3 □ Middle ring 3 Agent LOA≥5 □ Cross-ring handover can be demonstrated
  □ The first external customer pilot □ Penetration test T2/T3 passed □ LLM cost compliance
  Feature Flags: FF_OUTER_RING_AGENTS→true, FF_FEDERATED_LEARNING→true

Phase 2→3 Access Control:
  □ All 12 Agents can be run □ Multi-tenant verification □ Cold start shortened by ≥50% □ SOC2 TypeII passed
  □ Self-evolving closed loop stable for 30 days □ Full Z-Layer TRL≥4
```

---

## 15. GPU optimized deployment configuration

### 15.1 Mixed precision and inference optimization Helm configuration

```yaml
# values.yaml GPU optimization configuration [V1.0.1]
gpu_optimization:
  mixed_precision:
    training: "bf16" # bfloat16 training
    inference: "fp16" # float16 inference
    gradient_accumulation: "fp32"
  gradient_checkpointing:
    jepa_predictor: true # Checkpoint every 2 layers
    context_encoder: true # Checkpoint every 3 layers
    alignment_trainer: true # Full weight calculation
  deepspeed:
    enabled: true
    config_file: "deepspeed/zero-stage1.json" # Phase 0
  tensorrt:
    enabled: false # Phase 1+ enabled (FF_TENSORRT_INFERENCE)
    precision: "fp16"
    max_batch_size: 32
  flash_attention:
    enabled: true # Flash Attention v2
    backend: "flash_attn"
  memory_budget:
    inference_gpu_utilization_target: 0.60
    training_gpu_utilization_target: 0.80
    max_vram_pct: 0.85 # Leave 15% headroom
```

### 15.2 Community Edition vs Enterprise Edition Deployment Profile

```
Community Edition deployment:
  Helm: values-community.yaml
  Features:
    ├── Profile-S only (Single Tenant, 1 project)
    ├── Inner ring 5 Agent + Brain Core + EIP Gateway
    ├── Long Term Memory: Enable (Episode + Semantic)
    ├── Auto-evolution: Enable (1 time per day)
    ├── Third-party Agent: enabled (free tier, ≤3)
    ├── Standalone API: Enable
    ├── Middle/Outer Ring Agent: Disabled
    ├── Federated Learning: Disabled
    ├── Multi-tenancy: Disabled
    └── SOC 2: Not included

  Minimum hardware:
    GPU: 1× RTX 3060+ (12GB VRAM) or Cloud A100
    CPU: 8 cores
    RAM: 32GB
    Storage: 50GB SSD

Enterprise Edition deployment:
  Helm: values-profile-m.yaml or values-profile-l.yaml
  Features: All features enabled
  Hardware: See §3.2 Resource Baseline
```

---

## 16. GPU monitoring alarm extension

```yaml
# GPU optimization related monitoring (added to §11 monitoring alarm matrix)
- alert: GPU_VRAM_High
  expr: uewm_gpu_memory_used_bytes / uewm_gpu_memory_total_bytes > 0.85
  labels: {severity: warning}
  annotations: {summary: "GPU VRAM usage {{ $value | humanizePercentage }} > 85%"}

- alert: GPU_VRAM_Critical
  expr: uewm_gpu_memory_used_bytes / uewm_gpu_memory_total_bytes > 0.95
  labels: {severity: critical}
  annotations: {summary: "GPU VRAM {{ $value | humanizePercentage }} > 95% — pause training"}

- alert: GPU_Utilization_Low
  expr: uewm_gpu_utilization_pct < 20
  for: 30m
  labels: {severity: warning}
  annotations: {summary: "GPU utilization {{ $value }}% < 20% for 30min — resource waste"}

- alert: GPU_TensorCore_Low
  expr: uewm_tensor_core_utilization_pct < 30
  for: 15m
  labels: {severity: info}
  annotations: {summary: "Tensor Core utilization {{ $value }}% — verify mixed precision enabled"}
```

---

## 17. PoC deployment specifications (new in V2.0)

```
Phase 0A PoC deployment (minimal, 8 weeks):

No K8s required — a local Python environment will do
  
  Hardware: Mac M5 Max or RTX 3060
  Storage: SQLite + local file system
  Dependencies: PyTorch, HuggingFace, scikit-learn, statsmodels, matplotlib
  
  Directory structure:
    uewm-poc/
    ├── data/
    │ ├── raw/ # GitHub API raw data
    │ ├── gspace/ # G-Space Parquet file
    │ ├── zspace/ # Z-Space encoding vector (256-d) [V2.0.1]
    │ └── voe/ # VoE test scenarios (100 scenarios) [V2.0.1]
    ├── models/
    │ ├── encoders/ # CodeBERT checkpoints
    │ ├── projections/ # Projection head weight (MLP+BN) [V2.0.1]
    │ ├── phi/ # φ decoder weight
    │ ├── probes/ # Probe weight (linear + MLP per metric) [V2.0.1]
    │ └── predictor/ # JEPA predictor weight
    ├── results/
    │ ├── gate_review/ # Gate Review results
    │ ├── probing/ # Dimension-by-dimension probing R² report [V2.0.1]
    │ ├── voe/ # VoE ROC curve + AUC [V2.0.1]
    │ ├── sigreg/ # SIGReg normality test + training curve [V2.0.1]
    │ └── visualizations/# t-SNE, R² chart
    └── scripts/
        ├── collect.py # G-Space data collection
        ├── encode.py # Z-Space encoding (including projection head) [V2.0.1]
        ├── train_phi.py # Bridge function training
        ├── train_jepa.py # JEPA predictor training (including SIGReg) [V2.0.1]
        ├── probe.py # Physical probe training + evaluation [V2.0.1]
        ├── voe_test.py # Violation of expected test [V2.0.1]
        ├── evaluate.py # Gate Review automation
        └── discover.py # Discovery Signal analysis
```

---

## 18. Acceptance criteria mapping

| AC | Design Support | Verification Methods |
|----|---------|---------|
| R05 AC-1 | §4.1 + §12.3 | k6 50 concurrent 60min |
| R05 AC-2 | §8.1 + §12.5 | Chaos Test: Kill pod |
| R05 AC-3 | §7 | CI/CD End-to-End Demonstration |
| R05 AC-4 | §12.2-12.4 | Three Profile independent testing |
| R05 AC-5 | §10 + §13 | Configuration Difference Review + Upgrade Manual |
| R05 AC-6 | §5.1 | Dashboard: budget+burn-rate+level |
| R05 AC-7 | §5.2 + §3.3 | L2 injection → pause delay <30s |
| R05 AC-8 | §5.2 + §12.3 | L3 injection → action <60s |
| R05 AC-9 | §6 + INTEG §3 | 30-day cost ≤ $5K |
| NFR-9 | §3.3 | GPU contention P99<600ms |
| **R05 AC-10: Community Edition independent deployment** | **§15.2** | **Profile-S Community Edition complete closed loop** |
| **NFR-12: GPU VRAM within budget** | **§15.1+§16** | **nvidia-smi peak monitoring** |
| **R05 AC-11: G-Space Acquisition P99 < 500ms** | **§12.8** | **Performance Test** |
| **R05 AC-12: φ decoding P99 < 50ms** | **§12.8** | **Performance Test** |
| **R05 AC-13: PoC can be deployed and run locally** | **§17** | **Mac/RTX independent operation verification** |
| **GND-AC-1: G-Space ≥80 indicators >95% collection rate** | **§11.4** | **Health Dashboard** |