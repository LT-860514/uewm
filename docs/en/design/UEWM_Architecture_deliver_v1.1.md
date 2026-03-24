# 🧠 UEWM core architecture design document

**Document version:** deliver-v1.1
**Document Number:** UEWM-ARCH-001
**Last update:** 2026-03-24
**Status:** Design completed (100% coverage of R01, R05, R07, R11, NFR-1/2/3/8/9/11 + Long Memory MEM-AC-1~10)
**Combined source:** Architecture V7.0 + Combined Patch + Long Memory Subsystem — Full merger
**Change History:**
- V4.0–V7.0: orchestration module, TRL, MVLS, concurrency, calibration, alignment, POMDP, verification protocol, sharding, asynchronization
- deliver-v1.0: Full merging, no dependency on incremental patches
- **deliver-v1.1: Added §12 long-term memory subsystem (Episodic/Semantic Memory + Consolidation + Retrieval + Project Profile)**

---

## 1. Document purpose and scope

This document defines the core architecture design of UEWM, covering: H-JEPA hierarchical prediction architecture, latent space (Z-Layer) hierarchical system and TRL maturity model, EBM arbitration engine and calibration plan, Brain Core orchestration module (including asynchronous design), multi-project concurrency model and tenant sharding, cross-modal alignment training implementation, error budget and SLO default response, and system integration topology.

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
| P9 | Active introspection | Regular self-reflection |
| P10 | Human-machine collaboration | Role engineers can intervene at any time |
| P11 | Uncertainty perception | Probability distribution representation + information acquisition trigger under POMDP framework |
| P12 | Gradual maturity | TRL drives system behavior, and immature layers are automatically degraded |
| P13 | Orchestration is decision-making | Cross-Agent orchestration is the execution function of Brain Core |

---

## 3. Overall system architecture

