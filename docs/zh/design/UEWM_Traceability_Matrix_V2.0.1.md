# 📋 UEWM 需求-设计-验证 追溯矩阵

**文档版本：** V2.0.1  
**文档编号：** UEWM-TRACE-011  
**最后更新：** 2026-04-02  
**状态：** 设计完成 — 154 / 154 ✅  
**AC 构成:** R01-R13 扩展 (107) + MEM (10) + GPU (6) + EXT (8) + LIC (4) + GND (10) + LeWM (6) + NFR (14) = 154 唯一 AC (去重后)  
**用途：** 确保所有验收标准在 V2.0.1 设计文档中有明确对应且有可执行验证方法。

---

## R01 — JEPA 基础世界模型 (11 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 8 层 Z-Layer 2048-d | ARCH §7.1 | shape==(batch,2048) | 0 | ✅ |
| AC-2 | EBM Kendall τ ≥ 0.5 | ARCH §8.3 | 校准数据集 5-fold | 0 | ✅ |
| AC-3 | Predictor 1步 MSE<0.15 | ARCH §6.5 | Held-out 20% time-split | 0 | ✅ |
| AC-4 | MVLS 三层 TRL-3 | ARCH §7.3 | ARI≥0.3 + Granger p<0.05 | 0 | ✅ |
| AC-5 | 跨层因果 p<0.05 | ARCH §6.4 | Granger 每对相邻层 | 0 | ✅ |
| AC-6 | TRL 动态降权 | ARCH §7.3 | 注入低 ARI → EBM 降权 | 0 | ✅ |
| AC-7 | 编排输出排序+健康度 | ARCH §3.3 | 集成测试 | 0 | ✅ |
| AC-8 | 编码器选型论证 | ARCH §7.1 | 文档评审 | 0 | ✅ |
| AC-9 | 多项目无饥饿 | ARCH §3.4 | 负载测试 | 1 | ✅ |
| AC-10 | Per-Tenant 配额 | ARCH §3.4 | 集成测试 | 1 | ✅ |
| AC-11 | Transformer-XL 非 LLM 论证 | ARCH §6.1 | 文档评审 | 0 | ✅ |

## R02 — Agent 体系 (15 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 内环 5 Agent LOA≥7 | AGENT §2, §3 | 端到端闭环 | 0B | ✅ |
| AC-2 | 中环 3 Agent LOA≥5 | AGENT §11 | 演示 | 1 | ✅ |
| AC-3 | 外环 4 Agent LOA≥3 | AGENT §11 | 演示 | 2 | ✅ |
| AC-4 | LOA 3↔8 自动切换 | AGENT §3 | TRL 变化 → LOA | 0B | ✅ |
| AC-5 | Brain 不可用→规则引擎 | AGENT §4 | Kill Brain → 验证 | 0B | ✅ |
| AC-6 | 统一 EIP 协议 | EIP §3, AGENT §9.5 | 12 Agent 闭环 | 0B | ✅ |
| AC-7 | 交接门可配置 | AGENT §5 | 配置→验证 | 1 | ✅ |
| AC-8 | LOA 降级 30s 级联 | AGENT §5 | 注入→测延迟 | 0B | ✅ |
| AC-9 | 产物版本 60s 告警 | AGENT §8 | 不一致→告警 | 0B | ✅ |
| AC-10 | 执行引擎选型论证 | AGENT §6 | 文档评审 | 0B | ✅ |
| AC-11 | 第三方 ADS 合规验证 | AGENT §14 | 三工具验证 | 1 | ✅ |
| AC-12 | UAT 验收工作流 | AGENT §15 | 全流程 | 2 | ✅ |
| AC-13 | Agent 使用 RiskDecomposition | AGENT §9.2 | 集成测试 | 0B | ✅ |
| AC-14 | Agent 查询 G-Space | AGENT §9.5 | QUERY_GSPACE | 0B | ✅ |
| AC-15 | Agent 订阅 DISCOVERY_ALERT | AGENT §9.2 | 事件接收 | 1 | ✅ |

