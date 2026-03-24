# 🤖 UEWM Agent 体系设计文档

**文档版本：** deliver-v1.1  
**文档编号：** UEWM-AGENT-002  
**最后更新：** 2026-03-24  
**状态：** 设计完成（100% 覆盖 R02, R09, R11, R13, NFR-8/10 + Long Memory RECALL）  
**合并来源：** Agents Design V6.0 — 全量合并，消除补丁依赖  
**变更历史：**
- V3.0: 三环分层、ALFA、降级、跨环交接、执行引擎、适配器、产物管理、PM角色
- V4.0: 中环/外环适配器详细设计
- V5.0: 中环/外环 Agent 完整设计、DEGRADED 状态机、per-Profile 伸缩、Portal API 错误 Schema、LLM Prompt 管理
- V6.0: AWAITING_HUMAN_INPUT 超时策略、产物保留策略、EIP Client SDK 配置表；100% 覆盖达成
- **deliver-v1.0: 全量合并，无增量补丁依赖**

---

## 1. Agent 体系总览

12 个专业化 Agent，三环分层交付，EIP 协议与 Brain Core 交互，ALFA 框架动态 LOA 控制。

| # | Agent | 代号 | 核心职责 | Z-Layer | 环 | Phase | 执行引擎 |
|---|-------|------|---------|---------|-----|-------|---------|
| 1 | 产品分析 | AG-PA | 市场分析、竞品调研 | Z_market,Z_val | 外 | 2 | LLM |
| 2 | 产品设计 | AG-PD | 需求定义、原型 | Z_val,Z_biz | 外 | 2 | 混合 |
| 3 | 系统架构 | AG-SA | 技术选型、拓扑 | Z_arch,Z_logic | 中 | 1 | 混合 |
| 4 | 功能拆解 | AG-FD | 详细设计、任务分解 | Z_logic,Z_arch | 中 | 1 | 混合 |
| 5 | 代码开发 | AG-CD | 代码生成、审查 | Z_impl | 内 | 0 | 混合 |
| 6 | 代码测试 | AG-CT | 单元/集成测试 | Z_impl,Z_quality | 内 | 0 | 混合 |
| 7 | 部署上线 | AG-DO | CI/CD 编排 | Z_phys,Z_impl | 内 | 0 | 规则 |
| 8 | 系统测试 | AG-ST | E2E/性能测试 | Z_quality,Z_phys | 内 | 0 | 混合 |
| 9 | 监控告警 | AG-MA | 实时监控 | Z_phys | 内 | 0 | 规则 |
| 10 | BI 分析 | AG-BI | 数据分析、KPI | Z_val,Z_market | 外 | 2 | 混合 |
| 11 | 推广运营 | AG-PR | 渠道推广 | Z_market | 外 | 2 | LLM |
| 12 | 安全审计 | AG-AU | 权限审计、合规 | 全层 | 中 | 1 | 规则 |

---

## 2. 三环分层架构

内环(Phase 0, LOA 7-9): AG-CD/CT/DO/ST/MA — 端到端闭环自动运行。中环(Phase 1, LOA 5-7): AG-SA/FD/AU — 生成建议供人选择。外环(Phase 2, LOA 3-5): AG-PA/PD/BI/PR — 人主导Agent辅助。

---

## 3. ALFA 自动化等级框架

LOA = f(min_TRL → base_LOA, 历史表现 ±2, 风险上限)。TRL_TO_BASE_LOA: {0:1, 1:2, 2:4, 3:6, 4:8, 5:9}。RISK_CAP: {LOW:10, MEDIUM:8, HIGH:6, CRITICAL:4}。LOA→行为: 1-2 INFORMATION_ONLY, 3-4 OPTIONS_FOR_HUMAN, 5-6 RECOMMEND_AND_WAIT, 7-8 AUTO_EXECUTE_NOTIFY, 9-10 FULLY_AUTONOMOUS。变更时通过 EIP LOA_UPDATE 事件通知。

---

## 4. Agent 降级框架

每 Agent 不可用时的降级矩阵(全 12 Agent 含降级行为+全局影响+恢复条件)。外部工具: 必选依赖故障→LOA≤4, 可选依赖故障→LOA 不变。Brain Core 不可用→全 Agent 规则引擎模式。

---

## 5. 跨环交接协议

3 个交接门: 外→中(产品→架构, energy<0.3, 需人工), 中→内(架构→执行, energy<0.25, 需人工), 内→外(执行→商业反馈, 自动)。LOA 级联评估: 识别下游→评估影响→通知角色→更新里程碑→审计。