### 3.1 Four-layer bionic architecture```
┌─────────────────────────────────────────────────────────────────────┐
│ Level Zero: External World │
│ Code warehouse / CI/CD / Monitoring platform / User feedback / Market data / Log system │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Raw Signals
┌──────────────────────────────▼──────────────────────────────────────┐
│The first layer: Multi-modal perception layer (Perception Layer) │
│  Code Encoder │ Doc Encoder │ Metric Encoder │ Market Encoder        │
│  (AST+CFG→Z)  (NL→Z)       (TS→Z)           (Tabular→Z)           │
│         └──────────┴────────┬───────┴──────────────┘                │
│                   Projection & LayerNorm → 2048-d                   │
│ AlignmentTrainer (cross-modal alignment) │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│ Second level: H-JEPA Brain Core │
│  Z-Buffer Manager ← Z_market|Z_val|Z_biz|Z_logic|Z_arch|           │
│                      Z_impl|Z_quality|Z_phys                        │
│ H-JEPA Predictor ◄► Cross-layer causal graph ◄► EBM energy arbitration engine │
│ Long-term memory subsystem (episodic memory + semantic memory + consolidation + retrieval) [deliver-v1.1] │
│ Orchestration module (7 capabilities, including asynchronous) │
│ TRL Maturity Evaluator │
│ Error budget engine (Burn-Rate/level 4 alarm) │
│ Self-evolving engine (Safety Envelope/Circuit Breaker/Pareto) │
│ Self-reflection engine │ Cross-project knowledge engine │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ EIP Protocol (gRPC + Kafka + Stream)
┌──────────────────────────────▼──────────────────────────────────────┐
│ Layer 3: EIP Gateway (RBAC/mTLS/DynamicPermission) │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│The fourth layer: Agent terminal array (three-ring layered) │
│ Outer ring: AG-PA │ AG-PD │ AG-BI │ AG-PR (Phase 2, LOA 3-5) │
│ Central: AG-SA │ AG-FD │ AG-AU (Phase 1, LOA 5-7) │
│ Inner ring: AG-CD │ AG-CT │ AG-DO │ AG-ST │ AG-MA (Phase 0, LOA 7-9)│
└─────────────────────────────────────────────────────────────────────┘
```### 3.2 Brain Core internal component list

| # | Components | Responsibilities | Benchmarking Requirements |
|---|------|------|---------|
| 1 | Z-Buffer Manager | 8-layer hidden state read and write/snapshot/version | R01 |
| 2 | Perception Pipeline + AlignmentTrainer | Encoder Management/Projection/Cross-modal Alignment | R01, R12 |
| 3 | H-JEPA Predictor | Multi-timescale state prediction | R01 |
| 4 | Causal Graph Engine | Granger causal graph construction/query/backtracking | R01 |
| 5 | EBM Arbiter (including calibration plan) | Energy Arbitration/Sandbox Preview/Kendall τ Calibration | R01 |
| 5.1 | **Long Memory Subsystem** | **Episode Memory/Semantic Memory/Consolidation Engine/Retrieval Engine/Project Profile** | **R01,R03,R06,R10** |
| 6 | Orchestration Module (including asynchronous) | Task sequencing/handover/arbitration/milestones/conflicts | R01 G6, Gap-2 |
| 7 | TRL Evaluator | Z-Layer maturity automatic assessment/dynamic weight reduction | R01 G1-S1 |
| 8 | Evolution Engine | Safety Envelope/Circuit Breaker/Pareto/LoRA | R03 |
| 9 | Self-Reflection Engine | Regular introspection/blind spot detection/deviation analysis | R06 |
| 10 | Knowledge Engine | KSL Distillation/Privacy Budget/Federated Learning | R08 |
| 11 | Error Budget Engine | Burn-Rate/Level 4 Alarm/Automatic Downgrade | R05 Gap-1 |
| 12 | Request Router | Request distribution/response aggregation | R11 |

### 3.3 Orchestration Module

#### 3.3.1 Design positioning

Brain Core's "executive function" is alongside JEPA Predictor and EBM Arbiter. Derive project-level meta signals from Z-Layer signals, without introducing a standalone Z-Layer. Not the 13th Agent.

#### 3.3.2 Internal structure

Task Dependency Scheduler → Cross-Ring Handoff Evaluator → Resource Contention Arbiter → Milestone Tracker → LOA Cascade Assessor → Project Status Synthesizer → Cross-Agent Conflict Resolver

#### 3.3.3 Input signal

Schedule risk is derived from Z-Layer TRL progress; delivery risk is derived from Agent historical performance; quality risk is derived from EBM energy trend; project_health_score is derived from comprehensive weighting.```python
class OrchestratorInputSignals:
    """The orchestration module derives project-level meta signals from existing Z-Layer signals."""
    
    def derive_project_health(self, project_id):
        signals = {}
        for layer in self.get_project_layers(project_id):
            trl = self.get_trl(layer)
            target_trl = self.get_target_trl(layer, current_phase)
            signals[f"{layer}_progress_gap"] = target_trl - trl
        
        for agent_id in self.get_project_agents(project_id):
            perf = self.get_performance(agent_id)
            signals[f"{agent_id}_reliability"] = perf.success_rate
            signals[f"{agent_id}_current_loa"] = self.alfa.compute_effective_loa(agent_id, None)
        
        energy_trend = self.get_energy_trend(project_id, window_days=7)
        signals["energy_trend"] = energy_trend
        signals["project_health_score"] = self.weighted_aggregate(signals)
        return signals
