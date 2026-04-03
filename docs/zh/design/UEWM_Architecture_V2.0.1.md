# 🧠 UEWM 核心架构设计文档

**文档版本：** V2.0.1  
**文档编号：** UEWM-ARCH-001  
**最后更新：** 2026-04-02  
**状态：** 设计完成（100% 覆盖 R01, R05, R07, R11, NFR-1~14 + MEM-AC-1~10 + GPU-AC-1~6 + EXT-AC-1~8 + LIC-AC-1~4 + GND-AC-1~10 + LeWM-AC-1~6）  
**变更历史：**
- deliver-v1.1: H-JEPA, 8 Z-Layers, EBM, 编排模块, TRL, 长期记忆
- V1.0.1: GPU 优化, 第三方 Agent 适配层, 独立 API, 许可证策略
- V2.0.0: 双空间架构 (G-Space + Z-Space), 桥接函数, Discovery Engine, 双空间惊奇度, 增强 EBM 输出, 验证优先构建策略
- **V2.0.1: LeWorldModel 集成 — SIGReg 替换 VICReg, 投影头 (MLP+BN), 物理探测验证, 违反预期测试, 自适应隐维度 (256-d→2048-d), 端到端编码器微调策略**

---

## 1. 文档目的与范围

本文档定义 UEWM V2.0 核心架构设计。V2.0 的核心创新: **双空间架构 (Dual-Space Architecture)** — Z-Space (隐空间) 负责发现未命名模式, G-Space (可观测空间) 负责验证和锚定, 两者通过桥接函数耦合。隐空间发现, 可观测空间验证, 记忆巩固, 进化锐化。

涵盖: 双空间感知架构、H-JEPA 分层预测引擎 (双预测)、EBM 增强仲裁 (能量+风险分解)、Discovery Engine、G-Space Engine、桥接函数与一致性损失、Brain Core 编排模块、多项目并发模型与租户分片、GPU 优化策略、第三方 Agent 适配层、独立 Brain Core API、许可证与分发。

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
| P9 | 主动内省 | 定期自反省 (含接地健康度) |
| P10 | 人机协同 | 角色工程师可随时介入 |
| P11 | 不确定性感知 | POMDP 框架下概率分布表示 |
| P12 | 渐进成熟 | TRL 驱动系统行为 |
| P13 | 编排即决策 | 跨 Agent 编排是 Brain Core 的执行功能 |
| **P14** | **双空间锚定** | **隐空间每个预测必须最终可对照可观测量验证; 可观测空间从隐空间学习新指标** |
| **P15** | **验证优先** | **先用 PoC 证明科学假设, 再构建完整平台** |
| **P16** | **发现即知识** | **Z-Space 正确而 G-Space 无法解释的预测 = 新工程知识** |

---

## 3. 系统总体架构 (V2.0 五层仿生架构)

### 3.1 架构总览

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    第零层: 外部世界 (Observable World)                    │
│    代码仓库 / CI-CD / 监控平台 / Issue Tracker / 市场数据 / 日志系统      │
└────────────────────┬──────────────────────┬──────────────────────────────┘
                     │ Direct Measurements   │ Raw Signals (for encoding)
┌────────────────────▼──────────────────────▼──────────────────────────────┐
│              第一层: 双模感知层 (Dual Perception Layer)                    │
│                                                                          │
│  ┌─ G-Space Engine ────────────────┐  ┌─ Z-Space Encoders ────────────┐ │
│  │ ~80 named metrics per project   │  │ 8 modal encoders → 2048-d     │ │
│  │ No learning, direct measurement │  │ Discovers unnamed patterns    │ │
│  │ Reality anchor for Z-Space      │  │ Learned representations       │ │
│  └──────────────┬──────────────────┘  └──────────────┬────────────────┘ │
│                 │      Bridging Functions (φ, ψ)      │                  │
│                 └──────── Consistency Loss ────────────┘                  │
│                 AlignmentTrainer (跨模态对齐, V1.0.1 保留)                │
└────────────────────────────────┬─────────────────────────────────────────┘
                                │
┌────────────────────────────────▼─────────────────────────────────────────┐
│               第二层: H-JEPA Brain Core (V2.0 enhanced)                  │
│                                                                          │
│  Z-Buffer Manager ← 同时管理 Z-Layer 状态 + G-Space 状态                 │
│  H-JEPA Predictor ──► 双预测: Z(t+1) AND G(t+1) 同步输出               │
│  EBM Arbiter (V2.0) ──► Energy score + Risk Decomposition               │
│       unnamed_risk = energy not explained by G-Space → Discovery Signal  │
│  Causal Graph Engine ← Z-Space 边 + G-Space 边 统一因果图                │
│  Discovery Engine [V2.0 新增] ← 检测并命名未知模式                       │
│  长期记忆子系统 (四层: Procedural/Working/Episodic/Semantic)              │
│       Episodes 双索引: Z-snapshot + G-snapshot + discovery 标记           │
│  编排模块 (7项能力, 含异步化)                                            │
│  TRL 成熟度评估器                                                       │
│  错误预算引擎 (Burn-Rate/4级告警)                                       │
│  自进化引擎 (安全包络/断路器/帕累托) — 双空间惊奇度驱动                   │
│  自反省引擎 (6维, 含接地健康度)                                          │
│  跨项目知识引擎 (KSL/隐私预算/联邦学习)                                  │
└────────────────────────────────┬─────────────────────────────────────────┘
                                │ EIP Protocol (gRPC + Kafka + Stream)
┌────────────────────────────────▼─────────────────────────────────────────┐
│              第三层: EIP Gateway + 第三方 Agent 适配层                     │
│              (RBAC/mTLS/DynamicPermission/REST↔gRPC Gateway)             │
└────────────────────────────────┬─────────────────────────────────────────┘
                                │
┌────────────────────────────────▼─────────────────────────────────────────┐
│          第四层: Agent 终端阵列 (三环分层)                                │
│  外环: AG-PA │ AG-PD │ AG-BI │ AG-PR (Phase 2, LOA 3-5)                │
│    中环: AG-SA │ AG-FD │ AG-AU (Phase 1, LOA 5-7)                      │
│      内环: AG-CD │ AG-CT │ AG-DO │ AG-ST │ AG-MA (Phase 0B, LOA 7-9)   │
│  + Third-party Agents via SDK (Apache 2.0)                              │
└──────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Brain Core 内部组件清单 (V2.0)

| # | 组件 | 职责 | 来源 | 对标需求 |
|---|------|------|------|---------|
| 1 | Z-Buffer Manager | 8层隐状态 + G-Space 状态读写/快照/版本 | V1 + V2 增强 | R01 |
| 2 | Perception Pipeline + AlignmentTrainer | 编码器管理/投影/跨模态对齐 | V1 | R01, R12 |
| 3 | **G-Space Engine** | **~80 命名指标采集/归一化/存储** | **V2.0 新增** | **GND** |
| 4 | **Bridging Functions (φ, ψ)** | **Z↔G 耦合/一致性损失** | **V2.0 新增** | **GND** |
| 5 | H-JEPA Predictor | 多时间尺度状态预测 **(V2.0: 双预测 Z+G)** | V1 + V2 增强 | R01 |
| 6 | Causal Graph Engine | 格兰杰因果图 **(V2.0: Z边+G边)** | V1 + V2 增强 | R01 |
| 7 | EBM Arbiter | 能量仲裁 **(V2.0: + Risk Decomposition)** | V1 + V2 增强 | R01 |
| 8 | **Discovery Engine** | **检测 Z-correct/G-unexplained 事件, 提取新指标** | **V2.0 新增** | **GND** |
| 9 | Long Memory Subsystem | 四层记忆 **(V2.0: 双索引 Episodes)** | V1.1 + V2 增强 | R01,R03,R06,R10 |
| 10 | Orchestration Module | 任务排序/交接/仲裁/里程碑/冲突 | V1 | R01 |
| 11 | TRL Evaluator | Z-Layer 成熟度自动评估/动态降权 | V1 | R01 |
| 12 | Evolution Engine | 安全包络/断路器/帕累托/LoRA **(V2.0: 双空间惊奇度)** | V1 + V2 增强 | R03 |
| 13 | Self-Reflection Engine | 定期内省 **(V2.0: 6维含接地健康度)** | V1 + V2 增强 | R06 |
| 14 | Knowledge Engine | KSL蒸馏/隐私预算/联邦学习 | V1 | R08 |
| 15 | Error Budget Engine | Burn-Rate/4级告警/自动降级 | V1 | R05 |
| 16 | Request Router | 请求分发/响应聚合 | V1 | R11 |

### 3.3 编排模块 — 与 V1.0.1 相同 (7项能力, 异步化, 多项目并发)

(完整内容见 V1.0.1 ARCH §3.3, 无变更)

### 3.4 多项目编排并发模型 — 与 V1.0.1 相同

(完整内容见 V1.0.1 ARCH §3.4, 无变更)

### 3.5 租户分片架构 — 与 V1.0.1 相同

(完整内容见 V1.0.1 ARCH §3.6, 无变更)

---

## 4. G-Space Engine (V2.0 核心新增)

### 4.1 设计目标

为 Z-Space 隐空间提供持续的"现实锚点"。每个 Z-Space 预测最终都可对照 G-Space 可观测量验证。G-Space 自身不做学习, 仅采集和归一化。

### 4.2 G-Space 指标矩阵

