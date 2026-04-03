# 🔄 UEWM 自学习/自反省/自修正/自进化机制设计文档

**文档版本：** V2.0.1  
**文档编号：** UEWM-EVO-003  
**最后更新：** 2026-04-03  
**状态：** 设计完成（100% 覆盖 R03, R06, R08, R10, R12-Gap3 + 双空间惊奇度 + Discovery 联动 + SIGReg + VoE 验证）  
**变更历史：**
- V8.0/deliver-v1.0: 安全包络, 断路器, 帕累托, 偏见, KSL, 遗忘, 校准, 漂移验证
- V1.0.1: GPU 优化进化, 程序记忆形式化
- V2.0.0: 双空间惊奇度, REAL_SURPRISE 仅触发进化, Discovery Episode, 接地健康度
- **V2.0.1: SIGReg 替换 VICReg (正则化), 投影头集成, VoE 测试作为进化验证, 安全包络增加 SIGReg 正态性检查, 全量合并 V1.0.1 内容，消除所有引用依赖**

---

## 1. 概述 — 四大能力

自学习(双空间惊奇度驱动) + 自修正(漂移检测+因果回溯) + 自进化(LoRA+安全包络+帕累托) + 自反省(6维含接地健康度)。

V2.0 核心变化: 进化仅由**真实惊奇** (S_z HIGH + S_g HIGH) 触发, 不被 Z-Space 噪声误触发。双环持续改进闭环: 内环(Agent交互→惊奇度→LoRA进化) + 外环(定期反省→盲区发现→主动学习)。

---

## 2. 自学习机制

### 2.1 双空间惊奇度 (V2.0 核心变更)

```python
class DualSpaceSurprise:
    """V2.0: 在 Z-Space 和 G-Space 两个空间同时计算惊奇度。"""
    
    def compute(self, z_pred, z_obs, g_pred, g_obs):
        s_z = torch.norm(z_obs - z_pred, p=2) ** 2  # 隐空间惊奇度
        s_g = torch.norm(g_obs - g_pred, p=2) ** 2  # 可观测惊奇度
        
        z_high = s_z > self.theta_z  # 自适应阈值 (§2.5 校准)
        g_high = s_g > self.theta_g  # G-Space 阈值 (14天 P95)
        
        if z_high and g_high:
            return SurpriseCategory.REAL_SURPRISE
            # 世界真的变了 → 触发进化
        elif z_high and not g_high:
            return SurpriseCategory.Z_NOISE
            # 隐空间漂移 → 标记编码器, 不进化
        elif not z_high and g_high:
            return SurpriseCategory.GROUNDING_GAP
            # Z 正确但 G 不完整 → Discovery Engine
        else:
            return SurpriseCategory.NORMAL
            # 预测准确 → 正常
    
    # 14天滚动 P95 校准, 每项目独立
    # V2.0 增加: G-Space 阈值同样自适应校准
```

### 2.2 进化触发条件 (V2.0 变更)

```
V1.0.1: S(t) > θ → 触发进化
V2.0:   category == REAL_SURPRISE → 触发进化
        category == Z_NOISE → 标记编码器需重训练, 不触发进化
        category == GROUNDING_GAP → Discovery Engine 介入
        category == NORMAL → 无动作

这一变化确保进化引擎只在真实惊奇时训练,
消除了 V1.0.1 中"在 Z-Space 噪声上训练"的风险。
```

### 2.3 经验回放与课程学习

经验回放缓冲区 (ERB): 优先经验回放, 按惊奇度排序。课程学习: 简单→困难渐进。反事实数据增强。每次惊奇度超阈值自动创建 INCIDENT Episode 存入长期记忆 (Architecture §12.3)，检索历史相似 Episode 作为进化先验。V2.0: Episode 使用含 G-snapshot 的 EnhancedEpisode 格式。

### 2.4 惊奇度阈值校准

初始阈值: Z_impl=0.5, Z_quality=0.4, Z_phys=0.3。自适应: 14天滚动 P95, 最小100样本才启动, 每次调整≤10%, floor=0.1/ceiling=2.0。每项目可独立校准。V2.0 增加 θ_g (G-Space 阈值) 同样自适应校准。

---

## 3. 自修正机制

漂移检测 (Page-Hinkley / ADWIN / KL 散度)。因果根因定位。修正反馈传导。

### 3.4 漂移检测验证方案