```#### 3.3.4 Seven core competencies

| Capabilities | Outputs | SLO | Sync/Async |
|------|------|-----|----------|
| Task dependency sorting | Recommended execution order | < 2s | Synchronization |
| Cross-ring handover evaluation | Ready/Blocked+Reason | < 5s | Synchronization |
| Resource contention arbitration | Assign priority | < 1s | Asynchronous execution |
| Milestone Tracking | Deviation Report | < 1min | Asynchronous (every 30s) |
| LOA cascade assessment | Impact analysis | < 30s | Asynchronous event-driven |
| Project status synthesis | Structured report | ≤ 30s | Asynchronous (every 30s) |
| Cross-Agent conflict reconciliation | Arbitration/escalation | < 10s | Asynchronous |

#### 3.3.5 Interaction with EIP

Receive synchronous requests (SCHEDULE, HANDOFF_CHECK) via the ORCHESTRATE verb. Send asynchronous notifications (DIRECTIVE, LOA_UPDATE) via Kafka events.

#### 3.3.6 Asynchronous design```
Orchestration operation classification (synchronous vs asynchronous):

  Synchronization (blocking Agent requests, must be completed within Brain SLO):
    ├── SCHEDULE (task sorting query): < 2s → directly returns the current schedule
    └── HANDOFF_CHECK (handover readiness query): < 5s → Return the evaluation result directly

  Asynchronous (no blocking Agent, background execution + event notification):
    ├── RESOLVE_CONFLICT (Conflict Arbitration): May require multiple Agent information → Asynchronous processing → Kafka event notification
    ├── Milestone tracking update: background timing (every 30s) recalculation
    ├── LOA cascade evaluation: LOA change event trigger → asynchronous evaluation → notification within 30s
    ├── Comprehensive project health: background timing (every 30s) recalculation → Push Dashboard
    └── Resource arbitration execution: Scheduling decision → Kafka event → K8s Scheduler asynchronous execution

  Queue depth protection:
    ├── Asynchronous orchestration task queue: max depth = 100
    ├── More than 100 → discard the lowest priority task + alert
    └── Queue processing delay > 30s → Alarm DEVOPS

  Impact on LOA 7+ Agent:
    Agents with LOA ≥ 7 can execute autonomously without waiting for a synchronous response from the orchestration module.
    Scheduling recommendations for the orchestration module are issued in the form of asynchronous DIRECTIVE
    Agent can choose to follow or ignore (recorded in audit log)
```### 3.4 Multi-project orchestration concurrency model

Three-level scheduling: L1 weighted fair sharing (default) → L2 priority preemption (high voltage) → L3 tenant isolation (strong isolation).```
L1 Weighted Fair Share — Default mode:
  Each Tenant receives a share of resources proportional to its SLA level. Projects within the same Tenant are distributed according to priority weight.
  Free shares can be temporarily borrowed by other projects (preemptible, borrowing delay ≤ 5s return). Applicable: Normal operation, Profile-S/M.

L2 Priority Preemption — High Stress Mode:
  Trigger: Agent request queue depth > 3x normal value or SLO burn-rate > 5%/h.
  High-priority projects can preempt the Agent time slice of low-priority projects. The preempted task is suspended (not discarded) and will be automatically resumed after recovery.

L3 Tenant Isolation — Strong isolation mode:
  Trigger: Any Tenant's SLO fails to meet the standard for 10 consecutive minutes. Each Tenant Agent instance and GPU quota are fully isolated.
  Applicable to: Profile-L, or Tenants whose contracts require resource isolation.
```Per-Tenant quota: Profile-S 5 concurrency/1 project, Profile-M 50 concurrency/10 projects, Profile-L 200 concurrency/50 projects. Agent Concurrency: Maximum 5 instances per type of Profile-M.```python
class TenantResourceQuota:
    PROFILE_QUOTAS = {
        "Profile-S": {"max_concurrent_agent_tasks": 5, "max_projects": 1, "gpu_share_pct": 100, "evolution_slots_per_day": 1},
        "Profile-M": {"max_concurrent_agent_tasks": 50, "max_projects": 10, "gpu_share_pct": None, "evolution_slots_per_day": 5},
        "Profile-L": {"max_concurrent_agent_tasks": 200, "max_projects": 50, "gpu_share_pct": None, "evolution_slots_per_day": 15},
    }
    
    def can_schedule(self, tenant_id, agent_type, project_id):
        quota = self.get_tenant_quota(tenant_id)
        current_usage = self.get_current_usage(tenant_id)
        if current_usage.concurrent_tasks >= quota["max_concurrent_agent_tasks"]:
            return ScheduleVerdict.QUEUED(reason="tenant_quota_exceeded")
        return ScheduleVerdict.ALLOWED
