# 🧠 UEWM 核心架构设计文档

**文档版本：** deliver-v1.1  
**文档编号：** UEWM-ARCH-001  
**最后更新：** 2026-03-24  
**状态：** 设计完成（100% 覆盖 R01, R05, R07, R11, NFR-1/2/3/8/9/11 + Long Memory MEM-AC-1~10）  
**合并来源：** Architecture V7.0 + Combined Patch + Long Memory Subsystem — 全量合并  
**变更历史：**
- V4.0–V7.0: 编排模块、TRL、MVLS、并发、校准、对齐、POMDP、验证协议、分片、异步化
- deliver-v1.0: 全量合并，无增量补丁依赖
- **deliver-v1.1: 新增 §12 长期记忆子系统 (Episodic/Semantic Memory + Consolidation + Retrieval + Project Profile)**

---

## 1. 文档目的与范围

本文档定义 UEWM 核心架构设计，涵盖: H-JEPA 分层预测架构、隐空间(Z-Layer)分层体系与 TRL 成熟度模型、EBM 仲裁引擎与校准计划、Brain Core 编排模块(含异步化设计)、多项目并发模型与租户分片、跨模态对齐训练实现、错误预算与 SLO 违约响应、系统集成拓扑。

---

## 2. 架构设计原则

| # | 原则 | 说明 |
|---|------|------|
| P1 | JEPA-First | 所有推理在隐空间完成，不做 token 级生成 |
| P2 | 非生成式 | 采用 Joint Embedding Predictive Architecture |
| P3 | 能量最小化 | 全局决策通过 EBM 能量函数寻优 |
| P4 | 层级化抽象 | H-JEPA 多时间尺度多粒度预测 |
| P5 | 模型无关 | 底层感知模块可插拔 |
| P6 | 自进化 | 惊奇度驱动持续学习 |
| P7 | 安全可控 | 能量阈值 + 人工门禁 |
| P8 | 多团队通用 | Base Model + 独立 LoRA + 租户分片 |
| P9 | 主动内省 | 定期自反省 |
| P10 | 人机协同 | 角色工程师可随时介入 |
| P11 | 不确定性感知 | POMDP 框架下概率分布表示 + 信息获取触发 |
| P12 | 渐进成熟 | TRL 驱动系统行为，未成熟层自动降级 |
| P13 | 编排即决策 | 跨 Agent 编排是 Brain Core 的执行功能 |

---

## 3. 系统总体架构

### 3.1 四层仿生架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    第零层：外部世界 (External World)                  │
│    代码仓库 / CI/CD / 监控平台 / 用户反馈 / 市场数据 / 日志系统       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Raw Signals
┌──────────────────────────────▼──────────────────────────────────────┐
│                第一层：多模态感知层 (Perception Layer)                 │
│  Code Encoder │ Doc Encoder │ Metric Encoder │ Market Encoder        │
│  (AST+CFG→Z)  (NL→Z)       (TS→Z)           (Tabular→Z)           │
│         └──────────┴────────┬───────┴──────────────┘                │
│                   Projection & LayerNorm → 2048-d                   │
│                   AlignmentTrainer (跨模态对齐)                      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│              第二层：H-JEPA Brain Core                                │
│  Z-Buffer Manager ← Z_market|Z_val|Z_biz|Z_logic|Z_arch|           │
│                      Z_impl|Z_quality|Z_phys                        │
│  H-JEPA Predictor ◄► 跨层因果图 ◄► EBM 能量仲裁引擎                  │
│  长期记忆子系统 (情景记忆 + 语义记忆 + 巩固 + 检索) [deliver-v1.1]     │
│  编排模块 (7项能力, 含异步化)                                         │
│  TRL 成熟度评估器                                                    │
│  错误预算引擎 (Burn-Rate/4级告警)                                     │
│  自进化引擎 (安全包络/断路器/帕累托)                                   │
│  自反省引擎 │ 跨项目知识引擎                                          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ EIP Protocol (gRPC + Kafka + Stream)
┌──────────────────────────────▼──────────────────────────────────────┐
│              第三层：EIP Gateway (RBAC/mTLS/DynamicPermission)        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│          第四层：Agent 终端阵列 (三环分层)                             │
│  外环: AG-PA │ AG-PD │ AG-BI │ AG-PR (Phase 2, LOA 3-5)            │
│    中环: AG-SA │ AG-FD │ AG-AU (Phase 1, LOA 5-7)                  │
│      内环: AG-CD │ AG-CT │ AG-DO │ AG-ST │ AG-MA (Phase 0, LOA 7-9)│
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Brain Core 内部组件清单

