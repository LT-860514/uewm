# 🤖 UEWM Agent system design document

**Document version:** V2.0.1
**Document number:** UEWM-AGENT-002
**Last update:** 2026-04-03
**Status:** Design completed (100% coverage of R02, R09, R11, R13, NFR-8/10 + RECALL + 3rd party ADS + UAT + dual space awareness)
**Change History:**
- V6.0/deliver-v1.0: three-ring layering, ALFA, downgrade, execution engine, adapter, product management
- V1.0.1: Third-party ADS (§14), UAT workflow (§15), SDK release strategy (§16)
- V2.0.0: Agent dual space awareness (receiving RiskDecomposition + GSpacePrediction), Agent can query G-Space, Discovery Alert subscription
- **V2.0.1: (LeWM integration) SDK includes SIGReg monitoring tool; Agent receives 256-d Z-Space vector; VoE test integration; fully merges V1.0.1 content, eliminating all reference dependencies**

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

### 6.3 LLM Prompt management strategy

Versioned Prompt template (`prompts/{agent}/{task}/v{N}.yaml`). Estimated cost before calling → automatic downgrade model beyond ceiling. Optimization: context compression (-30-50% tokens), response caching (-60% duplicate calls), batch merging, model routing (simple tasks → cheap models). A/B testing framework: quality (EBM energy) + cost + delay three-dimensional evaluation. Deployment: K8s ConfigMap hot update, effective in <30s.

---

## 7. External system adapter layer

### 7.1 Adapter interface standard

`ExternalToolAdapter` base class: execute(command), health_check(), get_dependency_type(). GitHub/GitLab replaceable demo.

### 7.2 Complete adapter list (all 12 Agents)

| Agent | Required | Optional | Fault degradation |
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

### 8.3 Product retention strategy

Current version + the last 5 historical versions (6 in total). Storage: PostgreSQL (metadata) + object storage (content). Check the version number after each submission and delete the oldest (metadata is retained for 90 days of auditing). Referenced versions cannot be deleted.

---

## 9. Agent general architecture

### 9.1 Framework structure

```
Agent-Specific Logic → ALFA Controller → Adapter Layer →
Execution Engine → HITL Layer → EIP Client SDK (V2.0) →
State Machine + Safety/Audit
                                    │
                        V2.0 enhancement: EIP Client SDK now handles
                        ├── RiskDecomposition (from EipResponse)
                        ├── GSpacePrediction (from EipResponse)
                        ├── DISCOVERY_ALERT event subscription
                        └── QUERY_GSPACE verb call
```

### 9.2 Agent dual space perception (new in V2.0)

```python
class DualSpaceAwareAgent:
    """V2.0: Agent can use both energy (discovery) and risk (explainable) to make decisions."""
    
    async def make_decision(self, candidates, context):
        # 1. Request a Brain Core Assessment
        response = await self.eip.evaluate(candidates, context)
        
        # 2. Choose which signal to use based on LOA level
        if self.loa >= 7:
            # High degree of autonomy: mainly use energy (including discovering signals)
            best = response.results[0] # lowest energy
            if best.unnamed_risk_pct > 0.3:
                # 30%+ Unnamed Risk → Request Human Confirmation
                await self.request_human_input(
                    reason=f"High unnamed risk ({best.unnamed_risk_pct:.0%}), "
                           f"model sees something metrics can't explain")
            else:
                await self.execute(best.candidate_id)
        
        elif self.loa >= 5:
            # Medium autonomy: display both energy and risk decomposition
            await self.present_options_with_risk(response.results)
        
        else:
            # Low autonomy: only display risk decomposition (interpretable)
            await self.present_risk_only(response.results)
    
    async def on_discovery_alert(self, alert: DiscoveryAlertPayload):
        """Receive notifications of new discoveries from Discovery Engine."""
        #Record to Agent log
        self.log.info(f"Discovery: {alert.pattern_description} "
                      f"(confidence: {alert.confidence})")
        # If relevant to the current task, adjust behavior
        if self.is_relevant(alert):
            await self.adjust_strategy(alert)
```

### 9.3 State Machine

```
IDLE → OBSERVING → PLANNING → EXECUTING → VALIDATING → REPORTING → IDLE
         ↕ ↕
   AWAITING_APPROVAL AWAITING_HUMAN_INPUT (timeout: §9.4)
         ↕
       ERROR → PLANNING (retry) or IDLE (over limit)

Any state → DEGRADED (trigger: required tool failure/Brain unavailable/L3+/TRL fallback)
DEGRADED → IDLE (Recovery: 3 health checks OK / Brain recovery / Level-0 / TRL recovery)
```

### 9.4 AWAITING_HUMAN_INPUT timeout policy

