# 📡 UEWM Engineering Intelligent Protocol (EIP) Design Document

**Document version:** deliver-v1.1
**Document Number:** UEWM-EIP-007
**Last update:** 2026-03-24
**Status:** Design complete (100% coverage of R11 + Long Memory RECALL verb)
**Benchmarking requirements:** R11 (all), R09 (manual intervention messages), R02 (arrangement instructions)
**Merge source:** EIP Protocol V3.0 — Full merging, eliminating patch dependencies
**Change History:**
- V1.0: Initial version, aligned with R11 strongly typed payload specification
- V2.0: JSON example (§4.5); EipStatus extension; structured error code (§5.4)
- V3.0: Kafka Topic design (§2.4); AWAITING_COMMAND message (§3.3); EipStream service (§2.5)
- **deliver-v1.0: full merge, no incremental patch dependency**

---

## 1. Protocol Overview

EIP (Engineering Intelligence Protocol) is a unified communication protocol between Agent and Brain Core, which serves as the "central nervous system" of the UEWM system. All Agent interactions, human intervention, and orchestration instructions are transmitted through this protocol.

### 1.1 Design Constraints

- It is forbidden to retain `google.protobuf.Any` in the final IDL (requirements phase placeholders are not included in the code)
- Each EipVerb corresponds to a unique Request and Result message type (using oneof)
- The first entry in all enumerations must be XXX_UNKNOWN = 0 (Protobuf default value is safe)
- New message types must be backward compatible (only add fields, not delete/renumber)
- Each message type must be accompanied by at least one JSON example (see §4.5)

---

## 2. Message type and transport layer

### 2.1 Four message types

| Type | Direction | Transport Layer | Semantics |
|------|------|--------|------|
| Request | Agent→Brain | gRPC bidirectional flow | Synchronous request |
| Response | Brain→Agent | gRPC bidirectional flow | Request response |
| Event | Brain→Agent(s) | Kafka | Asynchronous events/broadcast |
| Stream | Bidirectional | gRPC server stream | Long connection status push |

### 2.2 Transport layer hybrid architecture

| Path | Protocol | Applicable Scenarios |
|------|------|---------|
| Agent↔Brain Synchronization Decision | gRPC Bidirectional Streaming (TLS) | PREDICT/EVALUATE/ORCHESTRATE |
| Agent→Brain status reporting | Kafka (asynchronous) | REPORT_STATUS |
| Brain→Agent(s) events | Kafka (asynchronous) | LOA_UPDATE/ARTIFACT_ALERT/HANDOFF_READY |
| Agent↔Brain Human Intervention | gRPC (TLS) | HUMAN_INTERVENTION |
| Dashboard/Agent real-time subscription | gRPC server stream | EipStreamService |

### 2.3 Message routing mode

| Pattern | Description | Example |
|------|------|------|
| Unicast (Unicast) | Agent↔Brain 1:1 | PREDICT request-response |
| Broadcast | Brain→All Agents | Global LOA Downgrade Notification |
| Ring Broadcast | Brain → All Agents in a certain ring | Inner ring evolution suspension notification |

### 2.4 Kafka Topic Design```
Topic naming: uewm.{scope}.{event_type}.{version}

Topics:
  uewm.events.loa-changed.v1 # LOA change event
  uewm.events.trl-updated.v1 # TRL update event
  uewm.events.handoff-ready.v1 # Handoff ready event
  uewm.events.artifact-mismatch.v1 # Product versions are inconsistent
  uewm.events.slo-alert.v1 # SLO alarm event
  uewm.events.evolution-completed.v1 # Evolution completed event
  uewm.events.privacy-budget.v1 # Privacy budget event
  uewm.events.awaiting-command.v1 # Agent is waiting for manual commands
  uewm.status.agent-heartbeat.v1 # Agent status reporting (high throughput)
  uewm.audit.decisions.v1 # Decision audit log (high throughput)
  uewm.dlq.{original_topic}.v1 # Dead letter queue

Partition strategy:
  events.* → partition by project_id (same as project events in order)
  status.* → partition by agent_id (same as Agent status in order)
  audit.* → partition by timestamp hash (uniform distribution)

Retention policy:
  events.* → 7 days | status.* → 24h | audit.* → 90 days | dlq.* → 30 days

Consumer Groups:
  uewm-brain-core     → status.agent-heartbeat
  uewm-orchestrator → events.* (orchestration module aggregation events)
  uewm-audit-writer → audit.* (write to Elasticsearch/ClickHouse)
  uewm-agent-{id} → events.* (filtered by agent_id)