| # | 组件 | 职责 | 对标需求 |
|---|------|------|---------|
| 1 | Z-Buffer Manager | 8层隐状态读写/快照/版本 | R01 |
| 2 | Perception Pipeline + AlignmentTrainer | 编码器管理/投影/跨模态对齐 | R01, R12 |
| 3 | H-JEPA Predictor | 多时间尺度状态预测 | R01 |
| 4 | Causal Graph Engine | 格兰杰因果图构建/查询/回溯 | R01 |
| 5 | EBM Arbiter (含校准计划) | 能量仲裁/沙盒预演/Kendall τ 校准 | R01 |
| 5.1 | **Long Memory Subsystem** | **情景记忆/语义记忆/巩固引擎/检索引擎/Project Profile** | **R01,R03,R06,R10** |
| 6 | Orchestration Module (含异步化) | 任务排序/交接/仲裁/里程碑/冲突 | R01 G6, Gap-2 |
| 7 | TRL Evaluator | Z-Layer 成熟度自动评估/动态降权 | R01 G1-S1 |
| 8 | Evolution Engine | 安全包络/断路器/帕累托/LoRA | R03 |
| 9 | Self-Reflection Engine | 定期内省/盲区检测/偏差分析 | R06 |
| 10 | Knowledge Engine | KSL蒸馏/隐私预算/联邦学习 | R08 |
| 11 | Error Budget Engine | Burn-Rate/4级告警/自动降级 | R05 Gap-1 |
| 12 | Request Router | 请求分发/响应聚合 | R11 |

### 3.3 编排模块 (Orchestration Module)

#### 3.3.1 设计定位

Brain Core 的"执行功能"，与 JEPA Predictor、EBM Arbiter 并列。从 Z-Layer 信号派生项目级元信号，不引入独立 Z-Layer。不是第 13 个 Agent。

#### 3.3.2 内部结构

Task Dependency Scheduler → Cross-Ring Handoff Evaluator → Resource Contention Arbiter → Milestone Tracker → LOA Cascade Assessor → Project Status Synthesizer → Cross-Agent Conflict Resolver

#### 3.3.3 输入信号

从 Z-Layer TRL 进度派生进度风险；从 Agent 历史表现派生交付风险；从 EBM 能量趋势派生质量风险；综合加权得出 project_health_score。

```python
class OrchestratorInputSignals:
    """编排模块从现有 Z-Layer 信号中派生项目级元信号。"""
    
    def derive_project_health(self, project_id):
        signals = {}
        for layer in self.get_project_layers(project_id):
            trl = self.get_trl(layer)
            target_trl = self.get_target_trl(layer, current_phase)
            signals[f"{layer}_progress_gap"] = target_trl - trl
        
        for agent_id in self.get_project_agents(project_id):
            perf = self.get_performance(agent_id)
            signals[f"{agent_id}_reliability"] = perf.success_rate
            signals[f"{agent_id}_current_loa"] = self.alfa.compute_effective_loa(agent_id, None)
        
        energy_trend = self.get_energy_trend(project_id, window_days=7)
        signals["energy_trend"] = energy_trend
        signals["project_health_score"] = self.weighted_aggregate(signals)
        return signals
```

#### 3.3.4 七项核心能力

| 能力 | 输出 | SLO | 同步/异步 |
|------|------|-----|----------|
| 任务依赖排序 | 推荐执行顺序 | < 2s | 同步 |
| 跨环交接评估 | 就绪/阻塞+原因 | < 5s | 同步 |
| 资源争用仲裁 | 分配优先级 | < 1s | 异步执行 |
| 里程碑跟踪 | 偏差报告 | < 1min | 异步(每30s) |
| LOA 级联评估 | 影响分析 | < 30s | 异步事件驱动 |
| 项目状态综合 | 结构化报告 | ≤ 30s | 异步(每30s) |
| 跨 Agent 冲突协调 | 仲裁/升级 | < 10s | 异步 |