## R03 — 自进化 (9 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 惊奇度→LoRA→惊奇度↓ | EVO §2 | 注入→进化→下降 | 0B | ✅ |
| AC-2 | 漂移检测 >90% | EVO §3 | 注入已知漂移 | 0B | ✅ |
| AC-3 | 版本可追溯回滚 | EVO §4.6 | 回滚 < 2min | 0B | ✅ |
| AC-4 | 安全包络 100% | EVO §4.7 | 注入超包络→回滚 | 0B | ✅ |
| AC-5 | 连续失败熔断 | EVO §4.8 | 3次→OPEN+48h | 0B | ✅ |
| AC-6 | 帕累托 >80% | EVO §4.9 | 30天统计 | 1 | ✅ |
| AC-7 | 30天无跷跷板 | EVO §4.12 | SeesawMonitor | 1 | ✅ |
| AC-8 | 仅 REAL_SURPRISE 触发进化 | EVO §2.2 | Z_NOISE 不触发验证 | 0B | ✅ |
| AC-9 | 一致性损失 post_check | EVO §4.7 | φ R² 不退化 | 0B | ✅ |

## R04 — 安全治理 (14 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 越权 100% 拦截 | SEC §4.5 | 测试矩阵 | 0B | ✅ |
| AC-2 | 高风险须审批 | SEC §5 | CRITICAL→审批 | 0B | ✅ |
| AC-3 | 审计完整可查 | SEC §7 | 全链路审计 | 0B | ✅ |
| AC-4 | KSL-0 零泄露 | SEC §10 | 全量扫描 | 1 | ✅ |
| AC-5 | T1-T6 渗透通过 | SEC §14 | 28 项通过 | 0B/1 | ✅ |
| AC-6 | RBAC 可配置审计 | SEC §4 | 变更→日志 | 0B | ✅ |
| AC-7 | mTLS+签名+链 | SEC §12 | 证书+签名 | 0B | ✅ |
| AC-8 | SOC2 TypeI 就绪 | SEC §11 | 8控制点 | 0B | ✅ |
| AC-9 | THIRD_PARTY 越权拦截 | SEC §4.3 | 第三方测试 | 1 | ✅ |
| AC-10 | 第三方强制审计 | SEC §4.3 | 审计验证 | 1 | ✅ |
| AC-11 | T6 G-Space 篡改防御 | SEC §3 T6 | 渗透测试 | 0B | ✅ |
| AC-12 | Discovery 审核权限 | SEC §4.4 | 权限验证 | 1 | ✅ |
| AC-13 | G-Space 采集审计 | SEC §7.4 | 审计日志 | 0B | ✅ |
| AC-14 | 28 项渗透测试通过 | SEC §14.1 | 全部通过 | 1 | ✅ |

## R05 — 部署运维 (13 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Profile-M P99<500ms@50并发 | DEPLOY §4.1, §12.3 | k6 50并发 60min | 0B | ✅ |
| AC-2 | 故障 <30s 自愈 | DEPLOY §8.1, §12.5 | 混沌: Kill pod | 0B | ✅ |
| AC-3 | CI/CD 全自动化 | ENG §6.3, DEPLOY §7 | 端到端演示 | 0B | ✅ |
| AC-4 | S/M/L 分别通过 SLO | DEPLOY §12.2-12.4 | 三Profile独立测试 | 0B/1/2 | ✅ |
| AC-5 | S→L 仅加资源 | DEPLOY §10, §13 | 配置差异审查+升级手册 | 2 | ✅ |
| AC-6 | 错误预算仪表盘 | DEPLOY §5.1 | 预算+burn-rate+级别 | 0B | ✅ |
| AC-7 | L2 进化暂停 <30s | DEPLOY §5.2, §3.3, §12.3 | SLO超标 → 暂停延迟 | 0B | ✅ |
| AC-8 | L3 动作 <60s | DEPLOY §5.2, §12.3 | 预算低 → 动作延迟 | 0B | ✅ |
| AC-9 | LLM 成本合规 | DEPLOY §6, INTEG §3 | 30天 ≤ $5,000 | 1 | ✅ |
| AC-10 | 社区版独立部署 | DEPLOY §15 | Profile-S 闭环 | 1 | ✅ |
| AC-11 | G-Space 采集 P99 < 500ms | DEPLOY §12.8 | 性能测试 | 0B | ✅ |
| AC-12 | φ 解码 P99 < 50ms | DEPLOY §12.8 | 性能测试 | 0B | ✅ |
| AC-13 | PoC 可本地部署运行 | DEPLOY §17 | Mac/RTX 验证 | 0A | ✅ |