```python
class GSpaceEngine:
    """
    采集并维护 ~80 直接可测量工程指标/项目。
    无 ML, 纯观测和归一化。系统的"现实锚点"。
    """
    
    METRICS = {
        "code": {  # ~15 指标, 每次 commit 更新
            "complexity_avg": {"unit": "cyclomatic", "source": "tree-sitter"},
            "complexity_max": {"unit": "cyclomatic", "source": "tree-sitter"},
            "coupling_score": {"unit": "ratio [0,1]", "source": "import graph"},
            "cohesion_score": {"unit": "ratio [0,1]", "source": "module analysis"},
            "churn_rate_7d": {"unit": "lines/day", "source": "git log"},
            "duplication_pct": {"unit": "%", "source": "jscpd/PMD"},
            "file_count": {"unit": "count", "source": "git ls-files"},
            "loc_total": {"unit": "lines", "source": "cloc"},
            "loc_delta": {"unit": "lines", "source": "git diff"},
            "files_changed": {"unit": "count", "source": "git diff"},
            "hotspot_concentration": {"unit": "gini [0,1]", "source": "churn analysis"},
            "dependency_count": {"unit": "count", "source": "go.mod/requirements.txt"},
            "outdated_deps_pct": {"unit": "%", "source": "pip-audit/npm-audit"},
            "lint_violations": {"unit": "count", "source": "golangci-lint/eslint"},
            "todo_count": {"unit": "count", "source": "grep TODO"},
        },
        "test": {  # ~8 指标, 每次 CI run 更新
            "pass_rate": {"unit": "%", "source": "CI results"},
            "coverage_pct": {"unit": "%", "source": "Cobertura/JaCoCo"},
            "coverage_delta": {"unit": "pp", "source": "diff with previous"},
            "flakiness_rate": {"unit": "%", "source": "CI reruns"},
            "test_count": {"unit": "count", "source": "test framework"},
            "test_duration_s": {"unit": "seconds", "source": "CI timing"},
            "test_duration_delta": {"unit": "seconds", "source": "diff"},
            "failed_test_count": {"unit": "count", "source": "CI report"},
        },
        "ops": {  # ~11 指标, 每分钟从 Prometheus 更新
            "p50_latency_ms": {"unit": "ms", "source": "Prometheus"},
            "p99_latency_ms": {"unit": "ms", "source": "Prometheus"},
            "error_rate_pct": {"unit": "%", "source": "Prometheus"},
            "cpu_usage_pct": {"unit": "%", "source": "Prometheus"},
            "memory_usage_pct": {"unit": "%", "source": "Prometheus"},
            "disk_usage_pct": {"unit": "%", "source": "Prometheus"},
            "request_rate_rps": {"unit": "req/s", "source": "Prometheus"},
            "uptime_pct_30d": {"unit": "%", "source": "Prometheus"},
            "incident_count_7d": {"unit": "count", "source": "PagerDuty"},
            "mttr_minutes": {"unit": "minutes", "source": "incident tracker"},
            "deploy_count_7d": {"unit": "count", "source": "CI/CD"},
        },
        "process": {  # ~7 指标, 每天更新
            "pr_merge_time_hours": {"unit": "hours", "source": "GitHub API"},
            "review_turnaround_hours": {"unit": "hours", "source": "GitHub API"},
            "pr_size_lines_avg": {"unit": "lines", "source": "GitHub API"},
            "author_count_7d": {"unit": "count", "source": "git log"},
            "bus_factor": {"unit": "count", "source": "git fame"},
            "sprint_velocity": {"unit": "points", "source": "Jira/Linear"},
            "issue_close_rate_7d": {"unit": "count", "source": "issue tracker"},
        },
        "discovered": {}  # V2.0: 动态增长, Discovery Engine 添加新指标
    }
    
    def observe(self, project_id: str) -> GSpaceState:
        """采集当前 G-Space 状态。无 ML, 纯测量。"""
        state = {}
        for domain, metrics in self.METRICS.items():
            for name, spec in metrics.items():
                state[f"{domain}.{name}"] = self.collectors[spec["source"]].collect(
                    project_id, name)
        return GSpaceState(project_id=project_id, values=state, timestamp=now())
    
    def add_discovered_metric(self, metric: ProposedGSpaceMetric):
        """Discovery Engine 提出的新指标经人工审核后添加到 G-Space。"""
        self.METRICS["discovered"][metric.name] = {
            "unit": metric.unit, "source": metric.data_source,
            "discovered_by": "discovery_engine",
            "discovery_date": now(), "confidence": metric.confidence,
        }
```

### 4.3 G-Space 数据存储

| 存储层 | 技术 | 保留期 | 查询 SLO |
|--------|------|--------|---------|
| 实时 | PostgreSQL (time-series partitioned) | 30 天 | < 100ms |
| 历史 | PostgreSQL + Parquet (S3) | 1 年 | < 5s |
| 归档 | S3 (zstd) | 永久 | < 5min |

G-Space 与 Z-Buffer 在同一个 PostgreSQL 实例中, 不同 schema。

---

## 5. 桥接函数 (Bridging Functions) — V2.0 核心新增

### 5.1 设计目标

耦合 Z-Space (隐空间, 发现) 和 G-Space (可观测空间, 验证)。φ: Z→G 解码 (隐空间预测可观测量)。ψ: G→Z 约束 (可观测量约束隐空间)。一致性损失确保两个空间不漂移。

### 5.2 φ 解码器 (Z → G)

```python
class PhiDecoder(nn.Module):
    """φ: 从 Z-Space 状态预测 G-Space 指标。
    每个 Z-Layer 解码到对应领域的 G-Space 指标。"""
    
    def __init__(self, z_dim=2048):
        super().__init__()
        self.layer_decoders = nn.ModuleDict({
            "Z_impl": nn.Sequential(nn.Linear(z_dim, 512), nn.ReLU(), 
                                     nn.Linear(512, 15)),     # → code.* 指标
            "Z_quality": nn.Sequential(nn.Linear(z_dim, 256), nn.ReLU(),
                                       nn.Linear(256, 8)),    # → test.* 指标
            "Z_phys": nn.Sequential(nn.Linear(z_dim, 256), nn.ReLU(),
                                    nn.Linear(256, 11)),      # → ops.* 指标
            "Z_arch": nn.Sequential(nn.Linear(z_dim, 128), nn.ReLU(),
                                    nn.Linear(128, 5)),       # → coupling/cohesion
            "Z_logic": nn.Sequential(nn.Linear(z_dim, 128), nn.ReLU(),
                                     nn.Linear(128, 7)),      # → process.* 指标
        })
    
    def forward(self, z_buffer):
        g_predicted = {}
        for layer_name, decoder in self.layer_decoders.items():
            if layer_name in z_buffer:
                g_predicted[layer_name] = decoder(z_buffer[layer_name])
        return g_predicted
    
    def per_dimension_r2(self, g_predicted, g_actual):
        """逐维度 R² — 用于自反省的接地健康度指标。"""
        r2_scores = {}
        for dim_name in g_actual:
            pred = g_predicted.get(dim_name)
            if pred is not None:
                ss_res = ((g_actual[dim_name] - pred) ** 2).sum()
                ss_tot = ((g_actual[dim_name] - g_actual[dim_name].mean()) ** 2).sum()
                r2_scores[dim_name] = 1 - ss_res / (ss_tot + 1e-8)
        return r2_scores
```

### 5.3 ψ 锚定器 (G → Z)

```python
class PsiAnchor(nn.Module):
    """ψ: 从 G-Space 观测约束 Z-Space 状态。
    确保 Z-Space 不漂移到与可观测现实矛盾的区域。"""
    
    def __init__(self, g_dim=80, z_dim=2048):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(g_dim, 512), nn.ReLU(),
            nn.Linear(512, z_dim))
    
    def forward(self, g_state):
        return self.encoder(g_state)
```

### 5.4 一致性损失与 SIGReg 统一训练目标 [V2.0.1 重写]

```python
class UEWMTrainingObjective:
    """
    V2.0.1 统一训练目标 (融合 LeWorldModel SIGReg):
    
    L_UEWM = L_pred + λ_sig · SIGReg(Z) + λ_con · L_consistency
    
    Term 1: L_pred — 下一状态预测损失 (JEPA 核心, MSE)
    Term 2: SIGReg(Z) — 各向同性高斯正则化 (替换 VICReg, 来自 LeWM)
             使用 Cramér-Wold 定理: 随机投影 + Epps-Pulley 正态性检验
             单一超参数 λ_sig, 通过对分搜索 O(log n) 优化
    Term 3: L_consistency — G-Space 一致性损失 (UEWM V2.0 独创)
             φ(Z_pred) ≈ G_actual + ψ(G_actual) ≈ Z_pred
    
    总超参数: 2 个 (λ_sig, λ_con)
    对比 V2.0.0: 4+ 个 (VICReg 的 var/inv/cov + consistency)
    对比 PLDM: 7 个 loss terms
    """
    
    def compute_loss(self, z_pred, z_target, g_actual, z_batch):
        # Term 1: 预测损失
        l_pred = F.mse_loss(z_pred, z_target)
        
        # Term 2: SIGReg (替换 VICReg, 来自 LeWorldModel)
        l_sigreg = self.sigreg(z_batch)
        
        # Term 3: G-Space 一致性 (UEWM V2.0 独创)
        g_from_z = self.phi(z_pred)
        z_from_g = self.psi(g_actual)
        l_consistency = (
            0.5 * F.mse_loss(g_from_z, g_actual) +
            0.5 * F.cosine_embedding_loss(z_pred, z_from_g, 
                                           torch.ones(z_pred.size(0)))
        )
        
        return l_pred + self.lambda_sig * l_sigreg + self.lambda_con * l_consistency
    
    def sigreg(self, z_batch, M=128):
        """SIGReg: Sketched-Isotropic-Gaussian Regularizer (LeWorldModel)。
        
        使用 Cramér-Wold 定理: 高维分布匹配目标 iff 所有1D投影匹配。
        将隐向量投影到 M 个随机方向, 对每个 1D 投影执行 Epps-Pulley 正态性检验。
        """
        # 生成 M 个随机投影方向 (单位向量)
        directions = torch.randn(z_batch.size(1), M, device=z_batch.device)
        directions = F.normalize(directions, dim=0)
        
        # 投影: (batch, z_dim) × (z_dim, M) → (batch, M)
        projections = z_batch @ directions
        
        # 对每个投影计算 Epps-Pulley 正态性检验统计量
        ep_stats = []
        for i in range(M):
            proj_i = projections[:, i]
            # 标准化
            proj_i = (proj_i - proj_i.mean()) / (proj_i.std() + 1e-8)
            # Epps-Pulley 统计量 (简化版)
            n = proj_i.size(0)
            T = (1/n) * torch.sum(torch.exp(-proj_i**2 / 2)) - torch.sqrt(torch.tensor(2.0))
            ep_stats.append(T)
        
        return torch.stack(ep_stats).mean()
```

### 5.5 编码器投影头 [V2.0.1 新增, LeWorldModel 关键发现]

```python
class EncoderProjectionHead(nn.Module):
    """
    LeWM 关键发现: 编码器输出和 Z-Space 之间的投影头
    对训练稳定性至关重要。
    
    架构: 1-layer MLP + BatchNorm (per LeWM ablation)
    无此投影头 → 端到端训练不稳定
    有此投影头 → 训练平滑收敛
    
    额外收益: 投影头实现维度适配
    编码器输出 (如 CodeBERT 768-d) → Z-Space (256-d PoC / 2048-d 全量)
    扩展 Z-Space 维度时仅需重训练投影头, 不需重训练编码器。
    """
    
    def __init__(self, encoder_dim, z_dim):
        super().__init__()
        self.projection = nn.Sequential(
            nn.Linear(encoder_dim, z_dim),
            nn.BatchNorm1d(z_dim),
        )
    
    def forward(self, encoder_output):
        return self.projection(encoder_output)

# 每个编码器的投影头配置
PROJECTION_CONFIGS = {
    "Z_impl":    {"encoder_dim": 768,  "z_dim": 256},  # CodeBERT → 256-d
    "Z_quality": {"encoder_dim": 128,  "z_dim": 256},  # CI metrics → 256-d
    "Z_phys":    {"encoder_dim": 512,  "z_dim": 256},  # TimesFM → 256-d
    "Z_arch":    {"encoder_dim": 768,  "z_dim": 256},  # GraphSAGE+BERT → 256-d
    "Z_logic":   {"encoder_dim": 768,  "z_dim": 256},  # BERT/RoBERTa → 256-d
}

# Predictor 也使用 dropout (LeWM: dropout=0.1 对稳定性关键)
PREDICTOR_DROPOUT = 0.1
```

### 5.6 编码器端到端微调策略 [V2.0.1 新增]

