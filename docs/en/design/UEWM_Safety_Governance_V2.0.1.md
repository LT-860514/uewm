# 🛡️ UEWM security boundary and governance design document

**Document version:** V2.0.1
**Document Number:** UEWM-SEC-004
**Last update:** 2026-04-03
**Status:** Design Complete (100% coverage of R04, NFR-4/5/7/8/11 + THIRD_PARTY role + Discovery Audit + Ground Health Safety)
**Change History:**
- V6.0/deliver-v1.0: Threat model, RBAC, SOC 2, keys, penetration, response plan
- V1.0.1: THIRD_PARTY role permissions (10th role)
- V2.0.0: Discovery Engine Security Audit, G-Space Data Security, Ground Loss Security Constraints, T6 Threats (G-Space Tampering)
- **V2.0.1: (LeWM integration) Security envelope adds SIGReg normality check; 7 post_checks after evolution; fully merges V1.0.1 content and eliminates all reference dependencies**

---

## 1-2. Overview & Security Layered Architecture

Security goals: No unauthorized access/misoperation/traceability/rollback/no leakage/no degradation. Five layers of defense: Network layer (mTLS)→Protocol layer (EIP signature)→Business layer (RBAC+EBM)→Data layer (KSL+DP)→Audit layer (signature chain).

---

## 3. UEWM threat model T1-T6

**T1 Agent injection/hijacking:** mTLS two-way authentication + message signature + input anomaly detection. EBM energy mutation >2σ alarm → isolate Agent + roll back Z-Buffer.

**T2 LoRA poisoning (manual feedback):** Bias detection (single user ≤30%) + feedback diversity + anomaly detection. Decision diversity entropy ≥ 0.6 → rollback LoRA+ flag suspicious feedback.

**T3 cross-tenant information leakage:** KSL classification + DP (ε budget) + Secure Aggregation. Reverse derivation <random +5%. Privacy Budget Manager + Regular Audits.

**T4 Privilege Escalation Attack:** LOA is forced to be verified on the Brain Core side, and the Agent cannot declare it on its own. Real-time alarm if the operation does not match the LOA.

**T5 Brain Core was attacked and downgraded:** Agent side hardcoded operation boundary + double signature. Brain health check failed → Full Agent rule engine mode.

**T6 G-Space indicator tampering (new in V2.0)**:

```
T6 Threat: Attackers tamper with G-Space indicators to mislead Brain Core decision-making

  Attack vector:
    ├── Tampering with Prometheus data → False ops.* indicators
    ├── Tampering with CI results → False test.* indicators
    ├── Tampering with Git statistics → Fake code.* metrics
    └── Inject fake Discovery → Add malicious G-Space indicator
  
  Defense:
    ├── G-Space data signature: Each collection comes with collector signature + timestamp
    ├── Anomaly detection: indicator mutation > 3σ → marked as suspicious, not used for consistency loss temporarily
    ├── Multi-source cross-validation: code.* is calculated from tree-sitter + git diff at the same time, inconsistent → warning
    ├── Discovery Review: New indicators must be reviewed manually (SECURITY + ARCHITECT)
    └── G-Space write audit: every time an indicator is written, the audit log is recorded (source/value/signature)
```

---

## 4. RBAC three-dimensional mapping model

### 4.1-4.2 Permission granularity & role matrix

