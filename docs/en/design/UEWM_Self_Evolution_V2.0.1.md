# 🔄 UEWM self-learning/self-reflection/self-correction/self-evolution mechanism design document

**Document version:** V2.0.1
**Document Number:** UEWM-EVO-003
**Last update:** 2026-04-03
**Status:** Design completed (100% coverage of R03, R06, R08, R10, R12-Gap3 + Dual Space Surprise + Discovery Linkage + SIGReg + VoE Verification)
**Change History:**
- V8.0/deliver-v1.0: safety envelope, circuit breaker, pareto, bias, KSL, forgetting, calibration, drift verification
- V1.0.1: GPU optimization evolution, program memory formalization
- V2.0.0: Dual Space Surprise, REAL_SURPRISE only triggers evolution, Discovery Episode, Grounded Health
- **V2.0.1: SIGReg replaces VICReg (regularization), projection head integration, VoE test as evolutionary verification, security envelope adds SIGReg normality check, fully merges V1.0.1 content, eliminates all reference dependencies**

---

## 1. Overview—Four Competencies

Self-learning (dual space surprise drive) + self-correction (drift detection + causal retrospection) + self-evolution (LoRA + safety envelope + Pareto) + self-reflection (6 dimensions including grounded health).

V2.0 core changes: Evolution is only triggered by **True Surprise** (S_z HIGH + S_g HIGH), and is not accidentally triggered by Z-Space noise. Double-loop continuous improvement closed loop: inner loop (Agent interaction → surprise → LoRA evolution) + outer loop (regular reflection → blind spot discovery → active learning).

---

## 2. Self-learning mechanism

### 2.1 Dual Space Surprise (V2.0 Core Change)

```python
class DualSpaceSurprise:
    """V2.0: Calculate the surprise degree simultaneously in Z-Space and G-Space."""
    
    def compute(self, z_pred, z_obs, g_pred, g_obs):
        s_z = torch.norm(z_obs - z_pred, p=2) ** 2 # Hidden space surprise degree
        s_g = torch.norm(g_obs - g_pred, p=2) ** 2 # Observable surprise degree
        
        z_high = s_z > self.theta_z # Adaptive threshold (§2.5 Calibration)
        g_high = s_g > self.theta_g # G-Space threshold (14 days P95)
        
        if z_high and g_high:
            return SurpriseCategory.REAL_SURPRISE
            # The world has really changed → Trigger evolution
        elif z_high and not g_high:
            return SurpriseCategory.Z_NOISE
            # latent space drift → marked encoder, no evolution
        elif not z_high and g_high:
            return SurpriseCategory.GROUNDING_GAP
            # Z is correct but G is incomplete → Discovery Engine
        else:
            return SurpriseCategory.NORMAL
            # Prediction accurate → normal
    
    # 14-day rolling P95 calibration, per project independently
    # V2.0 added: G-Space threshold is also adaptively calibrated
```

### 2.2 Evolution trigger conditions (V2.0 changes)

```
V1.0.1: S(t) > θ → trigger evolution
V2.0: category == REAL_SURPRISE → trigger evolution
        category == Z_NOISE → Mark encoder needs to be retrained and does not trigger evolution
        category == GROUNDING_GAP → Discovery Engine steps in
        category == NORMAL → no action

This change ensures that the evolution engine only trains on real surprises,
Eliminated the risk of "training on Z-Space noise" in V1.0.1.
```

### 2.3 Experience replay and course learning

Experience Replay Buffer (ERB): Prioritize experience replay, sorted by surprise. Course learning: easy → progressively more difficult. Counterfactual data augmentation. Each time the surprise degree exceeds the threshold, an INCIDENT Episode is automatically created and stored in long-term memory (Architecture §12.3), and historical similar Episodes are retrieved as evolutionary priors. V2.0: Episode uses EnhancedEpisode format with G-snapshot.

### 2.4 Surprise threshold calibration

Initial thresholds: Z_impl=0.5, Z_quality=0.4, Z_phys=0.3. Adaptive: 14-day rolling P95, minimum 100 samples required to start, each adjustment ≤10%, floor=0.1/ceiling=2.0. Each item can be calibrated independently. V2.0 increases θ_g (G-Space threshold) and also performs adaptive calibration.

---

## 3. Self-correction mechanism

Drift detection (Page-Hinkley/ADWIN/KL Divergence). Cause and effect location. Correct feedback conduction.

### 3.4 Drift detection verification scheme

