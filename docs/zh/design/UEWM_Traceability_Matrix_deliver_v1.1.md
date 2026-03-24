# 📋 UEWM 需求-设计-验证 追溯矩阵

**文档版本：** deliver-v1.1  
**文档编号：** UEWM-TRACE-011  
**最后更新：** 2026-03-24  
**状态：** 设计完成 — 93 原始 AC + 10 MEM-AC = 103/103 ✅  
**用途：** 确保 Requirements V6.1 的每个验收标准 (AC) 在设计文档中有明确对应，且有可执行的验证方法。  
**合并来源：** Traceability Matrix V2.0 — 更新文档版本引用至 deliver-v1.0

---

## 使用说明

- **Status 列:** ✅ = 设计完成且验证方法明确
- **Phase 列:** 0/1/2/3 = 该 AC 在哪个 Phase 验证
- **Design Ref 列:** 格式为 `文档缩写 §章节号`

---

## R01 — JEPA 基础世界模型 (10 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 8 层 Z-Layer 编码器输出 2048-d 向量 | ARCH §9.1, §9.3 | 编码器单元测试: 输出 shape == (batch, 2048) | 0 | ✅ |
| AC-2 | EBM Kendall τ ≥ 0.5 | ARCH §6.3 | 校准数据集 200 对 + 5-fold 交叉验证 | 0 | ✅ |
| AC-3 | Predictor 1步 MSE<0.15, 3步 MSE<0.3 | ARCH §5.8 | Held-out 20% 项目 (time-based split) | 0 | ✅ |
| AC-4 | MVLS 三层全部 TRL-3 | ARCH §4.3, §4.5 | TRL Evaluator: ARI≥0.3 + 格兰杰 p<0.05 | 0 | ✅ |
| AC-5 | 跨层因果信号保真度 p<0.05 | ARCH §4.5 Stage 2 | 格兰杰因果检验: 每对相邻层 | 0 | ✅ |
| AC-6 | TRL 自动评估+动态降权 | ARCH §4.3 | 注入低 ARI → 验证 EBM 降权 | 0 | ✅ |
| AC-7 | 编排模块输出任务排序+健康度 | ARCH §3.3, ENG §2.6 | 集成测试: 输入 Z-Layer → 输出排序+健康度 | 0 | ✅ |
| AC-8 | 编码器预训练选型论证 | ARCH §9.2 | 文档评审: 每编码器有选型/替代/否决 | 0 | ✅ |
| AC-9 | 多项目并发无饥饿 | ARCH §3.4 | 负载测试: 5项目 → 最大等待 < Tier-2 SLO | 1 | ✅ |
| AC-10 | Per-Tenant 配额排队 | ARCH §3.4 | 集成测试: 超配额 → QUEUED 不超 Tier SLO | 1 | ✅ |

## R02 — Agent 体系 (10 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 内环 5 Agent LOA≥7 | AGENT §2, §3 | 端到端: Code→Test→Deploy→Monitor 闭环 | 0 | ✅ |
| AC-2 | 中环 3 Agent LOA≥5 | AGENT §11.2 | 演示: AG-SA/FD/AU TRL-3下 LOA≥5 | 1 | ✅ |
| AC-3 | 外环 4 Agent LOA≥3 | AGENT §11.3 | 演示: AG-PA/PD/BI/PR TRL-2下 LOA≥3 | 2 | ✅ |
| AC-4 | LOA 3↔8 自动切换 | AGENT §3 | 注入 TRL 变化 → LOA 自动重计算 | 0 | ✅ |
| AC-5 | Brain 不可用→规则引擎 | AGENT §4 | Kill Brain pod → Agent 规则引擎验证 | 0 | ✅ |
| AC-6 | 统一 EIP 协议交互 | EIP §4, AGENT §9.4 | 12 Agent EipVerb 闭环测试 | 0 | ✅ |
| AC-7 | 交接门可配置 | AGENT §5 | 配置交接门参数 → 验证评估逻辑 | 1 | ✅ |
| AC-8 | LOA 降级 30s 内级联 | AGENT §5.2, ENG §2.5 | 注入 LOA 降级 → 测量评估延迟 | 0 | ✅ |
| AC-9 | 产物版本 60s 内告警 | AGENT §8 | 提交不一致版本 → 测量告警延迟 | 0 | ✅ |
| AC-10 | 执行引擎选型论证 | AGENT §6 | 文档评审: 每 Agent 有引擎+成本 | 0 | ✅ |