## R06 — 自反省 (5 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 定时报告自动生成 | EVO §6, ENG §2.9 | Cron → 报告生成 | 1 | ✅ |
| AC-2 | 偏差检出 > 80% | EVO §6.5 | 50注入检出≥40 | 1 | ✅ |
| AC-3 | 结果注入进化引擎 | EVO §6 | 反省→LoRA→改善 | 1 | ✅ |
| AC-4 | 误报率 < 20% | EVO §6.5 | 20对照误报≤4 | 1 | ✅ |
| AC-5 | 接地健康度维度功能正常 | EVO §6.1 | 6子指标验证 | 0B | ✅ |

## R07 — 多租户 (6 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 多团队多项目独立 | ARCH §3.6, DEPLOY §3 | 多Tenant并行 | 1 | ✅ |
| AC-2 | 团队级LoRA互不干扰 | EVO §5 | 修改A→B不受影响 | 1 | ✅ |
| AC-3 | 数据隔离审计 | SEC §10 | 跨Tenant全部拦截 | 1 | ✅ |
| AC-4 | KSL共存隔离 | EVO §5.5, SEC §14 | KSL-0审计=0 | 1 | ✅ |
| AC-5 | 并发仲裁无饥饿 | ARCH §3.4 | 最大等待<Tier-2 | 1 | ✅ |
| AC-6 | 配额排队 | ARCH §3.4 | 超配额→排队不影响他人 | 1 | ✅ |

## R08 — 知识迁移 (7 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 跨项目可迁移 | EVO §5 | 新项目接收→TRL提升 | 2 | ✅ |
| AC-2 | 冷启动缩短≥50% | EVO §5.7, ENG §5.7 | 5项目基线 vs 迁移 | 2 | ✅ |
| AC-3 | 联邦不泄露 | EVO §5.5, SEC §14 | 逆向<随机+5% | 2 | ✅ |
| AC-4 | KSL-0零泄露 | SEC §10 | 审计全量扫描 | 1 | ✅ |
| AC-5 | DP证明 | EVO §5.5, §5.6 | DP参数+组合定理 | 2 | ✅ |
| AC-6 | 隐私预算精确 | EVO §5.6 | 耗尽→阻断+告警 | 1 | ✅ |
| AC-7 | 联邦≥85% | EVO §5.8 | A/B(≥10项目) B/A≥0.85 | 2 | ✅ |

## R09 — 人工干预 (8 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Portal提交建议 | AGENT §10.5 | API: POST suggest | 0B | ✅ |
| AC-2 | Agent转发Brain | EIP §3.3, §4.5.8 | 端到端: 建议→分析→返回 | 0B | ✅ |
| AC-3 | Agent等待命令 | AGENT §9.2, §9.3 | 状态机: AWAITING+超时 | 0B | ✅ |
| AC-4 | 权限校验 | SEC §4.4 | 非授权→拒绝 | 0B | ✅ |
| AC-5 | LOA自动调整 | AGENT §3 | TRL变→LOA重算→行为切换 | 0B | ✅ |
| AC-6 | PM查看12 Agent | AGENT §10.2 | Dashboard API | 1 | ✅ |
| AC-7 | PM干预编排 | AGENT §10.2 | 调整优先级→编排响应 | 1 | ✅ |
| AC-8 | PM权限边界 | AGENT §10.2 | 修改LOA→拒绝 | 1 | ✅ |

## R10 — 人工反馈学习 (6 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 经验录入Buffer | EVO §7 | 干预→Buffer记录 | 1 | ✅ |
| AC-2 | 一致率≥60%/75% | EVO §7.8 | 月度测量≥50样本 | 1/2 | ✅ |
| AC-3 | 干预↓30% | EVO §7.8 | 月度频率对比 | 2 | ✅ |
| AC-4 | 恶意拦截>95% | EVO §7.9 | 40恶意中≥38拦截 | 1 | ✅ |
| AC-5 | 能量上升回滚 | EVO §7.7 | 注入→48h回滚 | 1 | ✅ |
| AC-6 | 单用户≤30% | EVO §4.10, §7.7 | BiasDetector验证 | 1 | ✅ |