注入漂移: 突变(20个,2σ) + 渐进(20个,0.1σ/day×14d) + 方差变化(10个,2x)。对照组50个。检测窗口24h。成功: 检出率≥90%, 误报率≤10%, P50延迟<2h。

---

## 4. 自进化机制

### 4.1-4.6 核心进化

LoRA 增量更新, 5触发策略(惊奇/漂移/定时/事件/手动), SIGReg正则化 (V2.0.1替换VICReg), 版本管理, 评估指标, 安全约束。

### 4.7 进化安全包络 (V2.0.1 增强)

单次: 单层回归≤10%, 总体≤5%, ΔW≤0.1, 因果边丢失≤5%。累积: ≤5次/24h, ≤15次/周, 连续3次回滚暂停48h, 7天累积≤15%。偏见: 决策熵≥0.6, 单用户≤30%, ≥3角色。

`post_evolution_check` 现有 **7 项** [V2.0.1]:
- □ 单层回归 ≤ 10%
- □ 总体回归 ≤ 5%
- □ ΔW ≤ 0.1
- □ 因果边丢失 ≤ 5%
- □ φ R² 不可下降超过 5% (V2.0.0)
- □ 一致性损失不可上升超过 10% (V2.0.0)
- □ **SIGReg 正态性不可退化 (V2.0.1, LeWM): Epps-Pulley p-value 不可从 >0.05 降至 <0.01; 如果正态性退化 → 进化破坏了 Z-Space 分布结构 → 回滚**

`pre_evolution_check + post_evolution_check` 完整实现。

### 4.8 进化断路器

CLOSED→OPEN(连续3回滚,暂停48h)→HALF_OPEN(降低lr 50%+单层+减候选)→CLOSED(成功)。失败时自动生成失败分析报告。

### 4.9 帕累托改进约束

多候选并行训练(n=5,不同lr)→帕累托前沿→距理想点最近。is_pareto_improvement: 无层退化超tolerance(0.02)且至少一层显著改善。

### 4.10 偏见检测系统

check_feedback_diversity: 单用户≤30% + ≥3角色。check_decision_diversity: Shannon 熵≥0.6。

### 4.11 进化失败根因分析

EvolutionFailureAnalyzer: 7类根因(数据质量/lr过高/层冲突/因果破坏/偏见漂移/分布偏移/候选不足)。单次回滚→立即分析。断路器OPEN→3次交叉分析。自动修复: auto_reduce_lr_50pct, auto_single_layer_mode, auto_increase_candidates。结构化 JSON 报告。

### 4.12 跷跷板效应 30 天监控

SeesawMonitor: 每层维护退化计数器, 30天滑动窗口。任一层连续退化>3次→SEESAW_DETECTED→告警SECURITY+ARCHITECT→冻结该层联合进化。仪表盘显示各层状态(HEALTHY/WARNING/SEESAW_DETECTED)。

---

## 5. 跨项目知识迁移与联邦进化

### 5.1-5.4 核心机制

多团队架构(Base Model+团队LoRA), 知识提取(脱敏→抽象→普适→去重), 联邦学习(DP+质量加权), 知识图谱(Pattern/AntiPattern/Decision/Metric)。

### 5.5 KSL 分级知识蒸馏

KSL-0(完全隔离) → KSL-1(统计级,ε≤0.5) → KSL-2(模式级,ε≤1.0,需人工审核) → KSL-3(联邦级,ε≤2.0,Secure Agg) → KSL-4(开放共享,同Tenant)。

#### 5.5.1 脱敏流水线详细设计

Level 1(自动正则): 项目名→[Project], 服务名→[服务类型], IP/email/API_key→[REDACTED], 数值→区间桶。Level 2(语义实体): 9类服务分类体系(用户/订单/支付/通知/网关/数据/消息/监控/存储)。Level 3(人工审核,KSL-2必须): Portal提交→SECURITY/ARCHITECT审核→48h SLA→超时保守排除。PII 最终扫描。

### 5.6 隐私预算管理器

每项目每月 ε 预算: KSL-1(5.0), KSL-2(10.0), KSL-3(20.0), KSL-4(∞)。can_share→consume→reset_monthly。耗尽→PRIVACY_BUDGET_EXHAUSTED 事件。

### 5.7 冷启动基线测量方法

