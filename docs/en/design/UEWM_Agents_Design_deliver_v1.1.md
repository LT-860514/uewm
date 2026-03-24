# 🤖 UEWM Agent system design document

**Document version:** deliver-v1.1
**Document number:** UEWM-AGENT-002
**Last update:** 2026-03-24
**Status:** Design completed (100% coverage of R02, R09, R11, R13, NFR-8/10 + Long Memory RECALL)
**Merge source:** Agents Design V6.0 - Full merging, eliminating patch dependencies
**Change History:**
- V3.0: Three-ring layering, ALFA, downgrade, cross-ring handover, execution engine, adapter, product management, PM role
- V4.0: Detailed design of middle ring/outer ring adapter
- V5.0: Complete design of middle/outer ring Agent, DEGRADED state machine, per-Profile scaling, Portal API error Schema, LLM Prompt management
- V6.0: AWAITING_HUMAN_INPUT timeout policy, product retention policy, EIP Client SDK configuration table; 100% coverage achieved
- **deliver-v1.0: full merge, no incremental patch dependency**

---

## 1. Agent system overview

12 specialized Agents, three-ring layered delivery, EIP protocol to interact with Brain Core, and ALFA framework dynamic LOA control.

| # | Agent | Codename | Core Responsibilities | Z-Layer | Ring | Phase | Execution Engine |
|---|-------|------|---------|---------|-----|-------|---------|
| 1 | Product Analysis | AG-PA | Market Analysis, Competitive Product Research | Z_market,Z_val | External | 2 | LLM |
| 2 | Product Design | AG-PD | Requirements Definition, Prototyping | Z_val,Z_biz | External | 2 | Mixed |
| 3 | System Architecture | AG-SA | Technology Selection, Topology | Z_arch,Z_logic | Medium | 1 | Mixed |
| 4 | Functional disassembly | AG-FD | Detailed design, task decomposition | Z_logic,Z_arch | Medium | 1 | Mixed |
| 5 | Code Development | AG-CD | Code Generation, Review | Z_impl | Inner | 0 | Mixed |
| 6 | Code Testing | AG-CT | Unit/Integration Testing | Z_impl,Z_quality | Inner | 0 | Mixed |
| 7 | Deployment and online | AG-DO | CI/CD orchestration | Z_phys,Z_impl | Internal | 0 | Rules |
| 8 | System Test | AG-ST | E2E/Performance Test | Z_quality,Z_phys | Inner | 0 | Mixed |
| 9 | Monitoring alarm | AG-MA | Real-time monitoring | Z_phys | Internal | 0 | Rules |
| 10 | BI Analysis | AG-BI | Data Analysis, KPI | Z_val,Z_market | External | 2 | Mixed |
| 11 | Promotion Operation | AG-PR | Channel Promotion | Z_market | External | 2 | LLM |
| 12 | Security Audit | AG-AU | Permission Audit, Compliance | Full Layer | Medium | 1 | Rules |

---

## 2. Three-ring layered architecture

Inner loop (Phase 0, LOA 7-9): AG-CD/CT/DO/ST/MA — end-to-end closed-loop automatic operation. Middle Ring (Phase 1, LOA 5-7): AG-SA/FD/AU — Generate suggestions for people to choose from. Outer ring (Phase 2, LOA 3-5): AG-PA/PD/BI/PR — Human-led Agent-assisted.

---

## 3. ALFA Automation Level Framework

LOA = f(min_TRL → base_LOA, historical performance ±2, upper limit of risk). TRL_TO_BASE_LOA: {0:1, 1:2, 2:4, 3:6, 4:8, 5:9}. RISK_CAP: {LOW:10, MEDIUM:8, HIGH:6, CRITICAL:4}. LOA → Behavior: 1-2 INFORMATION_ONLY, 3-4 OPTIONS_FOR_HUMAN, 5-6 RECOMMEND_AND_WAIT, 7-8 AUTO_EXECUTE_NOTIFY, 9-10 FULLY_AUTONOMOUS. Notified of changes via the EIP LOA_UPDATE event.

---

## 4. Agent downgrade framework

Degradation matrix when each Agent is unavailable (all 12 Agents include degradation behavior + global impact + recovery conditions). External tools: Mandatory dependency failure → LOA ≤ 4, optional dependency failure → LOA unchanged. Brain Core is unavailable→Full Agent rule engine mode.

---

## 5. Cross-ring handover protocol

3 handover doors: external→middle (product→architecture, energy<0.3, manual required), middle→internal (architecture→execution, energy<0.25, manual required), internal→outer (execution→business feedback, automatic). LOA cascade assessment: identify downstream → assess impact → notify roles → update milestones → audit.