```### 3.5 Component mapping table

Mapping of Architecture 12 components vs Engineering Spec 9+2 modules: Self-Reflection and Knowledge Engine are classified into the Evolution Engine sub-package in Eng Spec (code perspective vs functional perspective). See Engineering Spec §2.1 for details.

### 3.6 Tenant sharding architecture```
Tenant sharding design:
  Shard key: tenant_id (consistent hash), ≤ 10 Tenants/shard
  Sharding instance: Each shard is an independent Brain Core Deployment (Active-Standby)
  
  Profile-S: 1 shard (single tenant)
  Profile-M: 1 shard (≤10 tenants)
  Profile-L: N shards (N = ceil(tenant_count / 10))

  Cross-shard query:
    ├── Z-Buffer: Each shard is independent (no cross-shard query)
    ├── EBM evaluation: completed within shards (no cross-shard data required)
    ├── Federated learning: coordinated across shards by Knowledge Engine (independent component)
    └── Orchestration module: Intra-shard orchestration; cross-shard resource arbitration is handled by the global Orchestrator Coordinator

  Shard rebalancing:
    ├── Trigger: Number of Tenants in the shard > 10 or uneven load (CPU difference > 30%)
    ├── Method: Create a new shard → Migrate Tenant’s Z-Buffer + LoRA → Switch routing → Delete old shard data
    ├── Downtime: The Tenant’s Brain requests are queued during migration (estimated < 5min)
    └── Automation: K8s Operator manages the sharding life cycle

  EIP Gateway routing:
    EIP Gateway maintains tenant_id → shard_id mapping table
    Each EipRequest is routed to the correct Brain Core shard based on project_id → tenant_id → shard_id
```---

## 4. Hidden space layered design (Z-Layers)

### 4.1 Level definition

8 layers: Z_market(week/month) → Z_val(quarter) → Z_biz(week) → Z_logic(day) → Z_arch(day) → Z_impl(hour) → Z_quality(hour) → Z_phys(minute). Each layer outputs 2048-d vectors.

### 4.2 Inter-layer causal association diagram

Dynamic causal topology G=(V,E), Granger causality test (p<0.05) automatically discovers causal edges. Main chain: Z_market→Z_val→Z_biz→Z_logic→Z_arch→Z_impl→Z_quality, Z_impl→Z_phys. Feedback: Z_phys→Z_arch, Z_quality→Z_logic, Z_phys→Z_val, Z_quality→Z_val.

### 4.3 TRL Maturity Assessment Subsystem```
TRL-0 (concept): The encoder architecture is determined, but there is no training data and the latent space is meaningless
TRL-1 (prototype): Encoder produces vectors, but semantic clustering ARI < 0.3
TRL-2 (validation): Semantic clustering ARI ≥ 0.3, but cross-layer causality not verified
TRL-3 (integrated): One-way causality can be detected (this layer → neighbor layer Granger p<0.05)
TRL-4 (Mature): Bidirectional causal transmission is reliable, predicted MSE < 0.1, and can support Agent decision-making
TRL-5 (self-optimization): Self-evolution closed-loop verification passed, surprise degree converged
```TRL↔System behavior: Agent autonomy (TRL<3→not autonomous), EBM weight (TRL<3→0.1x), causal backtracking (TRL<3→one-way), evolutionary training (TRL<2→data collection only), manual intervention (TRL<3→must be approved).

Evaluation frequency: Daily 02:00 UTC + immediately after evolution + cold start every 6h.

### 4.4 MVLS minimum feasible latent space

Z_impl + Z_quality + Z_phys. Verification criteria: Z_impl→Z_quality direction accuracy >70%, Z_quality→Z_impl backtracking >60%, Z_phys anomaly prediction F1>0.6, cross-project variance <20%.

Expansion path: Phase 0 (3-layer TRL-3) → Phase 1 (+Z_arch, Z_logic) → Phase 2 (+Z_biz, Z_val) → Phase 3 (all 8-layer TRL-4+).

### 4.5 Cross-modal alignment training implementation

AlignmentTrainer as a Perception Pipeline submodule. Three stages:

Stage 1 intra-domain comparison (InfoNCE, ARI≥0.3): Z_impl at different time points for the same project should be closer than those for different projects. Stage 2 adjacent layer alignment (cross-modal comparison + causal prediction, MSE improvement >30%): Z_impl and Z_quality of the same project at the same time point should be closer than random pairing. Stage 3 Global Union (VICReg regularization, causal graph efficiency >80%): All layers form a unified semantic space.

Each stage has convergence criteria and termination conditions. Only use the training GPU pool (NFR-9). Phase 0 timeline: Week 1-4 Stage 1 (3 layers), Week 5-8 Stage 2 (3 pairs), Week 9+ MVLS verification.

---

## 5. H-JEPA hierarchical prediction engine

### 5.1-5.3 JEPA Core/Dynamics/Multiple Timescales

Context Encoder → Target Encoder (EMA) → Predictor (T-GCN + Transformer-XL). Predict Z vectors instead of tokens. Micro (minute → hour) / meso (day → week) / macro (month → quarter) three-level calculation.

### 5.4 POMDP uncertainty modeling

Z^(l) ~ N(μ^(l), Σ^(l)). Low tr(Σ)→Cognition is sufficient, high tr(Σ)→triggers information acquisition.

#### 5.4.1 Information acquisition triggering mechanism```python
class UncertaintyTriggeredActions:
    """Information acquisition strategy when Z-Layer uncertainty (tr(Σ)) exceeds the threshold."""
    
    UNCERTAINTY_THRESHOLDS = {
        # Layer: (moderate_threshold, high_threshold, critical_threshold)
        "Z_impl":    (0.5, 1.0, 2.0),
        "Z_quality": (0.5, 1.0, 2.0),
        "Z_phys": (0.3, 0.8, 1.5), # The physical layer is more sensitive to uncertainty
        "Z_arch":    (0.8, 1.5, 3.0),
        "Z_logic":   (0.6, 1.2, 2.5),
        "Z_biz":     (1.0, 2.0, 4.0),
        "Z_val":     (1.0, 2.0, 4.0),
        "Z_market": (1.5, 3.0, 5.0), # The market level has the highest uncertainty
    }
