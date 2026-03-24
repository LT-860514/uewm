# 🔌 UEWM 外部系统集成边界设计文档

**文档版本：** deliver-v1.0  
**文档编号：** UEWM-INTEG-010  
**创建日期：** 2026-03-22  
**最后更新：** 2026-03-23  
**状态：** 设计完成  
**合并来源：** Integration Map V1.0 — 无补丁，原版即完整  
**对标需求：** R13 (全部), R02.10 (执行引擎外部依赖), R05 (LLM 成本管理)

---

## 1. 概述

定义 UEWM 与外部系统的集成边界、适配器架构、故障降级策略和集成测试要求。

### 1.1 系统边界原则

```
UEWM 职责 (编排决策层):
  Brain Core → 决定 WHAT (做什么决策)
  Agent 执行引擎 → 负责 HOW-intelligent (代码生成、架构设计等)
  
外部系统职责 (执行层):
  Git/CI/K8s/Prometheus → 负责 HOW-mechanical (commit/deploy/monitor)
  LLM API → 负责 HOW-generative (文本/代码生成)
  
边界规则:
  ├── UEWM 不替代外部工具，不安装/配置/运维外部工具
  ├── 所有外部调用通过 Adapter Layer 隔离
  ├── Agent 对外部工具的操作权限由 RBAC + Agent LOA 共同约束
  └── 外部工具凭证通过 Vault 管理，不硬编码
```

---

## 2. 集成架构模式

### 2.1 适配器层 (Adapter Layer)

```
Agent ─→ Adapter Interface (抽象) ─→ Adapter Impl (具体工具)
                                       ├── GitHubAdapter
                                       ├── GitLabAdapter  ← 可替换
                                       └── BitbucketAdapter
```

所有适配器实现 `ExternalToolAdapter` 接口 (见 Agents Design §7.1)，提供:
- `execute(command)` — 执行工具操作
- `health_check()` — 健康检查
- `get_dependency_type()` — "required" | "optional"

### 2.2 集成模式分类

| 模式 | 协议 | 适用 | 示例 |
|------|------|------|------|
| 同步 REST/gRPC | HTTP/HTTPS, gRPC | 即时操作 | Git commit, K8s apply |
| 异步 Webhook | HTTP POST 回调 | 事件通知 | CI 完成通知, PR 事件 |
| 异步轮询 | HTTP GET + 指数退避 | 长时操作结果 | CI pipeline 状态 |
| CLI 调用 | 子进程 | 本地工具 | Semgrep, Trivy, PlantUML |
| 流式 API | SSE/WebSocket | 实时数据 | Prometheus 实时查询 |

---

## 3. LLM 外部依赖管理 [对标 R02.10 + R05 Gap-5]

### 3.1 LLM 适配器架构

```python
class LLMAdapter(ExternalToolAdapter):
    """LLM API 适配器 — Agent 执行引擎的 LLM 驱动模式"""
    
    def get_dependency_type(self) -> str: 
        return "required"  # 混合模式 Agent 的 LLM 为必选
    
    async def execute(self, command: LLMCommand) -> LLMResult:
        """按降级链路尝试调用 LLM"""
        for provider in self.degradation_chain:
            try:
                result = await provider.complete(command.prompt, command.max_tokens)
                self.cost_tracker.record(provider.name, result.tokens_used, result.cost)
                return result
            except (TimeoutError, RateLimitError, ServiceUnavailableError):
                continue
        # 所有 LLM 不可用 → 降级为规则引擎
        return LLMResult.DEGRADED(reason="All LLM providers unavailable")
    
    async def health_check(self) -> HealthStatus:
        """检查主 LLM provider 可用性"""
        try:
            await self.primary_provider.complete("test", max_tokens=1)
            return HealthStatus.HEALTHY
        except Exception:
            return HealthStatus.DEGRADED  # 非 UNHEALTHY, 因有降级链

class LLMDegradationChain:
    """LLM 降级链路定义"""
    CHAINS = {
        "AG-CD": [
            {"provider": "openai", "model": "gpt-4o", "cost_per_1k_tokens": 0.005},
            {"provider": "openai", "model": "gpt-4o-mini", "cost_per_1k_tokens": 0.00015},
            {"provider": "local", "model": "codellama-7b", "cost_per_1k_tokens": 0},
            {"provider": "rule_engine", "model": None, "cost_per_1k_tokens": 0},
        ],
        "AG-CT": [
            {"provider": "openai", "model": "gpt-4o-mini", "cost_per_1k_tokens": 0.00015},
            {"provider": "local", "model": "codellama-7b", "cost_per_1k_tokens": 0},
            {"provider": "rule_engine", "model": None, "cost_per_1k_tokens": 0},
        ],
        "AG-DO": [],  # 规则引擎, 无 LLM 依赖
        "AG-ST": [
            {"provider": "openai", "model": "gpt-4o-mini", "cost_per_1k_tokens": 0.00015},
            {"provider": "local", "model": "codellama-7b", "cost_per_1k_tokens": 0},
            {"provider": "rule_engine", "model": None, "cost_per_1k_tokens": 0},
        ],
        "AG-MA": [],  # 规则引擎, 无 LLM 依赖
    }
```