## R11 — EIP 协议 (15 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | IDL完整+兼容 | EIP §4 | protoc + buf lint/breaking | 0B | ✅ |
| AC-2 | 12 Agent集成 | EIP §8, AGENT §9.4 | 每Agent≥1 EipVerb闭环 | 0B | ✅ |
| AC-3 | gRPC P99<SLO | EIP §5, DEPLOY §12 | Profile-M负载测试 | 0B | ✅ |
| AC-4 | Kafka P99<2s | EIP §2.4, §5 | 事件延迟监控 | 0B | ✅ |
| AC-5 | 灰度升级 | EIP §6 | 新旧版本共存 | 1 | ✅ |
| AC-6 | 死信重放 | EIP §5.2 | 注入失败→重放→成功 | 0B | ✅ |
| AC-7 | 无Any | EIP §4 | grep Any = 0 | 0B | ✅ |
| AC-8 | 错误载荷拒绝 | EIP §5.4 | 不匹配→INVALID_PAYLOAD | 0B | ✅ |
| AC-9 | JSON示例完备 | EIP §4.5 | 12个示例覆盖全类型 | 0B | ✅ |
| AC-10 | PERMISSION_DENIED | EIP §4.5.9, §5.4 | 跨Tenant→PERMISSION_DENIED | 0B | ✅ |
| AC-11 | 第三方注册协议 | EIP §9 | 注册闭环 | 1 | ✅ |
| AC-12 | REST 网关转换 | EIP §10 | 7 动词验证 | 1 | ✅ |
| AC-13 | RiskDecomposition 字段 | EIP §4 V2.0 | EVALUATE 响应 | 0B | ✅ |
| AC-14 | GSpacePrediction 字段 | EIP §4 V2.0 | PREDICT 响应 | 0B | ✅ |
| AC-15 | DISCOVERY 事件可接收 | EIP §4 V2.0 | Kafka→Agent | 1 | ✅ |

## R12 — 训练数据 (12 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | MVLS三层样本量 | DATA §2.1, §10.1 | 数据统计报告 | 0B | ✅ |
| AC-2 | 版本可追溯 | DATA §5 | DVC回溯 | 0B | ✅ |
| AC-3 | 合成≤30%(Z_phys≤60%) | DATA §4, §4.1 | 标签统计 | 0B | ✅ |
| AC-4 | 合规通过 | DATA §6 | 许可证+PII | 0B | ✅ |
| AC-5 | 选型文档化 | ARCH §7.1 | 文档评审 | 0B | ✅ |
| AC-6 | 90天删除 | DATA §7, EVO §10 | 删除流程 | 1 | ✅ |
| AC-7 | KSL-0遗忘100% | EVO §10 | 删除→零残留 | 1 | ✅ |
| AC-8 | 遗忘策略评审 | EVO §10 | 文档评审 | 0B | ✅ |
| AC-9 | 编码器缓存减少 GPU ≥50% | DATA §10.5 | A/B 对比 | 0B | ✅ |
| AC-10 | G-Space 采集完整性 ≥80% | DATA §10.6 | 采集率监控 | 0B | ✅ |
| AC-11 | Z-G 数据对齐率 ≥90% | DATA §10.6 | 对齐检查 | 0B | ✅ |
| AC-12 | PoC 数据集交付 | DATA §8.1 | 完整性检查 | 0A | ✅ |

## R13 — 外部集成 (11 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 内环5适配器 | AGENT §7.2, INTEG §5 | 每适配器操作闭环 | 0B | ✅ |
| AC-2 | 工具切换 | AGENT §7.1, INTEG §2.1 | GitHub→GitLab热切换 | 0B | ✅ |
| AC-3 | 故障降级 | AGENT §4, INTEG §5 | Git不可用→LOA≤4 | 0B | ✅ |
| AC-4 | 凭证Vault | INTEG §4 | Vault审计+无硬编码 | 0B | ✅ |
| AC-5 | 第三方 Agent 凭证隔离 | INTEG §6.1 | Vault namespace 隔离验证 | 1 | ✅ |
| AC-6 | 第三方 Agent 网络隔离 | INTEG §6.1 | NetworkPolicy: 无法访问 uewm-data | 1 | ✅ |
| AC-7 | 第三方异常数据拦截 | INTEG §6.2 | 注入异常向量 → VQV 拦截 | 1 | ✅ |
| AC-8 | G-Space Prometheus 闭环 | INTEG §5.2 | ops.* 验证 | 0B | ✅ |
| AC-9 | G-Space GitHub API 闭环 | INTEG §5.2 | code.* 验证 | 0B | ✅ |
| AC-10 | G-Space 数据源故障降级 | INTEG §5.2 | Kill→stale 验证 | 0B | ✅ |
| AC-11 | 第三方 G-Space 查询 | INTEG §6.3 | QUERY_GSPACE 验证 | 1 | ✅ |

