# 📋 UEWM requirements-design-verification traceability matrix

**Document version:** V2.0.1
**Document Number:** UEWM-TRACE-011
**Last update:** 2026-04-02
**Status:** Design Complete — 154 / 154 ✅
**AC composition:** R01-R13 Extended (107) + MEM (10) + GPU (6) + EXT (8) + LIC (4) + GND (10) + LeWM (6) + NFR (14) = 154 unique AC (after deduplication)
**Purpose:** Ensure that all acceptance criteria are clearly mapped in the V2.0.1 design document and have executable verification methods.

---

## R01 — JEPA Base World Model (11 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 8-layer Z-Layer 2048-d | ARCH §7.1 | shape==(batch,2048) | 0 | ✅ |
| AC-2 | EBM Kendall τ ≥ 0.5 | ARCH §8.3 | Calibration data set 5-fold | 0 | ✅ |
| AC-3 | Predictor 1-step MSE<0.15 | ARCH §6.5 | Held-out 20% time-split | 0 | ✅ |
| AC-4 | MVLS three-layer TRL-3 | ARCH §7.3 | ARI≥0.3 + Granger p<0.05 | 0 | ✅ |
| AC-5 | Cross-level causality p<0.05 | ARCH §6.4 | Granger per pair of adjacent levels | 0 | ✅ |
| AC-6 | TRL dynamic downweighting | ARCH §7.3 | Inject low ARI → EBM downweighting | 0 | ✅ |
| AC-7 | Arrangement output sorting + health | ARCH §3.3 | Integration testing | 0 | ✅ |
| AC-8 | Encoder Selection Justification | ARCH §7.1 | Document Review | 0 | ✅ |
| AC-9 | Multi-project starvation | ARCH §3.4 | Load testing | 1 | ✅ |
| AC-10 | Per-Tenant Quota | ARCH §3.4 | Integration Tests | 1 | ✅ |
| AC-11 | Transformer-XL non-LLM argument | ARCH §6.1 | Document review | 0 | ✅ |

## R02 — Agent System (15 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Inner loop 5 Agent LOA≥7 | AGENT §2, §3 | End-to-end closed loop | 0B | ✅ |
| AC-2 | Central 3 Agent LOA≥5 | AGENT §11 | Demo | 1 | ✅ |
| AC-3 | Outer Ring 4 Agent LOA≥3 | AGENT §11 | Demo | 2 | ✅ |
| AC-4 | LOA 3↔8 automatic switching | AGENT §3 | TRL change → LOA | 0B | ✅ |
| AC-5 | Brain Unavailable → Rules Engine | AGENT §4 | Kill Brain → Verify | 0B | ✅ |
| AC-6 | Unified EIP Protocol | EIP §3, AGENT §9.5 | 12 Agent Closed Loop | 0B | ✅ |
| AC-7 | Transfer door configurable | AGENT §5 | Configure→Verify | 1 | ✅ |
| AC-8 | LOA downgrade 30s cascade | AGENT §5 | Inject → Test delay | 0B | ✅ |
| AC-9 | Product version 60s alarm | AGENT §8 | Inconsistency → Alarm | 0B | ✅ |
| AC-10 | Execution Engine Selection Demonstration | AGENT §6 | Document Review | 0B | ✅ |
| AC-11 | Third Party ADS Compliance Verification | AGENT §14 | Three Tool Verification | 1 | ✅ |
| AC-12 | UAT Acceptance Workflow | AGENT §15 | Full Process | 2 | ✅ |
| AC-13 | Agent Usage RiskDecomposition | AGENT §9.2 | Integration Test | 0B | ✅ |
| AC-14 | Agent Query G-Space | AGENT §9.5 | QUERY_GSPACE | 0B | ✅ |
| AC-15 | Agent Subscription DISCOVERY_ALERT | AGENT §9.2 | Event Reception | 1 | ✅ |

