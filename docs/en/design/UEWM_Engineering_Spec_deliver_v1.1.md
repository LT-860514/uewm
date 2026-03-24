# ⚙️ UEWM Engineering Specification

**Document version:** deliver-v1.1
**Document number:** UEWM-ENG-006
**Last update:** 2026-03-24
**Status:** Design completed (supports all AC verification + Long Memory timing diagram)
**Merge source:** Engineering Spec V2.0 + V3.0 + V4.0 (timing diagram/deployment/configuration) + V5.0 (EVALUATE expansion/closed-loop tracing) — full merge
**Benchmarking requirements:** Implementation-level specifications and timing interactions of all R01-R13

---

## 1. Overview

This document defines the implementation-level engineering specifications of the UEWM system, including key interaction sequence diagrams, component dependency matrices, deployment product specifications, configuration management specifications, and cold start protocols.

---

## 2. Key interaction sequence diagram

### 2.1 Sequence diagram 1: PREDICT request (Agent → Brain)

Agent sends PREDICT → EIP Gateway RBAC verification → Request Router routing → JEPA Predictor reads the current status from Z-Buffer → performs prediction → results return → audit log record.

### 2.2 Sequence diagram 2: REPORT_STATUS + surprise detection

Agent reports status → Perception Pipeline encoding → Z-Buffer update → JEPA comparison prediction vs actual → Calculate surprise degree → Super threshold → Trigger evolution.

### 2.3 Sequence diagram 3: EVALUATE including sandbox parallel preview```mermaid
sequenceDiagram
    autonumber
    participant Agent
    participant GW as EIP Gateway
    participant Router as Request Router
    participant EBM as EBM Arbiter
    participant JEPA as JEPA Predictor
    participant Audit as Audit Logger

    Agent->>GW: EipRequest(verb=EVALUATE, candidates=[A, B, C])
    GW->>Router: forward (RBAC OK)
    Router->>EBM: evaluate_candidates(candidates=[A,B,C], context)

    par sandbox parallel preview (GPU batch)
        EBM->>JEPA: sandbox_predict(candidate_A, steps=3)
        EBM->>JEPA: sandbox_predict(candidate_B, steps=3)
        EBM->>JEPA: sandbox_predict(candidate_C, steps=3)
    end
    JEPA-->>EBM: trajectory_A/B/C (3-step Z-Layer prediction trajectory)

    EBM->>EBM: compute_energy → E_A=0.45, E_B=0.22, E_C=0.38
    Note over EBM: Compare trajectory stability, not just final state energy
    EBM->>EBM: rank_by_energy() → [B(0.22), C(0.38), A(0.45)]
    EBM->>EBM: assess_risk(B) → LOW, check_safety_energy(B) → OK

    Router->>Audit: log(decision=EVALUATE, recommended=B, energies=[...])
    Router-->>GW: EipResponse(status=OK)
    GW-->>Agent: Returns the evaluation result
```### 2.4 Sequence diagram 4: ORCHESTRATE (SCHEDULE)

The orchestration module derives state from Z-Layer → orders task dependencies → returns recommended execution order.

### 2.5 Timing diagram 5: LOA cascade evaluation

TRL fallback event → ALFA recalculates LOA → Orchestration module identifies downstream → Assess impact → Kafka notification → Audit.

### 2.6 Sequence diagram 6: Orchestration module project health

Cron every 30s → the orchestration module reads signals from Z-Buffer/Agent/EBM → weighted synthesis → push to Dashboard.

### 2.7 Sequence diagram 7: cross-modal alignment training```mermaid
sequenceDiagram
    participant Cron as Alignment Scheduler
    participant AT as AlignmentTrainer
    participant TRL as TRL Evaluator
    participant GPU as Training GPU Pool

    Cron->>AT: trigger_alignment(stage=STAGE_1, layers=[Z_impl])
    AT->>TRL: check_prerequisites(STAGE_1, [Z_impl]) → OK
    AT->>GPU: request_training_gpu()
    alt GPU available
        GPU-->>AT: GPU-3 allocated
    else GPU busy (inference priority)
        Note over AT: Retry every 60s, max wait 30min
    end

    loop epoch 1..50
        AT->>AT: train_epoch(InfoNCE, temperature=0.07)
        AT->>AT: evaluate_ari = compute_ARI()
        alt ARI >= 0.3 (convergence)
            AT->>TRL: notify_alignment_complete → may upgrade TRL
        else ARI < 0.1 after 20 epochs (abort)
            AT-->>Cron: ABORTED
        end
    end
    AT->>GPU: release_training_gpu()