---

## 6. 执行引擎策略

Brain Core→WHAT, Agent 执行引擎→HOW-intelligent, 外部工具→HOW-mechanical。内环5Agent选型: AG-CD 混合(GPT-4o+规则,≤$1/次), AG-CT 混合(GPT-4o-mini,≤$0.05), AG-DO 规则(~$0), AG-ST 混合(GPT-4o-mini,≤$0.10), AG-MA 规则(~$0)。

### 6.3 LLM Prompt 管理策略 [V5.0]

版本化 Prompt 模板(`prompts/{agent}/{task}/v{N}.yaml`)。调用前预估成本→超天花板自动降级模型。优化: 上下文压缩(-30-50% tokens), 响应缓存(-60% 重复调用), 批量合并, 模型路由(简单任务→便宜模型)。A/B 测试框架: 质量(EBM能量)+成本+延迟三维评估。部署: K8s ConfigMap 热更新,<30s生效。

---

## 7. 外部系统适配器层

### 7.1 适配器接口标准

`ExternalToolAdapter` 基类: execute(command), health_check(), get_dependency_type()。GitHub/GitLab 可替换演示。

### 7.2 完整适配器清单 (全12 Agent)

| Agent | 必选 | 可选 | 故障降级 |
|-------|------|------|---------|
| AG-CD | GitAdapter (GitHub/GitLab) | IDEAdapter, PkgMgrAdapter | diff 文件 |
| AG-CT | CIAdapter (Actions/Jenkins) | CoverageAdapter, SonarQubeAdapter | 本地测试 |
| AG-DO | K8sAdapter, RegistryAdapter | HelmAdapter, ArgoCDAdapter | YAML 输出 |
| AG-ST | TestEnvAdapter | K6Adapter, PlaywrightAdapter | mock 模式 |
| AG-MA | PrometheusAdapter, GrafanaAdapter | JaegerAdapter, PagerDutyAdapter | metrics-server |
| AG-SA | — | PlantUMLAdapter, OpenAPIGenAdapter | 文本架构文档 |
| AG-FD | — | JiraAdapter, LinearAdapter | JSON Task List |
| AG-AU | SemgrepAdapter, TrivyAdapter | ZAPAdapter, GitLeaksAdapter | "未审计"+阻塞 |
| AG-PA | — | SimilarWebAdapter, CrunchbaseAdapter | 人工输入 |
| AG-PD | — | FigmaAdapter | 人工设计文档 |
| AG-BI | ClickHouseAdapter/PostgreSQLAdapter | MetabaseAdapter | 缓存数据 |
| AG-PR | — | WordPressAdapter, AhrefsAdapter | 方案文档 |

---

## 8. 产物版本管理

8 种产物类型(PRD, 架构文档, 功能分解, 代码变更, 测试报告, 部署清单, 监控报告, 安全审计报告)。版本不一致检测: 每次 SUBMIT_ARTIFACT 实时检测, ≤60s 告警。

### 8.3 产物保留策略 [V6.0]

当前版本 + 最近 5 个历史版本 (共6个)。存储: PostgreSQL(元数据) + 对象存储(内容)。每次提交后检查版本数，删除最旧(保留元数据90天审计)。被引用版本不可删除。

---

## 9. Agent 通用架构

### 9.1 框架结构

Agent-Specific Logic → ALFA Controller → Adapter Layer → Execution Engine → HITL Layer → EIP Client SDK → State Machine + Safety/Audit。

### 9.2 状态机 [V5.0 含 DEGRADED]

```
IDLE → OBSERVING → PLANNING → EXECUTING → VALIDATING → REPORTING → IDLE
         ↕                ↕
  AWAITING_APPROVAL  AWAITING_HUMAN_INPUT (timeout: §9.3)
         ↕
       ERROR → PLANNING(重试) 或 IDLE(超限)

任意状态 → DEGRADED (触发: 必选工具故障/Brain不可用/L3+/TRL回退)
DEGRADED → IDLE (恢复: 3次健康检查OK / Brain恢复 / Level-0 / TRL回升)
```

### 9.3 AWAITING_HUMAN_INPUT 超时策略 [V6.0]

默认4h (对齐 Tier-2 审批 SLA), CRITICAL 1h, OVERRIDE 2h。升级链: 50%→提醒原角色, 75%→升级PM, 100%→自动降级为 SUGGEST + Brain推荐默认方案。

### 9.4 EIP Client SDK 配置表 [V6.0]

