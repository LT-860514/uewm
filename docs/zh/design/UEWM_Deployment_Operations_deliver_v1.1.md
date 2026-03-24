# 🚀 UEWM 部署运维设计文档

**文档版本：** deliver-v1.1  
**文档编号：** UEWM-DEPLOY-009  
**最后更新：** 2026-03-24  
**状态：** 设计完成（100% 覆盖 R05, NFR-1/2/6/9 + Long Memory 运维）  
**合并来源：** Deployment V1.0 + V2.0(GPU/SLO测试) + V3.0(影子模式/告警) + V4.0(Tier3/升级/Phase过渡) — 全量合并  
**对标需求：** R05 (全部), NFR-1/2/3/6/9/11

---

## 1. 概述

定义 UEWM 的容器化部署架构、CI/CD 流水线、全链路可观测性、高可用设计、分级 SLO 体系、错误预算与自动降级、GPU 资源隔离和运维操作手册。

---

## 2. 技术选型

Kubernetes (容器编排), Helm (部署模板), Prometheus+Grafana+OTel (可观测), Patroni/PostgreSQL (数据), Redis Cluster (缓存), Kafka (消息), Harbor (镜像仓库), ArgoCD (GitOps)。

---

## 3. 部署架构

### 3.1 Kubernetes 命名空间

uewm-system (Brain Core + EIP Gateway), uewm-agents (12 Agent Deployments), uewm-data (PostgreSQL + Redis + Kafka + Milvus + Neo4j), uewm-monitoring (Prometheus + Grafana + OTel), uewm-vault (HashiCorp Vault)。

**[deliver-v1.1]** Neo4j 新增: 用于长期记忆语义记忆知识图谱 (Architecture §12.4)。Profile-S 单实例, Profile-M 3 节点因果一致集群, Profile-L 按分片独立部署。

### 3.2 资源基线

| 组件 | Profile-S | Profile-M | Profile-L |
|------|-----------|-----------|-----------|
| GPU | 2× A100 | 4× A100 | 8× A100 |
| CPU | 32 核 | 96 核 | 256 核 |
| RAM | 128 GB | 384 GB | 1 TB |
| Storage | 100 GB SSD | 1 TB SSD | 10 TB SSD |

### 3.3 GPU 资源隔离

```
GPU 资源分配策略:
  推理 GPU 池: 永远优先于训练
  训练 GPU 池: LoRA 进化仅使用剩余算力或独立训练 GPU
  
  Profile-M 示例 (4× A100):
    GPU 0-1: 推理专用 (Brain Core 决策)
    GPU 2: 推理溢出 + 训练共享 (推理优先抢占)
    GPU 3: 训练专用 (LoRA 进化)
    
  约束: 进化训练不可使推理 P99 超过 600ms
         600ms = Tier-1 SLO 基线 500ms (Profile-M) + 100ms 进化训练降级容差 [NFR-9]
         超过 600ms → 视为进化影响推理, 须立即暂停进化
         暂停延迟 SLO: < 30s (对标 R05 AC-7)
```

---

## 4. 分级 SLO 体系

### 4.1 Tier 1 SLO (核心路径 — Brain 推理)

| Profile | P50 | P99 | P99.9 | 测量点 |
|---------|-----|-----|-------|--------|
| Profile-S | < 100ms | < 300ms | < 1s | EIP Gateway→Brain 返回 |
| Profile-M | < 200ms | < 500ms | < 2s | 同上 |
| Profile-L | < 300ms | < 1000ms | < 3s | 同上 |

### 4.2 Tier 2 SLO (Agent 端到端)

简单任务(代码格式化/单元测试): P99 < 30s。中等任务(代码审查/功能拆解): P99 < 5min。复杂任务(架构评估/全量测试): P99 < 30min。需人工审批的任务: SLA < 4h。

### 4.3 Tier 3 SLO 监控规则