```### 2.8 Timing diagram 8: Error budget check and automatic downgrade

Prometheus collects every 10s → Error Budget Engine calculates burn-rate → Decision level → L2: Parallel pause evolution + lower priority (all completed within 30s) → 15min stable period after recovery → Downgrade to L0 → Resume evolution.

### 2.9 Sequence diagram 9: Regular self-reflection

Cron daily 03:00 UTC → 5-dimensional introspection (prediction consistency/causal graph health/cross-layer alignment/decision diversity/blind spot detection) → anomalies → inject evolution engine directed LoRA → audit.

### 2.10 Sequence diagram 10: Manual feedback learning

Human OVERRIDE → Brain EBM evaluation (current vs suggestion) → Calculate r_human → Buffer storage → 50 experience accumulation → Bias check (single user ≤30%, ≥3 roles) → Specialized LoRA training (lr=50%) → Security envelope check → ACCEPT/ROLLBACK.

### 2.11 Sequence diagram 11: Product version consistency detection

Agent SUBMIT_ARTIFACT → Z-Buffer record version → Orchestration module checks upstream reference → Version mismatch → Kafka ARTIFACT_ALERT → PM Dashboard + upstream and downstream Agent notification → ≤60s alarm.

### 2.12 Sequence diagram 12: external tool failure degradation

Adapter health_check failed → Required dependency failure → ALFA forces LOA≤4 → EIP LOA_UPDATE event → Orchestration module LOA cascade evaluation → Agent switches to degraded mode.

### 2.13 Complete closed-loop tracking: Observation → Surprise → Evolution → Verification```mermaid
sequenceDiagram
    participant Agent as AG-MA (monitoring)
    participant Percep as Perception
    participant ZBuf as Z-Buffer
    participant JEPA as JEPA Predictor
    participant Evo as Evolution Engine
    participant Envelope as Safety Envelope
    participant TRL as TRL Evaluator

    Note over Agent: Step 1: Report real observations
    Agent->>Percep: REPORT_STATUS(Z_phys: CPU=92%, latency=450ms)
    Percep->>ZBuf: update(Z_phys, z_phys_observed)

    Note over JEPA: Step 2: Compare forecast vs actual
    ZBuf->>JEPA: get_last_prediction(Z_phys)
    JEPA->>Evo: surprise = ||observed - predicted||² = 0.72

    Note over Evo: Step 3: Surprise > θ(0.3) → Trigger
    Evo->>Envelope: pre_evolution_check() → ALLOWED
    Evo->>Evo: multi_objective_evolution(n=5) → pareto_front → best
    Evo->>Envelope: post_evolution_check → ACCEPT

    Note over Evo: Step 4: Shadow Verification + Deployment
    Evo->>ZBuf: apply_new_lora()
    Evo->>TRL: notify → re-evaluate TRL

    Note over JEPA: Step 5: Verify closed loop
    Agent->>Percep: next observation
    JEPA->>Evo: new_surprise = 0.15 < 0.3 → Evolution is effective ✅