#### 3.3.5 与 EIP 的交互

通过 ORCHESTRATE 动词接收同步请求 (SCHEDULE, HANDOFF_CHECK)。通过 Kafka 事件发送异步通知 (DIRECTIVE, LOA_UPDATE)。

#### 3.3.6 异步化设计

```
编排操作分类 (同步 vs 异步):

  同步 (阻塞 Agent 请求, 必须在 Brain SLO 内完成):
    ├── SCHEDULE (任务排序查询): < 2s → 直接返回当前调度表
    └── HANDOFF_CHECK (交接就绪查询): < 5s → 直接返回评估结果

  异步 (不阻塞 Agent, 后台执行 + 事件通知):
    ├── RESOLVE_CONFLICT (冲突仲裁): 可能需要多 Agent 信息 → 异步处理 → Kafka 事件通知
    ├── 里程碑跟踪更新: 后台定时 (每 30s) 重新计算
    ├── LOA 级联评估: LOA 变更事件触发 → 异步评估 → 30s 内通知
    ├── 项目健康度综合: 后台定时 (每 30s) 重新计算 → 推送 Dashboard
    └── 资源仲裁执行: 调度决策 → Kafka 事件 → K8s Scheduler 异步执行

  队列深度保护:
    ├── 异步编排任务队列: max depth = 100
    ├── 超过 100 → 丢弃最低优先级任务 + 告警
    └── 队列处理延迟 > 30s → 告警 DEVOPS

  对 LOA 7+ Agent 的影响:
    LOA ≥ 7 的 Agent 可自主执行, 不等待编排模块同步响应
    编排模块的调度建议以异步 DIRECTIVE 形式下发
    Agent 可选择遵循或忽略 (记录在审计日志中)
```

### 3.4 多项目编排并发模型

三级调度: L1 加权公平共享(默认) → L2 优先级抢占(高压) → L3 租户隔离(强隔离)。

```
L1 加权公平共享 (Weighted Fair Share) — 默认模式:
  每个 Tenant 获得与其 SLA 等级成比例的资源份额。同一 Tenant 内项目按优先级权重分配。
  空闲份额可被其他项目临时借用 (preemptible, 借用延迟 ≤ 5s 归还)。适用: 常态运行, Profile-S/M。

L2 优先级抢占 (Priority Preemption) — 高压力模式:
  触发: Agent 请求队列深度 > 3x 正常值 或 SLO burn-rate > 5%/h。
  高优先级项目可抢占低优先级项目的 Agent 时间片。被抢占任务挂起 (非丢弃), 恢复后自动续行。

L3 租户隔离 (Tenant Isolation) — 强隔离模式:
  触发: 任一 Tenant 的 SLO 连续 10min 未达标。各 Tenant Agent 实例和 GPU 配额完全隔离。
  适用: Profile-L, 或合同要求资源隔离的 Tenant。
```

Per-Tenant 配额: Profile-S 5并发/1项目, Profile-M 50并发/10项目, Profile-L 200并发/50项目。Agent 并发: 每类型 Profile-M 最多 5 实例。

```python
class TenantResourceQuota:
    PROFILE_QUOTAS = {
        "Profile-S": {"max_concurrent_agent_tasks": 5, "max_projects": 1, "gpu_share_pct": 100, "evolution_slots_per_day": 1},
        "Profile-M": {"max_concurrent_agent_tasks": 50, "max_projects": 10, "gpu_share_pct": None, "evolution_slots_per_day": 5},
        "Profile-L": {"max_concurrent_agent_tasks": 200, "max_projects": 50, "gpu_share_pct": None, "evolution_slots_per_day": 15},
    }
    
    def can_schedule(self, tenant_id, agent_type, project_id):
        quota = self.get_tenant_quota(tenant_id)
        current_usage = self.get_current_usage(tenant_id)
        if current_usage.concurrent_tasks >= quota["max_concurrent_agent_tasks"]:
            return ScheduleVerdict.QUEUED(reason="tenant_quota_exceeded")
        return ScheduleVerdict.ALLOWED
```

### 3.5 组件映射表

Architecture 12 组件 vs Engineering Spec 9+2 模块的映射: Self-Reflection 和 Knowledge Engine 在 Eng Spec 中归入 Evolution Engine 子包(代码视角 vs 功能视角)。详见 Engineering Spec §2.1。