```MODERATE→Agent additional observation (LOA cap=7), HIGH→Request manual + LOA cap=5, CRITICAL→Delay decision + EBM weight temporarily reset to zero + orchestration blocking (LOA cap=3).

Uncertainty dashboard: real-time value of each layer tr(Σ) + threshold line, refreshed in 30s.

### 5.5-5.7 Hierarchical calculation/alignment protocol/end-to-end training

The MVLS stage only enables micro+real-time physical layer calculations, and macro/meso runs in Mock mode.

### 5.8 JEPA Predictor Verification Protocol```python
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
```---

## 6. EBM energy arbitration engine

### 6.1 Global energy function

E_total = Σ w_l^eff · Ẽ_l + λ_cross · E_cross + λ_safe · E_safety. w_l^eff = w_l × TRL_weight(l). TRL<3→weight 0 or 0.1.

### 6.2 Dimension/risk mapping/sandbox preview/automatic weight tuning

Quantile normalization → [0,1]. LOW[0,0.3)/MEDIUM[0.3,0.5)/HIGH[0.5,0.7)/CRITICAL[0.7,1.0]. Multi-scheme GPU batch parallel simulation to compare trajectory stability. Meta-learning automatically adjusts weights every week/every 100 decisions.

### 6.3 EBM Calibration Plan

**Calibration data set:** 200 pairs of paired comparison samples (5 types of decisions × 40-50 pairs each), 3-5 experts blind review, Dawid-Skene aggregation, minimum agreement rate 60%.

**Calibration process:** Step 1(Week 1-3): Build calibration set → Step 2(Week 4): Baseline τ measurement (expected ~0.2-0.3) → Step 3(Week 5-6): Bayesian optimization weights (Optuna+cross-validation) → Step 4(Week 7): Verify τ≥0.5 on 30% held-out → Step 5(Phase 1+): Supplement 50 samples + re-evaluation every quarter.

Calibration data version: DVC management, `datasets/calibration/v{X}/calibration_pairs.parquet`.

---

## 7. Engineering Intelligence Protocol (EIP)

Alignment to R11 V3.0 strongly typed conventions. See `UEWM_EIP_Protocol.md` for the complete IDL definition. Request/Response/Event/Stream four message types. 6 Agent→Brain verbs + 4 Brain→Agent verbs.

### 7.5 Error Budget and SLO Breach Response Architecture

Brain Core 99.95% (21.6min/month), EIP Gateway 99.99% (4.3min), Agent 99.9% (43.2min), End-to-End 99.5% (216min).

Level 4 Burn-Rate: L1 (observation, 1h>2x) → L2 (warning, 6h>5x, pause evolution) → L3 (critical, <20%, freeze new items) → L4 (exhausted, changes frozen).

SLO breach linkage: Brain exceeds standard → Evolution paused + LOA reduced by 1 level + Reflection postponed + Orchestration reduced. Agent exceeds the standard → LOA ≤ 4 + arrangement mark is limited. EIP Gateway exceeds the standard → full system + orchestration cache mode.

---

## 8-9. Data stream/encoder

Forward evolution flow (Idea→online), reverse evolution flow (accident→self-correction), and orchestration interaction flow.

8 encoder matrices include selection arguments (§9.2): CodeBERT(Z_impl), TFT(Z_quality trained from scratch), TimesFM(Z_phys), GraphSAGE+BERT(Z_arch), BERT/RoBERTa(Z_logic), TabNet+FinBERT(Z_biz/Z_val/Z_market). Each layer contains reasons for selection, alternatives, and reasons for rejection.

Projection adaptation layer→2048-d. Vector database: Phase 0 pgvector → Phase 1+ Milvus.

---

## 10. Technology selection

PyTorch 2.x, DeepSpeed/FSDP, vLLM/TensorRT, gRPC+Protobuf, Kafka, Redis+PostgreSQL, Neo4j, pgvector→Milvus, MLflow+DVC, Kubernetes, Prometheus+Grafana+OTel.

---

## 12. Long Memory Subsystem [New in deliver-v1.1]

### 12.1 Design motivation

Currently UEWM's Z-Buffer only maintains working memory (current state), and LoRA weights only encode procedural memory (implicit skills). The system lacks the episodic memory ("what happened last time") and semantic memory ("summative patterns") of the human brain. This results in the Brain Core being able to predict but not recall, and being able to learn but not be able to make decisions based on historical experience.

### 12.2 Three-layer memory model```
Layer 1: Working Memory — Z-Buffer [Existing]
  Stores the current Z-Layer vector, overwritten with each observation