## R03 — 自进化 (7 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 惊奇度→LoRA→惊奇度↓ | EVO §2, §2.5 | 注入高惊奇度 → 进化 → 惊奇度下降 | 0 | ✅ |
| AC-2 | 漂移检测 > 90% | EVO §3, §3.4 | 注入已知漂移 → 测量检测率 | 0 | ✅ |
| AC-3 | 版本可追溯回滚 | EVO §4.6, DEPLOY §8.2 | 回滚→功能恢复 < 2min | 0 | ✅ |
| AC-4 | 安全包络 100% 执行 | EVO §4.7 | 注入超包络 → 验证回滚 | 0 | ✅ |
| AC-5 | 连续失败熔断 | EVO §4.8 | 3次回滚 → 断路器 OPEN + 48h | 0 | ✅ |
| AC-6 | 帕累托 > 80% | EVO §4.9 | 30天统计: 帕累托命中率 | 1 | ✅ |
| AC-7 | 30天无跷跷板 | EVO §4.12 | SeesawMonitor 30天: 无层退化>3次 | 1 | ✅ |

## R04 — 安全治理 (8 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 越权 100% 拦截 | SEC §4.4, §4.5 | 717测试: 全部越权拦截 | 0 | ✅ |
| AC-2 | 高风险须审批 | SEC §5, §5.2 | CRITICAL → 审批流程触发 | 0 | ✅ |
| AC-3 | 审计完整可查 | SEC §7, §7.3 | 全链路 → 审计日志查询 | 0 | ✅ |
| AC-4 | KSL-0 零泄露 | SEC §10, EVO §5.5 | 审计全量扫描: 参与记录=0 | 1 | ✅ |
| AC-5 | T1-T5 渗透通过 | SEC §14 | 23项渗透测试全部通过 | 0/1 | ✅ |
| AC-6 | RBAC 可配置审计 | SEC §4 | 权限变更 → 审计日志 | 0 | ✅ |
| AC-7 | mTLS+签名+链 | SEC §12 | 证书轮换+签名验证+链完整性 | 0 | ✅ |
| AC-8 | SOC2 TypeI就绪 | SEC §11.3 | 8控制点评审通过 | 0 | ✅ |

## R05 — 部署运维 (9 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | Profile-M P99<500ms@50并发 | DEPLOY §4.1, §12.3 | k6 50并发 60min | 0 | ✅ |
| AC-2 | 故障 <30s 自愈 | DEPLOY §8.1, §12.5 | 混沌: Kill pod | 0 | ✅ |
| AC-3 | CI/CD 全自动化 | ENG §6.3, DEPLOY §7 | 端到端演示 | 0 | ✅ |
| AC-4 | S/M/L 分别通过 SLO | DEPLOY §12.2-12.4 | 三Profile独立测试 | 0/1/2 | ✅ |
| AC-5 | S→L 仅加资源 | DEPLOY §10, §13 | 配置差异审查+升级手册 | 2 | ✅ |
| AC-6 | 错误预算仪表盘 | DEPLOY §5.1 | 预算+burn-rate+级别 | 0 | ✅ |
| AC-7 | L2 进化暂停 <30s | DEPLOY §5.2, §3.3, §12.3 | SLO超标 → 暂停延迟 | 0 | ✅ |
| AC-8 | L3 动作 <60s | DEPLOY §5.2, §12.3 | 预算低 → 动作延迟 | 0 | ✅ |
| AC-9 | LLM 成本合规 | DEPLOY §6, INTEG §3 | 30天 ≤ $5,000 | 1 | ✅ |

