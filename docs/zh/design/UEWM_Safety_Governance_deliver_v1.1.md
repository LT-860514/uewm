# 🛡️ UEWM 安全边界与治理设计文档

**文档版本：** deliver-v1.1  
**文档编号：** UEWM-SEC-004  
**最后更新：** 2026-03-24  
**状态：** 设计完成（100% 覆盖 R04, NFR-4/5/7/8/11 + Long Memory 安全）  
**合并来源：** Safety Governance V6.0 + Combined Patch + Long Memory KSL 隔离 — 全量合并  
**变更历史：**
- V3.0: 威胁模型T1-T5、RBAC三维矩阵、SOC 2路线图、密钥管理、进化安全审计、审计日志容量
- V4.0: 渗透测试计划
- V5.0: 动态权限执行实现、安全事件响应预案
- V6.0: RBAC全量测试矩阵、审批工作流状态机、审计日志查询API；100% 覆盖达成
- **deliver-v1.0: 全量合并（含动态权限实现+响应预案），无增量补丁依赖**

---

## 1-2. 概述 & 安全分层架构

安全目标: 不越权/不误操作/可追溯/可回滚/不泄露/不退化。五层防御: 网络层(mTLS)→协议层(EIP签名)→业务层(RBAC+EBM)→数据层(KSL+DP)→审计层(签名链)。

---

## 3. UEWM 威胁模型 T1-T5

**T1 Agent注入/劫持:** mTLS双向认证+消息签名+输入异常检测。EBM能量突变>2σ告警→隔离Agent+回滚Z-Buffer。

**T2 LoRA投毒(人工反馈):** 偏见检测(单用户≤30%)+反馈多样性+异常检测。决策多样性熵≥0.6→回滚LoRA+标记可疑反馈。

**T3 跨租户信息泄露:** KSL分级+DP(ε预算)+Secure Aggregation。逆向推导<随机+5%。隐私预算管理器+定期审计。

**T4 提权攻击:** LOA在Brain Core侧强制验证,Agent不可自行声明。操作与LOA不匹配实时告警。

**T5 Brain Core被攻击降级:** Agent侧硬编码操作边界+双签名。Brain健康检查失败→全Agent规则引擎模式。

---

## 4. RBAC 三维映射模型

### 4.1-4.2 权限粒度 & 角色矩阵

7权限: READ/SUGGEST/REQUIRE/OVERRIDE/ABORT/ADMIN/EVOLVE。9角色: PM/ARCHITECT/DEVELOPER/QA/DEVOPS/MARKETING/SECURITY/PROJECT_MANAGER/SYSTEM_ADMIN。完整角色×Agent×权限矩阵已定义。

### 4.3 动态权限规则

LOA≤4→干预降级SUGGEST | CRITICAL→SECURITY联合审批 | 跨Tenant→一律禁止 | EVOLVE→双人确认。

### 4.4 动态权限执行实现 [V5.0]

DynamicPermissionEnforcer 在 EIP Gateway 层执行。优先级: (1)跨Tenant禁止→(2)CRITICAL需SECURITY→(3)LOA≤4降级SUGGEST→(4)EVOLVE双人确认→(5)标准RBAC矩阵。代码级实现含每条规则的具体检查逻辑和PERMISSION_DENIED/REQUIRES_CO_APPROVAL响应。

### 4.5 RBAC 全量测试矩阵 [V6.0]

8角色×12Agents×7权限=672组合。合法~120个(RBAC矩阵内), 越权~552个→100%拦截。动态规则附加45用例。总717测试,零容忍。自动化生成: 解析矩阵→全排列→must_deny/allowed→发EipRequest→验证。每次RBAC变更+每周回归。

---

## 5. 操作风险分级与人工审批门禁

LOW/MEDIUM/HIGH/CRITICAL 四级。CRITICAL→强制双人审批。

### 5.2 审批工作流状态机 [V6.0]

PENDING→ASSIGNED→REVIEWING→APPROVED/REJECTED/EXPIRED。ASSIGNED→ESCALATED(50% SLA未审核)。超时: LOW/MEDIUM→自动批准, HIGH→自动拒绝+告警, CRITICAL→自动拒绝+Kill Switch告警。SLA: LOW 4h, MEDIUM 2h, HIGH 1h, CRITICAL 30min。

---

## 6. EBM 安全能量函数

E_safety 约束: 单层安全+跨层安全+进化安全。与 Architecture §6 对齐。

---

## 7. 审计系统

### 7.1 审计数据模型

JSON: event_id, timestamp, event_type, agent_id, project_id, energy_score, risk_level, decision_summary, latency_ms。

### 7.2 审计日志容量规划

Profile-S: ~1.7GB/天, 1TB年。Profile-M: ~17GB/天, 10TB年。Profile-L: ~78GB/天, 50TB年。

Hot(SSD, 7天, P99<2s) → Warm(HDD/Parquet, 7-90天, P99<30s) → Cold(S3 Glacier+zstd 5:1, 90天+, P99<5min)。自动降温: Hot→Warm 每日02:00, Warm→Cold 每周日02:00。进化日志永久保留。

### 7.3 审计日志查询 API [V6.0]

