# 📊 UEWM 训练数据策略设计文档

**文档版本：** deliver-v1.1  
**文档编号：** UEWM-DATA-008  
**最后更新：** 2026-03-24  
**状态：** 设计完成（100% 覆盖 R12 + Long Memory 数据生命周期）  
**合并来源：** Data Strategy V1.0 + V2.0(向量质量) + V3.0(PII/许可证) + V4.0(合成标签/回滚级联/Phase0计划) — 全量合并  
**对标需求：** R12 (全部), R01 (编码器数据), R03 (进化训练数据)

---

## 1. 概述

定义 JEPA 世界模型各编码器的训练数据来源、获取方式、质量要求、标注策略和生命周期管理。

---

## 2. Z-Layer 编码器数据来源矩阵

### 2.1 MVLS 三层 (Phase 0)

| Z-Layer | 数据来源 | 数据格式 | 预训练基座 | 最小样本量 | 标注方式 | 更新频率 |
|---------|---------|---------|-----------|-----------|---------|---------|
| Z_impl | GitHub Top-10K 仓库 (Python/Go) | AST+CFG (Tree-sitter) | CodeBERT/StarCoder | 100K commit-level diff | 自监督 (同仓库不同commit) | 每月增量 |
| Z_quality | 同上仓库 CI/CD 日志 | 测试通过率+覆盖率(Cobertura/JaCoCo XML)+执行时间 | 从零训练 (结构化表格) | 50K CI pipeline 记录 | 自监督 (同项目时序) | 与Z_impl同步 |
| Z_phys | 公开 Prometheus dashboard + 合成数据 | Prometheus 时序格式 | TimesFM/Chronos | 10M 时序数据点 | 自监督(时序预测)+弱监督(故障标注) | 实时采集 |

### 2.2 Phase 1+ 扩展层

| Z-Layer | 数据来源 | 预训练基座 | 挑战 |
|---------|---------|-----------|------|
| Z_arch | 架构文档(README/ARCHITECTURE.md)+依赖图(pom.xml/go.mod) | GraphSAGE+BERT | 文档质量参差，需人工筛选 |
| Z_logic | 需求文档/User Story/Jira Issue (需脱敏) | BERT/RoBERTa | 需合作企业脱敏数据 |
| Z_biz/Z_val/Z_market | 公开财报+行业报告+产品评测 | TabNet+FinBERT | 数据稀少，主要依赖合成数据 |

---

## 3. 数据质量要求

去重标准: 同一仓库的 fork 只保留原始仓库。数据新鲜度: Z_phys 实时; Z_impl/Z_quality 月更; Z_arch+ 季更。清洗规则: 移除空仓库、测试覆盖率为 0 的项目、许可证不兼容的仓库。

### 3.1 向量质量标准

| 指标 | 阈值 | 说明 |
|------|------|------|
| L2 范数 | ∈ [0.5, 2.0] | 范围外的向量可能有编码异常 |
| NaN 比例 | = 0 | 零容忍 |
| 全零向量 | < 1% | 编码器可能未加载 |
| 每维最小方差 | > 0.01 | 防止维度坍缩 |
| 平均余弦相似度 | < 0.7 | 确保向量多样性 |
| 最少项目数 | Phase 0: 5, Phase 1+: 1000 | 数据覆盖度 |
| 最少编程语言 | Phase 0: 2, Phase 1+: 5 | 语言多样性 |
| 各层样本数比 | > 0.5 | 层间平衡 |

---

## 4. 合成数据策略

Phase 0 允许合成数据占比 ≤ 30% (用于数据增强，非主训练集)。Z_phys 层特批例外: 允许 ≤ 60% (公开 Prometheus 数据稀缺)，须在数据版本中特批标注，优先寻求早期客户真实数据替代。

合成方法: 对真实数据做受控扰动(代码变异、指标噪声注入)。合成数据必须标记为合成，不参与 TRL 评估的"真实数据"指标。

### 4.1 合成数据标记 Schema

```
Parquet Schema 中的合成数据标记:

  字段: is_synthetic (bool, required)
    true  = 合成数据 (代码变异/噪声注入生成)
    false = 真实数据 (GitHub 采集 / 客户项目)

  字段: synthetic_method (string, nullable)
    "code_mutation" | "noise_injection" | "interpolation" | null(真实数据)

  字段: synthetic_source_id (string, nullable)
    引用生成该合成样本的原始真实样本 ID (用于溯源)

TRL 评估器过滤规则:
  TRL Evaluator 在计算 ARI/因果检验/预测MSE 时: WHERE is_synthetic = false
  合成数据仅参与编码器预训练，不参与 TRL 达标评估。

DVC 元数据标签:
  每个数据版本的 manifest.json 包含:
    "synthetic_ratio": 0.28, "synthetic_count": 28000, "real_count": 72000,
    "z_phys_synthetic_ratio": 0.55  // Z_phys 层单独统计
```

---

## 5. 数据版本管理