---

## 6. Execution engine strategy

Brain Core→WHAT, Agent execution engine→HOW-intelligent, external tools→HOW-mechanical. Inner ring 5Agent selection: AG-CD mixed (GPT-4o+ rule, ≤$1/time), AG-CT mixed (GPT-4o-mini, ≤$0.05), AG-DO rule (~$0), AG-ST mixed (GPT-4o-mini, ≤$0.10), AG-MA rule (~$0).

### 6.3 LLM Prompt Management Strategy [V5.0]

Versioned Prompt template (`prompts/{agent}/{task}/v{N}.yaml`). Estimated cost before calling → automatic downgrade model beyond ceiling. Optimization: context compression (-30-50% tokens), response caching (-60% duplicate calls), batch merging, model routing (simple tasks → cheap models). A/B testing framework: quality (EBM energy) + cost + delay three-dimensional evaluation. Deployment: K8s ConfigMap hot update, effective in <30s.

---

## 7. External system adapter layer

### 7.1 Adapter interface standard

`ExternalToolAdapter` base class: execute(command), health_check(), get_dependency_type(). GitHub/GitLab replaceable demo.

### 7.2 Complete adapter list (all 12 Agents)| Agent | Required | Optional | Fault degradation |
|-------|------|------|---------|
| AG-CD | GitAdapter (GitHub/GitLab) | IDEAdapter, PkgMgrAdapter | diff file |
| AG-CT | CIAdapter (Actions/Jenkins) | CoverageAdapter, SonarQubeAdapter | Local testing |
| AG-DO | K8sAdapter, RegistryAdapter | HelmAdapter, ArgoCDAdapter | YAML output |
| AG-ST | TestEnvAdapter | K6Adapter, PlaywrightAdapter | mock mode |
| AG-MA | PrometheusAdapter, GrafanaAdapter | JaegerAdapter, PagerDutyAdapter | metrics-server |
| AG-SA | — | PlantUMLAdapter, OpenAPIGenAdapter | Text Schema Documentation |
| AG-FD | — | JiraAdapter, LinearAdapter | JSON Task List |
| AG-AU | SemgrepAdapter, TrivyAdapter | ZAPAdapter, GitLeaksAdapter | "Unaudited" + blocking |
| AG-PA | — | SimilarWebAdapter, CrunchbaseAdapter | Manual input |
| AG-PD | — | FigmaAdapter | Manual design document |
| AG-BI | ClickHouseAdapter/PostgreSQLAdapter | MetabaseAdapter | Cache data |
| AG-PR | — | WordPressAdapter, AhrefsAdapter | Solution Documentation |

---

## 8. Product version management

8 product types (PRD, architecture document, functional decomposition, code changes, test report, deployment checklist, monitoring report, security audit report). Version inconsistency detection: real-time detection every time SUBMIT_ARTIFACT, alarm ≤60s.

### 8.3 Product retention policy [V6.0]

Current version + the last 5 historical versions (6 in total). Storage: PostgreSQL (metadata) + object storage (content). Check the version number after each submission and delete the oldest (metadata is retained for 90 days of auditing). Referenced versions cannot be deleted.

---

## 9. Agent general architecture

### 9.1 Framework structure

Agent-Specific Logic → ALFA Controller → Adapter Layer → Execution Engine → HITL Layer → EIP Client SDK → State Machine + Safety/Audit.

### 9.2 State Machine [V5.0 including DEGRADED]```
IDLE → OBSERVING → PLANNING → EXECUTING → VALIDATING → REPORTING → IDLE
         ↕                ↕
  AWAITING_APPROVAL  AWAITING_HUMAN_INPUT (timeout: §9.3)
         ↕
       ERROR → PLANNING (retry) or IDLE (over limit)