Injection drift: mutation (20, 2σ) + gradual (20, 0.1σ/day×14d) + variance change (10, 2x). 50 in the control group. The detection window is 24h. Success: detection rate ≥90%, false alarm rate ≤10%, P50 delay <2h.

---

## 4. Self-evolution mechanism

### 4.1-4.6 Core Evolution

LoRA incremental update, 5 trigger strategies (surprise/drift/timing/event/manual), SIGReg regularization (V2.0.1 replaces VICReg), version management, evaluation indicators, security constraints.

### 4.7 Evolved Security Envelope (V2.0.1 Enhanced)

Single shot: single-layer regression ≤ 10%, overall ≤ 5%, ΔW ≤ 0.1, causal edge loss ≤ 5%. Accumulation: ≤5 times/24h, ≤15 times/week, 3 consecutive rollback pauses of 48h, 7-day accumulation ≤15%. Bias: Decision entropy ≥0.6, single user ≤30%, ≥3 roles.

`post_evolution_check` currently has **7 items** [V2.0.1]:
- □ Single layer regression ≤ 10%
- □ Overall regression ≤ 5%
- □ ΔW ≤ 0.1
- □ Loss of causal edges ≤ 5%
- □ φ R² cannot drop more than 5% (V2.0.0)
- □ Consistency loss cannot increase more than 10% (V2.0.0)
- □ **SIGReg Normality is not degenerate (V2.0.1, LeWM): Epps-Pulley p-value cannot be reduced from >0.05 to <0.01; if normality is degenerated → evolution destroys the Z-Space distribution structure → rollback**

`pre_evolution_check + post_evolution_check` fully implemented.

### 4.8 Evolutionary Circuit Breaker

CLOSED → OPEN (3 consecutive rollbacks, paused for 48h) → HALF_OPEN (reduce lr 50% + single layer + reduced candidate) → CLOSED (success). Automatically generate a failure analysis report in case of failure.

### 4.9 Pareto improvement constraints

Multiple candidate parallel training (n=5, different lr) → Pareto front → closest to the ideal point. is_pareto_improvement: No layer degradation exceeds tolerance (0.02) and at least one layer is significantly improved.

### 4.10 Bias detection system

check_feedback_diversity: Single user ≤30% + ≥3 roles. check_decision_diversity: Shannon entropy ≥ 0.6.

### 4.11 Analysis of root causes of evolutionary failure

EvolutionFailureAnalyzer: 7 types of root causes (data quality/lr too high/layer conflict/causal destruction/bias drift/distribution shift/insufficient candidates). Single rollback → immediate analysis. Circuit breaker OPEN → 3 times cross analysis. Automatic repair: auto_reduce_lr_50pct, auto_single_layer_mode, auto_increase_candidates. Structured JSON reporting.

### 4.12 Seesaw Effect 30 Day Monitoring

SeesawMonitor: Maintenance degradation counter for each layer, 30-day sliding window. Any layer continuously degrades > 3 times → SEESAW_DETECTED → Alarm SECURITY+ARCHITECT → Freeze the joint evolution of this layer. The dashboard displays the status of each layer (HEALTHY/WARNING/SEESAW_DETECTED).

---

## 5. Cross-project knowledge transfer and federated evolution

### 5.1-5.4 Core Mechanism

Multi-team architecture (Base Model + Team LoRA), knowledge extraction (desensitization → abstraction → universal → deduplication), federated learning (DP + quality weighting), knowledge graph (Pattern/AntiPattern/Decision/Metric).

### 5.5 KSL Hierarchical Knowledge Distillation

KSL-0 (complete isolation) → KSL-1 (statistical level, ε ≤ 0.5) → KSL-2 (mode level, ε ≤ 1.0, manual review required) → KSL-3 (federal level, ε ≤ 2.0, Secure Agg) → KSL-4 (open sharing, same as Tenant).

#### 5.5.1 Detailed design of desensitization pipeline

Level 1 (automatic regularization): Project name → [Project], service name → [Service Type], IP/email/API_key → [REDACTED], value → interval bucket. Level 2 (semantic entity): 9 types of service classification system (user/order/payment/notification/gateway/data/message/monitoring/storage). Level 3 (manual review, KSL-2 required): Portal submission → SECURITY/ARCHITECT review → 48h SLA → conservative exclusion of timeouts. PII final scan.

### 5.6 Privacy Budget Manager