### 3.2 LLM 成本追踪器

```python
class LLMCostTracker:
    """实时追踪 LLM 调用成本, 对标 R05 V6.0-S2"""
    
    def record(self, agent_id, provider, model, tokens, cost):
        """记录单次调用"""
        # 写入时序数据库 (Prometheus counter)
        ...
    
    def check_budget(self, agent_id, task_tier) -> BudgetStatus:
        """检查是否超过成本天花板"""
        PER_TASK_CEILING = {
            "simple": 0.01, "medium": 0.10, "complex": 1.00
        }
        current_task_cost = self.get_current_task_cost(agent_id)
        ceiling = PER_TASK_CEILING[task_tier]
        if current_task_cost >= ceiling:
            return BudgetStatus.EXCEEDED  # → 自动降级为小模型
        elif current_task_cost >= ceiling * 0.8:
            return BudgetStatus.WARNING
        return BudgetStatus.OK
```

---

## 4. 凭证管理 [对标 R13 AC-4]

| 凭证类型 | 管理方式 | 轮换 | 适用 Agent |
|---------|---------|------|-----------|
| Git API Token | Vault Dynamic Secrets | 每 24h | AG-CD |
| CI API Token | Vault Dynamic Secrets | 每 24h | AG-CT |
| K8s ServiceAccount | K8s RBAC + bound token | 自动 | AG-DO, AG-ST |
| Prometheus API Key | Vault KV v2 | 每 90 天 | AG-MA |
| LLM API Key | Vault KV v2 (加密 at-rest) | 每 90 天 | AG-CD, AG-CT, AG-ST |
| Jira/Linear API Token | Vault KV v2 | 每 90 天 | AG-FD |
| SAST Tool License | Vault KV v2 | 按许可证周期 | AG-AU |
| BI 数据库凭证 | Vault Dynamic Secrets | 每 1h (短期租约) | AG-BI |

---

## 5. 外部故障与 Agent LOA 降级联动总表

| Agent | 必选依赖故障 | LOA 影响 | 功能影响 |
|-------|------------|---------|---------|
| AG-CD | Git 不可用 | LOA → ≤4 | 生成 diff 文件供人工提交 |
| AG-CD | LLM 全链路不可用 | LOA → ≤4 | 规则模板生成代码 |
| AG-CT | CI 系统不可用 | LOA → ≤4 | 本地运行测试子集 |
| AG-DO | K8s API 不可用 | LOA → ≤4 | 生成 YAML 供人工 apply |
| AG-MA | Prometheus 不可用 | LOA → ≤4 | K8s metrics-server 基础指标 |
| AG-AU | SAST 工具不可用 | LOA → ≤4 | 标记"未审计"并阻塞交接门 |
| AG-BI | 数据仓库不可用 | LOA → ≤4 | 使用缓存聚合数据 |

---

## 6. 验收标准映射

| AC | 验证方法 |
|----|---------|
| R13 AC-1: 内环 5 Agent 必选适配器全部实现 | 集成测试: 每个适配器至少 1 个操作闭环 |
| R13 AC-2: 工具切换演示 | GitHub→GitLab 适配器热切换, AG-CD 功能不变 |
| R13 AC-3: 外部故障降级正确触发 | 注入 Git 不可用 → AG-CD LOA ≤4 验证 |
| R13 AC-4: 凭证通过 Vault 管理 | Vault 审计日志验证 + 无硬编码扫描 |