Default 4h (aligned with Tier-2 approval SLA), CRITICAL 1h, OVERRIDE 2h. Upgrade chain: 50%→remind original character, 75%→upgrade PM, 100%→automatically downgrade to SUGGEST + Brain recommended default solution.

### 9.5 EIP Client SDK configuration table (V2.0 enhanced)

| Agent | PREDICT | EVALUATE | ORCHESTRATE | RECALL | **QUERY_GSPACE** | Retry | Circuit Breaker | Heartbeat |
|-------|----------|----------|-------------|--------|------------------|------|------|------|
| AG-CD | 10s | 10s | 5s | 200ms | **2s** | 3 | 5 | 30s |
| AG-CT | 5s | 5s | 3s | 200ms | **2s** | 3 | 5 | 30s |
| AG-DO | 5s | 5s | 3s | 200ms | **2s** | 2 | 3 | 15s |
| AG-ST | 10s | 10s | 5s | 200ms | **2s** | 3 | 5 | 30s |
| AG-MA | 3s | 3s | 2s | 200ms | **1s** | 2 | 3 | 10s |
| AG-SA/FD/AU | 15s | 15s | 5s | 200ms | **2s** | 3 | 5 | 60s |
| AG-PA/PD/BI/PR | 15s | 15s | 5s | 200ms | **2s** | 3 | 5 | 60s |

**RECALL timeout configuration (unified for all Agents):** RECALL timeout 200ms, retry 1 time (memory retrieval is enhanced context, failure will not block decision-making), circuit breaker 10 consecutive timeouts. Brain Core automatically calls long-term memory retrieval when processing PREDICT/EVALUATE, and Agent is not aware of internal memory calls; Agent can also actively initiate a RECALL request to obtain memory context.

---

## 10. Manual intervention and PROJECT_MANAGER

### 10.1-10.4 Role Mapping/PM Capabilities/Intervention Types

PM: READ(all)+SUGGEST/REQUIRE(PA,PD,BI,PR)+READ(arrangement dashboard). PROJECT_MANAGER: Observable (12Agent status + orchestration output + TRL + health + error budget), interventionable (priority + handover gate + status report), non-interventionable (LOA/TRL/security approval/cross-tenant).

### 10.5 Portal API (V2.0 enhanced)

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
| **`/api/dashboard/gspace/{project_id}`** | **GET** | **200 G-Space real-time indicators** | **401/404** |
| **`/api/dashboard/discoveries`** | **GET** | **200 Discovery Engine discovery list** | **401** |
| **`/api/dashboard/discovery/{id}/approve`** | **POST** | **200 Approve new indicator** | **401/403** |
| **`/api/dashboard/discovery/{id}/reject`** | **POST** | **200 Rejected Proposal Indicator** | **401/403** |

Unified error Schema: `{error: {code, message, details, request_id, timestamp}}`. Current limit: read 100/min/user, write 20/min/user, global 1000/min/tenant.

---

## 11. Detailed design of all 12 Agents

Each Agent includes: Responsibilities/Input/Output/Execution Engine/LLM Dependency/One-Time Cost/Required Adapter/Optional Adapter/Downgrade Mode/Target LOA/State Machine Customization.

(5 inner rings: detailed in §6.2. 3 middle rings: AG-SA mixed GPT-4o≤$0.10, AG-FD mixed GPT-4o-mini≤$0.05, AG-AU rule ~$0. 4 outer rings: AG-PA LLM GPT-4o≤$0.10, AG-PD mixed ≤$0.10, AG-BI hybrid ClickHouse+GPT-4o-mini≤$0.05, AG-PR LLM≤$0.10).

---

## 12. Runtime resource configuration

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
| AC-6: Unified EIP Protocol | §9.5 EIP SDK |
| AC-7: Configurable transfer doors | §5 |
| AC-8: LOA downgrade 30s cascade | §5.2 |
| AC-9: Product version 60s alarm | §8 |
| AC-10: Execution Engine Selection Demonstration | §6.2 |
| **AC-11: Third Party Agent ADS Compliance Verification** | **§14** |
| **AC-12: UAT acceptance workflow closed loop** | **§15** |
| **AC-13: Agent receives and uses RiskDecomposition** | **§9.2** |
| **AC-14: Agent can query G-Space** | **§9.5 QUERY_GSPACE** |
| **AC-15: Agent Subscription DISCOVERY_ALERT** | **§9.2 on_discovery_alert** |

---

## 14. Third-party Agent Development Standard (ADS)

### 14.1 The relationship between third-party Agent and built-in Agent

