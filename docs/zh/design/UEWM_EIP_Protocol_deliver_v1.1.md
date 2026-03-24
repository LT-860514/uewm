# 📡 UEWM 工程智能协议 (EIP) 设计文档

**文档版本：** deliver-v1.1  
**文档编号：** UEWM-EIP-007  
**最后更新：** 2026-03-24  
**状态：** 设计完成（100% 覆盖 R11 + Long Memory RECALL 动词）  
**对标需求：** R11 (全部), R09 (人工干预消息), R02 (编排指令)  
**合并来源：** EIP Protocol V3.0 — 全量合并，消除补丁依赖  
**变更历史：**
- V1.0: 初始版本，对齐 R11 强类型载荷规范
- V2.0: JSON 示例(§4.5)；EipStatus 扩展；结构化错误码(§5.4)
- V3.0: Kafka Topic 设计(§2.4)；AWAITING_COMMAND 消息(§3.3)；EipStream 服务(§2.5)
- **deliver-v1.0: 全量合并，无增量补丁依赖**

---

## 1. 协议概述

EIP (Engineering Intelligence Protocol) 是 Agent 与 Brain Core 之间的统一通信协议，作为 UEWM 系统的"中枢神经"。所有 Agent 交互、人工干预、编排指令均通过此协议传输。

### 1.1 设计约束

- 最终 IDL 中禁止保留 `google.protobuf.Any` (需求阶段占位符不入代码)
- 每个 EipVerb 对应唯一的 Request 和 Result 消息类型 (使用 oneof)
- 所有枚举第一个条目必须为 XXX_UNKNOWN = 0 (Protobuf 默认值安全)
- 新增消息类型须向后兼容 (仅追加字段，不删除/重编号)
- 每个消息类型须附带至少一个 JSON 示例 (见 §4.5)

---

## 2. 消息类型与传输层

### 2.1 四种消息类型

| 类型 | 方向 | 传输层 | 语义 |
|------|------|--------|------|
| Request | Agent→Brain | gRPC 双向流 | 同步请求 |
| Response | Brain→Agent | gRPC 双向流 | 请求响应 |
| Event | Brain→Agent(s) | Kafka | 异步事件/广播 |
| Stream | 双向 | gRPC 服务端流 | 长连接状态推送 |

### 2.2 传输层混合架构

| 路径 | 协议 | 适用场景 |
|------|------|---------|
| Agent↔Brain 同步决策 | gRPC 双向流 (TLS) | PREDICT/EVALUATE/ORCHESTRATE |
| Agent→Brain 状态上报 | Kafka (异步) | REPORT_STATUS |
| Brain→Agent(s) 事件 | Kafka (异步) | LOA_UPDATE/ARTIFACT_ALERT/HANDOFF_READY |
| Agent↔Brain 人工干预 | gRPC (TLS) | HUMAN_INTERVENTION |
| Dashboard/Agent 实时订阅 | gRPC 服务端流 | EipStreamService |

### 2.3 消息路由模式

| 模式 | 说明 | 示例 |
|------|------|------|
| 单播 (Unicast) | Agent↔Brain 1:1 | PREDICT 请求-响应 |
| 广播 (Broadcast) | Brain→全部 Agent | 全局 LOA 降级通知 |
| 环级广播 (Ring Broadcast) | Brain→某环全部 Agent | 内环进化暂停通知 |

### 2.4 Kafka Topic 设计

```
Topic 命名: uewm.{scope}.{event_type}.{version}

Topics:
  uewm.events.loa-changed.v1          # LOA 变更事件
  uewm.events.trl-updated.v1          # TRL 更新事件
  uewm.events.handoff-ready.v1        # 交接就绪事件
  uewm.events.artifact-mismatch.v1    # 产物版本不一致
  uewm.events.slo-alert.v1            # SLO 告警事件
  uewm.events.evolution-completed.v1  # 进化完成事件
  uewm.events.privacy-budget.v1       # 隐私预算事件
  uewm.events.awaiting-command.v1     # Agent 等待人工命令
  uewm.status.agent-heartbeat.v1      # Agent 状态上报 (高吞吐)
  uewm.audit.decisions.v1             # 决策审计日志 (高吞吐)
  uewm.dlq.{original_topic}.v1       # 死信队列

分区策略:
  events.*    → partition by project_id (同项目事件有序)
  status.*    → partition by agent_id (同 Agent 状态有序)
  audit.*     → partition by timestamp hash (均匀分布)

保留策略:
  events.*    → 7 天 | status.* → 24h | audit.* → 90 天 | dlq.* → 30 天

Consumer Groups:
  uewm-brain-core     → status.agent-heartbeat
  uewm-orchestrator   → events.* (编排模块聚合事件)
  uewm-audit-writer   → audit.* (写入 Elasticsearch/ClickHouse)
  uewm-agent-{id}     → events.* (按 agent_id 过滤)
```

