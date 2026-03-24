# 🔄 UEWM self-learning/self-reflection/self-correction/self-evolution mechanism design document

**Document version:** deliver-v1.1
**Document Number:** UEWM-EVO-003
**Last update:** 2026-03-24
**Status:** Design completed (100% coverage of R03, R06, R08, R10, R12-Gap3 + Long Memory linkage)
**Combined source:** Self Evolution V8.0 + Combined Patch (§5.5.1 desensitization pipeline) + Long Memory linkage — full merge
**Change History:**
- V5.0: Security envelope, circuit breaker, Pareto, bias detection, KSL distillation, privacy budget, machine forgetting
- V6.0: Failure analyzer, seesaw monitoring, deviation test set, cold start baseline, federated benchmark, human-machine consistency rate
- V7.0: Detailed design of desensitization pipeline
- V8.0: Surprise threshold calibration, drift detection verification, malicious suggestion detection; 100% coverage achieved
- **deliver-v1.0: full merge (including desensitization pipeline), no incremental patch dependency**

---

## 1. Overview—Four Competencies

Self-learning (surprise-driven) + self-correction (drift detection + causal backtracking) + self-evolution (LoRA + security envelope + Pareto) + self-reflection (regular introspection + deviation detection). Double-loop continuous improvement closed loop: inner loop (Agent interaction → surprise → LoRA evolution) + outer loop (regular reflection → blind spot discovery → active learning).

---

## 2. Self-learning mechanism

Surprise degree S(t) = ||Z_observed - Z_predicted||². Experience Replay Buffer (ERB): Prioritize experience replay, sorted by surprise. Course learning: easy → progressively more difficult. Counterfactual data augmentation. **[deliver-v1.1] Each time the degree of surprise exceeds the threshold, an INCIDENT Episode is automatically created and stored in long-term memory (Architecture §12.3), and historical similar Episodes are retrieved as an evolutionary prior. **

### 2.5 Surprise threshold calibration [V8.0]

Initial thresholds: Z_impl=0.5, Z_quality=0.4, Z_phys=0.3. Adaptive: 14-day rolling P95, minimum 100 samples required to start, each adjustment ≤10%, floor=0.1/ceiling=2.0. Each item can be calibrated independently.

---

## 3. Self-correction mechanism

Drift detection (Page-Hinkley/ADWIN/KL Divergence). Cause and effect location. Correct feedback conduction.

### 3.4 Drift detection verification scheme [V8.0]

Injection drift: mutation (20, 2σ) + gradual (20, 0.1σ/day×14d) + variance change (10, 2x). 50 in the control group. The detection window is 24h. Success: detection rate ≥90%, false alarm rate ≤10%, P50 delay <2h.

---

## 4. Self-evolution mechanism

### 4.1-4.6 Core Evolution

LoRA incremental update, 5 trigger strategies (surprise/drift/timing/event/manual), VICReg/SIGReg regularization, version management, evaluation indicators, security constraints.

### 4.7 Evolving Security Envelope

Single shot: single-layer regression ≤ 10%, overall ≤ 5%, ΔW ≤ 0.1, causal edge loss ≤ 5%. Accumulation: ≤5 times/24h, ≤15 times/week, 3 consecutive rollback pauses of 48h, 7-day accumulation ≤15%. Bias: Decision entropy ≥0.6, single user ≤30%, ≥3 roles. pre_evolution_check + post_evolution_check complete implementation.

### 4.8 Evolutionary Circuit Breaker

CLOSED → OPEN (3 consecutive rollbacks, paused for 48h) → HALF_OPEN (reduce lr 50% + single layer + reduced candidate) → CLOSED (success). Automatically generate a failure analysis report in case of failure.

### 4.9 Pareto improvement constraints

Multiple candidate parallel training (n=5, different lr) → Pareto front → closest to the ideal point. is_pareto_improvement: No layer degradation exceeds tolerance (0.02) and at least one layer is significantly improved.

### 4.10 Bias detection system

check_feedback_diversity: Single user ≤30% + ≥3 roles. check_decision_diversity: Shannon entropy ≥ 0.6.

### 4.11 Root cause analysis of evolution failure [V6.0]