训练数据集实行版本化 (DVC)。每个模型版本关联其训练数据版本，支持联合回溯。数据回滚时自动标记依赖该数据的模型版本为"待验证"。

### 5.1 数据回滚级联自动化

```python
class DataRollbackCascade:
    """数据回滚时自动标记依赖模型版本"""
    
    async def on_data_rollback(self, data_version: str, layer: str):
        # 1. 查询 MLflow: 哪些模型版本使用了该数据版本
        dependent_models = await self.mlflow.search_runs(
            filter=f"params.training_data_version = '{data_version}' AND params.layer = '{layer}'"
        )
        # 2. 标记为 "DATA_ROLLED_BACK_PENDING_VERIFICATION"
        for model in dependent_models:
            await self.mlflow.set_tag(run_id=model.run_id, key="data_integrity_status",
                                      value="DATA_ROLLED_BACK_PENDING_VERIFICATION")
        # 3. 通知 DEVOPS + 4. 审计日志
    # DVC post-checkout hook 集成: .dvc/hooks/post-checkout → python -m uewm.data.rollback_cascade
```

---

## 6. 数据合规

### 6.1 PII 检测

工具: Microsoft Presidio (开源, 支持中英文)。检测实体: PERSON, EMAIL, PHONE, IP, CREDIT_CARD, API_KEY, PASSWORD 等。自定义正则: GitHub Token, AWS Key, Private Key Header, 中国身份证, 中国手机号。置信度 ≥ 70% 才标记。误报白名单: localhost, private IP range。DVC pre-commit hook 自动扫描。

### 6.2 许可证扫描

工具: scancode-toolkit (支持 200+ 许可证)。白名单: Apache-2.0, MIT, BSD-2/3, ISC, Unlicense, CC0。黑名单: GPL-2.0/3.0, AGPL-3.0, SSPL-1.0, BSL-1.1, CC-BY-NC。灰名单(需人工审核): LGPL, MPL-2.0, EPL-2.0。DVC pre-commit hook 集成: push 前自动检查所有数据源许可证。

---

## 7. 数据保留与删除策略

| 数据类别 | 保留期 | 删除触发 | 删除范围 |
|---------|--------|---------|---------|
| 开源采集训练数据 | 永久 | 许可证变更为不兼容 | 该仓库数据 |
| 客户项目训练数据 | 合同期+90天 | 合同终止/客户请求(30天)/KSL降级 | 原始数据+编码缓存+DVC版本 |
| 客户级 LoRA | 合同期+90天 | 与训练数据同步 | LoRA权重(基础模型不受影响) |
| 合成数据 | 与模型版本一致 | 模型废弃后180天 | 对应合成数据 |
| 联邦学习梯度聚合 | 仅保留聚合结果 | — | 不保留单项目原始梯度 |

**[deliver-v1.1] 长期记忆数据保留 (Architecture §12):**

| 数据类别 | 热(30天) | 温(180天) | 冷(180天+) | 删除规则 |
|---------|---------|----------|-----------|---------|
| Episode (Z快照+决策+结果) | PG+pgvector | PG元数据+S3快照 | S3归档(zstd) | importance×decay<0.05→归档; 客户退出→同训练数据一并删除(90天) |
| Fact (语义知识) | Neo4j | Neo4j | 导出JSON归档 | 跟随所属项目删除; KSL-0→全量删除; invalidated Fact 保留180天审计 |
| Project Profile | Redis缓存 | — | — | 实时重生成, 不独立保留 |

Episode 删除与机器遗忘联动: KSL-0 项目遗忘时 Episode+Fact 一并删除 (100% 完整)。KSL-1/2 项目遗忘时, 已共享的脱敏 Fact 保留 (DP 保护, 不含原始信息), 原始 Episode 删除。

删除审计: 来源+范围+确认+关联模型标记+完整性声明+时间戳。日志保留 ≥ 3 年。

---

## 8. Phase 0 数据采集计划

### 8.1 逐周计划

```
Week 1-2: 标杆项目选择与基础设施
  选择 5-10 个标杆开源项目 (>5K stars, 活跃CI, Python/Go)
  候选: FastAPI, Gin, Django, Hugo, Terraform, Prometheus, Grafana
  DVC 仓库初始化 + Parquet schema 定义 + GitHub API 采集脚本 + Tree-sitter 解析管线

Week 3-4: Z_impl 数据采集
  目标: 100K commit-level diff。每项目 ~15K commits。AST+CFG 解析→Parquet 入库。
  VectorQualityValidator 首轮验证。交付: Z_impl 数据达标, synthetic_ratio < 30%。

Week 5-6: Z_quality 数据采集
  目标: 50K CI pipeline 记录。数据源: GitHub Actions 日志 API。
  解析: 测试通过率+Cobertura/JaCoCo XML。清洗: 过滤覆盖率=0 项目。

Week 7-8: Z_phys 数据采集 + 合成数据
  目标: 10M 时序数据点。真实: 公开 Prometheus + Grafana demo。
  合成: 噪声注入(高斯/突变/周期异常), is_synthetic=true。Z_phys synthetic_ratio ≤ 60%。

Week 9-10: 质量验证 + 数据版本发布
  VectorQualityValidator 全量验证(3层)。许可证扫描(scancode) + PII检测(Presidio)。
  DVC v1.0 发布。manifest.json 完整(含 synthetic_ratio)。
  交付: R12 AC-1 (最小样本量) + AC-3 (合成占比) + AC-4 (合规)。

负责人: 数据工程师 × 2
阻塞风险: GitHub API 限流 → 申请 higher rate limit
阻塞风险: Prometheus 公开数据不足 → 合成数据占位, Phase 1 替换
```