### 3.6 租户分片架构

```
租户分片设计:
  分片键: tenant_id (一致性哈希), ≤ 10 Tenants/分片
  分片实例: 每个分片是一个独立的 Brain Core Deployment (Active-Standby)
  
  Profile-S: 1 分片 (单租户)
  Profile-M: 1 分片 (≤10 租户)
  Profile-L: N 分片 (N = ceil(tenant_count / 10))

  跨分片查询:
    ├── Z-Buffer: 每个分片独立 (不跨分片查询)
    ├── EBM 评估: 分片内完成 (不需要跨分片数据)
    ├── 联邦学习: 由 Knowledge Engine 跨分片协调 (独立组件)
    └── 编排模块: 分片内编排; 跨分片资源仲裁由全局 Orchestrator Coordinator 处理

  分片再平衡:
    ├── 触发: 分片内 Tenant 数 > 10 或 负载不均 (CPU 差异 > 30%)
    ├── 方式: 新建分片 → 迁移 Tenant 的 Z-Buffer + LoRA → 切换路由 → 删除旧分片数据
    ├── 停机: 迁移期间该 Tenant 的 Brain 请求排队 (预计 < 5min)
    └── 自动化: K8s Operator 管理分片生命周期

  EIP Gateway 路由:
    EIP Gateway 维护 tenant_id → shard_id 映射表
    每个 EipRequest 根据 project_id → tenant_id → shard_id 路由到正确的 Brain Core 分片
```

---

## 4. 隐空间分层设计 (Z-Layers)

### 4.1 层级定义

8 层: Z_market(周/月) → Z_val(季度) → Z_biz(周) → Z_logic(天) → Z_arch(天) → Z_impl(小时) → Z_quality(小时) → Z_phys(分钟)。每层输出 2048-d 向量。

### 4.2 层间因果关联图

动态因果拓扑 G=(V,E)，格兰杰因果检验 (p<0.05) 自动发现因果边。主链: Z_market→Z_val→Z_biz→Z_logic→Z_arch→Z_impl→Z_quality, Z_impl→Z_phys。反馈: Z_phys→Z_arch, Z_quality→Z_logic, Z_phys→Z_val, Z_quality→Z_val。

### 4.3 TRL 成熟度评估子系统

```
TRL-0 (概念): 编码器架构已确定，但无训练数据，隐空间无意义
TRL-1 (原型): 编码器可产出向量，但语义聚类 ARI < 0.3
TRL-2 (验证): 语义聚类 ARI ≥ 0.3，但跨层因果关系未验证
TRL-3 (集成): 单向因果关系可检测 (本层→邻居层 格兰杰 p<0.05)
TRL-4 (成熟): 双向因果传导可靠，预测 MSE < 0.1，可支撑 Agent 决策
TRL-5 (自优化): 自进化闭环验证通过，惊奇度收敛
```

TRL↔系统行为: Agent自主度(TRL<3→不可自主)、EBM权重(TRL<3→0.1x)、因果回溯(TRL<3→单向)、进化训练(TRL<2→仅数据收集)、人工介入(TRL<3→必须审批)。

评估频率: 每日02:00 UTC + 进化后立即 + 冷启动每6h。

### 4.4 MVLS 最小可行隐空间

Z_impl + Z_quality + Z_phys。验证标准: Z_impl→Z_quality 方向准确率>70%, Z_quality→Z_impl 回溯>60%, Z_phys 异常预测 F1>0.6, 跨项目方差<20%。

扩展路径: Phase 0(3层TRL-3) → Phase 1(+Z_arch,Z_logic) → Phase 2(+Z_biz,Z_val) → Phase 3(全8层TRL-4+)。

### 4.5 跨模态对齐训练实现

AlignmentTrainer 作为 Perception Pipeline 子模块。三阶段:

Stage 1 域内对比(InfoNCE, ARI≥0.3): 同一项目不同时间点的 Z_impl 应比不同项目的更近。Stage 2 相邻层对齐(跨模态对比+因果预测, MSE改善>30%): 同一项目同一时间点的 Z_impl 和 Z_quality 应比随机配对更近。Stage 3 全局联合(VICReg正则, 因果图有效率>80%): 所有层形成统一语义空间。