## R03 — Self-Evolve (9 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Surprise → LoRA → Surprise ↓ | EVO §2 | Injection → Evolution → Decline | 0B | ✅ |
| AC-2 | Drift Detection >90% | EVO §3 | Inject known drift | 0B | ✅ |
| AC-3 | Version traceable rollback | EVO §4.6 | Rollback < 2min | 0B | ✅ |
| AC-4 | Safe Envelope 100% | EVO §4.7 | Inject Hyper Envelope→Rollback | 0B | ✅ |
| AC-5 | Continuous failure of fusing | EVO §4.8 | 3 times→OPEN+48h | 0B | ✅ |
| AC-6 | Pareto >80% | EVO §4.9 | 30-day statistics | 1 | ✅ |
| AC-7 | 30 Days Without Seesaw | EVO §4.12 | SeesawMonitor | 1 | ✅ |
| AC-8 | Only REAL_SURPRISE triggers evolution | EVO §2.2 | Z_NOISE does not trigger verification | 0B | ✅ |
| AC-9 | Consistency loss post_check | EVO §4.7 | φ R² does not degrade | 0B | ✅ |

## R04 — Security Governance (14 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Override 100% interception | SEC §4.5 | Test Matrix | 0B | ✅ |
| AC-2 | High risk requires approval | SEC §5 | CRITICAL→Approval | 0B | ✅ |
| AC-3 | Complete audit available | SEC §7 | Full link audit | 0B | ✅ |
| AC-4 | KSL-0 Zero Leakage | SEC §10 | Full Scan | 1 | ✅ |
| AC-5 | T1-T6 Penetration Pass | SEC §14 | 28 Passes | 0B/1 | ✅ |
| AC-6 | RBAC Configurable Auditing | SEC §4 | Change → Log | 0B | ✅ |
| AC-7 | mTLS+signature+chain | SEC §12 | certificate+signature | 0B | ✅ |
| AC-8 | SOC2 TypeI Ready | SEC §11 | 8 Control Points | 0B | ✅ |
| AC-9 | THIRD_PARTY Overreach | SEC §4.3 | Third Party Testing | 1 | ✅ |
| AC-10 | Mandatory Third Party Audit | SEC §4.3 | Audit Verification | 1 | ✅ |
| AC-11 | T6 G-Space Tamper Defense | SEC §3 T6 | Penetration Testing | 0B | ✅ |
| AC-12 | Discovery Audit Permissions | SEC §4.4 | Permission Verification | 1 | ✅ |
| AC-13 | G-Space Collection Audit | SEC §7.4 | Audit Log | 0B | ✅ |
| AC-14 | 28 penetration tests passed | SEC §14.1 | All passed | 1 | ✅ |

## R05 — Deployment Operations (13 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Profile-M P99<500ms@50 concurrency | DEPLOY §4.1, §12.3 | k6 50 concurrency 60min | 0B | ✅ |
| AC-2 | Failure <30s self-healing | DEPLOY §8.1, §12.5 | Chaos: Kill pod | 0B | ✅ |
| AC-3 | CI/CD Full Automation | ENG §6.3, DEPLOY §7 | End-to-End Demonstration | 0B | ✅ |
| AC-4 | S/M/L respectively passed SLO | DEPLOY §12.2-12.4 | Three Profile independent tests | 0B/1/2 | ✅ |
| AC-5 | S→L Add resources only | DEPLOY §10, §13 | Configuration Difference Review + Upgrade Manual | 2 | ✅ |
| AC-6 | Error Budget Dashboard | DEPLOY §5.1 | Budget+burn-rate+Level | 0B | ✅ |
| AC-7 | L2 evolution pause <30s | DEPLOY §5.2, §3.3, §12.3 | SLO exceeded → Pause delay | 0B | ✅ |
| AC-8 | L3 action <60s | DEPLOY §5.2, §12.3 | Low budget → Action delay | 0B | ✅ |
| AC-9 | LLM Cost Compliance | DEPLOY §6, INTEG §3 | 30 days ≤ $5,000 | 1 | ✅ |
| AC-10 | Community Edition Independent Deployment | DEPLOY §15 | Profile-S Closed Loop | 1 | ✅ |
| AC-11 | G-Space Acquisition P99 < 500ms | DEPLOY §12.8 | Performance Test | 0B | ✅ |
| AC-12 | φ Decoding P99 < 50ms | DEPLOY §12.8 | Performance Test | 0B | ✅ |
| AC-13 | PoC can be deployed and run locally | DEPLOY §17 | Mac/RTX verification | 0A | ✅ |