```
Phase 0A PoC: 冻结预训练编码器 + 可训练投影头
  理由: 快速验证, 避免编码器训练不稳定
  SIGReg 仅作用于投影头输出 (Z-Space)

Phase 0B: 解冻编码器, 端到端微调
  理由: LeWM 证明 SIGReg 可防止端到端训练崩溃
  方法: 编码器 lr = 1e-5 (低), 投影头/预测器 lr = 1e-3 (高)
  监控: SIGReg loss 应快速下降后平稳 (per LeWM 训练曲线)
  如果训练不稳定: 重新冻结编码器, 仅训练投影头

Phase 1+: 完全端到端训练或自定义编码器从头训练
  取决于 Phase 0B 的端到端微调效果
```

### 5.7 训练集成

一致性损失 + SIGReg 在以下训练过程中加入:
- 编码器预训练: 编码后投影头输出经 SIGReg 正则化 + φ(Z) ≈ G 检查
- JEPA Predictor 训练: 预测 Z(t+1) 后检查 SIGReg(Z_batch) + φ(Z(t+1)) ≈ G(t+1)_actual
- LoRA 进化训练: 进化后检查 SIGReg 正态性未退化 + 一致性未退化
- 跨模态对齐: 对齐后检查 φ R² 未下降

权重: λ_sig = 0.1 (初始, 通过对分搜索优化), λ_con = 0.3。
Phase 0A PoC 期间可调, 进入 Phase 0B 后固定。

---

## 6. H-JEPA 分层预测引擎 (V2.0 双预测)

### 6.1 与 LLM/Transformer 的本质区别

```text
UEWM H-JEPA vs LLM/Transformer 架构对比:

  核心范式差异:
  ├── LLM/Transformer: 在 token 空间做自回归生成 (next-token prediction)
  ├── UEWM H-JEPA: 在隐空间做联合嵌入预测 (latent state prediction)
  └── 根本区别: UEWM 不生成文本/代码, 而是预测未来系统状态的向量表示

  Transformer-XL 在 UEWM 中的角色 (非 LLM 用法):
  ├── 用途: 仅作为 Predictor 内部的时序注意力组件
  │   不做 token 级自回归生成
  │   不做自然语言理解/生成
  │   仅对 2048-d Z 向量序列做时序依赖建模
  ├── 选型理由:
  │   T-GCN 捕获 Z-Layer 间的图结构 (因果拓扑)
  │   Transformer-XL 捕获同一 Z-Layer 的长距时序依赖 (segment-level recurrence)
  │   两者互补: 空间(图) + 时间(序列) = 时空预测
  ├── 替代方案评估:
  │   LSTM: 长距依赖弱, 且无法利用 GPU 并行 → 否决
  │   Mamba/S4: State-space model, 长序列高效但因果图交互弱 → Phase 2 候选
  │   Standard Transformer: 无 segment recurrence, 上下文窗口受限 → 否决
  │   Transformer-XL: segment-level recurrence + 相对位置编码 → 当选
  └── 关键约束: Transformer-XL 组件不接受原始文本输入, 仅接受 Z 向量序列
      输入: [Z_impl(t-n), ..., Z_impl(t)] (2048-d × n)
      输出: Z_impl(t+1) predicted (2048-d)
      与 LLM 的 [token_1, ..., token_n] → token_n+1 有本质区别

  与 Yann LeCun 发表的 JEPA 变体的关系:
  ├── I-JEPA (Image JEPA, 2023): 图像域, 预测图像 patch 的隐表示
  │   UEWM 借鉴: 联合嵌入 + 预测隐表示 (非像素/token)
  │   UEWM 差异: 多模态 (代码+文档+指标+市场), 非单模态图像
  ├── V-JEPA (Video JEPA, 2024): 视频域, 时空隐表示预测
  │   UEWM 借鉴: 多时间尺度层次化预测
  │   UEWM 差异: 工程领域的 8 层异构 Z-Space, 非视频帧序列
  └── UEWM 创新点 (超越已发表 JEPA):
      (1) 层间因果图 (Granger causality) — I/V-JEPA 无因果推理
      (2) EBM 能量仲裁 + 安全包络 — I/V-JEPA 无决策层
      (3) 惊奇度驱动自进化 — I/V-JEPA 无在线学习
      (4) 多租户隐私隔离 (KSL) — I/V-JEPA 无多租户
      (5) 长期记忆 (Episodic+Semantic) — I/V-JEPA 无记忆系统
```

### 6.2 JEPA 核心 (V2.0 增强: 双预测)

Context Encoder → Target Encoder (EMA) → Predictor (T-GCN + Transformer-XL)。预测 Z 向量而非 token。微观/中观/宏观三层计算。

**V2.0 增强:** Predictor 同时输出:
- Z(t+1) 预测: 未来隐空间状态 (发现模式)
- G(t+1) 预测: 未来可观测指标 (验证模式)

```python
class DualPredictorHead(nn.Module):
    """V2.0: JEPA Predictor 同时输出 Z 和 G 预测。"""
    
    def __init__(self, z_dim=2048, g_dim=80):
        super().__init__()
        self.z_head = nn.Linear(z_dim, z_dim)      # Z(t+1) 预测
        self.g_head = nn.Sequential(                 # G(t+1) 预测
            nn.Linear(z_dim, 512), nn.ReLU(),
            nn.Linear(512, g_dim))
    
    def forward(self, predictor_output):
        return {
            "z_predicted": self.z_head(predictor_output),
            "g_predicted": self.g_head(predictor_output),
        }
```

### 6.3 POMDP 不确定性建模

Z^(l) ~ N(μ^(l), Σ^(l))。低 tr(Σ)→认知充分, 高 tr(Σ)→触发信息获取。

#### 信息获取触发机制

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

### 6.4 跨模态对齐训练

AlignmentTrainer 作为 Perception Pipeline 子模块。三阶段:

Stage 1 域内对比(InfoNCE, ARI≥0.3): 同一项目不同时间点的 Z_impl 应比不同项目的更近。
Stage 2 相邻层对齐(跨模态对比+因果预测, MSE改善>30%): 同一项目同一时间点的 Z_impl 和 Z_quality 应比随机配对更近。
Stage 3 全局联合(VICReg正则, 因果图有效率>80%): 所有层形成统一语义空间。

每阶段有收敛准则和中止条件。仅使用训练GPU池(NFR-9)。Phase 0 时间线: Week 1-4 Stage 1(3层), Week 5-8 Stage 2(3对), Week 9+ MVLS验证。
（V2.0 更新：增加一致性损失检查，要求对齐后 φ R² 不可下降）

### 6.5 JEPA Predictor 验证协议

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
*(V2.0 更新：增加 G-Space 预测精度作为额外验证维度)*

---

## 7. 隐空间分层设计 (Z-Layers)

### 7.1 8 层 Z-Layer 定义

8 层: Z_market(周/月) → Z_val(季度) → Z_biz(周) → Z_logic(天) → Z_arch(天) → Z_impl(小时) → Z_quality(小时) → Z_phys(分钟)。每层输出 2048-d 向量。

动态因果拓扑 G=(V,E)，格兰杰因果检验 (p<0.05) 自动发现因果边。主链: Z_market→Z_val→Z_biz→Z_logic→Z_arch→Z_impl→Z_quality, Z_impl→Z_phys。反馈: Z_phys→Z_arch, Z_quality→Z_logic, Z_phys→Z_val, Z_quality→Z_val。

**[V2.0.1] 自适应隐维度策略 (LeWorldModel 启示):**

```
LeWM 以 192-d 实现探测 r > 0.99 — 证明高维不必要。

自适应隐维度:
  Phase 0A PoC:  256-d per Z-Layer
    理由: LeWM 192-d 足够物理域; 工程域可能需略多
    收益: 训练速度 8×, GPU 显存 8×, 检索速度 8×
    
  Phase 0B: 基于探测饱和度测试决定是否扩展
    如果 probing R² 在 256-d 已饱和 → 保持 256-d
    如果 probing R² 仍在提升 → 扩展到 512-d
    
  Phase 1+: 按需扩展 (512-d 到 2048-d)
    扩展依据: 逐维度 probing R² + 信息论分析
    每次扩展需证明: 新维度的边际 R² 提升 > 0.01

  向后兼容: 投影头负责维度适配
    编码器输出维度固定 (如 CodeBERT 768-d)
    投影头 → Z-Space dim (256/512/1024/2048)
    扩展时仅重训练投影头, 不需重训练编码器
```

### 7.2 Z-Layer 与 G-Space 的对应关系 (V2.0 新增)

| Z-Layer | G-Space 域 | 桥接方向 | 示例 |
|---------|-----------|---------|------|
| Z_impl | code.* | φ: Z_impl → complexity, churn, loc_delta | 代码变更 → 复杂度变化 |
| Z_quality | test.* | φ: Z_quality → pass_rate, coverage, duration | 质量状态 → 测试指标 |
| Z_phys | ops.* | φ: Z_phys → p99_latency, error_rate, cpu | 物理状态 → 运行指标 |
| Z_arch | code.coupling, code.cohesion | φ: Z_arch → coupling, dependency_count | 架构状态 → 耦合度 |
| Z_logic | process.* | φ: Z_logic → pr_merge_time, velocity | 逻辑状态 → 过程指标 |
| Z_biz/Z_val/Z_market | (Phase 2+) | 需要商业数据源 | Phase 2+ |

### 7.3 TRL 成熟度评估 (V2.0 增强)

```
TRL-0 (概念): 编码器架构已确定，但无训练数据，隐空间无意义
TRL-1 (原型): 编码器可产出向量，但语义聚类 ARI < 0.3
TRL-2 (验证): 语义聚类 ARI ≥ 0.3，但跨层因果关系未验证
TRL-3 (集成): 单向因果关系可检测 (本层→邻居层 格兰杰 p<0.05)
TRL-4 (成熟): 双向因果传导可靠，预测 MSE < 0.1，可支撑 Agent 决策
TRL-5 (自优化): 自进化闭环验证通过，惊奇度收敛
```

TRL↔系统行为: Agent自主度(TRL<3→不可自主)、EBM权重(TRL<3→0.1x)、因果回溯(TRL<3→单向)、进化训练(TRL<2→仅数据收集)、人工介入(TRL<3→必须审批)。评估频率: 每日02:00 UTC + 进化后立即 + 冷启动每6h。

```
TRL 增强评估 (V2.0):
  TRL 原始标准 (ARI, 因果检验) 不变
  新增辅助指标: φ R² (Z→G 解码精度)
    TRL < 2 时: φ R² 不参与评估 (数据不足)
    TRL ≥ 2 时: φ R² ≥ 0.1 为附加条件 (Z-Space 须有可观测意义)
    TRL ≥ 4 时: φ R² ≥ 0.3 为附加条件 (Z-Space 高精度解码)
```

### 7.4 MVLS 最小可行隐空间 + G-Space

MVLS: Z_impl + Z_quality + Z_phys + 对应 G-Space (code.* + test.* + ops.*)。
验证标准: V1.0.1 原始标准 + φ R² ≥ 0.2 for MVLS 三层。

---

## 8. EBM 能量仲裁引擎 (V2.0 增强)

### 8.1 全局能量函数

E_total = Σ w_l^eff · Ẽ_l + λ_cross · E_cross + λ_safe · E_safety。w_l^eff = w_l × TRL_weight(l)。TRL<3→权重0或0.1。