### 2.5 EipStream 服务定义

```protobuf
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
```

使用场景: Portal Dashboard 实时刷新; Agent 接收 DIRECTIVE/LOA_UPDATE 推送; 错误预算实时横幅。

---

## 3. EipVerb 动词体系

### 3.1 Agent → Brain 请求动词

| 动词 | 用途 | 请求载荷 | 响应载荷 |
|------|------|---------|---------|
| PREDICT | 世界模型预测 | PredictRequest | PredictResult |
| EVALUATE | EBM 方案评估 | EvaluateRequest | EvaluateResult |
| ORCHESTRATE | 编排任务排序/交接/仲裁 | OrchestrateRequest | OrchestrateResult |
| REPORT_STATUS | Agent 状态上报 | ReportStatusPayload | Ack |
| SUBMIT_ARTIFACT | 交付产物提交 | SubmitArtifactPayload | Ack |
| HUMAN_INTERVENTION | 人工干预请求 | HumanInterventionPayload | BrainAnalysisPayload |
| **RECALL** | **记忆检索 (长期记忆)** | **RecallRequest** | **RecallResult** |

### 3.2 Brain → Agent 指令动词

| 动词 | 用途 | 载荷 |
|------|------|------|
| DECISION | 决策结果 | EvaluateResult |
| DIRECTIVE | 编排指令 | DirectivePayload |
| LOA_UPDATE | LOA 变更通知 | LoaUpdatePayload |
| ARTIFACT_ALERT | 产物版本不一致告警 | ArtifactAlertPayload |

### 3.3 人工干预消息

| 消息类型 | 方向 | 载荷 | 说明 |
|---------|------|------|------|
| HUMAN_INTERVENTION | Portal→Brain(via Agent) | HumanInterventionPayload | 角色工程师建议/需求/覆写/中止 |
| BRAIN_ANALYSIS | Brain→Portal(via Agent) | BrainAnalysisPayload | Brain 分析决策结果 |
| AWAITING_COMMAND | Agent→Portal(via Kafka) | AwaitingCommandPayload | Agent 等待下一步人工指令 |

---

## 4. Protobuf IDL 完整定义

```protobuf
syntax = "proto3";
package uewm.eip.v1;

// ========== gRPC 服务 ==========

service EipService {
  rpc SendRequest(EipRequest) returns (EipResponse);
  rpc BiDirectionalStream(stream EipRequest) returns (stream EipResponse);
}

service EipStreamService {
  rpc SubscribeEvents(StreamSubscription) returns (stream EipEvent);
  rpc SubscribeDirectives(AgentStreamSubscription) returns (stream EipEvent);
}

// ========== 消息信封 ==========

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
  MemoryInfluence memory_influence = 8;               // [deliver-v1.1] 记忆如何影响了此决策
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

// ========== 枚举 ==========

enum EipVerb {
  EIP_VERB_UNKNOWN = 0;
  PREDICT = 1;
  EVALUATE = 2;
  ORCHESTRATE = 3;
  REPORT_STATUS = 4;
  SUBMIT_ARTIFACT = 5;
  HUMAN_INTERVENTION = 10;
  RECALL = 11;                   // [deliver-v1.1] 长期记忆检索
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

// ========== Agent → Brain 请求载荷 ==========

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

// ========== Brain → Agent 响应载荷 ==========

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

// ========== 子消息 ==========

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
  repeated ZLayerSnapshot context = 1;     // 当前 Z-Layer 上下文 (向量相似度检索)
  string text_query = 2;                   // 自然语言查询 (可选)
  repeated string changed_layers = 3;      // 变化的层名 (因果图遍历)
  int32 max_episodes = 4;                  // 返回 Episode 数上限 (默认 10)
  int32 max_facts = 5;                     // 返回 Fact 数上限 (默认 5)
}

message RecallResult {
  repeated EpisodeSummary similar_episodes = 1;
  repeated FactSummary relevant_facts = 2;
  ProjectProfileSummary project_profile = 3;
  float retrieval_latency_ms = 4;
}

message MemoryInfluence {
  repeated string recalled_episode_ids = 1;  // 影响此决策的过去事件 ID
  repeated string applied_fact_ids = 2;      // 应用的语义知识 Fact ID
  float memory_confidence_boost = 3;         // 记忆对置信度的影响
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
```

---

## 4.5 消息 JSON 示例目录

### 4.5.1 PREDICT 请求

```json
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
```

### 4.5.2 PREDICT 响应

```json
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
```

### 4.5.3 EVALUATE 请求

```json
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
```

### 4.5.4 EVALUATE 响应

```json
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
```