7Permissions: READ/SUGGEST/REQUIRE/OVERRIDE/ABORT/ADMIN/EVOLVE. 10 roles: PM/ARCHITECT/DEVELOPER/QA/DEVOPS/MARKETING/SECURITY/PROJECT_MANAGER/SYSTEM_ADMIN/**THIRD_PARTY**. The complete role×Agent×authority matrix is ​​defined.

### 4.3 Dynamic permission rules

LOA ≤ 4 → Intervention downgrade SUGGEST | CRITICAL → SECURITY joint approval | Cross-Tenant → All prohibited | EVOLVE → Double confirmation.

**THIRD_PARTY role permissions (10th role)**:

```
THIRD_PARTY role permissions:

  Default permissions:
    READ: Authorize Z-Layer (declared during registration)
    SUGGEST: only for its own Agent instance
    REPORT_STATUS: Authorize Z-Layer to write
    SUBMIT_ARTIFACT: Only its own products, requires Schema verification

Disallowed permissions:
    OVERRIDE / ABORT / ADMIN / EVOLVE: All prohibited
    REQUIRE: Forbidden (third parties cannot force built-in Agent)
    Cross-Tenant: Forbidden (inherits global rules)

  Dynamic limits:
    LOA: The upper limit is declared at the time of registration, not exceeding LOA 6 (inner ring LOA 7+ is not reachable by third parties)
    Quotas: Individual resource quotas (ARCH §14.6)
    Audit: Mandatory audit for each request (built-in Agent only audits decision-making classes)

  Upgrade path:
    free → standard: automatic (verified by ADS compliance)
    standard → premium: requires SECURITY review
    premium → built-in: code review required + two-person approval + full compliance testing
```

### 4.4 V2.0 enhancement: Discovery audit permissions

```
New G-Space Metrics Review by Discovery Engine:
  APPROVE_DISCOVERY: SECURITY + ARCHITECT (double)
  REJECT_DISCOVERY: SECURITY or ARCHITECT (single player)
  VIEW_DISCOVERY: PM, ARCHITECT, SECURITY, SYSTEM_ADMIN
  THIRD_PARTY: Discovery is not viewable (to avoid leaking internal schema)
```

### 4.5 Dynamic permission execution implementation

DynamicPermissionEnforcer is executed at the EIP Gateway layer. Priority: (1) Cross-Tenant prohibition → (2) CRITICAL requires SECURITY → (3) LOA ≤ 4 downgrade SUGGEST → (4) EVOLVE double confirmation → (5) Standard RBAC matrix. Code-level implementation includes specific checking logic and PERMISSION_DENIED/REQUIRES_CO_APPROVAL responses for each rule.

### 4.6 RBAC full test matrix

10 roles × 12 Agents × 7 permissions = 840 combinations (V2.0: +THIRD_PARTY role expanded to 10 roles). Legal ~120 (within RBAC matrix), unauthorized ~720 → 100% interception. Dynamic rules come with 45 additional use cases. Discovery permission test added. Total 907 tests, zero tolerance. Automatic generation: parse matrix → full arrangement → must_deny/allowed → send EipRequest → verify. Every RBAC change + weekly returns.

---

## 5. Operational risk classification and manual approval access control

LOW/MEDIUM/HIGH/CRITICAL Level 4. CRITICAL→Mandatory approval by two people.

### 5.2 Approval workflow state machine

PENDING→ASSIGNED→REVIEWING→APPROVED/REJECTED/EXPIRED. ASSIGNED→ESCALATED (50% SLA not reviewed). Timeout: LOW/MEDIUM→automatic approval, HIGH→automatic rejection+alarm, CRITICAL→automatic rejection+Kill Switch alarm. SLA: LOW 4h, MEDIUM 2h, HIGH 1h, CRITICAL 30min.

---

## 6. EBM safety energy function

E_safety constraints: single-layer safety + cross-layer safety + evolutionary safety. Aligned with Architecture §6.

---

## 7. Audit system

### 7.1 Audit data model

JSON: event_id, timestamp, event_type, agent_id, project_id, energy_score, risk_level, decision_summary, latency_ms.

### 7.2 Audit log capacity planning

Profile-S: ~1.7GB/day, 1TB per year. Profile-M: ~17GB/day, 10TB per year. Profile-L: ~78GB/day, 50TB per year.

Hot(SSD, 7 days, P99<2s) → Warm(HDD/Parquet, 7-90 days, P99<30s) → Cold(S3 Glacier+zstd 5:1, 90 days+, P99<5min). Automatic cooling: Hot→Warm every day at 02:00, Warm→Cold every Sunday at 02:00. Evolution logs are kept permanently.

### 7.3 Audit log query API

```
POST /api/audit/query
  Body: {time_range, filters:{agent_id, project_id, event_type,
         energy_range, risk_level, user_id}, sort, pagination, storage_tier}
  Response: {total, page, results:[{event_id, timestamp, event_type,
             summary, energy_score, risk_level}], query_latency_ms}

GET /api/audit/{event_id} # Single item details
GET /api/audit/stats # Aggregation statistics
GET /api/audit/export?format=csv # Export (for compliance)
```

Query performance: Hot single <100ms, time range (1h) <2s; Warm single <5s, aggregation <30s; Cold requires recovery request <5min.

### 7.4 V2.0 New audit dimension

```
Discovery Engine Audit:
  Each Discovery event: discovery_id, pattern, confidence, proposed_metric, evidence_count
  Each Discovery review: reviewer, decision (approve/reject), reason, timestamp
  G-Space indicator addition: metric_name, source, discovery_origin, added_by, timestamp
  
G-Space collection audit:
  Abnormal metric values: metric_name, value, expected_range, marked_suspicious, timestamp
  Collection failure: collector, metric, error, timestamp
```

---

## 8-10. Harmful behavior detection / rollback protection / data security

Harmful behavior classification + anti-loop + Kill Switch + SafeEvalAgent. Rollback granularity (layer/full model/Z-Buffer) + rollback safety check. Differential privacy + reverse detection.

### 8.4 Long-term memory security isolation

**KSL aware Episode/Fact isolation rules (based on Architecture §12.8):**

KSL-0: Episode+Fact is completely isolated, cross-project RECALL search returns zero results, and Episode+Fact is deleted together (100%) when forgotten. KSL-1: Only share aggregate statistical level Fact (DP ε≤0.5), Episode snapshots do not cross projects. KSL-2: Share post-desensitization Pattern/AntiPattern Fact (reviewed by SECURITY/ARCHITECT), Episode only share desensitization decision_summary. KSL-3: Federated Learning + Desensitization Fact + Aggregation Episode Statistics (Secure Aggregation). KSL-4: Fully shared memory within the same tenant, but is still prohibited across tenants.

**Memory Audit:** Each time RECALL is retrieved, the audit log is recorded (querier/project/returned Episode number/Fact number). Episode Create/Archive/Delete records complete audit chain. The MemoryInfluence field is written to the decision audit (NFR-8 benchmark) along with the EIP Response.

---

## 11. SOC 2 Compliance Roadmap

Phase 0→Type I ready, Phase 2→Type II compliant. Trust Criteria mapping: Security(RBAC+mTLS+KillSwitch), Availability(99.95%+error budget), Processing Integrity(EBM+Audit Chain), Confidentiality(KSL+DP), Privacy(GDPR/CCPA+Forgetting+PII). List of 8 CC control points. Data residency: Z-Layer does not span regions, and regions are configurable.

---

## 12. Key and certificate management

mTLS certificate: ≤90 days automatic rotation (Vault/built-in CA). LoRA weight: SHA-256 signature (MLflow). Audit log: append-only + daily signature chain. Key: Vault/K8s Secrets (at-rest encryption). External API: Vault Dynamic Secrets.

---

## 13. 进化安全审计维度

Before triggering → EVOLVE permission (double confirmation). Output → LoRA signature + log + comparison report. Emergency rollback→SECURITY single player. Audit reporting → automatic weekly (evolution/rollback/envelope trigger/bias). 3 consecutive rollbacks → circuit breaker → automatic failure analysis report.

---

## 14. Penetration Testing Plan

Gray box testing, independent staging, Phase 0/1/2 + half a year.

**Original 23 tests** (T1-T5): T1 (5 items: forged certificates/replays/encoding offsets/message tampering/DDoS), T2 (4 items: single-user bias/multi-account collaboration/progressive drift/extreme values), T3 (5 items: cross-tenant query/gradient reversal/KSL-0 leakage/budget bypass/namespace escape), T4 (4 items: forged LOA/low LOA high risk/bypassing approval/EVOLVE single person), T5 (4 items: Brain out-of-bounds command/Brain unavailable/response tampering/abnormal energy).

### 14.1 T6 penetration testing extension (new in V2.0, 5 items)

- T6-1: Tampering with Prometheus exporter data
- T6-2: Inject fake CI test results
- T6-3: Fake Discovery Proposal
- T6-4: G-Space indicator signature bypass
- T6-5: Multi-source cross-validation bypass

**28 total penetration tests. ** Timeline: Phase 0 M4 T1+T4+T5+T6 (2 weeks), Phase 1 M7 T2+T3 (2 weeks), Phase 2+ full return (3 weeks).

---

## 15. Security incident response plan

Level 4: SEV-1 (Critical, 15min) SEV-2 (High, 1h) SEV-3 (Medium, 4h) SEV-4 (Low, 24h). Plan A (Kill Switch): Full stop→Assessment→Recovery/Isolation→Afterwards. Plan B (T1 Agent injection): Alarm→Isolate→Z-Buffer rollback→Certificate revocation and reissue. Plan C (T3 suspected data leakage): L3 tenant isolation → full audit → federal suspension → notify tenant → privacy assessment (GDPR 72h). Plan D (T5 Brain is attacked): Agent rule engine → Brain isolation → Image reconstruction → LoRA rollback → Z-Buffer recovery → Ring-by-ring recovery.

---

## Appendix: ASL Security Level Framework / Future — Industrial Functional Safety

ASL-1 to ASL-4. Industrial functional safety moved to appendix (Phase 4+ Future Extension).

---

## 16. Acceptance criteria mapping

| AC | Design Support |
|----|---------|
| AC-1: 100% interception beyond authority | §4.5+§4.6 (907 test + third party) |
| AC-2: High risk requires approval | §5+§5.2 (state machine) |
| AC-3: The audit is complete and available | §7+§7.3 (Query API) |
| AC-4: KSL-0 Zero Leakage | §10 |
| AC-5: T1-T5 penetration | §14(23 items) |
| AC-6: RBAC Configurable Auditing | §4 |
| AC-7: mTLS+signature+chain | §12 |
| AC-8: SOC2 TypeI Ready | §11.3 |
| **AC-9: THIRD_PARTY character overrides 100% interception** | **§4.3** |
| **AC-10: Third-party Agent mandatory audit 100%** | **§4.3** |
| **AC-11: T6 G-Space Tamper Defense** | **§3 T6** |
| **AC-12: Discovery Audit Permission Verification** | **§4.4** |
| **AC-13: G-Space Collection Audit Complete** | **§7.4** |
| **AC-14: 28 penetration tests passed** | **§14.1** |