每阶段有收敛准则和中止条件。仅使用训练GPU池(NFR-9)。Phase 0 时间线: Week 1-4 Stage 1(3层), Week 5-8 Stage 2(3对), Week 9+ MVLS验证。

---

## 5. H-JEPA 分层预测引擎

### 5.1-5.3 JEPA 核心/动力学/多时间尺度

Context Encoder → Target Encoder (EMA) → Predictor (T-GCN + Transformer-XL)。预测 Z 向量而非 token。微观(分钟→小时)/中观(天→周)/宏观(月→季度)三层计算。

### 5.4 POMDP 不确定性建模

Z^(l) ~ N(μ^(l), Σ^(l))。低 tr(Σ)→认知充分, 高 tr(Σ)→触发信息获取。

#### 5.4.1 信息获取触发机制

```python
class UncertaintyTriggeredActions:
    """当 Z-Layer 不确定性 (tr(Σ)) 超过阈值时的信息获取策略。"""
    
    UNCERTAINTY_THRESHOLDS = {
        # Layer: (moderate_threshold, high_threshold, critical_threshold)
        "Z_impl":    (0.5, 1.0, 2.0),
        "Z_quality": (0.5, 1.0, 2.0),
        "Z_phys":    (0.3, 0.8, 1.5),   # 物理层对不确定性更敏感
        "Z_arch":    (0.8, 1.5, 3.0),
        "Z_logic":   (0.6, 1.2, 2.5),
        "Z_biz":     (1.0, 2.0, 4.0),
        "Z_val":     (1.0, 2.0, 4.0),
        "Z_market":  (1.5, 3.0, 5.0),   # 市场层不确定性最高
    }
```

MODERATE→Agent额外观测(LOA cap=7), HIGH→请求人工+LOA cap=5, CRITICAL→推迟决策+EBM权重临时归零+编排阻塞(LOA cap=3)。

不确定性仪表盘: 各层 tr(Σ) 实时值+阈值线, 30s 刷新。

### 5.5-5.7 分层计算/对齐协议/端到端训练

MVLS 阶段仅启用微观+实时物理层计算，宏观/中观以 Mock 模式运行。

### 5.8 JEPA Predictor 验证协议

```python
class PredictorValidationProtocol:
    """JEPA Predictor 预测精度验证方案"""
    
    VALIDATION_SPEC = {
        "validation_set_construction": {
            "method": "Held-out 20% projects (time-based split, not random)",
            "min_projects": 2,        # Phase 0: 至少 2/10 标杆项目做验证
            "split_point": "最后 20% 时间段的观测作为验证集",
            "rationale": "时间序列数据必须按时间切分，否则数据泄漏",
        },
        "evaluation_metrics": {
            "1_step_mse": {"threshold": 0.15, "layers": ["Z_impl", "Z_quality", "Z_phys"]},
            "3_step_mse": {"threshold": 0.30, "layers": ["Z_impl", "Z_quality", "Z_phys"]},
            "5_step_mse": {"threshold": 0.50, "layers": ["Z_impl", "Z_quality", "Z_phys"]},
        },
        "evaluation_cadence": "每次 LoRA 进化后 + 每周定时",
        "reporting": "结果写入 MLflow metrics, 可在 TRL Progress 仪表盘查看",
        "failure_action": "MSE 超标 → TRL Evaluator 可能降级该层 TRL",
    }
```

---

## 6. EBM 能量仲裁引擎

### 6.1 全局能量函数

E_total = Σ w_l^eff · Ẽ_l + λ_cross · E_cross + λ_safe · E_safety。w_l^eff = w_l × TRL_weight(l)。TRL<3→权重0或0.1。

### 6.2 量纲/风险映射/沙盒预演/权重自动调优

分位数归一化→[0,1]。LOW[0,0.3)/MEDIUM[0.3,0.5)/HIGH[0.5,0.7)/CRITICAL[0.7,1.0]。多方案 GPU batch 并行模拟，比较轨迹稳定性。Meta-learning 每周/每100次决策自动调优权重。

### 6.3 EBM 校准计划

**校准数据集:** 200 对成对比较样本 (5类决策×各40-50对), 3-5位专家盲评, Dawid-Skene 聚合, 最低一致率 60%。