## MEM — 长期记忆 (10 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| MEM-AC-1 | Episode 自动创建 (5 种触发) | ARCH §12.3, EVO §2/§7/§11 | 10 种触发→Episode 存储完整 | 0B | ✅ |
| MEM-AC-2 | 相似度检索 P99 < 200ms | ARCH §12.7, ENG §2.14 | pgvector ANN 向量检索+相关度 | 0B | ✅ |
| MEM-AC-3 | 事实自动提取 (≥3 Episode→Fact) | ARCH §12.4 | 注入一致模式→Fact 生成, 置信度>0.7 | 1 | ✅ |
| MEM-AC-4 | 矛盾自动解决 | ARCH §12.4 | 注入矛盾数据→旧 Fact invalidated | 1 | ✅ |
| MEM-AC-5 | 衰减归档 (90 天低重要性) | ARCH §12.3, DEPLOY §11.3 | 时间模拟→验证归档 | 1 | ✅ |
| MEM-AC-6 | Project Profile 生成 < 50ms | ARCH §12.6 | 性能测试+内容完整 (static/dynamic/risk) | 0B | ✅ |
| MEM-AC-7 | KSL-0 记忆完全隔离 | ARCH §12.8, SEC §8.4 | 跨项目 RECALL 返回零结果 | 1 | ✅ |
| MEM-AC-8 | 记忆增强决策质量 | ARCH §12.6, ENG §2.14 | A/B: 有记忆 vs 无记忆, Kendall τ ≥ +0.05 | 2 | ✅ |
| MEM-AC-9 | 巩固 < 30min 不影响 SLO | ARCH §12.5, DEPLOY §11.2 | 巩固期间 Brain P99 监控 | 1 | ✅ |
| MEM-AC-10 | 回忆影响可审计 | ARCH §12.7, SEC §8.4 | MemoryInfluence 字段审计日志验证 | 0B | ✅ |

## GPU — GPU 优化 (6 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| GPU-AC-1 | 混合精度训练 BF16, 显存减少≥35% | ARCH §13.2 | Profiling: BF16 vs FP32 显存对比 | 0B | ✅ |
| GPU-AC-2 | 梯度检查点显存降低≥50% | ARCH §13.3 | Profiling: 有/无检查点显存对比 | 0B | ✅ |
| GPU-AC-3 | TensorRT 推理延迟降低≥30% | ARCH §13.5 | Benchmark: PyTorch vs TensorRT P99 | 1 | ✅ |
| GPU-AC-4 | 各组件显存不超预算 | ARCH §13.6, ENG §8.1 | nvidia-smi 峰值监控 + 启动检查 | 0B | ✅ |
| GPU-AC-5 | GPU 利用率推理>60% 训练>80% | ARCH §13.7 | Prometheus GPU exporter 30min 采样 | 0B | ✅ |
| GPU-AC-6 | 跨平台 get_device() 功能验证 | ARCH §13.8 | Mac MPS / RTX CUDA / A100 三平台测试 | 0B | ✅ |

## EXT — 第三方 Agent (8 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| EXT-AC-1 | 第三方 Agent 注册流程可用 | ARCH §14.3, EIP §9 | 注册→审核→激活→健康检查闭环 | 1 | ✅ |
| EXT-AC-2 | REST 网关功能闭环 | ARCH §14.5, EIP §10 | REST→gRPC 转换 8 个路径验证 | 1 | ✅ |
| EXT-AC-3 | 资源隔离有效 | ARCH §14.6, INTEG §6 | 超配额→限流 + namespace 隔离验证 | 1 | ✅ |
| EXT-AC-4 | SDK 集成测试通过 | ARCH §14.8, AGENT §16 | Python SDK 注册+PREDICT+EVALUATE+RECALL | 1 | ✅ |
| EXT-AC-5 | ADS 合规工具可用 | ARCH §14.7, AGENT §14 | uewm-agent-lint/test/certify 三工具 | 1 | ✅ |
| EXT-AC-6 | 自定义 Z-Layer 注册 (Phase 3) | ARCH §14.4 | 自定义编码器→VQV 验证→入 Z-Buffer | 3 | ✅ |
| EXT-AC-7 | THIRD_PARTY RBAC 拦截 100% | SEC §4.3, ARCH §14.3 | 越权请求全部拦截 | 1 | ✅ |
| EXT-AC-8 | Standalone API 功能验证 | ARCH §15.2, ENG §8.4 | 无 Agent 部署→直接 predict/evaluate | 1 | ✅ |