## R06 — Self-Reflection (5 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Automatically generate scheduled reports | EVO §6, ENG §2.9 | Cron → Report generation | 1 | ✅ |
| AC-2 | Deviation detection > 80% | EVO §6.5 | 50 injection detection ≥ 40 | 1 | ✅ |
| AC-3 | Result Injection Evolution Engine | EVO §6 | Reflection→LoRA→Improvement | 1 | ✅ |
| AC-4 | False alarm rate < 20% | EVO §6.5 | 20 comparison false alarms ≤ 4 | 1 | ✅ |
| AC-5 | The ground health dimension functions normally | EVO §6.1 | 6 sub-indicators verification | 0B | ✅ |

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

## R09 — Human Intervention (8 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Portal Submit Suggestion | AGENT §10.5 | API: POST suggest | 0B | ✅ |
| AC-2 | Agent forwarding Brain | EIP §3.3, §4.5.8 | End-to-end: Suggestion→Analysis→Return | 0B | ✅ |
| AC-3 | Agent waits for command | AGENT §9.2, §9.3 | State machine: AWAITING+timeout | 0B | ✅ |
| AC-4 | Permission Verification | SEC §4.4 | Unauthorized→Reject | 0B | ✅ |
| AC-5 | LOA automatic adjustment | AGENT §3 | TRL change→LOA recalculation→behavior switching | 0B | ✅ |
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

## R11 — EIP Protocol (15 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | IDL full + compatible | EIP §4 | protoc + buf lint/breaking | 0B | ✅ |
| AC-2 | 12 Agent integration | EIP §8, AGENT §9.4 | Each Agent≥1 EipVerb closed loop | 0B | ✅ |
| AC-3 | gRPC P99<SLO | EIP §5, DEPLOY §12 | Profile-M Load Test | 0B | ✅ |
| AC-4 | Kafka P99<2s | EIP §2.4, §5 | Event latency monitoring | 0B | ✅ |
| AC-5 | Grayscale upgrade | EIP §6 | Old and new versions coexist | 1 | ✅ |
| AC-6 | Dead Letter Replay | EIP §5.2 | Injection failed→Replay→Success | 0B | ✅ |
| AC-7 | No Any | EIP §4 | grep Any = 0 | 0B | ✅ |
| AC-8 | Bad payload rejection | EIP §5.4 | Mismatch→INVALID_PAYLOAD | 0B | ✅ |
| AC-9 | Complete JSON examples | EIP §4.5 | 12 examples covering all types | 0B | ✅ |
| AC-10 | PERMISSION_DENIED | EIP §4.5.9, §5.4 | Cross-Tenant→PERMISSION_DENIED | 0B | ✅ |
| AC-11 | Third Party Registration Agreement | EIP §9 | Registration Closed Loop | 1 | ✅ |
| AC-12 | REST Gateway Transformation | EIP §10 | 7 Verb Verification | 1 | ✅ |
| AC-13 | RiskDecomposition field | EIP §4 V2.0 | EVALUATE response | 0B | ✅ |
| AC-14 | GSpacePrediction field | EIP §4 V2.0 | PREDICT response | 0B | ✅ |
| AC-15 | DISCOVERY events can be received | EIP §4 V2.0 | Kafka→Agent | 1 | ✅ |