Layer 2: Episodic Memory — [New]
  Storage: specific events (decision/accident/evolution/human intervention) and their Z-Layer snapshots and results
  Format: Episode = {trigger, Z-snapshot, decision, result, energy, surprise, timestamp, project}
  Capacity: 1K(Phase 0) → 5K(Phase 1) → 10K(Phase 2+) per project
  Index: time + Z vector similarity (pgvector ANN) + causal label + result label
  Purpose: "The last time a Z_impl-like pattern occurred, deployment caused a P99 spike"

Layer 3: Semantic Memory — [New]
  Storage: Stable facts (causality/patterns/anti-patterns/preferences) extracted from multiple episodes
  Format: Fact = {Topic, Relationship, Object, Confidence, Validity, SourceEpisode}
  Capacity: ~200(Phase 0) → ~1000(Phase 2+) per item
  Index: Neo4j Knowledge Graph (Entity-Relation-Entity)
  Purpose: "Increased code complexity on this project typically results in decreased test coverage within 72h"
```### 12.3 Episodic memory

#### Episode data structure```python
class Episode:
    episode_id: str;  project_id: str;  tenant_id: str;  timestamp: datetime
    trigger_type: str    # DECISION / INCIDENT / EVOLUTION / HUMAN_INTERVENTION / REFLECTION
    z_snapshot: Dict[str, bytes] # Z-Buffer slice frozen at decision time
    decision_summary: str;  decision_energy: float;  outcome: str;  outcome_energy: float
    surprise_score: float;  was_human_overridden: bool;  human_feedback: Optional[str]
    importance_score: float # [0,1] Multi-factor weighting
    decay_factor: float # Ebbinghaus decay [0,1]
    recall_count: int;  last_recalled: datetime
    extracted_fact_ids: List[str]
    ksl_level: int # Inherit project KSL