## LIC — 许可证 (4 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| LIC-AC-1 | AGPL/Apache 许可边界清晰 | ARCH §16.2 | 许可证扫描: 每组件许可正确 | 0B | ✅ |
| LIC-AC-2 | 社区版功能完整可用 | ARCH §16.3, DEPLOY §15.2 | 社区版 Profile-S 独立部署验证 | 1 | ✅ |
| LIC-AC-3 | CLA 工作流自动化 | ARCH §16.4 | PR→CLA Bot→签署→合并 | 0B | ✅ |
| LIC-AC-4 | Feature Flag 隔离验证 | ARCH §16.3, ENG §7.3 | 社区版禁用商业 Flag 后功能正常 | 1 | ✅ |

## GND — 双空间锚定 (10 ACs, V2.0 全新)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| GND-AC-1 | G-Space ≥80 指标, >95% 采集率 | ARCH §4.2, DEPLOY §11.4 | 采集健康仪表盘 | 0B | ✅ |
| GND-AC-2 | φ R² > 0.2 for ≥3 指标组 | ARCH §5.2 | 逐维度 R² 报告 | 0A | ✅ |
| GND-AC-3 | 一致性损失收敛 | ARCH §5.4 | 训练曲线 | 0A | ✅ |
| GND-AC-4 | 双空间惊奇度分类 ≥80% | ARCH §9.2, EVO §2.1 | 100 事件人工检查 | 0B | ✅ |
| GND-AC-5 | Discovery 90天 ≥1 有效模式 | ARCH §9.3 | 人工审核 | 1 | ✅ |
| GND-AC-6 | Z 超越 G 独立预测 (p<0.05) | ARCH §9, §16.1 | A/B 对比 | 0A | ✅ |
| GND-AC-7 | 接地健康度 6 子指标正常 | ARCH §11.2, EVO §6.1 | 全部计算+报告 | 0B | ✅ |
| GND-AC-8 | 风险分解覆盖 ≥70% energy | ARCH §8.2 | explained/total | 0B | ✅ |
| GND-AC-9 | G-Space Phase 1 增长 ≥5 指标 | ARCH §9.4 | 发现日志 | 1 | ✅ |
| GND-AC-10 | PoC Gate Review 全部通过 | ARCH §16.1 | ARI+φR²+p-value | 0A | ✅ |

## NFR (14 项)

| NFR | 描述 | Design Ref | 验证方法 | Phase | Status |
|-----|------|-----------|---------|-------|--------|
| NFR-1 | Brain P99各Profile | ARCH §7.5, DEPLOY §12 | 负载测试 | 0B/1/2 | ✅ |
| NFR-2 | 可用性99.95%/99.99% | DEPLOY §4.4, §12 | 48-72h无人守护 | 0B/1 | ✅ |
| NFR-3 | S→L仅加资源 | DEPLOY §10, §13, ARCH §3.6 | 扩展测试 | 2 | ✅ |
| NFR-4 | mTLS全链路 | SEC §12, EIP §7 | TLS+轮换 | 0B | ✅ |
| NFR-5 | 审计≥1年 | SEC §7.2 | 存储策略+查询SLO | 0B | ✅ |
| NFR-6 | <30s自愈, <2min回滚 | DEPLOY §8, §12.5 | 混沌测试 | 0B | ✅ |
| NFR-7 | KSL-0零泄露 | SEC §10 | 审计全量扫描 | 1 | ✅ |
| NFR-8 | 决策全链路审计 | SEC §7, DEPLOY §9 | 决策→日志→多维查询 | 0B | ✅ |
| NFR-9 | GPU推理优先 | DEPLOY §3.3 | GPU争用P99<600ms | 0B | ✅ |
| NFR-10 | 产物版本化 | AGENT §8, §8.3 | CRUD+版本查询 | 0B | ✅ |
| NFR-11 | Hot/Warm/Cold | SEC §7.2, DEPLOY §12 | Hot<2s, Warm<30s | 0B | ✅ |
| NFR-12 | GPU 显存预算合规 | ARCH §12 | VRAM 监控 | 0B | ✅ |
| NFR-13 | 第三方注册 SLO < 5min | ARCH §13 | 注册→激活 | 1 | ✅ |
| NFR-14 | Standalone API P99 < 300ms | ARCH §14 | 独立部署 | 1 | ✅ |