ε budget per project per month: KSL-1(5.0), KSL-2(10.0), KSL-3(20.0), KSL-4(∞). can_share→consume→reset_monthly. Exhausted → PRIVACY_BUDGET_EXHAUSTED event.

### 5.7 Cold start baseline measurement method

Baseline: ≥5 items of independent training → TRL-0 to TRL-2 median time. Measuring points: M1 (TRL-0 confirmed) → M2 (TRL-1 achieved) → M3 (TRL-2 achieved) → M4 (cold start completed, surprise <0.5). cold_start_duration = M3-M1. AC-2 verification: with migration vs without migration, shortened by ≥50%. Phase 0 M2-M3 execution.

### 5.8 Federated Learning Performance Benchmark

Group A (centralized, no DP) vs Group B (federated, ε=2.0+SecureAgg). ≥10 items, the same as the super parameters, and take the median after 3 repetitions. Metrics: prediction_mse + causal_accuracy → composite_score. AC-7 verification: B/A ≥ 0.85.

---

## 6. Self-reflection mechanism

Triggered regularly (daily/week/month/milestone). The self-reflection and memory consolidation engines run simultaneously (daily at 03:00 UTC). Create a REFLECTION Episode for exceptions found by introspection. The consolidation engine performs fact extraction immediately after introspection. A new "memory health" dimension has been added to the introspection report: Fact conflict rate, Episode archiving rate, and Profile coverage.

### 6.1 Six-dimensional introspection (V2.0: 5-dimensional → 6-dimensional)

**Dimension 1-5 (V1.0.1)**: Prediction consistency, causal graph health, cross-layer alignment, decision diversity, blind area detection (POMDP high Σ area). Produce structured reflection reports. Exception → Inject Evolution Engine Directed LoRA.

**Dimension 6: Grounding Health (new in V2.0)**:

```
Daily 03:00 UTC self-introspection check:

6a. φ Accuracy: per-dimension R² — target mean > 0.3
    Dimensions with R² < 0.1 are included in the "need pruning/retraining" list

6b. ψ Coherence: cosine similarity — Target > 0.5

6c. Discovery rate: DISCOVERY events / total predicted events
    Health: 5-15%
    <2%: Z-Space may be redundant
    >30%: Z-Space may drift, increase ψ weight

6d. G-Space coverage: indicator collection success rate — target > 95%
    <90%: Alarm DEVOPS (collector failure)

6e. Surprise classification accuracy: manual sampling 20 events/month
    Goal: Classification accuracy ≥ 80%

Exception handling:
  φ accuracy decrease → retrain bridge function (non-encoder)
  Discovery rate is too high → increase consistency_loss_weight
  G-Space coverage decreased → Alarm, non-model problem
```

### 6.2 Deviation test set methodology

BiasTestSetBuilder: 5 types of bias injection (high prediction/causal removal/cross-layer misalignment/decision monotonic/timing degradation). 50 injection + 20 control. 7-day testing window. AC-2: Detection rate ≥80% (≥40/50). AC-4: False alarm rate ≤20% (≤4/20). Phase 0 M3 execution (30 instances + 10 controls), Phase 1 M6 full volume.

---

## 7. Learn from human feedback

The whole process is recorded. r_human = f (energy difference, post hoc verification, role authority, novelty). Human Feedback Buffer (priority playback). 50 experience accumulation → bias check → special LoRA (lr=50% of self-evolution). Each manual intervention → Create HUMAN_INTERVENTION Episode (OVERRIDE:importance=1.0, REQUIREMENT:0.8, SUGGESTION:0.5) → 3+ consistent override extraction PREFERENCE Fact → Inject into Project Profile. V2.0: Manual feedback Episode including G-snapshot.

### 7.7 Safety guardrail

Energy gate control (≤200%), double confirmation (override), learning rate limit (50%), SIGReg protection (V2.0.1), 48h rollback, bias detection (single user ≤30%, ≥3 roles).

### 7.8 Human-machine consistency rate measurement

exact_match_rate: Brain top-1 == manual selection. relaxed: Brain top-1 in artificial top-3. Risk weighting (LOW×1, MEDIUM×1.5, HIGH×2, CRITICAL×3). Monthly measurement, ≥50 samples. AC-2: Phase 1≥60%, Phase 2≥75%. AC-3: Phase 2 intervention frequency decreases ≥30% from Phase 1 baseline.

### 7.9 Malicious suggestion detection

