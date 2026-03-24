# 📋 UEWM requirements-design-verification traceability matrix

**Document version:** deliver-v1.1
**Document Number:** UEWM-TRACE-011
**Last update:** 2026-03-24
**Status:** Design Complete — 93 Original AC + 10 MEM-AC = 103/103 ✅
**Purpose:** Ensure that each Acceptance Criteria (AC) of Requirements V6.1 is clearly mapped in the design document and has an executable verification method.  
**Merge source:** Traceability Matrix V2.0 - updated document version reference to deliver-v1.0

---

## Instructions for use

- **Status column:** ✅ = The design is completed and the verification method is clear
- **Phase column:** 0/1/2/3 = In which Phase the AC is verified
- **Design Ref column:** The format is `Document Abbreviation §Chapter Number`

---

## R01 — JEPA Base World Model (10 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 8-layer Z-Layer encoder output 2048-d vector | ARCH §9.1, §9.3 | Encoder unit test: output shape == (batch, 2048) | 0 | ✅ |
| AC-2 | EBM Kendall τ ≥ 0.5 | ARCH §6.3 | Calibration data set 200 pairs + 5-fold cross-validation | 0 | ✅ |
| AC-3 | Predictor 1-step MSE<0.15, 3-step MSE<0.3 | ARCH §5.8 | Held-out 20% items (time-based split) | 0 | ✅ |
| AC-4 | MVLS all three layers TRL-3 | ARCH §4.3, §4.5 | TRL Evaluator: ARI≥0.3 + Granger p<0.05 | 0 | ✅ |
| AC-5 | Cross-layer causal signal fidelity p<0.05 | ARCH §4.5 Stage 2 | Granger causality test: every pair of adjacent layers | 0 | ✅ |
| AC-6 | TRL automatic evaluation + dynamic downweighting | ARCH §4.3 | Inject low ARI → Verify EBM downweighting | 0 | ✅ |
| AC-7 | Arrangement module output task sorting + health | ARCH §3.3, ENG §2.6 | Integration test: Input Z-Layer → Output sorting + health | 0 | ✅ |
| AC-8 | Encoder pre-training selection justification | ARCH §9.2 | Document review: Selection/replacement/rejection per encoder | 0 | ✅ |
| AC-9 | Multi-project concurrency without starvation | ARCH §3.4 | Load test: 5 projects → Max wait < Tier-2 SLO | 1 | ✅ |
| AC-10 | Per-Tenant Quota Queuing | ARCH §3.4 | Integration Test: Quota Exceeded → QUEUED Not Exceeded Tier SLO | 1 | ✅ |

## R02 — Agent System (10 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Inner loop 5 Agent LOA≥7 | AGENT §2, §3 | End-to-end: Code→Test→Deploy→Monitor closed loop | 0 | ✅ |
| AC-2 | Central 3 Agent LOA≥5 | AGENT §11.2 | Demo: AG-SA/FD/AU TRL-3 under LOA≥5 | 1 | ✅ |
| AC-3 | Outer Ring 4 Agent LOA≥3 | AGENT §11.3 | Demonstration: AG-PA/PD/BI/PR TRL-2 under LOA≥3 | 2 | ✅ |
| AC-4 | LOA 3↔8 automatic switching | AGENT §3 | Inject TRL changes → LOA automatic recalculation | 0 | ✅ |
| AC-5 | Brain Unavailable → Rule Engine | AGENT §4 | Kill Brain pod → Agent Rule Engine Verification | 0 | ✅ |
| AC-6 | Unified EIP Protocol Interaction | EIP §4, AGENT §9.4 | 12 Agent EipVerb Closed Loop Test | 0 | ✅ |
| AC-7 | Configurable transfer door | AGENT §5 | Configure transfer door parameters → Verify evaluation logic | 1 | ✅ |
| AC-8 | LOA degradation cascade within 30s | AGENT §5.2, ENG §2.5 | Inject LOA degradation → Measurement evaluation delay | 0 | ✅ |
| AC-9 | Alarm within 60s of product version | AGENT §8 | Submit inconsistent version → Measure alarm delay | 0 | ✅ |
| AC-10 | Execution Engine Selection Demonstration | AGENT §6 | Document Review: Each Agent has engine + cost | 0 | ✅ |

## R03 — Self-Evolve (7 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Surprise → LoRA → Surprise ↓ | EVO §2, §2.5 | Inject high surprise → Evolve → Surprise decrease | 0 | ✅ |
| AC-2 | Drift Detection > 90% | EVO §3, §3.4 | Inject known drift → Measure detection rate | 0 | ✅ |
| AC-3 | Version traceable rollback | EVO §4.6, DEPLOY §8.2 | Rollback → Function recovery < 2min | 0 | ✅ |
| AC-4 | Security Envelope 100% Enforcement | EVO §4.7 | Inject Hyperenvelope → Verify Rollback | 0 | ✅ |
| AC-5 | Continuous failed circuit breakers | EVO §4.8 | 3 rollbacks → Circuit breaker OPEN + 48h | 0 | ✅ |
| AC-6 | Pareto > 80% | EVO §4.9 | 30-day stats: Pareto Hit Rate | 1 | ✅ |
| AC-7 | 30 days without seesaw | EVO §4.12 | SeesawMonitor 30 days: no layer degradation > 3 times | 1 | ✅ |