### 8.1.1 量纲/风险映射/沙盒预演/权重自动调优

分位数归一化→[0,1]。LOW[0,0.3)/MEDIUM[0.3,0.5)/HIGH[0.5,0.7)/CRITICAL[0.7,1.0]。多方案 GPU batch 并行模拟，比较轨迹稳定性。Meta-learning 每周/每100次决策自动调优权重。

### 8.2 V2.0 增强: Energy + Risk Decomposition

```python
class EnhancedEBMArbiter:
    """V2.0: EBM 输出 energy score (发现信号) + risk decomposition (可解释)。"""
    
    def evaluate(self, candidates, context, z_buffer, g_state, memory_ctx):
        results = []
        for candidate in candidates:
            # 1. 隐空间评估 (UEWM 原始 — 发现引擎)
            z_trajectory = self.jepa.sandbox_predict(candidate, steps=3)
            energy = self.compute_energy(z_trajectory)
            
            # 2. 可观测预测 (V2.0 — 验证引擎)
            g_predicted = self.phi.decode(z_trajectory[-1])
            
            # 3. 风险分解 (命名组件)
            risk = RiskDecomposition(
                test_risk=self.assess("test.coverage_delta", g_predicted, g_state, -2.0),
                perf_risk=self.assess("ops.p99_latency_ms", g_predicted, g_state, 1.2),
                complexity_risk=self.assess("code.complexity_avg", g_predicted, g_state, 1.15),
                cascade_risk=self.estimate_cascade(z_trajectory, context),
            )
            
            # 4. 未命名风险 = energy 中 G-Space 无法解释的部分
            explained = sum(r.contribution for r in risk.components)
            unnamed_risk = max(0, energy - explained)
            risk.unnamed_risk = unnamed_risk
            # unnamed_risk 高 → Discovery Engine 关注
            
            # 5. 记忆影响 (V1.0.1 保留)
            if memory_ctx:
                risk.apply_memory(memory_ctx)
            
            results.append(EvaluationResult(
                candidate_id=candidate.id,
                energy=energy,
                risk=risk,
                unnamed_risk_pct=unnamed_risk / energy if energy > 0 else 0,
                explanation=risk.generate_explanation(),
                memory_influence=memory_ctx,
            ))
        
        results.sort(key=lambda r: r.energy)
        return results
```

### 8.3 EBM 校准计划

**校准数据集:** 200 对成对比较样本 (5类决策×各40-50对), 3-5位专家盲评, Dawid-Skene 聚合, 最低一致率 60%。

**校准流程:** Step 1(Week 1-3): 构建校准集 → Step 2(Week 4): 基线 τ 测量 (预期~0.2-0.3) → Step 3(Week 5-6): Bayesian 优化权重 (Optuna+交叉验证) → Step 4(Week 7): 验证 τ≥0.5 on 30% held-out → Step 5(Phase 1+): 每季度补充50样本+重评估。

校准数据版本: DVC 管理, `datasets/calibration/v{X}/calibration_pairs.parquet`。

---

## 9. Discovery Engine (V2.0 核心新增)

### 9.1 设计目标

检测 Z-Space 正确预测但 G-Space 指标无法解释的事件。这是系统"生成新想法"的机制。

### 9.2 双空间惊奇度矩阵

```
S_z(t) = ||Z_observed - Z_predicted||²    (隐空间惊奇度)
S_g(t) = ||G_observed - G_predicted||²    (可观测惊奇度)

解释矩阵:
┌────────────────────────────────────────────────────────────────┐
│ S_z HIGH + S_g HIGH → 真实惊奇 (世界发生了变化)                  │
│   动作: 创建 INCIDENT Episode, 触发进化                         │
│                                                                │
│ S_z HIGH + S_g LOW  → Z-Space 噪声 (隐空间漂移)                 │
│   动作: 标记编码器需重训练, 不触发进化                            │
│                                                                │
│ S_z LOW  + S_g HIGH → 接地缺口 (需要新指标)                      │
│   动作: Discovery Engine 介入 — Z 正确但 G 不完整                │
│                                                                │
│ S_z LOW  + S_g LOW  → 正常 (预测准确)                            │
│   动作: 无, 记录为成功预测                                       │
└────────────────────────────────────────────────────────────────┘
```

### 9.3 Discovery Engine 实现

```python
class DiscoveryEngine:
    """检测 Z-Space 发现 G-Space 无法解释的模式。"""
    
    def analyze(self, z_pred, g_pred, g_actual, energy):
        z_correct = self.was_z_correct(z_pred, g_actual)  # via φ
        g_correct = self.was_g_correct(g_pred, g_actual)
        
        if z_correct and not g_correct:
            return self.handle_discovery(z_pred, g_actual, energy)
        elif not z_correct and g_correct:
            return self.handle_z_noise(z_pred, g_actual)
        elif not z_correct and not g_correct:
            return self.handle_blind_spot(z_pred, g_pred, g_actual)
        return DiscoveryResult.NORMAL
    
    def handle_discovery(self, z_pred, g_actual, energy):
        """最激动人心的情况: Z 预测正确但 G 指标无法解释。"""
        episode = Episode(
            trigger_type="DISCOVERY", z_snapshot=z_pred,
            g_snapshot=g_actual, importance_score=1.0)
        self.memory.store_episode(episode)
        
        # 归因: 哪些 Z 维度贡献最大?
        attribution = self.attribute_z_to_outcome(z_pred, g_actual)
        
        # 查找类似发现
        similar = self.memory.recall(z_snapshot=z_pred, 
                                     filter={"trigger_type": "DISCOVERY"}, max=20)
        
        if len(similar) >= 3:
            pattern = self.extract_pattern(similar, attribution.top_k(10))
            proposed_metric = ProposedGSpaceMetric(
                name=pattern.suggested_name,
                formula=pattern.formula,
                data_source=pattern.data_sources,
                expected_correlate=pattern.predicted_outcome,
                confidence=pattern.confidence,
                requires_human_review=True)
            return DiscoveryResult("NEW_PATTERN", proposed_metric=proposed_metric)
        
        return DiscoveryResult("POTENTIAL_DISCOVERY", evidence_count=len(similar))
```

### 9.4 G-Space 动态增长

```
Day 1:     G-Space ≈ 80 人工定义指标
Month 3:   Discovery Engine 提出 5 新指标, 2 经人工审核通过
Month 6:   G-Space ≈ 90 指标 (10 由模型发现)
Year 1:    G-Space ≈ 120 指标 (40 由模型发现)
Year 3:    G-Space ≈ 200+ 指标, 许多是人类从未想到要测量的

闭环: Z-Space 发现 → Discovery Engine 识别 → Semantic Memory 存储 →
      人工审核批准 → G-Space 新增指标 → 未来 G-Space 预测改善 →
      Z-Space 释放去发现下一个未命名模式
```

---

## 10. 长期记忆子系统 (V2.0 双索引增强)

### 10.1 四层记忆模型

```text
Layer 0: 程序记忆 (Procedural Memory) — LoRA 权重
  存储: 通过 LoRA 增量训练编码的隐性技能和决策模式
  格式: LoRA 权重矩阵 (ΔW = BA, rank r)
  机制: 自进化引擎通过惊奇度/漂移/反馈驱动 LoRA 更新
  与其他层的关系:
    ├── 接收 Layer 2 (Episodic) 的经验作为训练数据
    ├── 接收 Layer 3 (Semantic) 的 ANTI_PATTERN Fact 作为定向训练目标
    ├── 输出: 改善 Layer 1 (Working) 的预测精度 (降低惊奇度)
    └── 版本化: MLflow 管理, 可回滚, 与 Z-Buffer 快照关联
  容量: 每项目独立 LoRA (rank 8-64), 约 2-16 MB/层/项目
  索引: MLflow run_id + layer_name + project_id
  用途: "系统已学会: 当 Z_impl 变化超过 0.5 时, Z_quality 通常在 24h 内下降"

Layer 1: 工作记忆 (Working Memory) — Z-Buffer
  存储当前 Z-Layer 向量, 每次观测覆写

Layer 2: 情景记忆 (Episodic Memory)
  存储: 具体事件 (决策/事故/进化/人工干预) 及其 Z-Layer 快照和结果
  格式: Episode = {触发, Z快照, 决策, 结果, 能量, 惊奇度, 时间戳, 项目}
  容量: 每项目 1K(Phase 0) → 5K(Phase 1) → 10K(Phase 2+)
  索引: 时间 + Z向量相似度(pgvector ANN) + 因果标签 + 结果标签
  用途: "上次出现类似 Z_impl 模式时, 部署导致了 P99 飙升"

Layer 3: 语义记忆 (Semantic Memory)
  存储: 从多个 Episode 提取的稳定事实 (因果/模式/反模式/偏好)
  格式: Fact = {主题, 关系, 对象, 置信度, 有效期, 来源Episode}
  容量: 每项目 ~200(Phase 0) → ~1000(Phase 2+)
  索引: Neo4j 知识图谱 (Entity-Relation-Entity)
  用途: "此项目的代码复杂度上升通常在 72h 内导致测试覆盖率下降"

四层记忆交互闭环:
  观测 → Layer 1 (Z-Buffer 更新) → 惊奇度计算
  惊奇度 > θ → Layer 2 (创建 Episode)
  ≥3 一致 Episode → Layer 3 (提取 Fact)
  ANTI_PATTERN Fact → Layer 0 (定向 LoRA 训练)
  LoRA 更新 → Layer 1 (预测精度提升, 惊奇度下降)
  → 闭环完成
```

### 10.2 V2.0 Episode 增强: 双索引

```python
class EnhancedEpisode(Episode):
    """V2.0: Episode 同时包含 Z-snapshot 和 G-snapshot。"""
    
    # V1.0.1 保留字段
    z_snapshot: Dict[str, bytes]
    trigger_type: str  # DECISION/INCIDENT/EVOLUTION/HUMAN_INTERVENTION/REFLECTION
    
    # V2.0 新增字段
    g_snapshot: Dict[str, float]        # 决策时刻 G-Space 测量值
    g_predicted: Dict[str, float]       # 模型预测的 G-Space (事后填充)
    g_actual: Dict[str, float]          # 实际发生的 G-Space (事后填充)
    prediction_accuracy: float          # ||g_predicted - g_actual|| (事后计算)
    was_discovery: bool                 # Discovery Engine 是否标记
    discovery_pattern_id: Optional[str] # 关联的已提取模式
    surprise_category: str             # REAL/Z_NOISE/GROUNDING_GAP/NORMAL
```

### 10.3 记忆检索 (V2.0 增强: 5种检索模式)

(V1.0.1 的 4 种 + 新增第 5 种)

1. Z-Layer 向量相似度 (pgvector ANN)
2. 因果图遍历 (Neo4j 2跳)
3. 文本语义检索
4. Project Profile 注入
5. **G-Space 条件检索 (V2.0):** "上次 test.coverage_delta < -5% 时发生了什么?"

### 10.4-10.8 其他记忆子节

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

## 11. 自反省引擎 (V2.0: 6 维)

### 11.1 六维自反省

