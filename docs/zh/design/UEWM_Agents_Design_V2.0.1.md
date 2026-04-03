# 🤖 UEWM Agent 体系设计文档

**文档版本：** V2.0.1  
**文档编号：** UEWM-AGENT-002  
**最后更新：** 2026-04-03  
**状态：** 设计完成（100% 覆盖 R02, R09, R11, R13, NFR-8/10 + RECALL + 第三方 ADS + UAT + 双空间感知）  
**变更历史：**
- V6.0/deliver-v1.0: 三环分层, ALFA, 降级, 执行引擎, 适配器, 产物管理
- V1.0.1: 第三方 ADS (§14), UAT 工作流 (§15), SDK 发布策略 (§16)
- V2.0.0: Agent 双空间感知 (接收 RiskDecomposition + GSpacePrediction), Agent 可查询 G-Space, Discovery Alert 订阅
- **V2.0.1: (LeWM 集成) SDK 包含 SIGReg 监控工具; Agent 接收 256-d Z-Space 向量; VoE 测试集成; 全量合并 V1.0.1 内容，消除所有引用依赖**

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

### 6.3 LLM Prompt 管理策略

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

### 8.3 产物保留策略

当前版本 + 最近 5 个历史版本 (共6个)。存储: PostgreSQL(元数据) + 对象存储(内容)。每次提交后检查版本数，删除最旧(保留元数据90天审计)。被引用版本不可删除。

---

## 9. Agent 通用架构

### 9.1 框架结构

```
Agent-Specific Logic → ALFA Controller → Adapter Layer → 
Execution Engine → HITL Layer → EIP Client SDK (V2.0) → 
State Machine + Safety/Audit
                                    │
                        V2.0 增强: EIP Client SDK 现在处理
                        ├── RiskDecomposition (从 EipResponse)
                        ├── GSpacePrediction (从 EipResponse)
                        ├── DISCOVERY_ALERT 事件订阅
                        └── QUERY_GSPACE 动词调用
```

### 9.2 Agent 双空间感知 (V2.0 新增)

```python
class DualSpaceAwareAgent:
    """V2.0: Agent 可同时利用 energy (发现) 和 risk (可解释) 做决策。"""
    
    async def make_decision(self, candidates, context):
        # 1. 请求 Brain Core 评估
        response = await self.eip.evaluate(candidates, context)
        
        # 2. 根据 LOA 级别选择使用哪个信号
        if self.loa >= 7:
            # 高自主度: 主要用 energy (包含发现信号)
            best = response.results[0]  # 最低能量
            if best.unnamed_risk_pct > 0.3:
                # 30%+ 未命名风险 → 请求人工确认
                await self.request_human_input(
                    reason=f"High unnamed risk ({best.unnamed_risk_pct:.0%}), "
                           f"model sees something metrics can't explain")
            else:
                await self.execute(best.candidate_id)
        
        elif self.loa >= 5:
            # 中等自主度: 同时展示 energy 和 risk decomposition
            await self.present_options_with_risk(response.results)
        
        else:
            # 低自主度: 仅展示 risk decomposition (可解释)
            await self.present_risk_only(response.results)
    
    async def on_discovery_alert(self, alert: DiscoveryAlertPayload):
        """接收 Discovery Engine 的新发现通知。"""
        # 记录到 Agent 日志
        self.log.info(f"Discovery: {alert.pattern_description} "
                      f"(confidence: {alert.confidence})")
        # 如果与当前任务相关, 调整行为
        if self.is_relevant(alert):
            await self.adjust_strategy(alert)
```

### 9.3 状态机

```
IDLE → OBSERVING → PLANNING → EXECUTING → VALIDATING → REPORTING → IDLE
         ↕                ↕
   AWAITING_APPROVAL  AWAITING_HUMAN_INPUT (timeout: §9.4)
         ↕
       ERROR → PLANNING(重试) 或 IDLE(超限)

任意状态 → DEGRADED (触发: 必选工具故障/Brain不可用/L3+/TRL回退)
DEGRADED → IDLE (恢复: 3次健康检查OK / Brain恢复 / Level-0 / TRL回升)
```

### 9.4 AWAITING_HUMAN_INPUT 超时策略

默认4h (对齐 Tier-2 审批 SLA), CRITICAL 1h, OVERRIDE 2h。升级链: 50%→提醒原角色, 75%→升级PM, 100%→自动降级为 SUGGEST + Brain推荐默认方案。

### 9.5 EIP Client SDK 配置表 (V2.0 增强)