## R12 — Training data (12 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | MVLS three-tier sample size | DATA §2.1, §10.1 | Data statistics report | 0B | ✅ |
| AC-2 | Version traceability | DATA §5 | DVC traceback | 0B | ✅ |
| AC-3 | Synthesis ≤30% (Z_phys≤60%) | DATA §4, §4.1 | Tag statistics | 0B | ✅ |
| AC-4 | Compliance Passed | DATA §6 | License+PII | 0B | ✅ |
| AC-5 | Documentation of Selection | ARCH §7.1 | Document Review | 0B | ✅ |
| AC-6 | 90 Days Delete | DATA §7, EVO §10 | Delete Process | 1 | ✅ |
| AC-7 | KSL-0 Forget 100% | EVO §10 | Delete → Zero Residue | 1 | ✅ |
| AC-8 | Forgetting Policy Review | EVO §10 | Documentation Review | 0B | ✅ |
| AC-9 | Encoder cache reduction GPU ≥50% | DATA §10.5 | A/B comparison | 0B | ✅ |
| AC-10 | G-Space acquisition integrity ≥80% | DATA §10.6 | Acquisition rate monitoring | 0B | ✅ |
| AC-11 | Z-G data alignment rate ≥90% | DATA §10.6 | Alignment check | 0B | ✅ |
| AC-12 | PoC Dataset Delivery | DATA §8.1 | Integrity Check | 0A | ✅ |

## R13 — External Integration (11 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Inner Loop 5 Adapter | AGENT §7.2, INTEG §5 | Per Adapter Operation Closed Loop | 0B | ✅ |
| AC-2 | Tool switching | AGENT §7.1, INTEG §2.1 | GitHub→GitLab hot switching | 0B | ✅ |
| AC-3 | Fault degradation | AGENT §4, INTEG §5 | Git unavailable→LOA≤4 | 0B | ✅ |
| AC-4 | Credential Vault | INTEG §4 | Vault Audit + No Hardcoding | 0B | ✅ |
| AC-5 | Third-party Agent Credential Isolation | INTEG §6.1 | Vault namespace Isolation Verification | 1 | ✅ |
| AC-6 | Third-party Agent Network Isolation | INTEG §6.1 | NetworkPolicy: Unable to access uewm-data | 1 | ✅ |
| AC-7 | Third-party exception data interception | INTEG §6.2 | Inject exception vector → VQV interception | 1 | ✅ |
| AC-8 | G-Space Prometheus closed loop | INTEG §5.2 | ops.* verification | 0B | ✅ |
| AC-9 | G-Space GitHub API closed loop | INTEG §5.2 | code.* verification | 0B | ✅ |
| AC-10 | G-Space data source failure downgrade | INTEG §5.2 | Kill→stale verification | 0B | ✅ |
| AC-11 | Third Party G-Space Query | INTEG §6.3 | QUERY_GSPACE Verification | 1 | ✅ |

## MEM — Long Term Memory (10 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| MEM-AC-1 | Episode automatically created (5 triggers) | ARCH §12.3, EVO §2/§7/§11 | 10 triggers→Episode fully stored | 0B | ✅ |
| MEM-AC-2 | Similarity retrieval P99 < 200ms | ARCH §12.7, ENG §2.14 | pgvector ANN vector retrieval + correlation | 0B | ✅ |
| MEM-AC-3 | Automatic fact extraction (≥3 Episode→Fact) | ARCH §12.4 | Inject consistent pattern→Fact generation, confidence >0.7 | 1 | ✅ |
| MEM-AC-4 | Automatic conflict resolution | ARCH §12.4 | Inject conflicting data → old Fact invalidated | 1 | ✅ |
| MEM-AC-5 | Decay Archive (90 days low importance) | ARCH §12.3, DEPLOY §11.3 | Time Simulation → Validation Archive | 1 | ✅ |
| MEM-AC-6 | Project Profile generation < 50ms | ARCH §12.6 | Performance test + complete content (static/dynamic/risk) | 0B | ✅ |
| MEM-AC-7 | KSL-0 memory fully isolated | ARCH §12.8, SEC §8.4 | Cross-project RECALL returns zero results | 1 | ✅ |
| MEM-AC-8 | Memory-enhanced decision quality | ARCH §12.6, ENG §2.14 | A/B: with memory vs without memory, Kendall τ ≥ +0.05 | 2 | ✅ |
| MEM-AC-9 | Consolidation < 30min Does not affect SLO | ARCH §12.5, DEPLOY §11.2 | Brain P99 monitoring during consolidation | 1 | ✅ |
| MEM-AC-10 | MemoryInfluence Auditable | ARCH §12.7, SEC §8.4 | MemoryInfluence Field Audit Log Validation | 0B | ✅ |