## R04 — Security Governance (8 ACs)| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Override 100% interception | SEC §4.4, §4.5 | 717 test: All override interceptions | 0 | ✅ |
| AC-2 | High Risk Approval Required | SEC §5, §5.2 | CRITICAL → Approval Process Triggered | 0 | ✅ |
| AC-3 | Complete audit available | SEC §7, §7.3 | Full link → Audit log query | 0 | ✅ |
| AC-4 | KSL-0 zero leakage | SEC §10, EVO §5.5 | Audit full scan: participation record=0 | 1 | ✅ |
| AC-5 | T1-T5 penetration passed | SEC §14 | All 23 penetration tests passed | 0/1 | ✅ |
| AC-6 | RBAC Configurable Audit | SEC §4 | Permission Change → Audit Log | 0 | ✅ |
| AC-7 | mTLS + signature + chain | SEC §12 | Certificate rotation + signature verification + chain integrity | 0 | ✅ |
| AC-8 | SOC2 TypeI ready | SEC §11.3 | 8 control point review passed | 0 | ✅ |

## R05 — Deployment Operations (9 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Profile-M P99<500ms@50 concurrency | DEPLOY §4.1, §12.3 | k6 50 concurrency 60min | 0 | ✅ |
| AC-2 | Failure <30s self-healing | DEPLOY §8.1, §12.5 | Chaos: Kill pod | 0 | ✅ |
| AC-3 | CI/CD Full Automation | ENG §6.3, DEPLOY §7 | End-to-End Demonstration | 0 | ✅ |
| AC-4 | S/M/L passed SLO | DEPLOY §12.2-12.4 | Three Profile independent tests | 0/1/2 | ✅ |
| AC-5 | S→L Add resources only | DEPLOY §10, §13 | Configuration Difference Review + Upgrade Manual | 2 | ✅ |
| AC-6 | Error Budget Dashboard | DEPLOY §5.1 | Budget+burn-rate+Level | 0 | ✅ |
| AC-7 | L2 evolution pause <30s | DEPLOY §5.2, §3.3, §12.3 | SLO exceeded → Pause delay | 0 | ✅ |
| AC-8 | L3 action <60s | DEPLOY §5.2, §12.3 | Low budget → action delay | 0 | ✅ |
| AC-9 | LLM Cost Compliance | DEPLOY §6, INTEG §3 | 30 days ≤ $5,000 | 1 | ✅ |

## R06 — Self-Reflection (4 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Automatically generate scheduled reports | EVO §6, ENG §2.9 | Cron → Report generation | 1 | ✅ |
| AC-2 | Deviation detection > 80% | EVO §6.5 | 50 injection detection ≥ 40 | 1 | ✅ |
| AC-3 | Result Injection Evolution Engine | EVO §6 | Reflection→LoRA→Improvement | 1 | ✅ |
| AC-4 | False alarm rate < 20% | EVO §6.5 | 20 comparison false alarms ≤ 4 | 1 | ✅ |

## R07 — Multi-tenant (6 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Multi-team, multi-project independent | ARCH §3.6, DEPLOY §3 | Multi-Tenant parallel | 1 | ✅ |
| AC-2 | Team-level LoRA does not interfere with each other | EVO §5 | Modification A→B will not be affected | 1 | ✅ |
| AC-3 | Data isolation audit | SEC §10 | All interceptions across Tenants | 1 | ✅ |
| AC-4 | KSL coexistence isolation | EVO §5.5, SEC §14 | KSL-0 audit=0 | 1 | ✅ |
| AC-5 | Concurrent arbitration without starvation | ARCH §3.4 | Maximum wait <Tier-2 | 1 | ✅ |
| AC-6 | Quota queuing | ARCH §3.4 | Exceeding quota → queuing does not affect others | 1 | ✅ |

## R08 — Knowledge Transfer (7 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Cross-project migration | EVO §5 | New project acceptance → TRL improvement | 2 | ✅ |
| AC-2 | Cold start reduction ≥50% | EVO §5.7, ENG §5.7 | 5 project baseline vs migration | 2 | ✅ |
| AC-3 | Federation non-disclosure | EVO §5.5, SEC §14 | Reverse <random +5% | 2 | ✅ |
| AC-4 | KSL-0 zero leakage | SEC §10 | Audit full scan | 1 | ✅ |
| AC-5 | DP Proof | EVO §5.5, §5.6 | DP Parameter + Combination Theorem | 2 | ✅ |
| AC-6 | Accurate privacy budget | EVO §5.6 | Exhaustion → Block + Alert | 1 | ✅ |
| AC-7 | Federal≥85% | EVO §5.8 | A/B(≥10 items) B/A≥0.85 | 2 | ✅ |