| Agent | PREDICT | EVALUATE | ORCHESTRATE | 重试 | 熔断 | 心跳 |
|-------|---------|----------|-------------|------|------|------|
| AG-CD | 10s | 10s | 5s | 3 | 5连超时 | 30s |
| AG-CT | 5s | 5s | 3s | 3 | 5 | 30s |
| AG-DO | 5s | 5s | 3s | 2 | 3 | 15s |
| AG-ST | 10s | 10s | 5s | 3 | 5 | 30s |
| AG-MA | 3s | 3s | 2s | 2 | 3 | 10s |
| AG-SA/FD/AU | 10-15s | 10-15s | 5s | 3 | 5 | 60s |
| AG-PA/PD/BI/PR | 15s | 15s | 5s | 3 | 5 | 60s |

**[deliver-v1.1] RECALL 超时配置 (全 Agent 统一):** RECALL 超时 200ms, 重试 1 次 (记忆检索为增强型上下文, 失败不阻塞决策), 熔断 10 连续超时。Brain Core 在处理 PREDICT/EVALUATE 时自动调用长期记忆检索, Agent 不感知内部记忆调用; Agent 也可主动发起 RECALL 请求获取记忆上下文。

---

## 10. 人工干预与 PROJECT_MANAGER

### 10.1-10.4 角色映射/PM能力/干预类型

PM: READ(全部)+SUGGEST/REQUIRE(PA,PD,BI,PR)+READ(编排仪表盘)。PROJECT_MANAGER: 可观测(12Agent状态+编排输出+TRL+健康度+错误预算), 可干预(优先级+交接门+状态报告), 不可干预(LOA/TRL/安全审批/跨Tenant)。

### 10.5 Portal API [V5.0 含错误响应]

| 接口 | 方法 | 成功 | 错误 |
|------|------|------|------|
| `/api/agent/{id}/suggest` | POST | 200 accepted | 401/403/404/429 |
| `/api/agent/{id}/status` | GET | 200 状态 | 401/404 |
| `/api/agent/{id}/tasks` | GET | 200 任务列表 | 401/404 |
| `/api/agent/{id}/respond` | POST | 200 forwarded | 401/403/404/409 |
| `/api/dashboard/overview` | GET | 200 概览 | 401 |
| `/api/dashboard/orchestration` | GET | 200 编排(PM) | 401/403 |
| `/api/dashboard/error-budget` | GET | 200 错误预算 | 401 |
| `/api/dashboard/trl-progress` | GET | 200 TRL进度 | 401 |

统一错误Schema: `{error: {code, message, details, request_id, timestamp}}`。限流: 读100/min/user, 写20/min/user, 全局1000/min/tenant。

---

## 11. 全12 Agent 详细设计

每个 Agent 包含: 职责/输入输出/执行引擎/LLM依赖/单次成本/必选适配器/可选适配器/降级模式/目标LOA/状态机定制。

(内环5个: §6.2已详述。中环3个: AG-SA混合GPT-4o≤$0.10, AG-FD混合GPT-4o-mini≤$0.05, AG-AU规则~$0。外环4个: AG-PA LLM GPT-4o≤$0.10, AG-PD混合≤$0.10, AG-BI混合ClickHouse+GPT-4o-mini≤$0.05, AG-PR LLM≤$0.10。)

---

## 12. 运行时资源配置 [V5.0 含 per-Profile]

Profile-M 基线: AG-CD 8核16GB, AG-CT 4核8GB, AG-DO 2核4GB 等。per-Profile 伸缩: S(HPA min=1, max=1-2), M(min=1, max=3-5), L(min=2, max=10-20)。HPA CPU 阈值: S 80%, M 80%, L 70%。Profile-L 特殊: Tenant 隔离 namespace + GPU 分片 + NetworkPolicy。

---

## 13. 验收标准映射

| AC | 设计支撑 |
|----|---------|
| AC-1: 内环5Agent LOA≥7 | §2+§3 |
| AC-2: 中环3Agent LOA≥5 | §11.2 |
| AC-3: 外环4Agent LOA≥3 | §11.3 |
| AC-4: LOA 3↔8 自动切换 | §3 ALFA |
| AC-5: Brain不可用→规则引擎 | §4 降级框架 |
| AC-6: 统一 EIP 协议 | §9.4 EIP SDK |
| AC-7: 交接门可配置 | §5 |
| AC-8: LOA 降级30s级联 | §5.2 |
| AC-9: 产物版本60s告警 | §8 |
| AC-10: 执行引擎选型论证 | §6.2 |