---

## LeWM — LeWorldModel 集成 (6 ACs, V2.0.1 全新)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| LeWM-AC-1 | SIGReg 防崩溃 (正态性检验通过) | ARCH §5.4 | Epps-Pulley p > 0.05 on 100 投影 | 0A | ✅ |
| LeWM-AC-2 | 探测恢复 G-Space 指标 (linear r > 0.6) | ARCH §16.1 | 逐维度 linear + MLP 探测报告 | 0A | ✅ |
| LeWM-AC-3 | VoE 检测异常事件 (AUC > 0.80) | ARCH §16.1 | 50 正常 + 50 异常 ROC 曲线 | 0A | ✅ |
| LeWM-AC-4 | 投影头改善训练稳定性 | ARCH §5.5 | 有 vs 无投影头消融对比 | 0A | ✅ |
| LeWM-AC-5 | 双项损失收敛平滑单调 | ARCH §5.4 | 训练曲线视觉检查 + 方差分析 | 0A | ✅ |
| LeWM-AC-6 | 时间直化自然涌现 | ARCH §16.1 | 连续速度向量 cosine sim > 0.5 | 0B | ✅ |

---

## AC 统计

| 类别 | deliver-v1.1 | V1.0.1 | V2.0.0 | V2.0.1 | V2.0.1 新增 |
|------|-------------|--------|--------|--------|------------|
| R01 JEPA | 10 | 11 | 11 | 11 | 0 |
| R02 Agent | 10 | 12 | 15 | 15 | 0 |
| R03 进化 | 7 | 7 | 9 | 9 | 0 |
| R04 安全 | 8 | 10 | 14 | 14 | 0 |
| R05 部署 | 9 | 10 | 13 | 13 | 0 |
| R06 反省 | 4 | 4 | 5 | 5 | 0 |
| R07 多租户 | 6 | 6 | 6 | 6 | 0 |
| R08 知识迁移 | 7 | 7 | 7 | 7 | 0 |
| R09 人工干预 | 8 | 8 | 8 | 8 | 0 |
| R10 反馈学习 | 6 | 6 | 6 | 6 | 0 |
| R11 EIP | 10 | 12 | 15 | 15 | 0 |
| R12 数据 | 8 | 9 | 12 | 12 | 0 |
| R13 集成 | 4 | 7 | 11 | 11 | 0 |
| MEM 长期记忆 | 10 | 10 | 10 | 10 | 0 |
| GPU 优化 | 0 | 6 | 6 | 6 | 0 |
| EXT 第三方 | 0 | 8 | 8 | 8 | 0 |
| LIC 许可证 | 0 | 4 | 4 | 4 | 0 |
| GND 双空间 | 0 | 0 | 10 | 10 | 0 |
| **LeWM 集成** | **0** | **0** | **0** | **6** | **+6** |
| NFR | 11 | 14 | 14 | 14 | 0 |
| **总计** | **103** | **134** | **148** | **154** | **+6** |

---

## 文档缩写对照 (V2.0.1)

| 缩写 | 全称 | 版本 | V2.0.1 核心变更 |
|------|------|------|-------------|
| ARCH | UEWM_Architecture | V2.0.1 | +SIGReg, +投影头, +自适应隐维度, +VoE 验证, +探测验证 |
| AGENT | UEWM_Agents_Design | V2.0.1 | (V2.0.0 保持) |
| EVO | UEWM_Self_Evolution | V2.0.1 | +SIGReg 安全检查, +VoE 进化验证 |
| SEC | UEWM_Safety_Governance | V2.0.1 | (V2.0.0 保持) |
| ENG | UEWM_Engineering_Spec | V2.0.1 | +SIGReg 训练管线, +探测+VoE PoC 规格, +Gate Review 更新 |
| EIP | UEWM_EIP_Protocol | V2.0.1 | (V2.0.0 保持) |
| DATA | UEWM_Data_Strategy | V2.0.1 | +256-d 数据, +VoE 测试集, +探测数据 |
| DEPLOY | UEWM_Deployment_Operations | V2.0.1 | +PoC 目录含 probes/voe/sigreg |
| INTEG | UEWM_Integration_Map | V2.0.1 | (V2.0.0 保持) |