## R06 — 自反省 (4 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 定时报告自动生成 | EVO §6, ENG §2.9 | Cron → 报告生成 | 1 | ✅ |
| AC-2 | 偏差检出 > 80% | EVO §6.5 | 50注入检出≥40 | 1 | ✅ |
| AC-3 | 结果注入进化引擎 | EVO §6 | 反省→LoRA→改善 | 1 | ✅ |
| AC-4 | 误报率 < 20% | EVO §6.5 | 20对照误报≤4 | 1 | ✅ |

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
| AC-1 | Portal提交建议 | AGENT §10.5 | API: POST suggest | 0 | ✅ |
| AC-2 | Agent转发Brain | EIP §3.3, §4.5.8 | 端到端: 建议→分析→返回 | 0 | ✅ |
| AC-3 | Agent等待命令 | AGENT §9.2, §9.3 | 状态机: AWAITING+超时 | 0 | ✅ |
| AC-4 | 权限校验 | SEC §4.4 | 非授权→拒绝 | 0 | ✅ |
| AC-5 | LOA自动调整 | AGENT §3 | TRL变→LOA重算→行为切换 | 0 | ✅ |
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

## R11 — EIP 协议 (10 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | IDL完整+兼容 | EIP §4 | protoc + buf lint/breaking | 0 | ✅ |
| AC-2 | 12 Agent集成 | EIP §8, AGENT §9.4 | 每Agent≥1 EipVerb闭环 | 0 | ✅ |
| AC-3 | gRPC P99<SLO | EIP §5, DEPLOY §12 | Profile-M负载测试 | 0 | ✅ |
| AC-4 | Kafka P99<2s | EIP §2.4, §5 | 事件延迟监控 | 0 | ✅ |
| AC-5 | 灰度升级 | EIP §6 | 新旧版本共存 | 1 | ✅ |
| AC-6 | 死信重放 | EIP §5.2 | 注入失败→重放→成功 | 0 | ✅ |
| AC-7 | 无Any | EIP §4 | grep Any = 0 | 0 | ✅ |
| AC-8 | 错误载荷拒绝 | EIP §5.4 | 不匹配→INVALID_PAYLOAD | 0 | ✅ |
| AC-9 | JSON示例完备 | EIP §4.5 | 11个示例覆盖全类型 | 0 | ✅ |
| AC-10 | PERMISSION_DENIED | EIP §4.5.9, §5.4 | 跨Tenant→PERMISSION_DENIED | 0 | ✅ |

## R12 — 训练数据 (8 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | MVLS三层样本量 | DATA §2.1, §10.1 | 数据统计报告 | 0 | ✅ |
| AC-2 | 版本可追溯 | DATA §5 | DVC回溯 | 0 | ✅ |
| AC-3 | 合成≤30%(Z_phys≤60%) | DATA §4, §4.1 | 标签统计 | 0 | ✅ |
| AC-4 | 合规通过 | DATA §6 | 许可证+PII | 0 | ✅ |
| AC-5 | 选型文档化 | ARCH §9.2 | 文档评审 | 0 | ✅ |
| AC-6 | 90天删除 | DATA §7, EVO §10 | 删除流程 | 1 | ✅ |
| AC-7 | KSL-0遗忘100% | EVO §10 | 删除→零残留 | 1 | ✅ |
| AC-8 | 遗忘策略评审 | EVO §10 | 文档评审 | 0 | ✅ |

## R13 — 外部集成 (4 ACs)

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| AC-1 | 内环5适配器 | AGENT §7.2, INTEG §5 | 每适配器操作闭环 | 0 | ✅ |
| AC-2 | 工具切换 | AGENT §7.1, INTEG §2.1 | GitHub→GitLab热切换 | 0 | ✅ |
| AC-3 | 故障降级 | AGENT §4, INTEG §5 | Git不可用→LOA≤4 | 0 | ✅ |
| AC-4 | 凭证Vault | INTEG §4 | Vault审计+无硬编码 | 0 | ✅ |

## NFR 验证 (11 项)