## R09 — Human Intervention (8 ACs)| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Portal Submit Suggestion | AGENT §10.5 | API: POST suggest | 0 | ✅ |
| AC-2 | Agent forwarding Brain | EIP §3.3, §4.5.8 | End-to-end: Suggestion→Analysis→Return | 0 | ✅ |
| AC-3 | Agent waits for command | AGENT §9.2, §9.3 | State machine: AWAITING+timeout | 0 | ✅ |
| AC-4 | Permission Verification | SEC §4.4 | Unauthorized → Deny | 0 | ✅ |
| AC-5 | LOA automatic adjustment | AGENT §3 | TRL change→LOA recalculation→behavior switching | 0 | ✅ |
| AC-6 | PM View 12 Agent | AGENT §10.2 | Dashboard API | 1 | ✅ |
| AC-7 | PM Intervention Orchestration | AGENT §10.2 | Adjust Priority → Orchestrate Response | 1 | ✅ |
| AC-8 | PM authority boundaries | AGENT §10.2 | Modify LOA → Deny | 1 | ✅ |

## R10 — Learning with Human Feedback (6 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Experience Recording Buffer | EVO §7 | Intervention→Buffer Recording | 1 | ✅ |
| AC-2 | Consistency rate ≥60%/75% | EVO §7.8 | Monthly measurement ≥50 samples | 1/2 | ✅ |
| AC-3 | Intervention ↓30% | EVO §7.8 | Monthly frequency comparison | 2 | ✅ |
| AC-4 | Malicious interception >95% | EVO §7.9 | ≥38 interceptions out of 40 malicious | 1 | ✅ |
| AC-5 | Energy rise rollback | EVO §7.7 | Inject → 48h rollback | 1 | ✅ |
| AC-6 | Single user ≤30% | EVO §4.10, §7.7 | BiasDetector verification | 1 | ✅ |

## R11 — EIP Protocol (10 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | IDL full + compatible | EIP §4 | protoc + buf lint/breaking | 0 | ✅ |
| AC-2 | 12 Agent integration | EIP §8, AGENT §9.4 | EipVerb closed loop per Agent≥1 | 0 | ✅ |
| AC-3 | gRPC P99<SLO | EIP §5, DEPLOY §12 | Profile-M Load Test | 0 | ✅ |
| AC-4 | Kafka P99<2s | EIP §2.4, §5 | Event latency monitoring | 0 | ✅ |
| AC-5 | Grayscale upgrade | EIP §6 | Old and new versions coexist | 1 | ✅ |
| AC-6 | Dead Letter Replay | EIP §5.2 | Injection failed→Replay→Success | 0 | ✅ |
| AC-7 | No Any | EIP §4 | grep Any = 0 | 0 | ✅ |
| AC-8 | Bad payload rejection | EIP §5.4 | Mismatch→INVALID_PAYLOAD | 0 | ✅ |
| AC-9 | Complete JSON examples | EIP §4.5 | 11 examples covering all types | 0 | ✅ |
| AC-10 | PERMISSION_DENIED | EIP §4.5.9, §5.4 | Cross-Tenant→PERMISSION_DENIED | 0 | ✅ |

## R12 — Training data (8 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | MVLS three-tier sample size | DATA §2.1, §10.1 | Data statistics report | 0 | ✅ |
| AC-2 | Version traceability | DATA §5 | DVC traceback | 0 | ✅ |
| AC-3 | Synthesis ≤30% (Z_phys≤60%) | DATA §4, §4.1 | Tag Statistics | 0 | ✅ |
| AC-4 | Compliance Passed | DATA §6 | License+PII | 0 | ✅ |
| AC-5 | Documentation of Selection | ARCH §9.2 | Document Review | 0 | ✅ |
| AC-6 | 90 Days Delete | DATA §7, EVO §10 | Delete Process | 1 | ✅ |
| AC-7 | KSL-0 Forget 100% | EVO §10 | Delete → Zero Residue | 1 | ✅ |
| AC-8 | Forgetting Policy Review | EVO §10 | Documentation Review | 0 | ✅ |

## R13 — External Integration (4 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Inner Loop 5 Adapters | AGENT §7.2, INTEG §5 | Per Adapter Operation Closed Loop | 0 | ✅ |
| AC-2 | Tool switching | AGENT §7.1, INTEG §2.1 | GitHub→GitLab hot switching | 0 | ✅ |
| AC-3 | Fault degradation | AGENT §4, INTEG §5 | Git unavailable→LOA≤4 | 0 | ✅ |
| AC-4 | Credential Vault | INTEG §4 | Vault Audit + No Hardcoding | 0 | ✅ |