| Agent | PREDICT | EVALUATE | ORCHESTRATE | RECALL | **QUERY_GSPACE** | 重试 | 熔断 | 心跳 |
|-------|---------|----------|-------------|--------|-----------------|------|------|------|
| AG-CD | 10s | 10s | 5s | 200ms | **2s** | 3 | 5 | 30s |
| AG-CT | 5s | 5s | 3s | 200ms | **2s** | 3 | 5 | 30s |
| AG-DO | 5s | 5s | 3s | 200ms | **2s** | 2 | 3 | 15s |
| AG-ST | 10s | 10s | 5s | 200ms | **2s** | 3 | 5 | 30s |
| AG-MA | 3s | 3s | 2s | 200ms | **1s** | 2 | 3 | 10s |
| AG-SA/FD/AU | 15s | 15s | 5s | 200ms | **2s** | 3 | 5 | 60s |
| AG-PA/PD/BI/PR | 15s | 15s | 5s | 200ms | **2s** | 3 | 5 | 60s |

**RECALL 超时配置 (全 Agent 统一):** RECALL 超时 200ms, 重试 1 次 (记忆检索为增强型上下文, 失败不阻塞决策), 熔断 10 连续超时。Brain Core 在处理 PREDICT/EVALUATE 时自动调用长期记忆检索, Agent 不感知内部记忆调用; Agent 也可主动发起 RECALL 请求获取记忆上下文。

---

## 10. 人工干预与 PROJECT_MANAGER

### 10.1-10.4 角色映射/PM能力/干预类型

PM: READ(全部)+SUGGEST/REQUIRE(PA,PD,BI,PR)+READ(编排仪表盘)。PROJECT_MANAGER: 可观测(12Agent状态+编排输出+TRL+健康度+错误预算), 可干预(优先级+交接门+状态报告), 不可干预(LOA/TRL/安全审批/跨Tenant)。

### 10.5 Portal API (V2.0 增强)

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
| **`/api/dashboard/gspace/{project_id}`** | **GET** | **200 G-Space 实时指标** | **401/404** |
| **`/api/dashboard/discoveries`** | **GET** | **200 Discovery Engine 发现列表** | **401** |
| **`/api/dashboard/discovery/{id}/approve`** | **POST** | **200 批准新指标** | **401/403** |
| **`/api/dashboard/discovery/{id}/reject`** | **POST** | **200 拒绝提议指标** | **401/403** |

统一错误Schema: `{error: {code, message, details, request_id, timestamp}}`。限流: 读100/min/user, 写20/min/user, 全局1000/min/tenant。

---

## 11. 全12 Agent 详细设计

每个 Agent 包含: 职责/输入输出/执行引擎/LLM依赖/单次成本/必选适配器/可选适配器/降级模式/目标LOA/状态机定制。

(内环5个: §6.2已详述。中环3个: AG-SA混合GPT-4o≤$0.10, AG-FD混合GPT-4o-mini≤$0.05, AG-AU规则~$0。外环4个: AG-PA LLM GPT-4o≤$0.10, AG-PD混合≤$0.10, AG-BI混合ClickHouse+GPT-4o-mini≤$0.05, AG-PR LLM≤$0.10。)

---

## 12. 运行时资源配置

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
| AC-6: 统一 EIP 协议 | §9.5 EIP SDK |
| AC-7: 交接门可配置 | §5 |
| AC-8: LOA 降级30s级联 | §5.2 |
| AC-9: 产物版本60s告警 | §8 |
| AC-10: 执行引擎选型论证 | §6.2 |
| **AC-11: 第三方 Agent ADS 合规验证** | **§14** |
| **AC-12: UAT 验收工作流闭环** | **§15** |
| **AC-13: Agent 接收并使用 RiskDecomposition** | **§9.2** |
| **AC-14: Agent 可查询 G-Space** | **§9.5 QUERY_GSPACE** |
| **AC-15: Agent 订阅 DISCOVERY_ALERT** | **§9.2 on_discovery_alert** |

---

## 14. 第三方 Agent 开发标准 (ADS)

### 14.1 第三方 Agent 与内置 Agent 的关系

```
内置 Agent (12个): 由 UEWM 团队开发维护, 深度集成 ALFA/EIP/适配器层
第三方 Agent: 由外部开发者通过 Agent SDK 构建, 通过适配层接入

共同点:
  ├── 统一通过 EIP 协议与 Brain Core 交互
  ├── 统一受 RBAC 权限控制
  ├── 统一受 LOA 行为约束
  └── 统一纳入编排模块调度

差异点:
  ├── 第三方 Agent 不直接参与三环分层 (挂载在外部)
  ├── 第三方 Agent 初始 LOA 由注册时声明, 上限受 ALFA 约束
  ├── 第三方 Agent 使用独立资源配额 (ARCH §14.6)
  └── 第三方 Agent 可选择 REST 网关 (低门槛) 或 gRPC 原生 (高性能)
```