## GPU — GPU Optimized (6 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| GPU-AC-1 | Mixed precision training BF16, memory reduction ≥35% | ARCH §13.2 | Profiling: BF16 vs FP32 memory comparison | 0B | ✅ |
| GPU-AC-2 | Gradient checkpoint memory reduction ≥50% | ARCH §13.3 | Profiling: Comparison of memory with/without checkpoints | 0B | ✅ |
| GPU-AC-3 | TensorRT inference latency reduced by ≥30% | ARCH §13.5 | Benchmark: PyTorch vs TensorRT P99 | 1 | ✅ |
| GPU-AC-4 | The video memory of each component does not exceed the budget | ARCH §13.6, ENG §8.1 | nvidia-smi peak monitoring + startup check | 0B | ✅ |
| GPU-AC-5 | GPU utilization inference > 60% training > 80% | ARCH §13.7 | Prometheus GPU exporter 30min sampling | 0B | ✅ |
| GPU-AC-6 | Cross-platform get_device() function verification | ARCH §13.8 | Mac MPS / RTX CUDA / A100 three-platform test | 0B | ✅ |

## EXT — Third-party Agent (8 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| EXT-AC-1 | Third-party Agent registration process available | ARCH §14.3, EIP §9 | Registration → Review → Activation → Health Check Closed Loop | 1 | ✅ |
| EXT-AC-2 | REST gateway function closed loop | ARCH §14.5, EIP §10 | REST→gRPC conversion 8 path verification | 1 | ✅ |
| EXT-AC-3 | Resource isolation is valid | ARCH §14.6, INTEG §6 | Over quota → current limit + namespace isolation verification | 1 | ✅ |
| EXT-AC-4 | SDK integration test passed | ARCH §14.8, AGENT §16 | Python SDK registration+PREDICT+EVALUATE+RECALL | 1 | ✅ |
| EXT-AC-5 | ADS compliance tools available | ARCH §14.7, AGENT §14 | uewm-agent-lint/test/certify Three tools | 1 | ✅ |
| EXT-AC-6 | Custom Z-Layer registration (Phase 3) | ARCH §14.4 | Custom encoder→VQV verification→Enter Z-Buffer | 3 | ✅ |
| EXT-AC-7 | THIRD_PARTY RBAC interception 100% | SEC §4.3, ARCH §14.3 | All unauthorized requests interception | 1 | ✅ |
| EXT-AC-8 | Standalone API function verification | ARCH §15.2, ENG §8.4 | Agent-less deployment→directly predict/evaluate | 1 | ✅ |

## LIC — License (4 ACs)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| LIC-AC-1 | AGPL/Apache license boundaries clear | ARCH §16.2 | License scan: per-component license correct | 0B | ✅ |
| LIC-AC-2 | Community version fully functional | ARCH §16.3, DEPLOY §15.2 | Community version Profile-S independent deployment verification | 1 | ✅ |
| LIC-AC-3 | CLA Workflow Automation | ARCH §16.4 | PR→CLA Bot→Sign→Merge | 0B | ✅ |
| LIC-AC-4 | Feature Flag Segregated Verification | ARCH §16.3, ENG §7.3 | The community version functions normally after disabling the commercial Flag | 1 | ✅ |