EvolutionFailureAnalyzer: 7 types of root causes (data quality/lr too high/layer conflict/causal destruction/bias drift/distribution shift/insufficient candidates). Single rollback → immediate analysis. Circuit breaker OPEN → 3 times cross analysis. Automatic repair: auto_reduce_lr_50pct, auto_single_layer_mode, auto_increase_candidates. Structured JSON reporting.

### 4.12 Seesaw Effect 30 Days Monitoring [V6.0]

SeesawMonitor: Maintenance degradation counter for each layer, 30-day sliding window. Any layer continuously degrades > 3 times → SEESAW_DETECTED → Alarm SECURITY+ARCHITECT → Freeze the joint evolution of this layer. The dashboard displays the status of each layer (HEALTHY/WARNING/SEESAW_DETECTED).

---

## 5. Cross-project knowledge transfer and federated evolution

### 5.1-5.4 Core Mechanism

Multi-team architecture (Base Model + Team LoRA), knowledge extraction (desensitization → abstraction → universal → deduplication), federated learning (DP + quality weighting), knowledge graph (Pattern/AntiPattern/Decision/Metric).

### 5.5 KSL Hierarchical Knowledge Distillation

KSL-0 (complete isolation) → KSL-1 (statistical level, ε ≤ 0.5) → KSL-2 (mode level, ε ≤ 1.0, manual review required) → KSL-3 (federal level, ε ≤ 2.0, Secure Agg) → KSL-4 (open sharing, same as Tenant).

#### 5.5.1 Detailed design of desensitization pipeline [V7.0]

Level 1 (automatic regularization): Project name → [Project], service name → [Service Type], IP/email/API_key → [REDACTED], value → interval bucket. Level 2 (semantic entity): 9 types of service classification system (user/order/payment/notification/gateway/data/message/monitoring/storage). Level 3 (manual review, KSL-2 required): Portal submission → SECURITY/ARCHITECT review → 48h SLA → conservative exclusion of timeouts. PII final scan.

### 5.6 Privacy Budget Manager

ε budget per project per month: KSL-1(5.0), KSL-2(10.0), KSL-3(20.0), KSL-4(∞). can_share→consume→reset_monthly. Exhausted → PRIVACY_BUDGET_EXHAUSTED event.

### 5.7 Cold start baseline measurement method [V6.0]

Baseline: ≥5 items of independent training → TRL-0 to TRL-2 median time. Measuring points: M1 (TRL-0 confirmed) → M2 (TRL-1 achieved) → M3 (TRL-2 achieved) → M4 (cold start completed, surprise <0.5). cold_start_duration = M3-M1. AC-2 verification: with migration vs without migration, shortened by ≥50%. Phase 0 M2-M3 execution.

### 5.8 Federated Learning Performance Benchmark [V6.0]Group A (centralized, no DP) vs Group B (federated, ε=2.0+SecureAgg). ≥10 items, the same as the super parameters, and take the median after 3 repetitions. Metrics: prediction_mse + causal_accuracy → composite_score. AC-7 verification: B/A ≥ 0.85.

---

## 6. Self-reflection mechanism

Triggered regularly (daily/week/month/milestone). 5-dimensional introspection: prediction consistency, causal graph health, cross-layer alignment, decision diversity, blind area detection (POMDP high Σ area). Produce structured reflection reports. Exception → Inject Evolution Engine Directed LoRA. **[deliver-v1.1] Self-reflection runs simultaneously with the memory consolidation engine (daily at 03:00 UTC). Create a REFLECTION Episode for exceptions found by introspection. The consolidation engine performs fact extraction immediately after introspection (Architecture §12.5). A new "memory health" dimension has been added to the introspection report: Fact conflict rate, Episode archiving rate, and Profile coverage. **

### 6.5 Bias test set methodology [V6.0]

BiasTestSetBuilder: 5 types of bias injection (high prediction/causal removal/cross-layer misalignment/decision monotonic/timing degradation). 50 injection + 20 control. 7-day testing window. AC-2: Detection rate ≥80% (≥40/50). AC-4: False alarm rate ≤20% (≤4/20). Phase 0 M3 execution (30 instances + 10 controls), Phase 1 M6 full volume.

---