**校准流程:** Step 1(Week 1-3): 构建校准集 → Step 2(Week 4): 基线 τ 测量 (预期~0.2-0.3) → Step 3(Week 5-6): Bayesian 优化权重 (Optuna+交叉验证) → Step 4(Week 7): 验证 τ≥0.5 on 30% held-out → Step 5(Phase 1+): 每季度补充50样本+重评估。

校准数据版本: DVC 管理, `datasets/calibration/v{X}/calibration_pairs.parquet`。

---

## 7. 工程智能协议 (EIP)

对齐 R11 V3.0 强类型规范。完整 IDL 定义见 `UEWM_EIP_Protocol.md`。Request/Response/Event/Stream 四种消息类型。6 个 Agent→Brain 动词 + 4 个 Brain→Agent 动词。

### 7.5 错误预算与 SLO 违约响应架构

Brain Core 99.95% (21.6min/月), EIP Gateway 99.99% (4.3min), Agent 99.9% (43.2min), 端到端 99.5% (216min)。

4级 Burn-Rate: L1(观察,1h>2x) → L2(警告,6h>5x,暂停进化) → L3(危急,<20%,冻结新项目) → L4(耗尽,变更冻结)。

SLO 违约联动: Brain超标→进化暂停+LOA降1级+反省推迟+编排降频。Agent超标→LOA≤4+编排标记受限。EIP Gateway超标→全系统+编排缓存模式。

---

## 8-9. 数据流/编码器

正向演进流(Idea→上线), 逆向进化流(事故→自修正), 编排交互流。

8个编码器矩阵含选型论证(§9.2): CodeBERT(Z_impl), TFT(Z_quality从零训练), TimesFM(Z_phys), GraphSAGE+BERT(Z_arch), BERT/RoBERTa(Z_logic), TabNet+FinBERT(Z_biz/Z_val/Z_market)。每层含选型理由、替代方案、否决原因。

投影适配层→2048-d。向量数据库: Phase 0 pgvector → Phase 1+ Milvus。

---

## 10. 技术选型

PyTorch 2.x, DeepSpeed/FSDP, vLLM/TensorRT, gRPC+Protobuf, Kafka, Redis+PostgreSQL, Neo4j, pgvector→Milvus, MLflow+DVC, Kubernetes, Prometheus+Grafana+OTel。

---

## 12. 长期记忆子系统 (Long Memory Subsystem) [deliver-v1.1 新增]

### 12.1 设计动机

当前 UEWM 的 Z-Buffer 仅维护工作记忆 (当前状态)，LoRA 权重仅编码程序记忆 (隐性技能)。系统缺乏类人脑的情景记忆 ("上次发生了什么") 和语义记忆 ("总结性规律")。这导致 Brain Core 能预测但不能回忆，能学习但不能参考历史经验做决策。

### 12.2 三层记忆模型

```
Layer 1: 工作记忆 (Working Memory) — Z-Buffer [已有]
  存储当前 Z-Layer 向量, 每次观测覆写

Layer 2: 情景记忆 (Episodic Memory) — [新增]
  存储: 具体事件 (决策/事故/进化/人工干预) 及其 Z-Layer 快照和结果
  格式: Episode = {触发, Z快照, 决策, 结果, 能量, 惊奇度, 时间戳, 项目}
  容量: 每项目 1K(Phase 0) → 5K(Phase 1) → 10K(Phase 2+)
  索引: 时间 + Z向量相似度(pgvector ANN) + 因果标签 + 结果标签
  用途: "上次出现类似 Z_impl 模式时, 部署导致了 P99 飙升"

Layer 3: 语义记忆 (Semantic Memory) — [新增]
  存储: 从多个 Episode 提取的稳定事实 (因果/模式/反模式/偏好)
  格式: Fact = {主题, 关系, 对象, 置信度, 有效期, 来源Episode}
  容量: 每项目 ~200(Phase 0) → ~1000(Phase 2+)
  索引: Neo4j 知识图谱 (Entity-Relation-Entity)
  用途: "此项目的代码复杂度上升通常在 72h 内导致测试覆盖率下降"
```

### 12.3 情景记忆

#### Episode 数据结构