## NFR Verification (11 items)| NFR | Description | Design Ref | Verification Method | Phase | Status |
|-----|------|-----------|---------|-------|--------|
| NFR-1 | Brain P99 Profiles | ARCH §7.5, DEPLOY §12 | Load Test | 0/1/2 | ✅ |
| NFR-2 | Availability 99.95%/99.99% | DEPLOY §4.4, §12 | 48-72h | 0/1 | ✅ |
| NFR-3 | S→L add resources only | DEPLOY §10, §13, ARCH §3.6 | Extended Test | 2 | ✅ |
| NFR-4 | mTLS full link | SEC §12, EIP §7 | TLS+ rotation | 0 | ✅ |
| NFR-5 | Audit ≥ 1 year | SEC §7.2 | Storage Policy + Query SLO | 0 | ✅ |
| NFR-6 | <30s self-healing, <2min rollback | DEPLOY §8, §12.5 | Chaos test | 0 | ✅ |
| NFR-7 | KSL-0 zero leakage | SEC §10 | Audit full scan | 1 | ✅ |
| NFR-8 | Decision-making full-link audit | SEC §7, DEPLOY §9 | Decision → Log → Multidimensional query | 0 | ✅ |
| NFR-9 | GPU inference priority | DEPLOY §3.3 | GPU contention P99<600ms | 0 | ✅ |
| NFR-10 | Product versioning | AGENT §8, §8.3 | CRUD+ version query | 0 | ✅ |
| NFR-11 | Hot/Warm/Cold | SEC §7.2, DEPLOY §12 | Hot<2s, Warm<30s | 0 | ✅ |

## Long Memory — Long-term memory (10 ACs) [New in deliver-v1.1]

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| MEM-AC-1 | Episode automatically created (5 triggers) | ARCH §12.3, EVO §2/§7/§11 | 10 triggers→Episode fully stored | 0 | ✅ |
| MEM-AC-2 | Similarity search P99 < 200ms | ARCH §12.7, ENG §2.14 | pgvector ANN vector search + correlation | 0 | ✅ |
| MEM-AC-3 | Automatic fact extraction (≥3 Episode→Fact) | ARCH §12.4 | Inject consistent pattern→Fact generation, confidence >0.7 | 1 | ✅ |
| MEM-AC-4 | Automatic conflict resolution | ARCH §12.4 | Inject conflicting data → old Fact invalidated | 1 | ✅ |
| MEM-AC-5 | Decay Archive (90 days low importance) | ARCH §12.3, DEPLOY §11.3 | Time Simulation → Validation Archive | 1 | ✅ |
| MEM-AC-6 | Project Profile generation < 50ms | ARCH §12.6 | Performance testing + complete content (static/dynamic/risk) | 0 | ✅ |
| MEM-AC-7 | KSL-0 memory fully isolated | ARCH §12.8, SEC §8.4 | Cross-project RECALL returns zero results | 1 | ✅ |
| MEM-AC-8 | Memory-enhanced decision quality | ARCH §12.6, ENG §2.14 | A/B: with memory vs without memory, Kendall τ ≥ +0.05 | 2 | ✅ |
| MEM-AC-9 | Consolidation < 30min Does not affect SLO | ARCH §12.5, DEPLOY §11.2 | Brain P99 monitoring during consolidation | 1 | ✅ |
| MEM-AC-10 | MemoryInfluence auditable | ARCH §12.7, SEC §8.4 | MemoryInfluence field audit log validation | 0 | ✅ |

---

## Document abbreviation comparison (deliver-v1.1 version)

| Abbreviation | Full name | Version |
|------|------|------|
| ARCH | UEWM_Architecture | **deliver-v1.1** (with §12 long-term memory) |
| AGENT | UEWM_Agents_Design | **deliver-v1.1** (including RECALL SDK) |
| EVO | UEWM_Self_Evolution | **deliver-v1.1** (including memory linkage) |
| SEC | UEWM_Safety_Governance | **deliver-v1.1** (with §8.4 memory safety) |
| ENG | UEWM_Engineering_Spec | **deliver-v1.1** (including §2.14-2.15 memory timing diagram) |
| EIP | UEWM_EIP_Protocol | **deliver-v1.1** (with RECALL verb) |
| DATA | UEWM_Data_Strategy | **deliver-v1.1** (including Episode life cycle) |
| DEPLOY | UEWM_Deployment_Operations | **deliver-v1.1** (including §11.2-11.3 memory operation and maintenance) |
| INTEG | UEWM_Integration_Map | **deliver-v1.0** (no changes) |