| 维度 | 来源 | 健康标准 |
|------|------|---------|
| 1. 预测一致性 | Z-Space | 1步 MSE < 0.15, 3步 MSE < 0.3 |
| 2. 因果图健康 | Causal Graph | 有效边率 > 80% |
| 3. 跨层对齐 | AlignmentTrainer | ARI > 0.3 |
| 4. 决策多样性 | EBM | Shannon 熵 ≥ 0.6 |
| 5. 盲区检测 | POMDP | 高 Σ 区域占比 < 20% |
| **6. 接地健康度 (V2.0)** | **Bridging** | **见下** |

### 11.2 接地健康度 (Grounding Health) — V2.0 新增

```
接地健康度子指标:
  φ 精度: Z→G 解码 R² (目标: 均值 > 0.3 across G-Space 维度)
  ψ 一致性: G→Z 约束余弦相似度 (目标: > 0.5)
  发现率: Z 正确 + G 无法解释的比例 (健康: 5-15%)
    太低 (<2%): Z-Space 可能冗余 (不一定坏)
    太高 (>30%): Z-Space 可能漂移, 增加 ψ 权重
  G-Space 覆盖率: 指标采集成功率 (目标: > 95%)
  逐维度健康: R² < 0.05 的 Z 维度 → 标记为需修剪或重训练
```

---

## 12. GPU 优化策略

### 13.1 设计目标

在有限 GPU 资源下最大化训练效率和推理吞吐, 通过混合精度、梯度检查点、模型量化、算子融合和智能调度减少 GPU 显存占用和计算时间。

### 13.2 混合精度训练策略

```python
class MixedPrecisionPolicy:
    """
    全局混合精度策略: 训练 BF16, 推理 FP16/INT8, 梯度累积 FP32。
    目标: 训练显存减少 ~40%, 推理延迟降低 ~30%。
    """
    
    TRAINING_PRECISION = {
        "forward_pass": "bfloat16",      # BF16: 动态范围大, 不易溢出
        "backward_pass": "bfloat16",
        "gradient_accumulation": "float32",  # 梯度在 FP32 下累积 (防止精度丢失)
        "optimizer_states": "float32",       # Adam 状态保持 FP32
        "loss_scaling": "dynamic",           # PyTorch GradScaler (BF16 模式下可选)
    }
    
    INFERENCE_PRECISION = {
        "brain_core_jepa": "float16",     # JEPA Predictor 推理
        "brain_core_ebm": "float16",      # EBM 能量计算
        "encoder_forward": "float16",     # 编码器前向推理
        "memory_retrieval": "float32",    # pgvector 检索保持 FP32 精度
    }
    
    QUANTIZATION_PIPELINE = {
        "phase_0": "FP16 推理 (基线)",
        "phase_1": "INT8 动态量化 (torch.quantization.quantize_dynamic)",
        "phase_2": "INT8 静态量化 (校准数据集 1000 样本)",
        "phase_3": "INT4 GPTQ/AWQ (仅 LLM 适配器内的本地模型)",
    }
```

### 13.3 梯度检查点 (Gradient Checkpointing)

```python
class GradientCheckpointConfig:
    """
    对大型组件启用梯度检查点: 用计算换显存。
    预期效果: 显存减少 60-70%, 训练时间增加 ~20%。
    """
    
    CHECKPOINT_TARGETS = {
        "jepa_predictor": {
            "enabled": True,
            "strategy": "every_2_layers",   # 每 2 个 Transformer-XL 层做一次检查点
            "memory_saving": "~65%",
            "compute_overhead": "~20%",
        },
        "context_encoder": {
            "enabled": True,
            "strategy": "every_3_layers",   # 编码器较浅, 每 3 层
            "memory_saving": "~50%",
            "compute_overhead": "~15%",
        },
        "alignment_trainer": {
            "enabled": True,
            "strategy": "full_recompute",   # 对齐训练批量大, 全量重计算
            "memory_saving": "~70%",
            "compute_overhead": "~25%",
        },
        "evolution_lora": {
            "enabled": False,               # LoRA 参数少, 不需要
            "reason": "LoRA rank 8-64, 参数量 < 1M, 显存占用可忽略",
        },
    }
    
    # PyTorch 实现
    IMPLEMENTATION = """
    from torch.utils.checkpoint import checkpoint_sequential
    
    class CheckpointedJEPAPredictor(nn.Module):
        def forward(self, z_sequence):
            # 将 Transformer-XL 层分组, 每组做检查点
            segments = [self.layers[i:i+2] for i in range(0, len(self.layers), 2)]
            x = z_sequence
            for segment in segments:
                x = checkpoint_sequential(segment, 1, x, use_reentrant=False)
            return x
    """
```

### 13.4 DeepSpeed ZeRO 配置

```json
{
  "description": "DeepSpeed ZeRO 配置 — 按训练阶段选择 ZeRO Stage",
  "phase_0_mvls_training": {
    "stage": 1,
    "rationale": "Phase 0 单 GPU 训练为主, ZeRO-1 分割优化器状态即可",
    "config": {
      "zero_optimization": {
        "stage": 1,
        "allgather_partitions": true,
        "reduce_scatter": true,
        "overlap_comm": true
      },
      "bf16": { "enabled": true },
      "gradient_clipping": 1.0
    }
  },
  "phase_1_alignment_training": {
    "stage": 2,
    "rationale": "跨模态对齐需更大 batch, ZeRO-2 额外分割梯度",
    "config": {
      "zero_optimization": {
        "stage": 2,
        "contiguous_gradients": true,
        "overlap_comm": true,
        "reduce_bucket_size": 50000000
      },
      "bf16": { "enabled": true },
      "gradient_accumulation_steps": 4
    }
  },
  "phase_2_full_training": {
    "stage": 3,
    "rationale": "全 8 层联合训练, ZeRO-3 分割模型参数",
    "config": {
      "zero_optimization": {
        "stage": 3,
        "offload_param": { "device": "cpu", "pin_memory": true },
        "offload_optimizer": { "device": "cpu", "pin_memory": true },
        "overlap_comm": true,
        "sub_group_size": 1000000000
      },
      "bf16": { "enabled": true },
      "gradient_accumulation_steps": 8
    }
  }
}
```

### 13.5 推理优化 (TensorRT / vLLM)

```
推理优化管线:

  JEPA Predictor 推理优化:
  ├── TensorRT 转换: torch.export → ONNX → TensorRT engine
  │   优化: 算子融合 (LayerNorm+Linear, Attention+Softmax)
  │         动态 batch 大小 (1-32)
  │         FP16 精度
  │   预期: 推理延迟降低 40-60%, 吞吐提升 2-3x
  ├── CUDA Graph: 对固定 shape 推理路径启用 CUDA Graph 捕获
  │   适用: PREDICT 请求 (固定 8 层 × 2048-d 输入)
  │   预期: 推理延迟降低 10-20% (减少 kernel launch 开销)
  └── Flash Attention v2: 替换标准注意力
      适用: Transformer-XL 自注意力层
      预期: 显存 O(N²) → O(N), 速度提升 2-4x

  EBM 沙盒预演优化:
  ├── 批量预演: 多候选方案 GPU batch 并行 (已有, ENG §2.3)
  ├── 早停: 如果某候选能量已超过当前最优 2x, 提前终止该轨迹
  └── 缓存: 相同 Z-Buffer 状态下的预演结果缓存 30s

  LLM 本地模型推理优化 (Agent 执行引擎):
  ├── vLLM 部署: PagedAttention + continuous batching
  │   配置: max_model_len=4096, gpu_memory_utilization=0.85
  │   适用: CodeLlama-7B 本地降级模型
  ├── 量化: GPTQ 4-bit (仅本地 LLM, 非 JEPA)
  └── 动态批处理: 合并多 Agent 的 LLM 请求
```

### 13.6 GPU 显存预算 (Per-Component)

| 组件 | Profile-S (2×A100 80GB) | Profile-M (4×A100) | Phase | 备注 |
|------|------------------------|---------------------|-------|------|
| JEPA Predictor (FP16) | 8 GB | 8 GB | 0 | 固定, 不随项目数增长 |
| 8× Encoders (FP16) | 12 GB | 12 GB | 0-2 | Phase 0 仅 3 编码器 ~5GB |
| EBM Arbiter | 2 GB | 2 GB | 0 | 轻量 MLP |
| Z-Buffer (活跃项目) | 2 GB | 10 GB | 0-2 | ~200MB/项目 |
| AlignmentTrainer (训练时) | 16 GB | 16 GB | 0 | 仅训练 GPU 池, 梯度检查点后 |
| LoRA Evolution (训练时) | 4 GB | 4 GB | 0 | rank 8-64, 非常轻量 |
| CodeLlama-7B (INT4, 可选) | 4 GB | 4 GB | 1+ | 本地 LLM 降级 |
| Memory Retrieval (pgvector) | 1 GB | 2 GB | 0 | 向量索引缓存 |
| **推理 GPU 总计** | **~25 GB / GPU** | **~25 GB / GPU** | | **留 55 GB 余量** |
| **训练 GPU 总计** | **~36 GB / GPU** | **~36 GB / GPU** | | **留 44 GB 余量** |

### 13.7 GPU 利用率监控与基准测试

```
GPU Profiling 方法论:

  工具: nvidia-smi + PyTorch Profiler + Nsight Systems

  关键指标:
    gpu_utilization_pct          目标: 推理 > 60%, 训练 > 80%
    gpu_memory_used_bytes        目标: < 85% 峰值 (留 headroom)
    gpu_memory_high_water_mark   每组件记录最大显存
    sm_efficiency_pct            Streaming Multiprocessor 效率
    tensor_core_utilization_pct  Tensor Core 利用率 (BF16/FP16 时)

  基准测试计划:
    Phase 0 Week 2: 单编码器 GPU profiling (显存+延迟)
    Phase 0 Week 6: MVLS 三编码器联合 profiling
    Phase 0 Week 10: JEPA Predictor + EBM 推理 profiling
    Phase 1 Month 1: TensorRT 转换前后对比
    每季度: 全系统 GPU 基准回归测试

  Prometheus Exporter:
    uewm_gpu_memory_used_bytes{component, device}
    uewm_gpu_utilization_pct{device}
    uewm_inference_throughput_rps{component}
    uewm_training_throughput_samples_per_sec{component}

  告警规则:
    GPU 显存 > 85%: warning → 触发垃圾回收
    GPU 显存 > 95%: critical → 暂停训练, 仅保留推理
    GPU 利用率 < 20% 持续 30min: warning → 资源浪费
```

### 13.8 跨平台 GPU 优化 (Mac M-series / RTX 3060 / A100)

```
开发环境 GPU 策略 (对标 UEWM-PREP-015):

  Mac M5 Max (主开发机):
    后端: MPS (Metal Performance Shaders)
    精度: FP32 (MPS 对 BF16 支持有限)
    用途: 功能开发 + 单元测试 + 小批量验证
    限制: 无 CUDA, 无 TensorRT, 无 DeepSpeed
    策略: get_device() 抽象层自动选择 MPS

  RTX 3060 (CUDA 验证机, 12GB VRAM):
    精度: FP16 (无 BF16 原生支持)
    用途: CUDA 功能验证 + 小规模训练验证
    限制: 12GB VRAM, 需严格显存预算
    策略:
      梯度检查点: 强制全部启用
      batch size: 自动缩小到 RTX 3060 适配
      LoRA rank: 限制 ≤ 16

  Cloud A100 (训练/CI):
    精度: BF16 训练 + FP16 推理
    用途: 全量训练 + 对齐 + 负载测试
    策略: DeepSpeed ZeRO + Flash Attention + TensorRT

  get_device() 增强:
    除设备选择外, 返回设备能力 (DeviceCapabilities):
      max_vram, supports_bf16, supports_flash_attention,
      supports_tensorrt, recommended_batch_size, precision_policy
```