```### 2.5 EipStream service definition```protobuf
service EipStreamService {
  rpc SubscribeEvents(StreamSubscription) returns (stream EipEvent);
  rpc SubscribeDirectives(AgentStreamSubscription) returns (stream EipEvent);
}

message StreamSubscription {
  repeated EipEventType event_types = 1;
  string project_id = 2;
  string agent_id = 3;
  RoutingScope min_scope = 4;
}

message AgentStreamSubscription {
  string agent_id = 1;
  string ring = 2;   // inner/middle/outer
}
```Usage scenarios: Portal Dashboard refreshes in real time; Agent receives DIRECTIVE/LOA_UPDATE push; Error budget real-time banner.

---

## 3. EipVerb verb system

### 3.1 Agent → Brain request verb

| Verb | Purpose | Request payload | Response payload |
|------|------|---------|---------|
| PREDICT | World Model Prediction | PredictRequest | PredictResult |
| EVALUATE | EBM solution evaluation | EvaluateRequest | EvaluateResult |
| ORCHESTRATE | Orchestration task sequencing/handover/arbitration | OrchestrateRequest | OrchestrateResult |
| REPORT_STATUS | Agent status report | ReportStatusPayload | Ack |
| SUBMIT_ARTIFACT | Deliverable product submission | SubmitArtifactPayload | Ack |
| HUMAN_INTERVENTION | Human Intervention Request | HumanInterventionPayload | BrainAnalysisPayload |
| **RECALL** | **Memory Retrieval (Long Term Memory)** | **RecallRequest** | **RecallResult** |

### 3.2 Brain → Agent command verb

| Verb | Purpose | Load |
|------|------|------|
| DECISION | Decision result | EvaluateResult |
| DIRECTIVE | Orchestration instructions | DirectivePayload |
| LOA_UPDATE | LOA change notification | LoaUpdatePayload |
| ARTIFACT_ALERT | Product version inconsistency alarm | ArtifactAlertPayload |

### 3.3 Manual intervention message

| Message Type | Direction | Payload | Description |
|---------|------|------|------|
| HUMAN_INTERVENTION | Portal→Brain(via Agent) | HumanInterventionPayload | Character Engineer Suggestions/Requirements/Override/Abort |
| BRAIN_ANALYSIS | Brain→Portal(via Agent) | BrainAnalysisPayload | Brain analysis decision results |
| AWAITING_COMMAND | Agent→Portal(via Kafka) | AwaitingCommandPayload | Agent waits for the next manual command |

---

## 4. Protobuf IDL complete definition```protobuf
syntax = "proto3";
package uewm.eip.v1;

// ========== gRPC service ==========

service EipService {
  rpc SendRequest(EipRequest) returns (EipResponse);
  rpc BiDirectionalStream(stream EipRequest) returns (stream EipResponse);
}

service EipStreamService {
  rpc SubscribeEvents(StreamSubscription) returns (stream EipEvent);
  rpc SubscribeDirectives(AgentStreamSubscription) returns (stream EipEvent);
}

// ========== Message envelope ==========

message EipRequest {
  string request_id = 1;
  string agent_id = 2;
  string project_id = 3;
  EipVerb verb = 4;
  oneof payload {
    PredictRequest predict = 10;
    EvaluateRequest evaluate = 11;
    OrchestrateRequest orchestrate = 12;
    ReportStatusPayload report_status = 13;
    SubmitArtifactPayload submit_artifact = 14;
    HumanInterventionPayload human_intervention = 15;
    RecallRequest recall = 16;                        // [deliver-v1.1]
  }
  int64 timestamp_ms = 6;
  string eip_version = 7;
}

message EipResponse {
  string request_id = 1;
  EipStatus status = 2;
  oneof result {
    PredictResult predict_result = 10;
    EvaluateResult evaluate_result = 11;
    OrchestrateResult orchestrate_result = 12;
    BrainAnalysisPayload brain_analysis = 15;
    RecallResult recall_result = 16;                  // [deliver-v1.1]
  }
  EnergyReport energy = 4;
  int64 latency_ms = 5;
  string error_message = 6;
  string error_code = 7;
  MemoryInfluence memory_influence = 8; // [deliver-v1.1] How memory affects this decision
}