```### 2.14 Sequence Diagram 14: Memory Enhancement Decision (EVALUATE + Memory) [New in deliver-v1.1]```mermaid
sequenceDiagram
    autonumber
    participant Agent
    participant EBM as EBM Arbiter
    participant Mem as Long Memory
    participant Profile as Project Profile
    participant Audit as Audit

    Agent->>EBM: EVALUATE(candidates=[A,B])
    par parallelism: memory retrieval + energy calculation
        EBM->>Mem: recall(z_snapshot, changed_layers=[Z_impl])
        Mem->>Mem: vector_search → 3 similar Episodes
        Mem->>Mem: graph_query(Z_impl, 2 hops) → 2 CAUSAL Facts
        Mem->>Profile: get → {static, dynamic, risk:["DB migration 2/3 downtime"]}
        Mem-->>EBM: MemoryContext
        EBM->>EBM: sandbox_predict(A,B) → E_A, E_B
    end
    EBM->>EBM: ANTI_PATTERN matches A → E_A+=20%, PREFERENCE tends to B → E_B-=5%
    EBM-->>Agent: recommended=B + MemoryInfluence(episodes, facts)
    EBM->>Audit: log(decision + memory_influence)
```### 2.15 Sequence Diagram 15: Memory Consolidation (Daily Consolidation) [New in deliver-v1.1]```mermaid
sequenceDiagram
    autonumber
    participant Cron as 03:00 UTC
    participant Consol as Consolidation
    participant EpiStore as Episodic (PG)
    participant FactExt as Fact Extractor
    participant SemStore as Semantic (Neo4j)
    participant Profile as Profile (Redis)

    Cron->>Consol: trigger
    Consol->>EpiStore: decay_cleanup (archive decay<0.05)
    Consol->>EpiStore: get_new_episodes(24h)
    Consol->>FactExt: extract → check contradictions → insert/invalidate
    Consol->>SemStore: update_confidence + decay_stale
    Consol->>Profile: regenerate(static+dynamic+risk)
```---

## 3. Component dependency matrix

### 3.1 Startup sequence

PostgreSQL → Redis → Kafka → Vault → **Neo4j** → Brain Core (Z-Buffer→Perception→JEPA→EBM→**Long Memory**→Orchestrator→Evolution→TRL) → EIP Gateway → Agents (Inner Ring → Middle Ring → Outer Ring) → Portal API

### 3.2 Dependencies between components

| Components | Strong dependencies | Weak dependencies |
|------|--------|--------|
| Brain Core | PostgreSQL, Redis | Kafka (bufferable), Vault (cacheable) |
| EIP Gateway | Brain Core | Kafka |
| Agent | EIP Gateway | External tools (downgrade operation) |
| Evolution Engine | Z-Buffer, MLflow | DVC, GPU (can be queued) |
| **Long Memory** | **PostgreSQL+pgvector, Neo4j, Redis** | **S3 (warm/cold storage)** |

---

## 4. Component mapping

Architecture 12 Components → Engineering Spec Module Mapping:
- `uewm/brain-core` container: Z-Buffer + JEPA + EBM + Orchestrator + TRL + Error Budget + Request Router
- `uewm/perception` container: Perception Pipeline + 8 Encoders + AlignmentTrainer
- `uewm/evolution` container: Evolution Engine + Safety Envelope + Circuit Breaker + Pareto + Bias + Reflection + Knowledge
- `uewm/eip-gateway` container: EIP Gateway + gRPC Router + RBAC Enforcer
- `uewm/agent-{type}` Container: Agent Framework + ALFA + Adapters + Execution Engine
- `uewm/portal-api` container: Portal REST API + WebSocket

---

## 5. Key protocols and processes

### 5.1-5.6 EIP message flow/evolution trigger/downgrade switching

For details, see EIP Protocol §4, Self Evolution §11, Agents Design §4.

### 5.7 Cold start protocol```
Phase A — Passive Observation (Day 1-7):
  REPORT_STATUS only, no PREDICT. TRL Evaluator evaluates every 6h.
  Measuring point M1: TRL-0 Acknowledgment timestamp

Phase B - Knowledge Transfer (Day 3-10, parallel to A):
  The orchestration module checks available knowledge sources (by KSL). Privacy Budget Manager controls migration.
  TRL re-evaluation is triggered immediately after each migration.

Phase C — Progressive Enablement (Day 7+):
  ALFA automatically calculates LOA based on TRL. TRL<3→INFORMATION_ONLY.
  Measuring point M2: TRL-1 achieved (ARI>0 but <0.3)
  Measuring point M3: TRL-2 achieved (ARI≥0.3)
  cold_start_duration = M3 - M1