```python
class Episode:
    episode_id: str;  project_id: str;  tenant_id: str;  timestamp: datetime
    trigger_type: str    # DECISION / INCIDENT / EVOLUTION / HUMAN_INTERVENTION / REFLECTION
    z_snapshot: Dict[str, bytes]  # 决策时刻冻结的 Z-Buffer 切片
    decision_summary: str;  decision_energy: float;  outcome: str;  outcome_energy: float
    surprise_score: float;  was_human_overridden: bool;  human_feedback: Optional[str]
    importance_score: float  # [0,1] 多因素加权
    decay_factor: float      # 艾宾浩斯衰减 [0,1]
    recall_count: int;  last_recalled: datetime
    extracted_fact_ids: List[str]
    ksl_level: int           # 继承项目 KSL
```

#### Episode 触发规则

EVALUATE 完成→创建 DECISION Episode, 惊奇度超阈值→INCIDENT Episode, LoRA 进化完成→EVOLUTION Episode (importance=1.0), 人工干预→HUMAN_INTERVENTION Episode, 自反省异常→REFLECTION Episode。

#### 重要性评分

```python
importance = (surprise × 0.25) + (energy_delta × 0.20) + (human_override × 0.20) 
           + (failure_value × 0.15) + (risk_level × 0.10) + (recall_boost × 0.10)
```

#### 艾宾浩斯衰减

decay = exp(-0.1 × days_since) × exp(-0.05 × days_since_recall) × (0.5 + 0.5 × importance)。importance > 0.8 的 Episode 永不归档 (里程碑事件)。

### 12.4 语义记忆

#### Fact 数据结构

```python
class Fact:
    fact_id: str;  project_id: str;  tenant_id: str
    subject: str;  relation: str;  object: str        # 知识三元组
    confidence: float;  valid_from: datetime;  valid_until: Optional[datetime]
    is_invalidated: bool;  invalidated_by: Optional[str]
    source_episode_ids: List[str];  min_episodes_required: int = 3
    fact_type: str   # CAUSAL / CORRELATION / PREFERENCE / PATTERN / ANTI_PATTERN / TEMPORAL
    ksl_level: int
```

#### 事实提取规则

3+ 一致 Episode 同 Z-Layer 变化方向→同结果 → CAUSAL Fact。3+ 相似 Z 快照→FAILURE → ANTI_PATTERN Fact。3+ 人工覆写同类决策 → PREFERENCE Fact。4+ 周期性重复 → TEMPORAL Fact。

#### 矛盾处理

新 Fact 提取时扫描语义相似度>0.8 的已有 Fact，矛盾时: 时间优先(新推翻旧) + 频率加权(更多支撑Episode胜出)。旧 Fact 标记 is_invalidated=true。置信度接近(差<0.1)时升级人工确认。

### 12.5 记忆巩固引擎

每日 03:00 UTC 运行 (与自反省同步)。Stage 1(5min): Episode 衰减清洗→归档冷存储。Stage 2(10min): 新 Episode 事实提取→矛盾检测→确认写入。Stage 3(5min): 已有 Fact 置信度更新 (新支撑↑, 长期无支撑↓)。Stage 4(2min): Project Profile 生成。

巩固驱动进化: ANTI_PATTERN Fact → 注入进化引擎定向训练。矛盾解决 → 触发 LoRA 微调。进化产出巩固素材: 进化 Episode(importance=1.0) → 提取进化有效性 Fact。

### 12.6 Project Profile (项目档案)

```python
class ProjectProfile:
    """从语义记忆自动生成, ~50ms 可查询, 注入每次 EBM/JEPA 决策。"""
    
    static_facts: List[str]      # 稳定特征 (变化缓慢)
    # "Python/Go 双语言, 微服务, 12 服务", "测试覆盖率稳定 78-82%"
    
    dynamic_context: List[str]   # 近期活动 (频繁更新)
    # "支付服务重构中 (Z_impl 变化频繁)", "上次部署导致 P99 飙升已回滚"
    
    risk_memories: List[str]     # 从 FAILURE Episodes 提取
    # "大规模 DB 迁移历史上 2/3 次导致停机"
```

Profile 注入: PREDICT→影响不确定性估计(risk→提高Σ), EVALUATE→影响能量权重(PREFERENCE→-5%, ANTI_PATTERN→+20%), ORCHESTRATE→影响任务排序(dynamic_context→优先级)。缓存 Redis TTL=30s。

### 12.7 记忆检索引擎