Any state → DEGRADED (trigger: required tool failure/Brain unavailable/L3+/TRL fallback)
DEGRADED → IDLE (Recovery: 3 health checks OK / Brain recovery / Level-0 / TRL recovery)
```### 9.3 AWAITING_HUMAN_INPUT timeout policy [V6.0]

Default 4h (aligned with Tier-2 approval SLA), CRITICAL 1h, OVERRIDE 2h. Upgrade chain: 50%→remind original character, 75%→upgrade PM, 100%→automatically downgrade to SUGGEST + Brain recommended default solution.

### 9.4 EIP Client SDK configuration table [V6.0]

| Agent | PREDICT | EVALUATE | ORCHESTRATE | Retry | Meltdown | Heartbeat |
|-------|----------|----------|-------------|------|------|------|
| AG-CD | 10s | 10s | 5s | 3 | 5 consecutive timeouts | 30s |
| AG-CT | 5s | 5s | 3s | 3 | 5 | 30s |
| AG-DO | 5s | 5s | 3s | 2 | 3 | 15s |
| AG-ST | 10s | 10s | 5s | 3 | 5 | 30s |
| AG-MA | 3s | 3s | 2s | 2 | 3 | 10s |
| AG-SA/FD/AU | 10-15s | 10-15s | 5s | 3 | 5 | 60s |
| AG-PA/PD/BI/PR | 15s | 15s | 5s | 3 | 5 | 60s |

**[deliver-v1.1] RECALL timeout configuration (unified for all Agents):** RECALL timeout 200ms, retry 1 time (memory retrieval is enhanced context, failure will not block decision-making), circuit breaker 10 consecutive timeouts. Brain Core automatically calls long-term memory retrieval when processing PREDICT/EVALUATE, and Agent is not aware of internal memory calls; Agent can also actively initiate a RECALL request to obtain memory context.

---

## 10. Manual intervention and PROJECT_MANAGER

### 10.1-10.4 Role Mapping/PM Capabilities/Intervention Types

PM: READ(all)+SUGGEST/REQUIRE(PA,PD,BI,PR)+READ(arrangement dashboard). PROJECT_MANAGER: Observable (12Agent status + orchestration output + TRL + health + error budget), interventionable (priority + handover gate + status report), non-interventionable (LOA/TRL/security approval/cross-tenant).

### 10.5 Portal API [V5.0 including error response]

| Interface | Method | Success | Error |
|------|------|------|------|
| `/api/agent/{id}/suggest` | POST | 200 accepted | 401/403/404/429 |
| `/api/agent/{id}/status` | GET | 200 status | 401/404 |
| `/api/agent/{id}/tasks` | GET | 200 task list | 401/404 |
| `/api/agent/{id}/respond` | POST | 200 forwarded | 401/403/404/409 |
| `/api/dashboard/overview` | GET | 200 Overview | 401 |
| `/api/dashboard/orchestration` | GET | 200 Orchestration(PM) | 401/403 |
| `/api/dashboard/error-budget` | GET | 200 Error budget | 401 |
| `/api/dashboard/trl-progress` | GET | 200 TRL progress | 401 |

Unified error Schema: `{error: {code, message, details, request_id, timestamp}}`. Current limit: read 100/min/user, write 20/min/user, global 1000/min/tenant.

---

## 11. Detailed design of all 12 Agents

Each Agent includes: Responsibilities/Input/Output/Execution Engine/LLM Dependency/One-Time Cost/Required Adapter/Optional Adapter/Downgrade Mode/Target LOA/State Machine Customization.

(5 inner rings: detailed in §6.2. 3 middle rings: AG-SA mixed GPT-4o≤$0.10, AG-FD mixed GPT-4o-mini≤$0.05, AG-AU rule ~$0. 4 outer rings: AG-PA LLM GPT-4o≤$0.10, AG-PD mixed ≤$0.10, AG-BI hybrid ClickHouse+GPT-4o-mini≤$0.05, AG-PR LLM≤$0.10).

---

## 12. Runtime resource configuration [V5.0 includes per-Profile]

Profile-M baseline: AG-CD 8-core 16GB, AG-CT 4-core 8GB, AG-DO 2-core 4GB, etc. per-Profile scaling: S(HPA min=1, max=1-2), M(min=1, max=3-5), L(min=2, max=10-20). HPA CPU thresholds: S 80%, M 80%, L 70%. Profile-L special: Tenant isolation namespace + GPU sharding + NetworkPolicy.

---

## 13. Acceptance criteria mapping

| AC | Design Support |
|----|---------|
| AC-1: Inner loop 5Agent LOA≥7 | §2+§3 |
| AC-2: Zhonghuan 3Agent LOA≥5 | §11.2 |
| AC-3: Outer Ring 4Agent LOA≥3 | §11.3 |
| AC-4: LOA 3↔8 automatic switching | §3 ALFA |
| AC-5: Brain is unavailable → Rules Engine | §4 Downgrade Framework |
| AC-6: Unified EIP Protocol | §9.4 EIP SDK |
| AC-7: Configurable transfer doors | §5 |
| AC-8: LOA downgrade 30s cascade | §5.2 |
| AC-9: Product version 60s alarm | §8 |
| AC-10: Execution Engine Selection Demonstration | §6.2 |