基线: ≥5项目独立训练→TRL-0到TRL-2中位数时间。测量点: M1(TRL-0确认) → M2(TRL-1达成) → M3(TRL-2达成) → M4(冷启动完成,惊奇度<0.5)。cold_start_duration = M3-M1。AC-2验证: 有迁移 vs 无迁移, 缩短≥50%。Phase 0 M2-M3 执行。

### 5.8 联邦学习性能基准测试

A组(中心化,无DP) vs B组(联邦,ε=2.0+SecureAgg)。≥10项目, 同超参, 3次重复取中位数。指标: prediction_mse + causal_accuracy → composite_score。AC-7验证: B/A ≥ 0.85。

---

## 6. 自反省机制

定期触发(日/周/月/里程碑)。自反省与记忆巩固引擎同步运行 (每日 03:00 UTC)。反省发现的异常创建 REFLECTION Episode。巩固引擎在反省后立即执行事实提取。反省报告中新增"记忆健康度"维度: Fact 矛盾率、Episode 归档率、Profile 覆盖度。

### 6.1 六维内省 (V2.0: 5维→6维)

**第 1-5 维 (V1.0.1)**: 预测一致性, 因果图健康, 跨层对齐, 决策多样性, 盲区检测(POMDP高Σ区域)。产出结构化反省报告。异常→注入进化引擎定向 LoRA。

**第 6 维: 接地健康度 (Grounding Health, V2.0 新增)**:

```
每日 03:00 UTC 自反省时同步检查:

6a. φ 精度: per-dimension R² — 目标均值 > 0.3
    R² < 0.1 的维度列入"需修剪/重训练"列表

6b. ψ 一致性: cosine similarity — 目标 > 0.5

6c. 发现率: DISCOVERY 事件 / 总预测事件
    健康: 5-15%
    <2%: Z-Space 可能冗余
    >30%: Z-Space 可能漂移, 增加 ψ 权重

6d. G-Space 覆盖率: 指标采集成功率 — 目标 > 95%
    <90%: 告警 DEVOPS (采集器故障)

6e. 惊奇分类准确率: 手工抽检 20 事件/月
    目标: 分类准确率 ≥ 80%

异常处理:
  φ 精度下降 → 重训练桥接函数 (非编码器)
  发现率过高 → 增加 consistency_loss_weight
  G-Space 覆盖率下降 → 告警, 非模型问题
```

### 6.2 偏差测试集方法论

BiasTestSetBuilder: 5类偏差注入(预测偏高/因果移除/跨层不对齐/决策单调/时序退化)。50注入+20对照。7天检测窗口。AC-2: 检出率≥80%(≥40/50)。AC-4: 误报率≤20%(≤4/20)。Phase 0 M3 执行(30实例+10对照), Phase 1 M6 全量。

---

## 7. 从人工反馈中学习

全流程记录。r_human = f(能量差, 事后验证, 角色权威, 新颖度)。Human Feedback Buffer(优先级回放)。50经验累积→偏见检查→专项 LoRA(lr=50% of 自进化)。每次人工干预→创建 HUMAN_INTERVENTION Episode (OVERRIDE:importance=1.0, REQUIREMENT:0.8, SUGGESTION:0.5)→3+一致覆写提取 PREFERENCE Fact→注入 Project Profile。V2.0: 人工反馈 Episode 含 G-snapshot。

### 7.7 安全护栏

能量门禁(≤200%), 双人确认(override), 学习率限制(50%), SIGReg保护 (V2.0.1), 48h回滚, 偏见检测(单用户≤30%, ≥3角色)。

### 7.8 人机一致率测量

exact_match_rate: Brain top-1 == 人工选择。relaxed: Brain top-1 in 人工 top-3。风险加权(LOW×1, MEDIUM×1.5, HIGH×2, CRITICAL×3)。月度测量,≥50样本。AC-2: Phase 1≥60%, Phase 2≥75%。AC-3: Phase 2 干预频率相比 Phase 1 基线下降≥30%。

### 7.9 恶意建议检测

5类检测: 能量爆炸(>200%→block), 安全违规(E_safety超标→block), 回退注入(历史回滚匹配→warn+justification), 范围越权(RBAC→block), 矛盾建议(7天内相似度>0.8→clarify)。验证: 40恶意+60合法, 拦截率≥95%(≥38/40), 误拦率≤5%(≤3/60)。

---

## 8-9. 向量数据库增强训练管道 / 联合训练策略

pgvector(Phase 0)→Milvus(Phase 1+)。SIGReg 正则化 (V2.0.1替换VICReg)。语义聚类 ARI, 跨模态预测 MSE, 因果信号保真度评估。