```yaml
- alert: Tier3_SelfReflection_Slow
  expr: uewm_reflection_duration_seconds > 300  # > 5min
  labels: {severity: warning, tier: "3"}

- alert: Tier3_KnowledgeAggregation_Slow
  expr: uewm_knowledge_aggregation_duration_seconds > 3600  # > 1h
  labels: {severity: warning, tier: "3"}

- alert: Tier3_Evolution_Slow
  expr: uewm_evolution_iteration_duration_seconds > 900  # > 15min (Profile-S)
  labels: {severity: warning, tier: "3"}

- alert: Tier3_ModelRollback_Slow
  expr: uewm_model_rollback_duration_seconds > 120  # > 2min
  labels: {severity: critical, tier: "3"}
```

### 4.4 可用性 SLO

Brain Core 99.95% (≤ 22 min/月), EIP Gateway 99.99% (≤ 4 min), Agent 各 99.9% (≤ 44 min), 端到端 99.5%, 数据层 99.99%。

---

## 5. 错误预算与 SLO 违约响应

### 5.1 错误预算仪表盘

显示: 各组件月剩余预算(百分比+分钟数), 24h/7d/30d burn-rate趋势, 当前告警级别(L0-L4), 自动触发的保护性动作列表, 预测耗尽日期。

### 5.2 Burn-Rate 四级告警

| 级别 | 触发条件 | 自动响应 | 响应SLA |
|------|---------|---------|---------|
| L1 观察 | 1h burn-rate > 2x | 无 (Grafana→Slack) | 1h |
| L2 警告 | 6h burn-rate > 5x | 暂停进化+降低外环优先级+HPA扩容 | 30min |
| L3 危急 | 月预算<20% 或 1h>14x | L2全部+冻结新项目+外环暂停+LOA降1-2级 | 15min |
| L4 耗尽 | 月预算=0% | 变更冻结(禁止进化/部署,仅故障修复需双人审批) | 即时 |

### 5.3 影子模式实现

Phase 0 期间错误预算以影子模式运行: 记录"应触发的动作"但不实际执行冻结或降级。生成标定报告(30天触发统计, L4触发率需<1%)。Phase 1 激活门禁: ≥30天影子数据, ≥100事件, 标定报告经 DEVOPS+SECURITY 审批。

### 5.4 告警通道配置

| 级别 | 通知渠道 | 接收角色 |
|------|---------|---------|
| L1 | Slack #uewm-alerts | DEVOPS |
| L2 | PagerDuty (P2) + Slack | DEVOPS + SECURITY |
| L3 | PagerDuty (P1) + Slack + Email + Portal 横幅 | 全通道 |
| L4 | PagerDuty (P1) + Slack + Email + Portal + SMS | SYSTEM_ADMIN |

Portal 横幅: L3 橙色警告(外环暂停,项目冻结), L4 红色危急(变更冻结,仅故障修复)。

---

## 6. LLM 成本管理

月度预算: Profile-S ≤$500, Profile-M ≤$5,000, Profile-L ≤$25,000。Per-Task 天花板: 简单≤$0.01, 中等≤$0.10, 复杂≤$1.00。80%预算告警, 100%降级为小模型/规则引擎。每 Agent LLM 成本实时可查。每日报告(Agent×项目×Tenant三维)。成本异常: 单Agent单日>3x历史均值→告警。

---

## 7. CI/CD 流水线

CI: Lint+Tests → Protobuf编译+Schema兼容 → 集成测试(EIP闭环) → 安全扫描(Trivy+Semgrep) → 容器构建(multi-arch) → 推送Harbor。CD: Staging部署 → 1h soak test → 金丝雀10%/30min → 全量发布 → Post-deploy健康检查5min。

---

## 8. 高可用与灾备

### 8.1 自愈机制

Brain Core: Active-Standby, <30s 切换。EIP Gateway: 3 replicas Active-Active。Agent: HPA + readiness probe。数据层: Patroni(PG)/Sentinel(Redis)/ISR(Kafka)。

### 8.2 模型版本回滚

MLflow 版本管理。回滚 SLO < 2min。回滚范围: 单层LoRA / 全模型 / Z-Buffer快照。

---

## 9. Brain Core 决策审计

每次决策记录: 输入Z-Layer信号 + EBM能量分 + 编排建议 + 最终决策 + 延迟。支持按时间/Agent/项目/能量值多维查询。写入Kafka audit topic → Elasticsearch/ClickHouse。

---

## 10. 可扩展性

S→M→L 仅需加资源不改架构: Brain GPU数/Agent HPA max/数据层replica数/SLO阈值通过 Helm values 切换。租户分片见 Architecture §3.6。