---

## 13. 第三方 Agent 适配层架构

### 14.1 设计目标

允许第三方开发者构建自定义 Agent, 接入 UEWM Brain Core 的世界模型能力, 同时保证安全隔离和资源公平。

### 14.2 适配层架构

```
第三方 Agent 接入架构:

  ┌───────────────────────────────────────────────────────┐
  │                 Third-party Agents                     │
  │  Custom Agent A │ Custom Agent B │ Custom Agent C      │
  │  (Python SDK)     (REST Adapter)   (gRPC native)      │
  └───────────┬──────────┬──────────────┬─────────────────┘
              │          │              │
  ┌───────────▼──────────▼──────────────▼─────────────────┐
  │             Third-party Adaptation Layer               │
  │  ┌──────────────────────────────────────────────────┐ │
  │  │  REST↔gRPC Gateway (协议转换)                     │ │
  │  │  Agent Registry (注册/发现/健康检查)               │ │
  │  │  Capability Negotiator (能力协商)                  │ │
  │  │  Sandbox Enforcer (资源隔离/配额)                  │ │
  │  │  Schema Validator (载荷校验)                       │ │
  │  └──────────────────────────────────────────────────┘ │
  └───────────────────────┬───────────────────────────────┘
                          │
  ┌───────────────────────▼───────────────────────────────┐
  │              EIP Gateway (RBAC / mTLS)                  │
  │              (现有, 增加 THIRD_PARTY 角色)               │
  └───────────────────────┬───────────────────────────────┘
                          │
  ┌───────────────────────▼───────────────────────────────┐
  │                    Brain Core                           │
  └─────────────────────────────────────────────────────────┘
```

### 14.3 Agent 注册协议

```python
class AgentRegistration:
    """第三方 Agent 注册到 UEWM 系统的协议。"""
    
    class RegistrationRequest:
        agent_type: str          # 自定义类型名 (e.g., "custom-nlp-reviewer")
        agent_version: str       # 语义版本号
        supported_verbs: List[str]  # 支持的 EIP 动词 ["PREDICT", "EVALUATE", "RECALL"]
        z_layer_read: List[str]  # 需要读取的 Z-Layer ["Z_impl", "Z_quality"]
        z_layer_write: List[str] # 需要写入的 Z-Layer (通过 REPORT_STATUS)
        ring_classification: str # "inner" / "middle" / "outer" (自声明, 系统验证)
        required_loa_range: Tuple[int, int]  # 期望 LOA 范围 (e.g., (3, 6))
        health_check_endpoint: str  # 健康检查 URL
        metadata: Dict[str, str]    # 描述、联系人、文档链接
    
    class RegistrationResponse:
        agent_id: str            # 系统分配的唯一 ID: "EXT-{type}-{uuid}"
        api_key: str             # Vault 生成的 API Key (用于 mTLS 证书申请)
        granted_verbs: List[str] # 实际授权的动词 (可能少于请求)
        granted_z_layers: List[str]  # 实际授权的 Z-Layer
        assigned_loa: int        # 初始 LOA (通常 = required_loa_range[0])
        resource_quota: ResourceQuota  # 分配的资源配额
        sdk_config: SDKConfig    # 推荐的超时/重试/熔断配置
    
    # 注册生命周期
    LIFECYCLE = """
      PENDING → (审核通过) → REGISTERED → (健康检查OK) → ACTIVE
      ACTIVE → (健康检查连续失败) → SUSPENDED → (恢复) → ACTIVE
      ACTIVE → (手动注销/违规) → DEREGISTERED
      
      审核要求:
        inner ring 第三方 Agent: SECURITY + ARCHITECT 双人审核
        middle ring: ARCHITECT 审核
        outer ring: 自动审核 (Schema 验证通过即可)
    """
```

### 14.4 能力协商

```python
class CapabilityNegotiation:
    """
    第三方 Agent 声明能力, 系统根据能力决定授权范围。
    """
    
    class AgentCapability:
        # EIP 动词能力
        can_predict: bool = False     # 需要 Z-Layer 读权限
        can_evaluate: bool = False    # 需要 EBM 调用权限
        can_report_status: bool = True  # 所有 Agent 必须支持
        can_submit_artifact: bool = False
        can_recall: bool = False      # 需要 Long Memory 读权限
        can_orchestrate: bool = False  # 通常不授权第三方
        
        # Z-Layer 能力
        encoders_provided: List[str] = []  # 自带编码器 (扩展 Z-Space)
        custom_z_layers: List[str] = []    # 自定义 Z-Layer (Phase 3+)
    
    # 能力→权限映射
    CAPABILITY_TO_PERMISSION = {
        "can_predict": ["READ:Z-Buffer:{granted_layers}"],
        "can_evaluate": ["READ:Z-Buffer:*", "INVOKE:EBM:evaluate"],
        "can_report_status": ["WRITE:Z-Buffer:{granted_layers}"],
        "can_submit_artifact": ["WRITE:Artifact:own"],
        "can_recall": ["READ:Memory:{project_scope}"],
    }
    
    # 自定义 Z-Layer 扩展 (Phase 3+)
    CUSTOM_Z_LAYER_SPEC = """
      第三方 Agent 可注册自定义 Z-Layer:
        条件: 提供兼容的 Encoder (输出 2048-d 向量)
        注册: 声明 z_layer_name, encoder_type, 预训练基座
        验证: VectorQualityValidator 通过 (L2 范数, NaN, 方差)
        集成: 自动纳入 Z-Buffer, 但 TRL 初始为 0
        限制: 不参与核心因果图 (直到 TRL ≥ 2)
    """
```

### 14.5 REST↔gRPC 网关

```
REST 适配层 (降低第三方接入门槛):

  POST /api/v1/ext/predict     → 转换为 EipRequest(verb=PREDICT)
  POST /api/v1/ext/evaluate    → 转换为 EipRequest(verb=EVALUATE)
  POST /api/v1/ext/report      → 转换为 EipRequest(verb=REPORT_STATUS)
  POST /api/v1/ext/artifact    → 转换为 EipRequest(verb=SUBMIT_ARTIFACT)
  POST /api/v1/ext/recall      → 转换为 EipRequest(verb=RECALL)
  GET  /api/v1/ext/health      → Agent 健康状态
  GET  /api/v1/ext/schema      → 获取支持的 Protobuf Schema (JSON Schema 格式)
  
  认证: Bearer Token (Vault 签发, 每 24h 轮换)
  限流: 读 50/min, 写 10/min (第三方默认, 可升级)
  格式: JSON 请求体, 自动转换为 Protobuf
  版本: URL 路径版本 (/api/v1/, /api/v2/)
  文档: OpenAPI 3.0 自动生成
```

### 14.6 第三方 Agent 资源隔离

```python
class ThirdPartyResourceQuota:
    """第三方 Agent 资源配额 (独立于内置 Agent)。"""
    
    QUOTA_TIERS = {
        "free": {
            "max_concurrent_requests": 5,
            "max_requests_per_minute": 30,
            "max_z_buffer_read_layers": 3,
            "max_z_buffer_write_layers": 1,
            "memory_recall_enabled": False,
            "evolution_participation": False,
            "max_artifact_size_mb": 10,
        },
        "standard": {
            "max_concurrent_requests": 20,
            "max_requests_per_minute": 120,
            "max_z_buffer_read_layers": 5,
            "max_z_buffer_write_layers": 2,
            "memory_recall_enabled": True,
            "evolution_participation": False,
            "max_artifact_size_mb": 100,
        },
        "premium": {
            "max_concurrent_requests": 50,
            "max_requests_per_minute": 300,
            "max_z_buffer_read_layers": 8,  # 全部
            "max_z_buffer_write_layers": 4,
            "memory_recall_enabled": True,
            "evolution_participation": True,  # 可贡献训练数据
            "max_artifact_size_mb": 500,
        },
    }
    
    # 资源隔离机制
    ISOLATION = """
      网络: 独立 K8s namespace (uewm-ext-agents)
      CPU/内存: ResourceQuota per Agent registration
      GPU: 不直接访问 GPU (通过 Brain Core API 间接使用)
      存储: 独立 PV, 不与内置 Agent 共享
      Kafka: 独立 consumer group, 独立 topic 前缀 (uewm.ext.*)
    """
```

### 14.7 Agent 开发标准与合规

```
第三方 Agent 开发标准 (Agent Development Standard, ADS):

  ADS-1 协议合规:
    □ 实现 EipService gRPC 接口 (或使用 REST 网关)
    □ 所有请求携带有效 agent_id + api_key
    □ 支持 REPORT_STATUS 心跳 (≤ 60s 间隔)
    □ 正确处理 EipStatus 错误码 (重试/熔断)

  ADS-2 安全合规:
    □ 不硬编码凭证 (使用 Vault SDK 或环境变量)
    □ 不尝试直接访问 Z-Buffer (仅通过 EIP)
    □ 不尝试跨 Tenant 请求
    □ 遵循分配的 LOA 行为边界
    □ 不在日志中输出 Z-Layer 向量原始值

  ADS-3 质量合规:
    □ 提供健康检查端点 (HTTP 200 / gRPC HealthCheck)
    □ 提交的产物(Artifact)包含版本号和校验和
    □ 上报状态数据符合 Z-Layer 编码规范 (2048-d, L2∈[0.5,2.0])
    □ 响应超时不超过注册时声明的 SLO

  ADS-4 文档合规:
    □ 提供 README 描述 Agent 功能和适用场景
    □ 提供 Z-Layer 映射说明 (读/写哪些层, 含义)
    □ 提供故障降级行为说明

  合规验证工具:
    uewm-agent-lint: 静态检查代码合规 (ADS-2)
    uewm-agent-test: 集成测试套件 (ADS-1, ADS-3)
    uewm-agent-certify: 认证流程 (全部 ADS)
```

### 14.8 Python SDK

```python
# uewm-agent-sdk (PyPI 包)
from uewm_sdk import UEWMAgent, ZLayerData

class MyCustomAgent(UEWMAgent):
    """第三方 Agent 开发示例。"""
    
    def __init__(self):
        super().__init__(
            agent_type="custom-code-reviewer",
            supported_verbs=["PREDICT", "EVALUATE", "REPORT_STATUS", "RECALL"],
            z_layers_read=["Z_impl", "Z_quality"],
            z_layers_write=["Z_quality"],
        )
    
    async def on_directive(self, directive):
        """接收 Brain Core 编排指令。"""
        if directive.action == "REVIEW_CODE":
            result = await self.do_code_review(directive.context)
            # 上报结果到 Z_quality
            await self.report_status(
                layer="Z_quality",
                data=ZLayerData.from_metrics(result.quality_scores)
            )
    
    async def do_code_review(self, context):
        # 先检索历史经验
        memories = await self.recall(
            changed_layers=["Z_impl"],
            max_episodes=5
        )
        # 请求 Brain Core 预测
        prediction = await self.predict(
            target_layers=["Z_quality"],
            steps=1
        )
        # 自定义业务逻辑...
        return ReviewResult(...)

# SDK 内置功能:
# - mTLS 证书自动申请和轮换
# - EIP 消息序列化/反序列化
# - 心跳自动上报
# - 熔断器 (Hystrix-style)
# - 重试 (指数退避)
# - 指标上报 (Prometheus exporter)
# - 日志规范 (结构化 JSON)
```