Phase D - Completion Determination:
  Full MVLS layer surprise < 0.5 → cold start completed
  Measuring point M4: Cold start complete
```### 5.8 Data pipeline verification integration

Training pipeline: collection → cleaning → encoding → **VectorQualityValidator** → warehousing → versioning. Trigger: DVC pre-commit → MLflow post-training → LoRA post-evolution → monthly cron. Blocking rules: NaN>0→hard blocking, all zeros>1%→hard blocking, L2 abnormality>10%→soft blocking. Warning: L2 abnormality 5-10%, cosine>0.65, low variance>5%.

---

## 6. Deploy product specifications

### 6.1 Container image list

| Image | Base Image | GPU |
|------|---------|-----|
| `uewm/brain-core` | pytorch:2.x-cuda12 | Yes |
| `uewm/perception` | pytorch:2.x-cuda12 | Yes |
| `uewm/evolution` | pytorch:2.x-cuda12 | Yes |
| `uewm/eip-gateway` | golang:1.22-alpine | No |
| `uewm/agent-{type}` | python:3.12-slim | No (AG-CD optional) |
| `uewm/portal-api` | node:20-alpine | No |

### 6.2 Helm Chart Structure```
helm/uewm/
├── Chart.yaml
├── values.yaml (Profile-S default)
├── values-profile-m.yaml
├── values-profile-l.yaml
├── templates/
│ ├── brain-core/ (2 replicas Active-Standby, no HPA)
│   ├── eip-gateway/ (3 replicas Active-Active, HPA CPU 80%)
│ ├── agents/ (one Deployment + HPA per Agent type)
│   ├── data/ (PostgreSQL/Redis/Kafka/Milvus/Neo4j StatefulSets)
│   ├── monitoring/ (Prometheus/Grafana/OTel)
│   ├── security/ (Vault/cert-manager/NetworkPolicies)
│   └── namespaces.yaml
```### 6.3 CI/CD Pipeline

CI: Lint+Tests → Protobuf compilation + Schema compatibility (buf) → Integration testing (EIP closed loop) → Security scanning (Trivy+Semgrep) → Container building (multi-arch) → Harbor push. CD: Staging deployment → 1h soak → Canary 10% → Full release → 5min health check.

---

## 7. Configuration management specifications

### 7.1 Configuration level (high → low priority)

Runtime Override (K8s ConfigMap hot-reload) → Profile Override (values-profile-*.yaml) → Default Values (values.yaml) → Code Defaults

### 7.2 Profile differentiated configuration

| Configuration items | Profile-S | Profile-M | Profile-L |
|--------|-----------|-----------|-----------|
| brain.replicas | 1 | 2 (Active-Standby) | 2 + sharded by tenant |
| brain.gpu_count | 2 | 4 | 8 |
| agent.{type}.max_replicas | 2 | 5 | 20 |
| slo.brain_p99_ms | 300 | 500 | 1000 |
| evolution.max_per_day | 1 | 5 | 15 |
| llm.monthly_budget_usd | 500 | 5000 | 25000 |
| audit.storage_budget_tb | 1 | 10 | 50 |
| error_budget.shadow_mode | true(Phase 0) | true(Phase 0) | false |

### 7.3 Feature Flags

| Flag | Default | Description |
|------|------|------|
| FF_EVOLUTION_ENABLED | false (early phase 0) | Evolution engine master switch |
| FF_FEDERATED_LEARNING | false | Federated Learning (Phase 2+) |
| FF_ERROR_BUDGET_ENFORCE | false (shadow) | Error budget execution vs shadow |
| FF_OUTER_RING_AGENTS | false | Outer Ring Agent (Phase 2+) |
| FF_MIDDLE_RING_AGENTS | false | Middle Ring Agent (Phase 1+) |
| FF_LLM_COST_ENFORCE | true | LLM cost ceiling |
| FF_ALIGNMENT_TRAINING | true | Cross-modal alignment training |

### 7.4 Configuration change audit

All changes are recorded in the audit log through Git (values.yaml) or K8s ConfigMap change events: changer, diff, time, and associated PR number.