message EipEvent {
  string event_id = 1;
  EipEventType type = 2;
  string source = 3;
  oneof data {
    LoaUpdatePayload loa_update = 10;
    DirectivePayload directive = 11;
    ArtifactAlertPayload artifact_alert = 12;
    TrlUpdatePayload trl_update = 13;
    HandoffReadyPayload handoff_ready = 14;
    AwaitingCommandPayload awaiting_command = 15;
  }
  RoutingScope scope = 5;
}

// ========== Enum ==========

enum EipVerb {
  EIP_VERB_UNKNOWN = 0;
  PREDICT = 1;
  EVALUATE = 2;
  ORCHESTRATE = 3;
  REPORT_STATUS = 4;
  SUBMIT_ARTIFACT = 5;
  HUMAN_INTERVENTION = 10;
  RECALL = 11; // [deliver-v1.1] Long-term memory retrieval
}

enum EipStatus {
  EIP_STATUS_UNKNOWN = 0;
  OK = 1;  ERROR = 2;  PARTIAL = 3;  AWAITING_HUMAN = 4;
  INVALID_PAYLOAD = 5;  PERMISSION_DENIED = 6;  QUOTA_EXCEEDED = 7;  TIMEOUT = 8;
}

enum EipEventType {
  EIP_EVENT_TYPE_UNKNOWN = 0;
  LOA_CHANGED = 1;  TRL_UPDATED = 2;  HANDOFF_READY = 3;
  ARTIFACT_VERSION_MISMATCH = 4;  SLO_ALERT = 5;  EVOLUTION_COMPLETED = 6;
  PRIVACY_BUDGET_EXHAUSTED = 7;  AWAITING_COMMAND = 8;
}

enum RoutingScope { ROUTING_SCOPE_UNKNOWN = 0; UNICAST = 1; BROADCAST = 2; RING_BROADCAST = 3; }
enum AgentState { AGENT_STATE_UNKNOWN = 0; IDLE = 1; EXECUTING = 2; AWAITING_HUMAN = 3; ERROR = 4; DEGRADED = 5; }
enum OrchestrateAction { ORCHESTRATE_ACTION_UNKNOWN = 0; SCHEDULE = 1; HANDOFF_CHECK = 2; RESOLVE_CONFLICT = 3; STATUS_REPORT = 4; }
enum DirectiveType { DIRECTIVE_TYPE_UNKNOWN = 0; START = 1; PAUSE = 2; HANDOFF = 3; DEGRADE = 4; RESUME = 5; }
enum InterventionType { INTERVENTION_TYPE_UNKNOWN = 0; SUGGESTION = 1; REQUIREMENT = 2; OVERRIDE = 3; ABORT = 4; }

// ========== Agent → Brain request payload ==========

message PredictRequest {
  repeated ZLayerSnapshot current_state = 1;
  int32 prediction_steps = 2;
  repeated string target_layers = 3;
}

message EvaluateRequest {
  repeated CandidateEmbedding candidates = 1;
  string evaluation_context = 2;
  bool return_ranking = 3;
}

message OrchestrateRequest {
  OrchestrateAction action = 1;
  string project_id = 2;
  repeated string involved_agents = 3;
  string context = 4;
}

message ReportStatusPayload {
  AgentState state = 1;
  float current_loa = 2;
  TaskProgress task_progress = 3;
  map<string, float> metrics = 4;
}

message SubmitArtifactPayload {
  string artifact_type = 1;
  string artifact_version = 2;
  bytes artifact_content = 3;
  string schema_ref = 4;
  repeated string upstream_artifact_refs = 5;
}

message HumanInterventionPayload {
  InterventionType type = 1;
  string role = 2;
  string target_agent_id = 3;
  string content = 4;
  string justification = 5;
}

// ========== Brain → Agent response payload ==========

message PredictResult {
  repeated ZLayerPrediction predictions = 1;
  float confidence = 2;
  repeated CausalPathway causal_explanations = 3;
}

message EvaluateResult {
  repeated CandidateScore scores = 1;
  int32 recommended_index = 2;
  string reasoning = 3;
}

message OrchestrateResult {
  repeated TaskScheduleEntry schedule = 1;
  HandoffStatus handoff_status = 2;
  string conflict_resolution = 3;
}

message BrainAnalysisPayload {
  string original_intervention_id = 1;
  EvaluateResult analysis = 2;
  repeated string recommended_actions = 3;
  float alignment_score = 4;
}