## GND — Dual Space Anchoring (10 ACs, new in V2.0)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| GND-AC-1 | G-Space ≥80 indicators, >95% collection rate | ARCH §4.2, DEPLOY §11.4 | Collection health dashboard | 0B | ✅ |
| GND-AC-2 | φ R² > 0.2 for ≥3 indicator groups | ARCH §5.2 | Dimension-wise R² report | 0A | ✅ |
| GND-AC-3 | Consistency Loss Convergence | ARCH §5.4 | Training Curve | 0A | ✅ |
| GND-AC-4 | Dual space surprise classification ≥80% | ARCH §9.2, EVO §2.1 | 100 events manual inspection | 0B | ✅ |
| GND-AC-5 | Discovery 90 days ≥1 valid mode | ARCH §9.3 | Manual review | 1 | ✅ |
| GND-AC-6 | Z exceeds G independent prediction (p<0.05) | ARCH §9, §16.1 | A/B comparison | 0A | ✅ |
| GND-AC-7 | Ground health 6 sub-indicators normal | ARCH §11.2, EVO §6.1 | All calculations + reports | 0B | ✅ |
| GND-AC-8 | Risk decomposition coverage ≥70% energy | ARCH §8.2 | explained/total | 0B | ✅ |
| GND-AC-9 | G-Space Phase 1 Growth ≥5 Indicator | ARCH §9.4 | Discovery Log | 1 | ✅ |
| GND-AC-10 | PoC Gate Review All passed | ARCH §16.1 | ARI+φR²+p-value | 0A | ✅ |

## NFR (14 items)

| NFR | Description | Design Ref | Verification Method | Phase | Status |
|-----|------|-----------|---------|-------|--------|
| NFR-1 | Brain P99 Profiles | ARCH §7.5, DEPLOY §12 | Load Test | 0B/1/2 | ✅ |
| NFR-2 | Availability 99.95%/99.99% | DEPLOY §4.4, §12 | 48-72h unattended | 0B/1 | ✅ |
| NFR-3 | S→L add resources only | DEPLOY §10, §13, ARCH §3.6 | Extended Test | 2 | ✅ |
| NFR-4 | mTLS full link | SEC §12, EIP §7 | TLS+ rotation | 0B | ✅ |
| NFR-5 | Audit ≥ 1 year | SEC §7.2 | Storage policy + query SLO | 0B | ✅ |
| NFR-6 | <30s self-healing, <2min rollback | DEPLOY §8, §12.5 | Chaos test | 0B | ✅ |
| NFR-7 | KSL-0 zero leakage | SEC §10 | Audit full scan | 1 | ✅ |
| NFR-8 | Decision-making full-link audit | SEC §7, DEPLOY §9 | Decision → Log → Multidimensional query | 0B | ✅ |
| NFR-9 | GPU inference priority | DEPLOY §3.3 | GPU contention P99<600ms | 0B | ✅ |
| NFR-10 | Product versioning | AGENT §8, §8.3 | CRUD+ version query | 0B | ✅ |
| NFR-11 | Hot/Warm/Cold | SEC §7.2, DEPLOY §12 | Hot<2s, Warm<30s | 0B | ✅ |
| NFR-12 | GPU Memory Budget Compliance | ARCH §12 | VRAM Monitoring | 0B | ✅ |
| NFR-13 | Third Party Registration SLO < 5min | ARCH §13 | Register→Activate | 1 | ✅ |
| NFR-14 | Standalone API P99 < 300ms | ARCH §14 | Standalone deployment | 1 | ✅ |

---

## LeWM — LeWorldModel integration (6 ACs, new in V2.0.1)