---

## 11. 监控告警规则矩阵

Brain P99, Gateway 错误率, Agent 任务完成率, GPU 利用率, Kafka lag, PG replication lag, Redis 内存, Disk 使用率。每项含 warning/critical 阈值和通知渠道。

### 11.2 长期记忆监控规则 [deliver-v1.1 新增]

```yaml
- alert: Memory_Consolidation_Slow
  expr: uewm_memory_consolidation_duration_seconds > 1800  # > 30min
  labels: {severity: warning}
  annotations: {summary: "Memory consolidation took {{ $value }}s (SLO: < 1800s)"}

- alert: Memory_Retrieval_Slow
  expr: histogram_quantile(0.99, uewm_memory_recall_duration_seconds_bucket) > 0.2  # P99 > 200ms
  labels: {severity: warning}
  annotations: {summary: "Memory RECALL P99 {{ $value }}s (SLO: < 200ms)"}

- alert: Memory_Episode_Storage_High
  expr: uewm_episode_count_total > 8000  # 接近 10K 上限
  labels: {severity: warning}
  annotations: {summary: "Episode count {{ $value }} approaching 10K limit"}

- alert: Memory_Fact_Contradiction_Spike
  expr: rate(uewm_fact_contradictions_total[1h]) > 5
  labels: {severity: warning}
  annotations: {summary: "{{ $value }} fact contradictions/hour — possible model drift"}
```

### 11.3 长期记忆存储容量 [deliver-v1.1 新增]

| Profile | Episodes/天 | 热存储(30天) | 温存储(180天) | Fact 数/项目 | 总增量 |
|---------|------------|-------------|-------------|-------------|--------|
| Profile-S | ~100 | ~150 MB | ~900 MB | ~200 | +~1 GB |
| Profile-M | ~500 | ~750 MB | ~4.5 GB | ~500 | +~5 GB |
| Profile-L | ~2,000 | ~3 GB | ~18 GB | ~1,000 | +~21 GB |

存储: Episode 热层使用 PostgreSQL + pgvector (与现有 PG 实例共享), 温/冷层使用 S3。Semantic Memory 使用 Neo4j (新增组件)。Profile 缓存使用现有 Redis。

---

## 12. SLO 验证负载测试计划

### 12.1 测试方法论

测试工具: k6 (HTTP/gRPC) + custom EIP client (Protobuf)。独立性能测试集群。硬件与各 Profile 基线一致。预加载 MVLS Z-Buffer, 预热缓存。Prometheus+Grafana 实时监控, OTel trace。

### 12.2 Profile-S 负载测试

| 测试项 | 负载参数 | SLO 目标 | 持续时间 |
|--------|---------|---------|---------|
| Brain P99 | 5并发EIP | P50<100ms, P99<300ms | 30min |
| 峰值 | 10并发(2x) | P99<500ms | 5min |
| Agent端到端 | 1简单+1中等并行 | <30s / <5min | 3轮 |
| 可用性 | 24h无人值守 | Brain 99.95%, GW 99.99% | 24h |
| 故障恢复 | Kill Brain pod | <30s自愈 | 单次 |

### 12.3 Profile-M 负载测试

| 测试项 | 负载参数 | SLO 目标 | 持续时间 |
|--------|---------|---------|---------|
| Brain P99 | 50并发 | P50<200ms, P99<500ms | 60min |
| 峰值 | 100并发(2x) | P99<800ms | 10min |
| 多Agent并行 | 10项目×5Agent | 公平分配,无饥饿 | 30min |
| GPU争用 | 推理满载+进化 | 推理P99<600ms(NFR-9) | 30min |
| 进化暂停 | L2注入 | 暂停<30s | 单次 |
| L3降级 | L3注入 | 全部动作<60s | 单次 |
| 模型回滚 | 触发回滚 | <2min | 单次 |
| 可用性 | 48h无人值守 | Brain 99.95% | 48h |
| LLM成本 | 30天模拟 | ≤$5,000 | 模拟30天 |

### 12.4 Profile-L 负载测试

200并发, P99<1000ms, 多租户隔离(20 Tenant), 扩展性(S→L仅加资源), 72h可用性。