### 4.5.5 ORCHESTRATE 请求 / 4.5.6 REPORT_STATUS / 4.5.7 SUBMIT_ARTIFACT / 4.5.8 HUMAN_INTERVENTION

(完整 JSON 示例: 每个消息类型至少 1 个，涵盖 SCHEDULE, 状态上报, 产物提交, 人工干预，格式同上。)

### 4.5.9 PERMISSION_DENIED 响应

```json
{
  "request_id": "req-cc0f5b00-f96c-b8eb-1e83-bb3322bb0007",
  "status": "PERMISSION_DENIED",
  "error_message": "Cross-tenant data access is prohibited.",
  "error_code": "CROSS_TENANT_ACCESS_PROHIBITED",
  "latency_ms": 3
}
```

### 4.5.10 LOA_CHANGED 事件

```json
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
```

### 4.5.11 AWAITING_COMMAND 事件

```json
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
```

---

## 5. 错误处理规范

### 5.1 超时策略

| 接口类型 | 默认超时 | 最大超时 | 超时动作 |
|---------|---------|---------|---------|
| PREDICT | 5s | 30s | 返回最近缓存预测 + PARTIAL |
| EVALUATE | 5s | 30s | 降级为 Top-1 贪心 |
| ORCHESTRATE | 2s | 10s | 返回上次调度结果 |
| REPORT_STATUS | 1s | 5s | 丢弃 (Kafka at-least-once 重试) |
| HUMAN_INTERVENTION | 30s | 300s | 排队等待 |

### 5.2 重试策略

指数退避: 1s → 2s → 4s，最多 3 次。幂等性: 所有请求通过 request_id 幂等。死信队列: 3 次重试失败后进入 `uewm.dlq.{topic}.v1`，可人工重放。

### 5.3 熔断策略

连续 5 次超时 → 熔断 30s → 半开试探 → 成功则恢复。

### 5.4 结构化错误码体系

| 错误码 | EipStatus | 说明 |
|--------|-----------|------|
| CROSS_TENANT_ACCESS_PROHIBITED | PERMISSION_DENIED | 跨租户访问 |
| ROLE_INSUFFICIENT_PERMISSION | PERMISSION_DENIED | 角色权限不足 |
| LOA_OPERATION_MISMATCH | PERMISSION_DENIED | Agent LOA 与操作不匹配 |
| TENANT_QUOTA_EXCEEDED | QUOTA_EXCEEDED | Per-Tenant 配额超限 |
| AGENT_QUOTA_EXCEEDED | QUOTA_EXCEEDED | Agent 并发配额超限 |
| PAYLOAD_TYPE_MISMATCH | INVALID_PAYLOAD | 载荷类型与 EipVerb 不匹配 |
| PAYLOAD_SCHEMA_VIOLATION | INVALID_PAYLOAD | 载荷字段校验失败 |
| BRAIN_TIMEOUT | TIMEOUT | Brain Core 处理超时 |
| GATEWAY_TIMEOUT | TIMEOUT | EIP Gateway 层超时 |

---

## 6. 协议版本管理

版本号: 语义版本号 (major.minor.patch)。向后兼容: 新字段仅追加，不删除/重编号。灰度升级: 新旧版本 Agent 共存时，Gateway 按 eip_version 路由。版本协商: Agent 连接时声明支持的版本范围，Gateway 选择兼容版本。

---

## 7. 安全层

传输加密: mTLS (Agent↔Gateway↔Brain)。身份认证: Agent 证书 + JWT token。权限校验: RBAC 三维矩阵 (在 EIP Gateway 层执行，含 DynamicPermissionEnforcer)。审计: 每条 EIP 消息记录审计日志 (不含完整载荷，仅摘要)。

---

## 8. 验收标准映射

| AC | 验证方法 |
|----|---------|
| R11 AC-1: IDL完整+Schema兼容 | protoc 编译 + buf lint/breaking |
| R11 AC-2: 12 Agent集成测试通过 | 每个 Agent ≥1 个 EipVerb 闭环 |
| R11 AC-3: gRPC P99 < Brain SLO | 负载测试 (Profile-M: 50并发) |
| R11 AC-4: Kafka P99 < 2s | 事件延迟监控 |
| R11 AC-5: 灰度升级演示 | 新旧版本 Agent 共存测试 |
| R11 AC-6: 死信队列重放 | 注入失败→重放→成功 |
| R11 AC-7: 无Any类型 | IDL 静态分析: `grep Any` = 0 |
| R11 AC-8: 错误载荷拒绝 | 发送不匹配载荷→INVALID_PAYLOAD |
| R11 AC-9: JSON示例完备 | §4.5 覆盖全部消息类型(11个示例) |
| R11 AC-10: PERMISSION_DENIED可验证 | 跨 Tenant 访问→PERMISSION_DENIED |