V2.0 增强: 第三方 Agent 可通过 REST 网关访问 G-Space 查询 API (只读), 获取可解释的项目指标。

---

## 14. 独立 Brain Core API

### 15.1 设计目标

Brain Core 可作为独立的 "世界模型即服务" (WMaaS) 运行, 无需部署任何 Agent, 直接通过 API 查询 Z-Layer 状态、预测和评估。

### 15.2 独立 API 端点

```
Brain Core Standalone API (无需 Agent):

  POST /api/v1/brain/ingest
    描述: 直接向 Z-Buffer 注入观测数据 (替代 Agent REPORT_STATUS)
    输入: { "layer": "Z_impl", "data": <base64 encoded 2048-d vector>,
            "project_id": "...", "source": "external" }
    用途: 用户自行编码数据, 直接注入世界模型

  POST /api/v1/brain/predict
    描述: 直接请求 JEPA 预测 (替代 Agent PREDICT)
    输入: { "target_layers": ["Z_quality"], "steps": 3 }
    输出: { "predictions": [...], "confidence": 0.85 }

  POST /api/v1/brain/evaluate
    描述: 直接请求 EBM 评估 (替代 Agent EVALUATE)
    输入: { "candidates": [...], "context": "..." }
    输出: { "scores": [...], "recommended_index": 1 }

  GET /api/v1/brain/z-buffer/{project_id}
    描述: 读取当前 Z-Buffer 状态
    输出: { "layers": { "Z_impl": { "trl": 3, "energy": 0.15 }, ... } }

  GET /api/v1/brain/causal-graph/{project_id}
    描述: 查询因果图
    输出: { "edges": [{"from": "Z_impl", "to": "Z_quality", "strength": 0.72}] }

  [V2.0.1 新增] GET /api/v1/brain/g-space-query
    描述: 通过 Discovery Engine 将 Z向量 解码为 G空间观测预测
    输出: { "g_state_predictions": { "code.complexity": ..., "test.coverage": ... } }

  认证: API Key (Vault) 或 OAuth 2.0
  文档: OpenAPI 3.0 + Swagger UI
  限流: 基于 Tenant 配额
```

### 15.3 独立部署模式

```
Brain Core 独立部署 (无 Agent):

  Helm values-standalone.yaml:
    agents.enabled: false
    portal.enabled: false       # 可选
    brain.standalone_api.enabled: true
    brain.observation_source: "api"  # 不从 Agent 获取, 从 API 获取

  最小依赖: PostgreSQL + Redis + (可选 Neo4j)
  GPU: 1× A100 (或 RTX 3060 开发模式)

  用途:
    (1) 研究人员直接实验世界模型
    (2) 用户用自己的 Agent 框架 (非 UEWM Agent)
    (3) 集成到现有 CI/CD 系统作为 "预测引擎"
    (4) 开源社区快速试用 (无需部署 12 Agent)
```

```
V2.0 新增端点:

  GET  /api/v1/brain/g-space/{project_id}
    描述: 读取当前 G-Space 状态 (全部可观测指标)
    输出: { "code": { "complexity_avg": 12.4, ... }, "test": {...}, ... }
  
  GET  /api/v1/brain/g-space/{project_id}/history?from=&to=
    描述: 读取 G-Space 历史趋势
    
  GET  /api/v1/brain/discoveries/{project_id}
    描述: 读取 Discovery Engine 发现的新模式
    输出: [{ "pattern_id": "...", "description": "...", "confidence": 0.85 }]
```

---

## 15. 许可证与分发架构

### 16.1 双重许可模型

```
许可证架构:

  开源版 (AGPL v3):
  ├── Brain Core (H-JEPA + EBM + Z-Buffer + Evolution + Memory)
  ├── EIP Protocol (Protobuf IDL + gRPC Gateway)
  ├── Agent Framework (通用框架 + EIP Client SDK)
  ├── 内环 5 Agent (AG-CD/CT/DO/ST/MA)
  ├── Third-party Agent SDK
  ├── Standalone Brain Core API
  └── 限制: 单 Tenant, Profile-S, 无联邦学习

  商业版 (Commercial License):
  ├── 开源版全部内容 +
  ├── 中环/外环 7 Agent (AG-SA/FD/AU/PA/PD/BI/PR)
  ├── 多租户支持 (Profile-M/L)
  ├── 联邦学习引擎
  ├── 企业级安全 (SOC 2, 渗透测试报告)
  ├── 优先支持 + SLA
  ├── LLM 成本优化工具
  └── 高级监控仪表盘

  CLA (Contributor License Agreement):
    所有外部贡献者必须签署 CLA
    贡献者保留版权, 授予 Anthropic 永久许可
    CLA Bot: 自动检查 PR 的 CLA 签署状态
```

### 16.2 组件许可边界

| 组件 | 许可证 | AGPL 触发分析 |
|------|--------|-------------|
| Brain Core 二进制 | AGPL v3 | 作为服务提供时需开源修改 |
| EIP Protocol (.proto) | Apache 2.0 | 协议定义不触发 AGPL (互操作性) |
| Third-party Agent SDK | Apache 2.0 | SDK 不触发 AGPL (独立进程, 网络调用) |
| Agent Framework | AGPL v3 | 内置 Agent 基于此框架 |
| Helm Charts | AGPL v3 | 部署配置随主项目 |
| 文档 | CC BY-SA 4.0 | 文档独立许可 |

### 16.3 社区版 vs 企业版 Feature Flag

| 特性 | 社区版 (开源) | 企业版 (商业) |
|------|-------------|-------------|
| Brain Core | ✅ | ✅ |
| EIP Protocol | ✅ | ✅ |
| 内环 5 Agent | ✅ | ✅ |
| 长期记忆 | ✅ | ✅ |
| 自进化引擎 | ✅ | ✅ |
| 第三方 Agent SDK | ✅ | ✅ |
| Standalone API | ✅ | ✅ |
| 中环/外环 Agent | ❌ (FF_MIDDLE/OUTER_RING) | ✅ |
| 多租户 | ❌ (单 Tenant) | ✅ |
| Profile-M/L | ❌ (仅 Profile-S) | ✅ |
| 联邦学习 | ❌ | ✅ |
| SOC 2 报告 | ❌ | ✅ |
| 企业 SSO/SAML | ❌ | ✅ |
| 优先支持 | 社区论坛 | 专属工程师 |

### 16.4 贡献者工作流

```
外部贡献流程:

  1. Fork → Branch → Develop → Test
  2. 提交 PR → CLA Bot 检查 → CI 通过
  3. Code Review (模块 Owner):
     brain-core/: ARCHITECT 级别 reviewer
     agents/: 对应 Agent 的 domain expert
     eip/: Protocol team reviewer
     sdk/: SDK team reviewer
  4. 合并 → Release Notes 自动生成
  
  模块 Ownership:
    CODEOWNERS 文件定义每个目录的 reviewer
    外部贡献不可修改: 安全包络参数, RBAC 矩阵, KSL 分级逻辑
    外部贡献可修改: Agent 适配器, 编码器, SDK 扩展, 文档, 测试
```

---

## 16. 验证优先构建策略 (V2.0 核心新增)

### 16.1 Phase 0A: PoC 验证 (Weeks 1-8)

```
Week 1-2: G-Space Engine
  3 仓库 (FastAPI, Gin, Prometheus) 采集 ~80 指标
  存储: SQLite (PoC 阶段)
  交付: G-Space 时间序列, ≥2000 commits/repo

Week 3-4: Z-Space 基线 + 投影头
  CodeBERT → 投影头 (MLP+BN) → Z_impl (256-d)  [V2.0.1: 256-d, 含投影头]
  CI 结果编码 → 投影头 → Z_quality (256-d)
  SIGReg 正则化训练 (替换 VICReg)  [V2.0.1: SIGReg]
  验证: SIGReg loss 曲线平滑收敛 (per LeWM 训练特征)
  交付: 训练曲线 + Epps-Pulley 正态性检验通过

Week 5-6: 桥接验证 + 物理探测 [V2.0.1: 采用 LeWM 探测方法论]
  训练 φ 解码器: Z_impl → code.* 指标
  训练 φ 解码器: Z_quality → test.* 指标
  
  [V2.0.1 新增] 物理探测测试 (Physical Probing, from LeWM):
    对每个 Z-Layer 训练轻量探测头:
      Linear probe: Z → W·Z + b → single G-metric
      MLP probe: Z → Linear(512) → ReLU → Linear(1) → single G-metric
    
    探测目标:
      Z_impl  → code.complexity_avg, code.coupling_score, code.churn_rate_7d
      Z_quality → test.pass_rate, test.coverage_pct, test.test_duration_s
    
    成功标准:
      Linear probe Pearson r > 0.6 for ≥3 G-Space metrics per Z-Layer
      MLP probe Pearson r > 0.85 for ≥5 G-Space metrics per Z-Layer
    
    [V2.0.1] 这比 ARI 聚类检查更强:
      ARI > 0.2 → 补充指标 (聚类质量)
      Probing r > 0.6 → 主要指标 (结构编码验证)
  
  关键测试: Z_impl 预测 test.coverage_delta 是否优于
            code.* 指标单独预测?
  YES → Z-Space 有超越测量值的价值 → 继续
  NO  → Z-Space 冗余 → 调查编码器/投影头架构
  交付: B5 vs B6 vs B7 对比表 + 逐维度探测 R² 报告

Week 7-8: 发现信号 PoC + 违反预期测试
  训练 JEPA predictor on 3-layer Z-Space
  运行预测 → 采集双空间惊奇度
  检查惊奇度矩阵: 有多少 "Z correct + G wrong" (发现)?
  手工检查 top-20 潜在发现

  [V2.0.1 新增] 违反预期测试 (Violation-of-Expectation, from LeWM):
    生成 50 正常场景 + 50 异常场景:
    
    正常场景 (应得低惊奇度):
      普通 commit → 正常测试结果
      标准部署 → 稳定指标
      渐进重构 → 渐进复杂度降低
    
    异常场景 (应得高惊奇度):
      "传送": test.coverage 从 40% 跳到 95% (单 commit)
      "不可能的物理": p99 延迟下降 90% 无任何代码变更
      "因果矛盾": 复杂度翻倍但覆盖率提升 (违反学到的因果关系)
      "凭空出现": 零 commit 但测试数量增加 50%
      "回退诡异": 回滚到旧版本但指标不恢复
    
    指标: ROC-AUC (正常 vs 异常惊奇度分数)
    目标: AUC > 0.80
    
    意义: 这直接证明模型是否"理解"软件工程因果关系
  
  交付: 发现率, 噪声率, VoE ROC-AUC, 定性评估

Gate Review [V2.0.1 更新]:
  PASS: Probing r > 0.6 (linear) AND φ R² > 0.2 AND VoE AUC > 0.80 AND Z 超越 G
  PARTIAL: Probing r > 0.4 OR φ R² > 0.1 OR VoE AUC > 0.65 → 继续但调整
  FAIL: Probing r < 0.3 AND φ R² < 0.05 AND VoE AUC < 0.55 → 根本性重新思考

  [V2.0.1] 附加检查:
    □ SIGReg 正态性检验通过 (Epps-Pulley p > 0.05)
    □ 训练曲线平滑单调收敛 (非噪声/非单调)
    □ 投影头消融: 有投影头 vs 无投影头训练稳定性对比
    □ 时间直化 (temporal straightening): 连续速度向量余弦相似度 > 0.5
```