```#### Episode trigger rules

EVALUATE completed→create DECISION Episode, surprise exceeds threshold→INCIDENT Episode, LoRA evolution completed→EVOLUTION Episode (importance=1.0), manual intervention→HUMAN_INTERVENTION Episode, self-reflection exception→REFLECTION Episode.

#### Importance Rating```python
importance = (surprise × 0.25) + (energy_delta × 0.20) + (human_override × 0.20) 
           + (failure_value × 0.15) + (risk_level × 0.10) + (recall_boost × 0.10)
```#### Ebbinghaus decay

decay = exp(-0.1 × days_since) × exp(-0.05 × days_since_recall) × (0.5 + 0.5 × importance). Episodes with importance > 0.8 are never archived (milestone events).

### 12.4 Semantic memory

#### Fact data structure```python
class Fact:
    fact_id: str;  project_id: str;  tenant_id: str
    subject: str; relation: str; object: str # Knowledge triple
    confidence: float;  valid_from: datetime;  valid_until: Optional[datetime]
    is_invalidated: bool;  invalidated_by: Optional[str]
    source_episode_ids: List[str];  min_episodes_required: int = 3
    fact_type: str   # CAUSAL / CORRELATION / PREFERENCE / PATTERN / ANTI_PATTERN / TEMPORAL
    ksl_level: int
```#### Fact extraction rules

3+ Consistent Episode Same Z-Layer change direction → Same result → CAUSAL Fact. 3+ Similar Z Snapshot → FAILURE → ANTI_PATTERN Fact. 3+ Manual overwriting of similar decisions → PREFERENCE Fact. 4+ Periodic Repeat → TEMPORAL Fact.

#### Conflict handling

When extracting new Facts, scan existing Facts with semantic similarity >0.8. When there is a contradiction: time priority (new overturns old) + frequency weighting (more support for Episode wins). Old Fact flag is_invalidated=true. When the confidence level is close (difference <0.1), upgrade to manual confirmation.

### 12.5 Memory Consolidation Engine

Runs daily at 03:00 UTC (synchronized with self-reflection). Stage 1(5min): Episode decay cleaning→archive cold storage. Stage 2 (10min): New Episode fact extraction → contradiction detection → confirmation writing. Stage 3(5min): Fact confidence has been updated (new support ↑, long-term no support ↓). Stage 4(2min): Project Profile generation.

Consolidation drives evolution: ANTI_PATTERN Fact → Inject evolution engine directed training. Conflict resolution → trigger LoRA fine-tuning. Evolution outputs consolidation material: Evolution Episode(importance=1.0) → Extract evolution effectiveness Fact.

### 12.6 Project Profile```python
class ProjectProfile:
    """Automatically generated from semantic memory, queryable in ~50ms, injected into every EBM/JEPA decision."""
    
    static_facts: List[str] # Stable features (changes slowly)
    # "Python/Go dual language, microservices, 12 services", "Test coverage is stable 78-82%"
    
    dynamic_context: List[str] # Recent activities (frequently updated)
    # "The payment service is being reconstructed (Z_impl changes frequently)", "The last deployment caused a spike in P99 and has been rolled back"
    
    risk_memories: List[str] # Extracted from FAILURE Episodes
    # "Large-scale DB migrations have historically resulted in downtime 2/3 times"