---

## 10. 机器遗忘策略

| KSL | 遗忘方式 | 完整性 | 时限 |
|-----|---------|--------|------|
| 0 | 删除LoRA+数据 | 100% | 30天 |
| 1/2 | 删除+DP近似遗忘 | 近似(ε≤1.0) | 30天;精确90天 |
| 3 | 删除+联邦DP近似 | 近似(ε≤2.0) | 近似30天;精确按规模 |
| 4 | 删除+从checkpoint重微调 | 视范围 | 60天 |

删除审计: 来源+范围+确认+关联模型标记+完整性声明+时间戳。日志保留≥3年。

---

## 11. 进化流程完整时序 (V2.0 更新)

```
触发 (仅 REAL_SURPRISE, 非 Z_NOISE) →
pre_check (频率+累积回归+断路器) →
偏见检测 →
多候选帕累托训练 (5个, BF16+梯度检查点) →
post_check (7项, V2.0.1含SIGReg正态性) →
ACCEPT/ROLLBACK →
影子模式 48h →
版本快照+审计 →
断路器记录 →
创建 EVOLUTION Episode (importance=1.0, 含 G-snapshot, V2.0) →
提取进化有效性 Fact →
连续回滚提取 ANTI_PATTERN Fact
```

### 11.5 进化训练 GPU 优化

```
进化训练 GPU 优化策略 (对标 Architecture §13):

  LoRA 进化训练 (主要进化方式):
    精度: BF16 训练 + FP32 梯度累积
    显存: rank 8-64, < 4 GB/次, 不需要梯度检查点
    优化: 多候选并行训练 (n=5) 在同一 GPU 上顺序执行 (非并行)
          原因: LoRA 训练快 (~5min/候选), 并行反而增加显存碎片
    
  对齐训练 (AlignmentTrainer, 周期性):
    精度: BF16 + 梯度检查点 (每 3 编码器层)
    DeepSpeed: Phase 0 ZeRO-1, Phase 1+ ZeRO-2
    显存: ~16 GB (启用检查点后, 原 ~45 GB)
    调度: 仅在训练 GPU 池空闲时启动, 推理优先
    
  反事实数据增强 (ERB 经验回放):
    优化: CPU 预处理 + GPU 仅做前向推理
    批量: 动态 batch (根据可用 GPU 显存自适应)
    缓存: 编码器输出缓存 (避免重复编码相同项目)

  程序记忆 (Layer 0, Architecture §12.2) 与进化的关系:
    LoRA 权重即程序记忆
    进化成功: 程序记忆更新 (新技能习得)
    进化回滚: 程序记忆回退 (技能遗忘)
    断路器 OPEN: 程序记忆冻结 (停止学习)
    冷启动: 程序记忆为空 (无先验技能)
    知识迁移: 从他项目复制程序记忆片段 (KSL 约束)
```

---

## 12. 验收标准映射

| AC | 设计支撑 |
|----|---------|
| R03 AC-1: 惊奇度→LoRA→惊奇度↓ | §2+§2.4(校准) |
| R03 AC-2: 漂移检测>90% | §3+§3.4(验证方案) |
| R03 AC-3: 版本可追溯回滚 | §4.6 |
| R03 AC-4: 安全包络100% | §4.7 |
| R03 AC-5: 熔断演示 | §4.8 |
| R03 AC-6: 帕累托>80% | §4.9 |
| R03 AC-7: 30天无跷跷板 | §4.12 |
| R06 AC-1~4: 自反省 | §6+§6.2 |
| R08 AC-2: 冷启动≥50% | §5.7 |
| R08 AC-7: 联邦≥85% | §5.8 |
| R10 AC-2: 一致率≥60%/75% | §7.8 |
| R10 AC-3: 干预↓≥30% | §7.8 |
| R10 AC-4: 恶意拦截>95% | §7.9 |
| R12 AC-7: KSL-0遗忘100% | §10 |
| **R03 AC-8: 仅 REAL_SURPRISE 触发进化** | **§2.2** |
| **R03 AC-9: 一致性损失 post_check 不退化** | **§4.7 V2.0** |
| **R03 AC-10: SIGReg 正态性 post_check 不退化 (LeWM)** | **§4.7 V2.0.1** |
| **R06 AC-5: 接地健康度维度功能正常** | **§6.1** |