```
Built-in Agent (12): developed and maintained by the UEWM team, deeply integrated with the ALFA/EIP/adapter layer
Third-party Agent: built by external developers through Agent SDK and accessed through the adaptation layer

Common points:
  ├── Unified interaction with Brain Core through EIP protocol
  ├── Uniformly controlled by RBAC permissions
  ├── Uniformly subject to LOA behavior constraints
  └── Unified into the orchestration module scheduling

Differences:
  ├── Third-party Agent does not directly participate in the three-ring layering (mounted externally)
  ├── The initial LOA of the third-party Agent is declared at the time of registration, and the upper limit is subject to ALFA.
  ├── Third-party Agent uses independent resource quota (ARCH §14.6)
  └── Third-party Agent can choose REST gateway (low threshold) or gRPC native (high performance)
```

### 14.2 Agent Development Standard (ADS) Compliance Checklist

| Standard number | Category | Requirements | Verification method | Severity level |
|---------|------|------|---------|---------|
| ADS-1.1 | Protocol | Implement REPORT_STATUS heartbeat (≤60s) | uewm-agent-test heartbeat detection | BLOCKER |
| ADS-1.2 | Protocol | Correctly handle all EipStatus error codes | uewm-agent-test error injection | BLOCKER |
| ADS-1.3 | Protocol | request_id idempotence | Repeat request testing | MAJOR |
| ADS-2.1 | Security | Credentials not hardcoded | uewm-agent-lint static scan | BLOCKER |
| ADS-2.2 | Security | Do not attempt cross-tenant requests | uewm-agent-test permission test | BLOCKER |
| ADS-2.3 | Security | Log does not contain Z-Layer raw vector | uewm-agent-lint log audit | MAJOR |
| ADS-3.1 | Quality | Health Check Endpoint Reachability | HTTP/gRPC Probes | BLOCKER |
| ADS-3.2 | Quality | REPORT_STATUS data L2 norm ∈ [0.5, 2.0] | VectorQualityValidator | MAJOR |
| ADS-3.3 | Quality | Response timeout does not exceed stated SLO | Latency Monitoring | MINOR |
| ADS-4.1 | Documentation | README describing functions/scenarios/Z-Layer mapping | Manual review | MINOR |

### 14.3 Interaction between third-party Agent and orchestration module

Third-party Agents are registered and included in the scheduling of the orchestration module, but their default priority is lower than the built-in Agents. The orchestration module's DIRECTIVE for third-party Agents is "recommended" mode (not mandatory), and the Agent can ignore it but record audits. The artifacts of third-party Agents are included in version consistency detection, but do not block the built-in Agent handover door.

---

## 15. Product Acceptance Testing (UAT) Workflow

### 15.1 Design Goals

Bridge the gap between system testing (AG-ST) and product requirements validation to ensure the end product meets original product requirements.

### 15.2 UAT workflow

```
UAT closed loop (AG-PA/PD product requirements → AG-ST system testing → AG-BI data verification):

  Step 1: AG-PA requirements definition phase
    Output: Acceptance Criteria list
    Format: AC = {id, description, z_layer_mapping, verification_method, priority}
    Storage: SUBMIT_ARTIFACT(type=PRD, contains=AC_list)

  Step 2: AG-ST system testing phase
    Input: AC list (read from product version system)
    Mapping: Each AC → 1+ E2E test cases
    Output: AC level pass/fail report
    Brain Core: EVALUATE(candidates=[AC_pass, AC_fail], context=product_validation)

  Step 3: AG-BI data verification stage
    Input: AC verification results + runtime metrics
    Analysis: Acceptance Rate, Priority Weighted Pass Rate, Trends
    Output: Product Acceptance Dashboard
    Alarm: High priority AC failure → Portal notifies PM

  Step 4: Manual confirmation
    PM/PD reviews UAT results through Portal
    AG-PD can update PRD based on UAT results (iterative closed loop)
    
  Cross-Agent handover:
    AG-PA/PD (outer ring) → product requirements + AC → AG-ST (inner ring) → test results
    → AG-BI (Outer Loop) → Analysis Report → PM → Approval/Iteration
```

---

## 16. Agent SDK release strategy

```
Agent SDK release plan:

  uewm-agent-sdk (Python, PyPI):
    Phase 0: Internal use, 12 built-in Agents based on this SDK
    Phase 1: Alpha release, invitation-only third-party trial
    Phase 2: Beta release, public PyPI
    Phase 3: GA release, SLA commitment

  SDK includes:
    uewm_sdk.agent: UEWMAgent base class, life cycle management
    uewm_sdk.eip: EIP Client (gRPC), message serialization
    uewm_sdk.rest: REST Client (replaces gRPC)
    uewm_sdk.health: health check, heartbeat
    uewm_sdk.metrics: Prometheus metrics export
    uewm_sdk.testing: Compliance testing suite
    uewm_sdk.gspace: GSpaceQueryClient (new in V2.0)
    uewm_sdk.discovery: DiscoveryAlertHandler (new in V2.0)
    uewm_sdk.sigreg: SIGReg monitoring tool (new in V2.0.1/LeWM)
    
  License: Apache 2.0 (independent of the main AGPL project, does not trigger copyleft)
```