| AC | Description | Design Ref | Verification Method | Phase | Status |
|----|------|-----------|---------|-------|--------|
| LeWM-AC-1 | SIGReg anti-collapse (normality test passed) | ARCH §5.4 | Epps-Pulley p > 0.05 on 100 projections | 0A | ✅ |
| LeWM-AC-2 | Detection recovery G-Space indicator (linear r > 0.6) | ARCH §16.1 | Dimension-wise linear + MLP detection report | 0A | ✅ |
| LeWM-AC-3 | VoE detects abnormal events (AUC > 0.80) | ARCH §16.1 | 50 Normal + 50 Abnormal ROC Curve | 0A | ✅ |
| LeWM-AC-4 | Projection head improves training stability | ARCH §5.5 | Ablation comparison with vs without projection head | 0A | ✅ |
| LeWM-AC-5 | Binomial loss convergent smooth monotonic | ARCH §5.4 | Visual inspection of training curves + ANOVA | 0A | ✅ |
| LeWM-AC-6 | Time straightened natural emergence | ARCH §16.1 | Continuous velocity vector cosine sim > 0.5 | 0B | ✅ |

---

## AC Statistics

| Category | deliver-v1.1 | V1.0.1 | V2.0.0 | V2.0.1 | V2.0.1 New |
|------|-------------|--------|--------|--------|------------|
| R01 JEPA | 10 | 11 | 11 | 11 | 0 |
| R02 Agent | 10 | 12 | 15 | 15 | 0 |
| R03 Evolution | 7 | 7 | 9 | 9 | 0 |
| R04 Safety | 8 | 10 | 14 | 14 | 0 |
| R05 Deployment | 9 | 10 | 13 | 13 | 0 |
| R06 Reflection | 4 | 4 | 5 | 5 | 0 |
| R07 Multi-Tenant | 6 | 6 | 6 | 6 | 0 |
| R08 Knowledge Transfer | 7 | 7 | 7 | 7 | 0 |
| R09 Manual Intervention | 8 | 8 | 8 | 8 | 0 |
| R10 Feedback Learning | 6 | 6 | 6 | 6 | 0 |
| R11 EIP | 10 | 12 | 15 | 15 | 0 |
| R12 data | 8 | 9 | 12 | 12 | 0 |
| R13 Integration | 4 | 7 | 11 | 11 | 0 |
| MEM long-term memory | 10 | 10 | 10 | 10 | 0 |
| GPU Optimization | 0 | 6 | 6 | 6 | 0 |
| EXT Third Party | 0 | 8 | 8 | 8 | 0 |
| LIC License | 0 | 4 | 4 | 4 | 0 |
| GND Dual Space | 0 | 0 | 10 | 10 | 0 |
| **LeWM Integration** | **0** | **0** | **0** | **6** | **+6** |
| NFR | 11 | 14 | 14 | 14 | 0 |
| **Total** | **103** | **134** | **148** | **154** | **+6** |

---

## Document abbreviation comparison (V2.0.1)

| Abbreviation | Full name | Version | V2.0.1 Core Changes |
|------|------|------|-------------|
| ARCH | UEWM_Architecture | V2.0.1 | +SIGReg, +Projection Head, +Adaptive Hidden Dimension, +VoE Verification, +Detection Verification |
| AGENT | UEWM_Agents_Design | V2.0.1 | (V2.0.0 remains) |
| EVO | UEWM_Self_Evolution | V2.0.1 | +SIGReg security check, +VoE evolution verification |
| SEC | UEWM_Safety_Governance | V2.0.1 | (V2.0.0 maintained) |
| ENG | UEWM_Engineering_Spec | V2.0.1 | +SIGReg Training Pipeline, +Detection +VoE PoC Spec, +Gate Review Updates |
| EIP | UEWM_EIP_Protocol | V2.0.1 | (V2.0.0 remains) |
| DATA | UEWM_Data_Strategy | V2.0.1 | +256-d data, +VoE test set, +probe data |
| DEPLOY | UEWM_Deployment_Operations | V2.0.1 | +PoC directory containing probes/voe/sigreg |
| INTEG | UEWM_Integration_Map | V2.0.1 | (V2.0.0 remains) |