5 types of detection: energy explosion (>200%→block), security violation (E_safety exceeds standard→block), rollback injection (historical rollback matching→warn+justification), scope override (RBAC→block), conflicting suggestions (similarity >0.8 within 7 days→clarify). Verification: 40 malicious + 60 legitimate, interception rate ≥95% (≥38/40), false interception rate ≤5% (≤3/60).

---

## 8-9. Vector database enhanced training pipeline/joint training strategy

pgvector(Phase 0)→Milvus(Phase 1+). SIGReg regularization (V2.0.1 replaces VICReg). Semantic clustering ARI, cross-modal prediction MSE, causal signal fidelity assessment.

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

## 11. Complete timing of the evolution process (V2.0 update)

```
trigger (only REAL_SURPRISE, not Z_NOISE) →
pre_check (frequency + cumulative regression + circuit breaker) →
Bias Detection →
Multi-candidate Pareto training (5, BF16+gradient checkpoint) →
post_check (7 items, V2.0.1 contains SIGReg normality) →
ACCEPT/ROLLBACK →
Shadow Mode 48h →
Version snapshot + audit →
Circuit breaker records →
Create EVOLUTION Episode (importance=1.0, including G-snapshot, V2.0) →
Extract Evolutionary Effectiveness Fact →
Continuous rollback extraction ANTI_PATTERN Fact
```

### 11.5 Evolutionary training GPU optimization

```
Evolutionary training GPU optimization strategy (benchmarking Architecture §13):

LoRA evolution training (main evolution method):
    Accuracy: BF16 training + FP32 gradient accumulation
    Video memory: rank 8-64, < 4 GB/time, no gradient checkpoints required
    Optimization: Multiple candidate parallel training (n=5) is executed sequentially on the same GPU (non-parallel)
          Reason: LoRA training is fast (~5min/candidate), but parallelization increases video memory fragmentation.
    
  AlignmentTrainer (AlignmentTrainer, periodic):
    Accuracy: BF16 + gradient checkpoints (every 3 encoder layers)
    DeepSpeed: Phase 0 ZeRO-1, Phase 1+ ZeRO-2
    Video Memory: ~16 GB (with checkpointing enabled, originally ~45 GB)
    Scheduling: Only started when the training GPU pool is idle, inference takes priority
    
  Counterfactual data augmentation (ERB experience replay):
    Optimization: CPU preprocessing + GPU only forward inference
    Batch: dynamic batch (adaptive based on available GPU memory)
    Cache: Encoder output cache (avoids encoding the same item repeatedly)

  The relationship between program memory (Layer 0, Architecture §12.2) and evolution:
    LoRA weight is program memory
    Successful evolution: Program memory update (new skill acquisition)
    Evolutionary rollback: program memory rollback (skill forgetting)
    Circuit breaker OPEN: program memory freeze (stop learning)
    Cold start: program memory is empty (no prior skills)
    Knowledge transfer: Copy program memory fragments (KSL constraints) from other projects
```

---

## 12. Acceptance criteria mapping

| AC | Design Support |
|----|---------|
| R03 AC-1: Surprise → LoRA → Surprise ↓ | §2+§2.4 (Calibration) |
| R03 AC-2: Drift detection >90% | §3+§3.4 (verification plan) |
| R03 AC-3: Version Traceable Rollback | §4.6 |
| R03 AC-4: 100% Safety Envelope | §4.7 |
| R03 AC-5: Meltdown Demonstration | §4.8 |
| R03 AC-6: Pareto>80% | §4.9 |
| R03 AC-7: No Seesaw for 30 Days | §4.12 |
| R06 AC-1~4: Self-Reflection | §6+§6.2 |
| R08 AC-2: Cold start ≥50% | §5.7 |
| R08 AC-7: Federation ≥85% | §5.8 |
| R10 AC-2: Consistency rate ≥60%/75% | §7.8 |
| R10 AC-3: Intervention↓≥30% | §7.8 |
| R10 AC-4: Malicious interception >95% | §7.9 |
| R12 AC-7: KSL-0 Oblivion 100% | §10 |
| **R03 AC-8: Only REAL_SURPRISE triggers evolution** | **§2.2** |
| **R03 AC-9: Consistency loss post_check does not degrade** | **§4.7 V2.0** |
| **R03 AC-10: SIGReg normality post_check non-degenerate (LeWM)** | **§4.7 V2.0.1** |
| **R06 AC-5: Ground health dimension functional** | **§6.1** |