message DirectivePayload {
  DirectiveType type = 1;
  string target_agent_id = 2;
  map<string, string> parameters = 3;
  string reason = 4;
}

message LoaUpdatePayload {
  string agent_id = 1;
  float old_loa = 2;
  float new_loa = 3;
  string trigger_reason = 4;
  repeated CascadeImpact downstream_impacts = 5;
}

message ArtifactAlertPayload {
  string artifact_type = 1;
  string expected_version = 2;
  string actual_version = 3;
  string upstream_agent_id = 4;
  string downstream_agent_id = 5;
}

message AwaitingCommandPayload {
  string agent_id = 1;
  string original_intervention_id = 2;
  BrainAnalysisPayload brain_analysis = 3;
  repeated string suggested_commands = 4;
  int64 timeout_ms = 5;
  string awaiting_role = 6;
}

// ========== Sub-message ==========

message ZLayerSnapshot { string layer_name = 1; bytes embedding = 2; int32 trl = 3; int64 timestamp_ms = 4; }
message ZLayerPrediction { string layer_name = 1; bytes predicted_embedding = 2; float prediction_mse = 3; }
message CandidateEmbedding { string candidate_id = 1; bytes embedding = 2; string description = 3; }
message CandidateScore { string candidate_id = 1; float total_energy = 2; map<string, float> layer_energies = 3; string risk_level = 4; }
message CausalPathway { repeated string path_nodes = 1; float strength = 2; }
message CascadeImpact { string affected_agent_id = 1; string impact_description = 2; string recommended_action = 3; }
message TaskProgress { string task_id = 1; float completion_pct = 2; string current_step = 3; int64 estimated_remaining_ms = 4; }
message EnergyReport { map<string, float> layer_energies = 1; float total_energy = 2; float cross_layer_energy = 3; float safety_energy = 4; bool approval_required = 5; string risk_level = 6; }
message TaskScheduleEntry { string agent_id = 1; string task_id = 2; int32 priority = 3; int64 estimated_start_ms = 4; }
message HandoffStatus { string gate_name = 1; bool ready = 2; string block_reason = 3; float energy_score = 4; }
message TrlUpdatePayload { string layer_name = 1; int32 old_trl = 2; int32 new_trl = 3; string reason = 4; }
message HandoffReadyPayload { string source_ring = 1; string target_ring = 2; string project_id = 3; repeated string ready_artifacts = 4; }

// ========== Long Memory Messages [deliver-v1.1] ==========

message RecallRequest {
  repeated ZLayerSnapshot context = 1; // Current Z-Layer context (vector similarity retrieval)
  string text_query = 2; // Natural language query (optional)
  repeated string changed_layers = 3; // changed layer names (cause and effect graph traversal)
  int32 max_episodes = 4; // Returns the upper limit of the number of Episodes (default 10)
  int32 max_facts = 5; // Return the upper limit of the number of Facts (default 5)
}

message RecallResult {
  repeated EpisodeSummary similar_episodes = 1;
  repeated FactSummary relevant_facts = 2;
  ProjectProfileSummary project_profile = 3;
  float retrieval_latency_ms = 4;
}

message MemoryInfluence {
  repeated string recalled_episode_ids = 1; // IDs of past events that affected this decision
  repeated string applied_fact_ids = 2; //Applied semantic knowledge Fact ID
  float memory_confidence_boost = 3; // The impact of memory on confidence
}

message EpisodeSummary {
  string episode_id = 1;
  string trigger_type = 2;
  string decision_summary = 3;
  string outcome = 4;
  float similarity_score = 5;
  int64 timestamp_ms = 6;
}

message FactSummary {
  string fact_id = 1;
  string subject = 2;
  string relation = 3;
  string object = 4;
  float confidence = 5;
  string fact_type = 6;
}

message ProjectProfileSummary {
  repeated string static_facts = 1;
  repeated string dynamic_context = 2;
  repeated string risk_memories = 3;
}