```Profile injection: PREDICT→affects uncertainty estimation (risk→increase Σ), EVALUATE→affects energy weight (PREFERENCE→-5%, ANTI_PATTERN→+20%), ORCHESTRATE→affects task ordering (dynamic_context→priority). Cache Redis TTL=30s.

### 12.7 Memory retrieval engine

Four retrieval modes: (1) Z-Layer vector similarity (current state vs past episode snapshot, pgvector ANN), (2) causal graph traversal (changed_layers → 2-hop causal chain, Neo4j), (3) text semantic retrieval (natural language query), (4) Project Profile injection (always). Retrieval SLO: P99 < 200ms. Exposed via the EIP RECALL verb.

### 12.8 KSL Perceptual Memory Isolation

KSL-0: Episode/Fact completely isolated, cross-project retrieval returns zero, forgetting 100%. KSL-1: Shareable aggregate statistical level Fact (DP ε≤0.5). KSL-2: Desensitization Pattern/AntiPattern (reviewed). KSL-3: Federation + Desensitization Fact + Aggregation Episode Statistics. KSL-4: Fully shared memory with Tenant.

### 12.9 Storage architecture

Episode: Hot (30 days, PostgreSQL+pgvector, ~25MB/day Profile-M) → Warm (30-180 days, PG metadata + S3 snapshot, <5s) → Cold (180 days+, S3 archive, <5min). Semantic: Neo4j knowledge graph. Profile: Redis cache (TTL=30s).

---

## 13. Acceptance criteria mapping

| AC | Design Support | Verification Methods |
|----|---------|---------|
| R01 AC-1: 8-layer 2048-d | §9.1 Encoder matrix | Unit test: input→output shape==(batch,2048) |
| R01 AC-2: Kendall τ≥0.5 | §6.3 Calibration plan | Calibration data set +5-fold cross-validation |
| R01 AC-3: 1-step MSE<0.15 | §5.8 Verification protocol | Held-out 20% project, time-based split |
| R01 AC-4: MVLS TRL-3 | §4.3+§4.5 | TRL Evaluator: ARI≥0.3+Granger p<0.05 |
| R01 AC-5: Causal p<0.05 | §4.5 Stage 2 | Granger Test: Every pair of adjacent layers |
| R01 AC-6: TRL dynamic weight reduction | §4.3 | Inject low ARI → verify EBM weight reduction |
| R01 AC-7: Arrange output sorting | §3.3 | Integration test: Input Z-Layer → Output sorting + health |
| R01 AC-8: Selection justification | §9.2 | Document review: Selection/substitution/rejection per encoder |
| R01 AC-9: Multiple projects without starvation | §3.4 | Load test: 5 projects → Max wait <Tier-2 SLO |
| R01 AC-10: Quota queuing | §3.4 | Integration test: Quota exceeded → QUEUED does not exceed Tier SLO |
| **MEM-AC-1: Episode automatic creation** | **§12.3** | **10 triggers→Verify that episode storage is complete** |
| **MEM-AC-2: Similarity retrieval P99<200ms** | **§12.7** | **Vector retrieval delay + correlation test** |
| **MEM-AC-3: Automatic fact extraction** | **§12.4** | **5 consistent Episode→Fact generated, confidence >0.7** |
| **MEM-AC-4: Automatic conflict resolution** | **§12.4** | **Inject conflict → old Fact invalidated** |
| **MEM-AC-5: Decay Archiving** | **§12.3** | **Low importance automatic archiving after 90 days** |
| **MEM-AC-6: Profile generation <50ms** | **§12.6** | **Including static/dynamic/risk three parts** |
| **MEM-AC-7: KSL-0 Memory Isolation** | **§12.8** | **Cross-project search returns zero results** |
| **MEM-AC-8: Memory Enhanced Decision Quality** | **§12.6** | **A/B: Kendall τ Improved ≥0.05** |
| **MEM-AC-9: Consolidation <30min does not impact SLO** | **§12.5** | **Performance Monitoring** |
| **MEM-AC-10: Memory Influence Auditable** | **§12.7** | **MemoryInfluence Audit Log Verification** |
| NFR-1: Brain P99 | §7.5 | Load Testing Profile-S/M/L |
| NFR-2: Availability | §7.5 | 48-72h unattended operation |
| NFR-3: S→L | §3.6 | Extended test: add resources only |
| NFR-8: Decision Audit | §3.2 #12 | Decision → Audit Log → Multidimensional Query |
| NFR-9: GPU Contention | §7.5 | GPU Contention Load Test |
| NFR-11: Log Hierarchy | §7.5 | Hot/Warm/Cold Query SLO Verification |