### 14.2 Agent 开发标准 (ADS) 合规清单

| 标准编号 | 类别 | 要求 | 验证方式 | 严重级别 |
|---------|------|------|---------|---------|
| ADS-1.1 | 协议 | 实现 REPORT_STATUS 心跳 (≤60s) | uewm-agent-test 心跳检测 | BLOCKER |
| ADS-1.2 | 协议 | 正确处理全部 EipStatus 错误码 | uewm-agent-test 错误注入 | BLOCKER |
| ADS-1.3 | 协议 | request_id 幂等性 | 重复请求测试 | MAJOR |
| ADS-2.1 | 安全 | 凭证不硬编码 | uewm-agent-lint 静态扫描 | BLOCKER |
| ADS-2.2 | 安全 | 不尝试跨 Tenant 请求 | uewm-agent-test 权限测试 | BLOCKER |
| ADS-2.3 | 安全 | 日志不含 Z-Layer 原始向量 | uewm-agent-lint 日志审计 | MAJOR |
| ADS-3.1 | 质量 | 健康检查端点可达 | HTTP/gRPC 探针 | BLOCKER |
| ADS-3.2 | 质量 | REPORT_STATUS 数据 L2 范数 ∈ [0.5, 2.0] | VectorQualityValidator | MAJOR |
| ADS-3.3 | 质量 | 响应超时不超过声明 SLO | 延迟监控 | MINOR |
| ADS-4.1 | 文档 | README 描述功能/场景/Z-Layer 映射 | 人工审核 | MINOR |

### 14.3 第三方 Agent 与编排模块的交互

第三方 Agent 注册后纳入编排模块调度, 但默认优先级低于内置 Agent。编排模块对第三方 Agent 的 DIRECTIVE 为"建议"模式 (非强制), Agent 可忽略但记录审计。第三方 Agent 的产物(Artifact)纳入版本一致性检测, 但不阻塞内置 Agent 交接门。

---

## 15. 产品验收测试(UAT)工作流

### 15.1 设计目标

弥合系统测试 (AG-ST) 与产品需求验证之间的间隙, 确保最终产物满足原始产品需求。

### 15.2 UAT 工作流

```
UAT 闭环 (AG-PA/PD 产品需求 → AG-ST 系统测试 → AG-BI 数据验证):

  Step 1: AG-PA 需求定义阶段
    输出: 验收标准列表 (Acceptance Criteria)
    格式: AC = {id, description, z_layer_mapping, verification_method, priority}
    存储: SUBMIT_ARTIFACT(type=PRD, contains=AC_list)

  Step 2: AG-ST 系统测试阶段
    输入: AC 列表 (从产物版本系统读取)
    映射: 每个 AC → 1+ E2E 测试用例
    输出: AC 级别的通过/失败报告
    Brain Core: EVALUATE(candidates=[AC_pass, AC_fail], context=product_validation)

  Step 3: AG-BI 数据验证阶段
    输入: AC 验证结果 + 运行时指标
    分析: 验收率, 按优先级加权通过率, 趋势
    输出: 产品验收仪表盘
    告警: 高优先级 AC 失败 → Portal 通知 PM

  Step 4: 人工确认
    PM/PD 通过 Portal 审核 UAT 结果
    AG-PD 可根据 UAT 结果更新 PRD (迭代闭环)
    
  跨 Agent 交接:
    AG-PA/PD (外环) → 产品需求+AC → AG-ST (内环) → 测试结果
    → AG-BI (外环) → 分析报告 → PM → 审批/迭代
```

---

## 16. Agent SDK 发布策略

```
Agent SDK 发布计划:

  uewm-agent-sdk (Python, PyPI):
    Phase 0: 内部使用, 12 内置 Agent 基于此 SDK
    Phase 1: Alpha 发布, 邀请制第三方试用
    Phase 2: Beta 发布, 公开 PyPI
    Phase 3: GA 发布, SLA 承诺

  SDK 包含:
    uewm_sdk.agent: UEWMAgent 基类, 生命周期管理
    uewm_sdk.eip: EIP Client (gRPC), 消息序列化
    uewm_sdk.rest: REST Client (替代 gRPC)
    uewm_sdk.health: 健康检查, 心跳
    uewm_sdk.metrics: Prometheus 指标导出
    uewm_sdk.testing: 合规测试套件
    uewm_sdk.gspace: GSpaceQueryClient (V2.0 新增)
    uewm_sdk.discovery: DiscoveryAlertHandler (V2.0 新增)
    uewm_sdk.sigreg: SIGReg 监控工具 (V2.0.1/LeWM 新增)
    
  许可证: Apache 2.0 (独立于 AGPL 主项目, 不触发 copyleft)
```