message StreamSubscription { repeated EipEventType event_types = 1; string project_id = 2; string agent_id = 3; RoutingScope min_scope = 4; }
message AgentStreamSubscription { string agent_id = 1; string ring = 2; }
```---

## 4.5 Message JSON sample directory

### 4.5.1 PREDICT request```json
{
  "request_id": "req-550e8400-e29b-41d4-a716-446655440000",
  "agent_id": "AG-CD-instance-01",
  "project_id": "proj-alpha-001",
  "verb": "PREDICT",
  "predict": {
    "current_state": [
      {"layer_name": "Z_impl", "embedding": "<base64>", "trl": 3, "timestamp_ms": 1711100000000},
      {"layer_name": "Z_quality", "embedding": "<base64>", "trl": 3, "timestamp_ms": 1711100000000}
    ],
    "prediction_steps": 3,
    "target_layers": ["Z_quality", "Z_phys"]
  },
  "timestamp_ms": 1711100001000,
  "eip_version": "1.0.0"
}
```### 4.5.2 PREDICT response```json
{
  "request_id": "req-550e8400-e29b-41d4-a716-446655440000",
  "status": "OK",
  "predict_result": {
    "predictions": [
      {"layer_name": "Z_quality", "predicted_embedding": "<base64>", "prediction_mse": 0.08},
      {"layer_name": "Z_phys", "predicted_embedding": "<base64>", "prediction_mse": 0.12}
    ],
    "confidence": 0.85,
    "causal_explanations": [{"path_nodes": ["Z_impl", "Z_quality", "Z_phys"], "strength": 0.72}]
  },
  "energy": {"layer_energies": {"Z_impl": 0.15, "Z_quality": 0.22, "Z_phys": 0.18}, "total_energy": 0.55, "cross_layer_energy": 0.10, "safety_energy": 0.05, "approval_required": false, "risk_level": "LOW"},
  "latency_ms": 145
}
```### 4.5.3 EVALUATE request```json
{
  "request_id": "req-660f9500-f30c-52e5-b827-557766550001",
  "agent_id": "AG-SA-instance-01", "project_id": "proj-alpha-001", "verb": "EVALUATE",
  "evaluate": {
    "candidates": [
      {"candidate_id": "arch-microservice", "embedding": "<base64>", "description": "Microservice with API gateway"},
      {"candidate_id": "arch-monolith", "embedding": "<base64>", "description": "Modular monolith"}
    ],
    "evaluation_context": "architecture_decision", "return_ranking": true
  },
  "timestamp_ms": 1711100002000, "eip_version": "1.0.0"
}
```### 4.5.4 EVALUATE response```json
{
  "request_id": "req-660f9500-f30c-52e5-b827-557766550001", "status": "OK",
  "evaluate_result": {
    "scores": [
      {"candidate_id": "arch-microservice", "total_energy": 0.35, "layer_energies": {"Z_arch": 0.15, "Z_impl": 0.10, "Z_phys": 0.10}, "risk_level": "MEDIUM"},
      {"candidate_id": "arch-monolith", "total_energy": 0.22, "layer_energies": {"Z_arch": 0.08, "Z_impl": 0.07, "Z_phys": 0.07}, "risk_level": "LOW"}
    ],
    "recommended_index": 1,
    "reasoning": "Monolith lower energy (0.22 vs 0.35) given team size and TRL-3 maturity"
  },
  "latency_ms": 89
}
```### 4.5.5 ORCHESTRATE request / 4.5.6 REPORT_STATUS / 4.5.7 SUBMIT_ARTIFACT / 4.5.8 HUMAN_INTERVENTION

(Complete JSON example: at least 1 of each message type, covering SCHEDULE, status reporting, product submission, manual intervention, the format is the same as above.)

### 4.5.9 PERMISSION_DENIED response```json
{
  "request_id": "req-cc0f5b00-f96c-b8eb-1e83-bb3322bb0007",
  "status": "PERMISSION_DENIED",
  "error_message": "Cross-tenant data access is prohibited.",
  "error_code": "CROSS_TENANT_ACCESS_PROHIBITED",
  "latency_ms": 3
}
```### 4.5.10 LOA_CHANGED event```json
{
  "event_id": "evt-dd1a6c00-a07d-c9fc-2f94-cc4433cc0008",
  "type": "LOA_CHANGED", "source": "brain_core",
  "loa_update": {
    "agent_id": "AG-SA-instance-01", "old_loa": 7.0, "new_loa": 4.0,
    "trigger_reason": "Z_arch TRL regression from 3 to 2",
    "downstream_impacts": [{"affected_agent_id": "AG-FD-instance-01", "impact_description": "Upstream architecture output outdated", "recommended_action": "Pause until human architecture input"}]
  },
  "scope": "RING_BROADCAST"
}
```### 4.5.11 AWAITING_COMMAND event```json
{
  "event_id": "evt-awaiting-001", "type": "AWAITING_COMMAND", "source": "AG-SA-instance-01",
  "awaiting_command": {
    "agent_id": "AG-SA-instance-01", "original_intervention_id": "req-bb0e4a00",
    "brain_analysis": {"analysis": {"scores": [{"candidate_id": "grpc-approach", "total_energy": 0.28}], "recommended_index": 0}, "recommended_actions": ["Update API contracts", "Generate stubs"], "alignment_score": 0.88},
    "suggested_commands": ["approve_and_proceed", "modify_approach", "abort"],
    "timeout_ms": 14400000, "awaiting_role": "ARCHITECT"
  },
  "scope": "UNICAST"
}
```---

## 5. Error handling specifications

### 5.1 Timeout strategy

| Interface type | Default timeout | Maximum timeout | Timeout action |
|---------|---------|---------|---------|
| PREDICT | 5s | 30s | Return the most recent cached prediction + PARTIAL |
| EVALUATE | 5s | 30s | Demoted to Top-1 Greedy |
| ORCHESTRATE | 2s | 10s | Return the last scheduling result |
| REPORT_STATUS | 1s | 5s | Discarded (Kafka at-least-once retry) |
| HUMAN_INTERVENTION | 30s | 300s | Waiting in line |

### 5.2 Retry strategy

Exponential backoff: 1s → 2s → 4s, up to 3 times. Idempotence: All requests passed request_id are idempotent. Dead letter queue: After 3 failed retries, it enters `uewm.dlq.{topic}.v1` and can be replayed manually.

### 5.3 Circuit breaker strategy

5 consecutive timeouts → fuse for 30s → half-open test → recovery if successful.

### 5.4 Structured error code system

| Error code | EipStatus | Description |
|--------|-----------|------|
| CROSS_TENANT_ACCESS_PROHIBITED | PERMISSION_DENIED | Cross-tenant access |
| ROLE_INSUFFICIENT_PERMISSION | PERMISSION_DENIED | Insufficient role permissions |
| LOA_OPERATION_MISMATCH | PERMISSION_DENIED | Agent LOA does not match operation |
| TENANT_QUOTA_EXCEEDED | QUOTA_EXCEEDED | Per-Tenant quota exceeded |
| AGENT_QUOTA_EXCEEDED | QUOTA_EXCEEDED | Agent concurrent quota exceeded |
| PAYLOAD_TYPE_MISMATCH | INVALID_PAYLOAD | Payload type does not match EipVerb |
| PAYLOAD_SCHEMA_VIOLATION | INVALID_PAYLOAD | Payload field verification failed |
| BRAIN_TIMEOUT | TIMEOUT | Brain Core processing timeout |
| GATEWAY_TIMEOUT | TIMEOUT | EIP Gateway layer timeout |

---

## 6. Protocol version management

Version number: Semantic version number (major.minor.patch). Backward compatibility: New fields are only appended, not deleted/renumbered. Grayscale upgrade: When old and new versions of Agent coexist, Gateway routes according to eip_version. Version negotiation: Agent declares the supported version range when connecting, and Gateway selects a compatible version.

---

## 7. Security layer

Transmission encryption: mTLS (Agent↔Gateway↔Brain). Identity authentication: Agent certificate + JWT token. Permission verification: RBAC three-dimensional matrix (executed at the EIP Gateway layer, including DynamicPermissionEnforcer). Audit: Audit logs are recorded for each EIP message (not including full payload, only summary).

---

## 8. Acceptance criteria mapping

| AC | Verification method |
|----|---------|
| R11 AC-1: IDL complete + Schema compatible | protoc compilation + buf lint/breaking |
| R11 AC-2: 12 Agent integration test passed | Each Agent ≥1 EipVerb closed loop |
| R11 AC-3: gRPC P99 < Brain SLO | Load Test (Profile-M: 50 concurrency) |
| R11 AC-4: Kafka P99 < 2s | Event latency monitoring |
| R11 AC-5: Grayscale upgrade demonstration | Coexistence test of new and old versions of Agent |
| R11 AC-6: Dead Letter Queue Replay | Injection failed→Replay→Success |
| R11 AC-7: No Any type | IDL static analysis: `grep Any` = 0 |
| R11 AC-8: Wrong payload rejection | Send mismatch payload → INVALID_PAYLOAD |
| R11 AC-9: Complete JSON examples | §4.5 Covering all message types (11 examples) |
| R11 AC-10: PERMISSION_DENIED Verifiable | Cross-Tenant Access → PERMISSION_DENIED |