四种检索模式: (1) Z-Layer 向量相似度 (当前状态 vs 过去 Episode 快照, pgvector ANN), (2) 因果图遍历 (changed_layers → 2 跳因果链, Neo4j), (3) 文本语义检索 (自然语言查询), (4) Project Profile 注入 (总是)。检索 SLO: P99 < 200ms。通过 EIP RECALL 动词暴露。

### 12.8 KSL 感知记忆隔离

KSL-0: Episode/Fact 完全隔离, 跨项目检索返回零, 遗忘100%。KSL-1: 可共享聚合统计级 Fact (DP ε≤0.5)。KSL-2: 脱敏 Pattern/AntiPattern (经审核)。KSL-3: 联邦+脱敏 Fact+聚合 Episode 统计。KSL-4: 同 Tenant 完全共享 Memory。

### 12.9 存储架构

Episode: 热(30天, PostgreSQL+pgvector, ~25MB/天 Profile-M) → 温(30-180天, PG元数据+S3快照, <5s) → 冷(180天+, S3归档, <5min)。Semantic: Neo4j 知识图谱。Profile: Redis 缓存(TTL=30s)。

---

## 13. 验收标准映射

| AC | 设计支撑 | 验证方法 |
|----|---------|---------|
| R01 AC-1: 8层2048-d | §9.1 编码器矩阵 | 单元测试: 输入→输出 shape==(batch,2048) |
| R01 AC-2: Kendall τ≥0.5 | §6.3 校准计划 | 校准数据集+5-fold交叉验证 |
| R01 AC-3: 1步MSE<0.15 | §5.8 验证协议 | Held-out 20% 项目, time-based split |
| R01 AC-4: MVLS TRL-3 | §4.3+§4.5 | TRL Evaluator: ARI≥0.3+格兰杰p<0.05 |
| R01 AC-5: 因果 p<0.05 | §4.5 Stage 2 | 格兰杰检验: 每对相邻层 |
| R01 AC-6: TRL 动态降权 | §4.3 | 注入低ARI→验证EBM降权 |
| R01 AC-7: 编排输出排序 | §3.3 | 集成测试: 输入Z-Layer→输出排序+健康度 |
| R01 AC-8: 选型论证 | §9.2 | 文档评审: 每编码器有选型/替代/否决 |
| R01 AC-9: 多项目无饥饿 | §3.4 | 负载测试: 5项目→最大等待<Tier-2 SLO |
| R01 AC-10: 配额排队 | §3.4 | 集成测试: 超配额→QUEUED不超Tier SLO |
| **MEM-AC-1: Episode 自动创建** | **§12.3** | **10 种触发→验证 Episode 存储完整** |
| **MEM-AC-2: 相似度检索 P99<200ms** | **§12.7** | **向量检索延迟+相关度测试** |
| **MEM-AC-3: 事实自动提取** | **§12.4** | **5 个一致 Episode→Fact 生成, 置信度>0.7** |
| **MEM-AC-4: 矛盾自动解决** | **§12.4** | **注入矛盾→旧 Fact invalidated** |
| **MEM-AC-5: 衰减归档** | **§12.3** | **低重要性 90 天后自动归档** |
| **MEM-AC-6: Profile 生成<50ms** | **§12.6** | **含 static/dynamic/risk 三部分** |
| **MEM-AC-7: KSL-0 记忆隔离** | **§12.8** | **跨项目检索返回零结果** |
| **MEM-AC-8: 记忆增强决策质量** | **§12.6** | **A/B: Kendall τ 提升≥0.05** |
| **MEM-AC-9: 巩固<30min 不影响 SLO** | **§12.5** | **性能监控** |
| **MEM-AC-10: 回忆影响可审计** | **§12.7** | **MemoryInfluence 审计日志验证** |
| NFR-1: Brain P99 | §7.5 | 负载测试 Profile-S/M/L |
| NFR-2: 可用性 | §7.5 | 48-72h 无人值守运行 |
| NFR-3: S→L | §3.6 | 扩展测试: 仅加资源 |
| NFR-8: 决策审计 | §3.2 #12 | 决策→审计日志→多维查询 |
| NFR-9: GPU争用 | §7.5 | GPU争用负载测试 |
| NFR-11: 日志分层 | §7.5 | Hot/Warm/Cold 查询SLO验证 |