### 16.2 Phase 0B: 最小可行 Brain (Months 3-6)

```
通过 PoC Gate → 构建真正的 Brain Core:
  Z-Buffer Manager (V1 设计)
  G-Space Engine (生产级: Prometheus + GitHub API + CI API)
  H-JEPA Predictor (双预测: Z + G)
  EBM Arbiter (增强: energy + risk decomposition)
  Bridging Functions (φ, ψ, consistency loss)
  Discovery Engine (模式检测)
  Causal Graph Engine (Z边 + G边)
  Long Memory (四层, 双索引)
  TRL Evaluator, Safety Envelope, Circuit Breaker
  EIP Gateway (简化: gRPC, Kafka 可选)

首个产品: "Engineering Oracle" GitHub App
  PR → 预测 test/performance/complexity 影响
  Deploy → 预测事故概率
  Weekly → 项目健康报告 + 因果解释
  Discovery log → 模型看到但指标无法解释的内容

硬件: 1-2× A100 (或 RTX 3060 开发)
团队: 2-3 工程师
```

### 16.3 Phase 1: Agents + Memory (Months 7-12)

```
添加 Agent 层:
  内环 5 Agent (AG-CD/CT/DO/ST/MA)
  完整 EIP Protocol (gRPC + Kafka)
  ALFA 框架 (LOA 控制)
  记忆巩固引擎
  自进化 (LoRA + 双空间惊奇度驱动)
  第三方 Agent SDK
  Standalone Brain Core API
```

### 16.4 Phase 2-3: Full UEWM (Year 2+)

```
V1.0.1 全部设计内容:
  中环/外环 Agents, 多租户 (KSL), 联邦学习,
  SOC 2 合规, 企业功能, 全 8 Z-Layer 覆盖
```

---

## 17. 验收标准映射

### R01 — JEPA 基础世界模型 (11 ACs)

| AC | 设计支撑 | 验证方法 |
|----|---------|---------|
| AC-1: 8层2048-d | §7.1 | 单元测试: shape==(batch,2048) |
| AC-2: Kendall τ≥0.5 | §8.3 | 校准数据集+5-fold |
| AC-3: 1步MSE<0.15 | §6.5 | Held-out 20%, time-split |
| AC-4: MVLS TRL-3 | §7.3+§7.4 | ARI≥0.3+格兰杰 p<0.05 |
| AC-5: 因果 p<0.05 | §6.4 | 格兰杰检验 |
| AC-6: TRL 动态降权 | §7.3 | 注入低ARI→EBM降权 |
| AC-7: 编排输出排序 | §3.3 | 集成测试 |
| AC-8: 选型论证 | §7.1 编码器矩阵 | 文档评审 |
| AC-9: 多项目无饥饿 | §3.4 | 负载测试 |
| AC-10: 配额排队 | §3.4 | 集成测试 |
| AC-11: Transformer-XL 非 LLM 论证 | §6.1 | 文档评审 |

### MEM — 长期记忆 (10 ACs)

| AC | 设计支撑 | 验证方法 |
|----|---------|---------|
| MEM-AC-1: 情景检索 | §12 | Z-Layer 相似度检索准确率 >80% |
| MEM-AC-2: 艾宾浩斯 | §12 | 高 importance 的 Episode 永不归档 |
| MEM-AC-3: 事实提取 | §12 | ≥3 一致 Episode → Fact |
| MEM-AC-4: 反模式反馈 | §12 | 巩固引擎能将反模式注入 LoRA |
| MEM-AC-5: Profile 注入 | §12 | PREDICT 和 EVALUATE 含有 profile 提速 |
| MEM-AC-6: 检索延时 | §12 | P99 < 200ms |
| MEM-AC-7: 租户隔离 | §12 | KSL-0 不能跨项目检索 |
| MEM-AC-8: 归档流程 | §12 | 从热存储(PgSql)->冷库(S3) < 5min |
| MEM-AC-9: 联邦聚合 | §12 | KSL-3 统计分析 DP ε≤0.5 |
| MEM-AC-10: 矛盾调解 | §12 | 时间优先机制处理旧 Fact 矛盾 |

### GPU — GPU 优化 (6 ACs)

| AC | 设计支撑 | 验证方法 |
|----|---------|---------|
| GPU-AC-1: 混合精度训练 BF16 | §13.2 | 训练吞吐: BF16 vs FP32, 显存减少≥35% |
| GPU-AC-2: 梯度检查点显存降低≥50% | §13.3 | Profiling: 有/无检查点显存对比 |
| GPU-AC-3: TensorRT 推理延迟降低≥30% | §13.5 | Benchmark: PyTorch vs TensorRT P99 |
| GPU-AC-4: 各组件显存不超预算 | §13.6 | nvidia-smi 峰值监控 |
| GPU-AC-5: GPU 利用率推理>60%训练>80% | §13.7 | Prometheus GPU exporter 30min 采样 |
| GPU-AC-6: 跨平台 get_device() 功能验证 | §13.8 | Mac/RTX/A100 三平台单元测试 |

### EXT — 第三方 Agent (8 ACs)

| AC | 设计支撑 | 验证方法 |
|----|---------|---------|
| EXT-AC-1: 第三方 Agent 注册流程可用 | §14.3 | 注册→审核→激活→健康检查 |
| EXT-AC-2: REST 网关功能闭环 | §14.5 | REST→gRPC 转换 5 个动词 |
| EXT-AC-3: 资源隔离有效 | §14.6 | 超配额→限流+隔离验证 |
| EXT-AC-4: SDK 集成测试通过 | §14.8 | Python SDK 完成注册+PREDICT+EVALUATE |
| EXT-AC-5: ADS 合规工具可用 | §14.7 | uewm-agent-lint/test/certify 三工具 |
| EXT-AC-6: 自定义 Z-Layer 注册 | §14.4 | 注册自定义编码器→VQV 验证→入 Z-Buffer |
| EXT-AC-7: 第三方 RBAC 拦截 | §14.3 | 越权请求 100% 拦截 |
| EXT-AC-8: Standalone API 功能验证 | §15.2 | 无 Agent 部署→直接 predict/evaluate |

### LIC — 许可证 (4 ACs)

| AC | 设计支撑 | 验证方法 |
|----|---------|---------|
| LIC-AC-1: AGPL/Apache 边界清晰 | §16.2 | 许可证扫描: 每组件许可正确 |
| LIC-AC-2: 社区版功能完整可用 | §16.3 | 社区版 Profile-S 独立部署验证 |
| LIC-AC-3: CLA 工作流自动化 | §16.4 | PR→CLA Bot→签署→合并 |
| LIC-AC-4: Feature Flag 隔离验证 | §16.3 | 社区版禁用商业 Flag 后功能正常 |

### GND — 双空间锚定 (10 ACs, V2.0 全新)

| AC | 设计支撑 | 验证方法 |
|----|---------|---------|
| GND-AC-1: G-Space ≥80 指标/项目, >95% 采集率 | §4.2 | 指标采集健康仪表盘 |
| GND-AC-2: φ 解码器 R² > 0.2 for ≥3 G-Space 指标组 | §5.2 | 逐维度 R² 报告 |
| GND-AC-3: 一致性损失收敛 | §5.4 | 训练曲线: loss < 阈值 |
| GND-AC-4: 双空间惊奇度正确分类 ≥80% 事件 | §9.2 | 100 惊奇事件人工检查 |
| GND-AC-5: Discovery Engine 90天内识别 ≥1 有效未命名模式 | §9.3 | 人工审核提出的指标 |
| GND-AC-6: Z-Space 超越 G-Space 独立预测 (p < 0.05) | §9, §16.1 | A/B: Z+G vs G-only |
| GND-AC-7: 自反省接地健康度 6 子指标功能正常 | §11.2 | 全部子指标计算+报告 |
| GND-AC-8: 风险分解覆盖 ≥70% EBM energy | §8.2 | explained/total ratio |
| GND-AC-9: G-Space Phase 1 增长 ≥5 发现指标 | §9.4 | 发现日志 + 人工审核 |
| GND-AC-10: PoC Gate Review 全部通过 | §16.1 | ARI, φ R², Z-value-add |

### LeWM — LeWorldModel 集成 (6 ACs, V2.0.1 全新)

| AC | 设计支撑 | 验证方法 |
|----|---------|---------|
| LeWM-AC-1: SIGReg 防止崩溃 (正态性检验通过) | §5.4 | Epps-Pulley p > 0.05 on 100 随机投影 |
| LeWM-AC-2: 探测恢复 G-Space 指标 (linear r > 0.6) | §16.1 | 逐维度探测报告 |
| LeWM-AC-3: VoE 检测异常工程事件 (AUC > 0.80) | §16.1 | 正常 vs 异常 ROC 曲线 |
| LeWM-AC-4: 投影头改善训练稳定性 | §5.5 | 有 vs 无投影头消融对比 |
| LeWM-AC-5: 双项损失收敛平滑单调 | §5.4 | 训练曲线检查 |
| LeWM-AC-6: 时间直化自然涌现 | §16.1 | 连续速度向量余弦相似度 > 0.5 |

### NFR (14 项)

| AC | 设计支撑 | 验证方法 |
|----|---------|---------|
| NFR-1: Brain P99 | 负载规划 | 负载测试 Profile-S/M/L |
| NFR-2: 可用性 | 高可用架构 | 48-72h 无人值守运行 |
| NFR-3: S→L | §3.6 | 扩展测试: 仅加资源 |
| NFR-8: 决策审计 | 日志规范 | 决策→审计日志→多维查询 |
| NFR-9: GPU争用 | 资源分配 | GPU争用负载测试 |
| NFR-11: 日志分层 | 监控体系 | Hot/Warm/Cold 查询SLO验证 |
| NFR-12: GPU 显存预算合规 | §13.6 | 各组件 VRAM 不超分配 |
| NFR-13: 第三方 Agent 注册 SLO | §14.3 | 注册→激活 < 5min (自动审核) |
| NFR-14: Standalone API P99 | §15.2 | 独立部署 P99 < 300ms |

**总计: 154 ACs (107 R扩展 + 10 MEM + 6 GPU + 8 EXT + 4 LIC + 10 GND + 6 LeWM + 3 NFR新增)**