### 12.5 混沌测试矩阵

| 故障注入 | 期望行为 | Profile |
|---------|---------|---------|
| Kill Brain pod | <30s自愈(Active-Standby) | S,M,L |
| Kill EIP Gateway pod | 负载均衡剔除,无感知 | M,L |
| Kill Agent pod | HPA重启,任务不丢失 | M,L |
| Redis主节点故障 | <10s Sentinel切换 | M,L |
| PostgreSQL Primary故障 | Patroni切换<15s | M,L |
| Kafka Broker故障(1/3) | ISR,无消息丢失 | M,L |
| 网络分区(Brain↔Agent) | Agent规则引擎模式 | M |
| GPU驱动异常 | 延迟升高→L2告警→进化暂停 | M |
| 磁盘满(audit log) | Hot→Warm加速降温+告警 | M |

### 12.6 测试时间线

Phase 0 M3: Profile-S全量+Profile-M Tier-1(1周)。Phase 0 M4: Profile-M全量+混沌(2周)。Phase 1 M7: 多Agent多项目(1周)。Phase 2 M10: Profile-L全量+多租户(2周)。Phase 3+: 季度回归(1周)。

### 12.7 测试通过标准

AC-1→P99<500ms@50并发60min, AC-2→混沌恢复<30s, AC-4→S/M/L各通过, AC-5→S→L仅加资源, AC-7→L2暂停<30s, AC-8→L3动作<60s, AC-9→30天LLM≤$5K。

---

## 13. Profile 升级运行手册

```
前置: 硬件就位 + Helm values审核 + Level-0 + 备份(Z-Buffer+LoRA+配置)

步骤 (零停机):
  1. 数据层扩容: PG Replica(Patroni) → Redis Cluster扩节点 → Kafka Broker+重平衡
  2. Brain Core扩容: Helm upgrade → 新Pod readiness后旧Pod终止 → P99验证
  3. Agent扩容: 更新HPA max_replicas → CPU自动扩容
  4. 配置切换: SLO阈值 + 错误预算重置 + LLM预算更新 + 编排配额更新
  5. 验证: 1h soak test → 全部SLO达标
  
回滚: Helm rollback < 10min
```

---

## 14. Phase 过渡运行手册

```
Phase 0→1 门禁:
  □ MVLS 三层 TRL≥3  □ 内环5 Agent LOA≥7  □ EIP 12 Agent集成测试通过
  □ 错误预算影子标定报告审批  □ 渗透测试T1/T4/T5通过  □ Profile-M负载测试通过
  Feature Flags: FF_MIDDLE_RING_AGENTS→true, FF_ERROR_BUDGET_ENFORCE→true

Phase 1→2 门禁:
  □ Z_arch/Z_logic TRL≥3  □ 中环3 Agent LOA≥5  □ 跨环交接可演示
  □ 首个外部客户试点  □ 渗透测试T2/T3通过  □ LLM成本合规
  Feature Flags: FF_OUTER_RING_AGENTS→true, FF_FEDERATED_LEARNING→true

Phase 2→3 门禁:
  □ 全12 Agent可运行  □ 多租户验证  □ 冷启动缩短≥50%  □ SOC2 TypeII通过
  □ 自进化闭环30天稳定  □ 全Z-Layer TRL≥4
```

---

## 15. 验收标准映射

| AC | 设计支撑 | 验证方法 |
|----|---------|---------|
| R05 AC-1 | §4.1 + §12.3 | k6 50并发 60min |
| R05 AC-2 | §8.1 + §12.5 | 混沌测试: Kill pod |
| R05 AC-3 | §7 | CI/CD 端到端演示 |
| R05 AC-4 | §12.2-12.4 | 三Profile独立测试 |
| R05 AC-5 | §10 + §13 | 配置差异审查+升级手册 |
| R05 AC-6 | §5.1 | 仪表盘: 预算+burn-rate+级别 |
| R05 AC-7 | §5.2 + §3.3 | L2注入→暂停延迟<30s |
| R05 AC-8 | §5.2 + §12.3 | L3注入→动作<60s |
| R05 AC-9 | §6 + INTEG §3 | 30天成本≤$5K |
| NFR-9 | §3.3 | GPU争用P99<600ms |