| NFR | 描述 | Design Ref | 验证方法 | Phase | Status |
|-----|------|-----------|---------|-------|--------|
| NFR-1 | Brain P99各Profile | ARCH §7.5, DEPLOY §12 | 负载测试 | 0/1/2 | ✅ |
| NFR-2 | 可用性99.95%/99.99% | DEPLOY §4.4, §12 | 48-72h | 0/1 | ✅ |
| NFR-3 | S→L仅加资源 | DEPLOY §10, §13, ARCH §3.6 | 扩展测试 | 2 | ✅ |
| NFR-4 | mTLS全链路 | SEC §12, EIP §7 | TLS+轮换 | 0 | ✅ |
| NFR-5 | 审计≥1年 | SEC §7.2 | 存储策略+查询SLO | 0 | ✅ |
| NFR-6 | <30s自愈, <2min回滚 | DEPLOY §8, §12.5 | 混沌测试 | 0 | ✅ |
| NFR-7 | KSL-0零泄露 | SEC §10 | 审计全量扫描 | 1 | ✅ |
| NFR-8 | 决策全链路审计 | SEC §7, DEPLOY §9 | 决策→日志→多维查询 | 0 | ✅ |
| NFR-9 | GPU推理优先 | DEPLOY §3.3 | GPU争用P99<600ms | 0 | ✅ |
| NFR-10 | 产物版本化 | AGENT §8, §8.3 | CRUD+版本查询 | 0 | ✅ |
| NFR-11 | Hot/Warm/Cold | SEC §7.2, DEPLOY §12 | Hot<2s, Warm<30s | 0 | ✅ |

## Long Memory — 长期记忆 (10 ACs) [deliver-v1.1 新增]

| AC | 描述 | Design Ref | 验证方法 | Phase | Status |
|----|------|-----------|---------|-------|--------|
| MEM-AC-1 | Episode 自动创建 (5 种触发) | ARCH §12.3, EVO §2/§7/§11 | 10 种触发→Episode 存储完整 | 0 | ✅ |
| MEM-AC-2 | 相似度检索 P99 < 200ms | ARCH §12.7, ENG §2.14 | pgvector ANN 向量检索+相关度 | 0 | ✅ |
| MEM-AC-3 | 事实自动提取 (≥3 Episode→Fact) | ARCH §12.4 | 注入一致模式→Fact 生成, 置信度>0.7 | 1 | ✅ |
| MEM-AC-4 | 矛盾自动解决 | ARCH §12.4 | 注入矛盾数据→旧 Fact invalidated | 1 | ✅ |
| MEM-AC-5 | 衰减归档 (90 天低重要性) | ARCH §12.3, DEPLOY §11.3 | 时间模拟→验证归档 | 1 | ✅ |
| MEM-AC-6 | Project Profile 生成 < 50ms | ARCH §12.6 | 性能测试+内容完整 (static/dynamic/risk) | 0 | ✅ |
| MEM-AC-7 | KSL-0 记忆完全隔离 | ARCH §12.8, SEC §8.4 | 跨项目 RECALL 返回零结果 | 1 | ✅ |
| MEM-AC-8 | 记忆增强决策质量 | ARCH §12.6, ENG §2.14 | A/B: 有记忆 vs 无记忆, Kendall τ ≥ +0.05 | 2 | ✅ |
| MEM-AC-9 | 巩固 < 30min 不影响 SLO | ARCH §12.5, DEPLOY §11.2 | 巩固期间 Brain P99 监控 | 1 | ✅ |
| MEM-AC-10 | 回忆影响可审计 | ARCH §12.7, SEC §8.4 | MemoryInfluence 字段审计日志验证 | 0 | ✅ |

---

## 文档缩写对照 (deliver-v1.1 版本)

| 缩写 | 全称 | 版本 |
|------|------|------|
| ARCH | UEWM_Architecture | **deliver-v1.1** (含 §12 长期记忆) |
| AGENT | UEWM_Agents_Design | **deliver-v1.1** (含 RECALL SDK) |
| EVO | UEWM_Self_Evolution | **deliver-v1.1** (含记忆联动) |
| SEC | UEWM_Safety_Governance | **deliver-v1.1** (含 §8.4 记忆安全) |
| ENG | UEWM_Engineering_Spec | **deliver-v1.1** (含 §2.14-2.15 记忆时序图) |
| EIP | UEWM_EIP_Protocol | **deliver-v1.1** (含 RECALL 动词) |
| DATA | UEWM_Data_Strategy | **deliver-v1.1** (含 Episode 生命周期) |
| DEPLOY | UEWM_Deployment_Operations | **deliver-v1.1** (含 §11.2-11.3 记忆运维) |
| INTEG | UEWM_Integration_Map | **deliver-v1.0** (无变更) |