```
POST /api/audit/query
  Body: {time_range, filters:{agent_id, project_id, event_type, 
         energy_range, risk_level, user_id}, sort, pagination, storage_tier}
  Response: {total, page, results:[{event_id, timestamp, event_type, 
             summary, energy_score, risk_level}], query_latency_ms}

GET /api/audit/{event_id}         # 单条详细
GET /api/audit/stats              # 聚合统计
GET /api/audit/export?format=csv  # 导出(合规用)
```

查询性能: Hot单条<100ms, 时间范围(1h)<2s; Warm单条<5s, 聚合<30s; Cold需恢复请求<5min。

---

## 8-10. 有害行为检测 / 回滚保护 / 数据安全

有害行为分类+防循环+Kill Switch+SafeEvalAgent。回滚粒度(层/全模型/Z-Buffer)+回滚安全检查。差分隐私+逆向检测。

### 8.4 长期记忆安全隔离 [deliver-v1.1 新增]

**KSL 感知 Episode/Fact 隔离规则 (对标 Architecture §12.8):**

KSL-0: Episode+Fact 完全隔离, 跨项目 RECALL 检索返回零结果, 遗忘时 Episode+Fact 一并删除(100%)。KSL-1: 仅共享聚合统计级 Fact(DP ε≤0.5), Episode 快照不跨项目。KSL-2: 共享脱敏后 Pattern/AntiPattern Fact(经 SECURITY/ARCHITECT 审核), Episode 仅共享脱敏 decision_summary。KSL-3: 联邦学习+脱敏 Fact+聚合 Episode 统计(Secure Aggregation)。KSL-4: 同 Tenant 内完全共享 Memory, 跨 Tenant 仍禁止。

**记忆审计:** 每次 RECALL 检索记录审计日志(查询者/项目/返回Episode数/Fact数)。Episode 创建/归档/删除记录完整审计链。MemoryInfluence 字段随 EIP Response 写入决策审计(NFR-8 对标)。

---

## 11. SOC 2 合规路线图

Phase 0→Type I 就绪, Phase 2→Type II 合规。Trust Criteria 映射: Security(RBAC+mTLS+KillSwitch), Availability(99.95%+错误预算), Processing Integrity(EBM+审计链), Confidentiality(KSL+DP), Privacy(GDPR/CCPA+遗忘+PII)。8个CC控制点清单。数据驻留: Z-Layer不跨区域, 区域可配置。

---

## 12. 密钥与证书管理

mTLS证书: ≤90天自动轮换(Vault/内置CA)。LoRA权重: SHA-256签名(MLflow)。审计日志: append-only+每日签名链。密钥: Vault/K8s Secrets(at-rest加密)。外部API: Vault Dynamic Secrets。

---

## 13. 进化安全审计维度

触发前→EVOLVE权限(双人确认)。产出→LoRA签名+日志+对比报告。紧急回滚→SECURITY单人。审计报告→每周自动(进化/回滚/包络触发/偏见)。连续3次回滚→断路器→自动失败分析报告。

---

## 14. 渗透测试计划 [V4.0]

灰盒测试, 独立Staging, Phase 0/1/2+半年度。23项测试: T1(5项:伪造证书/重放/编码偏移/消息篡改/DDoS), T2(4项:单用户偏见/多账户协同/渐进漂移/极端值), T3(5项:跨Tenant查询/梯度逆向/KSL-0泄露/预算绕过/namespace逃逸), T4(4项:伪造LOA/低LOA高风险/绕过审批/EVOLVE单人), T5(4项:Brain越界指令/Brain不可用/响应篡改/异常能量)。时间线: Phase 0 M4 T1+T4+T5(2周), Phase 1 M7 T2+T3(2周), Phase 2+ 全量回归(3周)。

---

## 15. 安全事件响应预案 [V5.0]

4级: SEV-1(Critical,15min) SEV-2(High,1h) SEV-3(Medium,4h) SEV-4(Low,24h)。预案A(Kill Switch): 全停→评估→恢复/隔离→事后。预案B(T1 Agent注入): 告警→隔离→Z-Buffer回滚→证书吊销重发。预案C(T3 数据泄露嫌疑): L3租户隔离→全量审计→联邦暂停→通知Tenant→隐私评估(GDPR 72h)。预案D(T5 Brain被攻击): Agent规则引擎→Brain隔离→镜像重建→LoRA回滚→Z-Buffer恢复→逐环恢复。

---

## 14/附录: ASL 安全等级框架 / Future — 工业功能安全

ASL-1到ASL-4。工业功能安全移至附录(Phase 4+ Future Extension)。

---

## 16. 验收标准映射

| AC | 设计支撑 |
|----|---------|
| AC-1: 越权100%拦截 | §4.4+§4.5(717测试) |
| AC-2: 高风险须审批 | §5+§5.2(状态机) |
| AC-3: 审计完整可查 | §7+§7.3(查询API) |
| AC-4: KSL-0零泄露 | §10 |
| AC-5: T1-T5渗透通过 | §14(23项) |
| AC-6: RBAC可配置审计 | §4 |
| AC-7: mTLS+签名+链 | §12 |
| AC-8: SOC2 TypeI就绪 | §11.3 |