## 7. Learn from human feedback

The whole process is recorded. r_human = f (energy difference, post hoc verification, role authority, novelty). Human Feedback Buffer (priority playback). 50 experience accumulation → bias check → special LoRA (lr=50% of self-evolution). **[deliver-v1.1] Each human intervention → Create HUMAN_INTERVENTION Episode (OVERRIDE:importance=1.0, REQUIREMENT:0.8, SUGGESTION:0.5) → 3+ consistent override extraction PREFERENCE Fact → Inject into Project Profile (Architecture §12.6). **

### 7.7 Safety guardrail

Energy gate control (≤200%), double confirmation (override), learning rate limit (50%), VICReg protection, 48h rollback, bias detection (single user ≤30%, ≥3 roles).

### 7.8 Human-machine consistency rate measurement [V6.0]

exact_match_rate: Brain top-1 == manual selection. relaxed: Brain top-1 in artificial top-3. Risk weighting (LOW×1, MEDIUM×1.5, HIGH×2, CRITICAL×3). Monthly measurement, ≥50 samples. AC-2: Phase 1≥60%, Phase 2≥75%. AC-3: Phase 2 intervention frequency decreases ≥30% from Phase 1 baseline.

### 7.9 Malicious suggestion detection [V8.0]

5 types of detection: energy explosion (>200%→block), security violation (E_safety exceeds standard→block), rollback injection (historical rollback matching→warn+justification), scope override (RBAC→block), conflicting suggestions (similarity >0.8 within 7 days→clarify). Verification: 40 malicious + 60 legitimate, interception rate ≥95% (≥38/40), false interception rate ≤5% (≤3/60).

---

## 8-9. Vector database enhanced training pipeline/joint training strategy

pgvector(Phase 0)→Milvus(Phase 1+). VICReg/SIGReg regularization. Semantic clustering ARI, cross-modal prediction MSE, causal signal fidelity assessment.

---

## 10. Machine forgetting strategy

| KSL | Forgetting Methods | Integrity | Time Limits |
|-----|---------|--------|------|
| 0 | Delete LoRA+ data | 100% | 30 days |
| 1/2 | Delete + DP approximate forgetting | Approximate (ε≤1.0) | 30 days; precise 90 days |
| 3 | Delete + Federal DP Approximate | Approximate (ε ≤ 2.0) | Approximate 30 days; Exact by scale |
| 4 | Delete + Retune from checkpoint | Depending on scope | 60 days |

Delete audit: source + scope + confirmation + associated model tag + integrity statement + timestamp. Logs are retained for ≥3 years.

---

## 11. Complete sequence of evolution process

Trigger → pre_check (frequency + cumulative regression + circuit breaker) → bias detection → multi-candidate Pareto training (5) → post_check (5 items) → ACCEPT/ROLLBACK → shadow mode 48h → version snapshot + audit → circuit breaker record. **[deliver-v1.1] Each evolution is completed (including rollback) → Create EVOLUTION Episode (importance=1.0) → Extract evolution validity Fact → Continuous rollback to extract ANTI_PATTERN Fact (Architecture §12.5). **

---

## 12. Acceptance criteria mapping

| AC | Design Support |
|----|---------|
| R03 AC-1: Surprise → LoRA → Surprise ↓ | §2+§2.5 (Calibration) |
| R03 AC-2: Drift detection >90% | §3+§3.4 (verification plan) |
| R03 AC-3: Version Traceable Rollback | §4.6 |
| R03 AC-4: 100% Safety Envelope | §4.7 |
| R03 AC-5: Meltdown Demonstration | §4.8 |
| R03 AC-6: Pareto>80% | §4.9 |
| R03 AC-7: No Seesaw for 30 Days | §4.12 |
| R06 AC-1-4: Self-Reflection | §6+§6.5 |
| R08 AC-2: Cold start ≥50% | §5.7 |
| R08 AC-7: Federation ≥85% | §5.8 |
| R10 AC-2: Consistency rate ≥60%/75% | §7.8 |
| R10 AC-3: Intervention↓≥30% | §7.8 |
| R10 AC-4: Malicious interception >95% | §7.9 |
| R12 AC-7: KSL-0 Oblivion 100% | §10 |