---

## 9. 训练数据阶段规划

| Phase | Z-Layer | 数据来源 | 目标 |
|-------|---------|---------|------|
| Phase 0 (M1-M4) | Z_impl, Z_quality, Z_phys | 开源GitHub+公开Prometheus+合成 | MVLS 三层 TRL-3 |
| Phase 1 (M5-M7) | +Z_arch, Z_logic | 架构文档+脱敏需求数据 | 核心五层 TRL-3+ |
| Phase 2 (M8-M10) | +Z_biz, Z_val, Z_market | 财报+行业报告+合成+客户数据 | 扩展七层 TRL-2+ |
| Phase 3 (M11+) | 全8层 | 积累真实客户数据 | 全层 TRL-4+ |

---

## 10. 向量质量自动化验证流水线

### 10.1 验证规则引擎

```python
class VectorQualityValidator:
    """自动化向量质量验证。触发: 编码器训练后/增量导入/合成生成/LoRA进化/手动审计。"""
    
    class QualityRules:
        L2_NORM_MIN = 0.5;  L2_NORM_MAX = 2.0
        NAN_RATIO_MAX = 0.0;  ZERO_VECTOR_RATIO_MAX = 0.01
        MIN_VARIANCE_PER_DIM = 0.01;  MAX_AVG_COSINE_SIMILARITY = 0.7
        MIN_PROJECTS = 1000;  MIN_LANGUAGES = 5;  MIN_LAYER_SAMPLE_RATIO = 0.5
    
    def validate_batch(self, vectors, metadata, layer_name) -> ValidationReport:
        # Rule 1: NaN检测(零容忍) → Rule 2: L2范数范围 → Rule 3: 全零向量
        # → Rule 4: 每维方差 → Rule 5: 平均余弦相似度(抽样1000)
    
    def validate_dataset_coverage(self, dataset_manifest) -> ValidationReport:
        # 项目数量 → 编程语言覆盖 → 各层样本数比
```

### 10.2 验证流水线集成

触发源: DVC push钩子 → MLflow callback → LoRA post-check → 手动CLI。结果: PASSED→入库 | WARNING→入库+告警 | FAILED→阻断(NaN硬阻断, L2异常软阻断, 余弦过高→增加VICReg)。

### 10.3 验证报告格式

```json
{
  "report_id": "vqv-2026-03-22-Z_impl-v1.2",
  "layer": "Z_impl", "data_version": "v1.2", "model_version": "codbert-ft-v3",
  "timestamp": "2026-03-22T10:00:00Z", "total_vectors": 105000, "overall_passed": true,
  "checks": [
    {"name": "nan_ratio", "value": 0.0, "threshold": 0.0, "passed": true},
    {"name": "l2_norm_out_of_range", "value": 0.012, "threshold": 0.05, "passed": true},
    {"name": "zero_vector_ratio", "value": 0.002, "threshold": 0.01, "passed": true},
    {"name": "low_variance_dims", "value": 0.03, "threshold": 0.10, "passed": true},
    {"name": "avg_cosine_similarity", "value": 0.52, "threshold": 0.70, "passed": true}
  ]
}
```

---

## 11. 验收标准映射

| AC | 设计支撑 | 验证方法 |
|----|---------|---------|
| R12 AC-1: MVLS 三层最小样本量 | §2.1 + §10.1 validate_dataset_coverage | 数据统计报告 |
| R12 AC-2: 模型-数据版本可追溯 | §5 DVC+MLflow | DVC 回溯测试 |
| R12 AC-3: 合成数据 ≤30% (Z_phys ≤60%) | §4 + §4.1 + §10.2 | 数据标签统计 |
| R12 AC-4: 合规审查通过 | §6 PII+许可证 | 扫描报告 |
| R12 AC-5: 编码器预训练选型文档化 | ARCH §9.2 | 文档评审 |
| R12 AC-6: 客户数据 90 天内删除 | §7 | 删除流程测试 |
| R12 AC-7: KSL-0 遗忘 100% (30天) | EVO §10 | 遗忘测试: 删除→零残留 |
| R12 AC-8: 机器遗忘策略文档评审 | EVO §10 | 文档评审通过 |
