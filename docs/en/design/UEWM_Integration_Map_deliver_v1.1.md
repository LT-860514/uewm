# 🔌 UEWM external system integration boundary design document

**Document version:** deliver-v1.0
**Document Number:** UEWM-INTEG-010
**Creation date:** 2026-03-22
**Last update:** 2026-03-23
**Status:** Design completed
**Merge source:** Integration Map V1.0 - No patches, the original version is complete
**Benchmarking requirements:** R13 (all), R02.10 (execution engine external dependencies), R05 (LLM cost management)

---

## 1. Overview

Define UEWM integration boundaries with external systems, adapter architecture, failure degradation strategies, and integration testing requirements.

### 1.1 System Boundary Principle```
UEWM responsibilities (orchestration decision-making level):
  Brain Core → Decide WHAT (What decision to make)
  Agent execution engine → responsible for HOW-intelligent (code generation, architecture design, etc.)
  
External system responsibilities (execution level):
  Git/CI/K8s/Prometheus → responsible for HOW-mechanical (commit/deploy/monitor)
  LLM API → responsible for HOW-generative (text/code generation)
  
Boundary rules:
  ├── UEWM does not replace external tools and does not install/configure/operate external tools.
  ├── All external calls are isolated through Adapter Layer
  ├── Agent’s operation permissions on external tools are jointly restricted by RBAC + Agent LOA
  └── External tool credentials are managed through Vault and are not hard-coded
```---

## 2. Integrated architecture pattern

### 2.1 Adapter Layer```
Agent ─→ Adapter Interface (abstract) ─→ Adapter Impl (concrete tool)
                                       ├── GitHubAdapter
                                       ├── GitLabAdapter ← Replaceable
                                       └── BitbucketAdapter
```All adapters implement the `ExternalToolAdapter` interface (see Agents Design §7.1), providing:
- `execute(command)` — execute tool operation
- `health_check()` — health check
- `get_dependency_type()` — "required" | "optional"

### 2.2 Integrated mode classification

| Pattern | Protocol | Applicable | Example |
|------|------|------|------|
| Synchronization REST/gRPC | HTTP/HTTPS, gRPC | Instant operations | Git commit, K8s apply |
| Asynchronous Webhook | HTTP POST callback | Event notification | CI completion notification, PR event |
| Asynchronous polling | HTTP GET + exponential backoff | Long operation results | CI pipeline status |
| CLI calls | Subprocesses | Local tools | Semgrep, Trivy, PlantUML |
| Streaming API | SSE/WebSocket | Real-time data | Prometheus real-time query |

---

## 3. LLM external dependency management [Benchmark R02.10 + R05 Gap-5]

### 3.1 LLM adapter architecture```python
class LLMAdapter(ExternalToolAdapter):
    """LLM API Adapter — LLM driver mode for Agent execution engine"""
    
    def get_dependency_type(self) -> str: 
        return "required" # LLM of mixed mode Agent is required
    
    async def execute(self, command: LLMCommand) -> LLMResult:
        """Attempt to call LLM on downgraded link"""
        for provider in self.degradation_chain:
            try:
                result = await provider.complete(command.prompt, command.max_tokens)
                self.cost_tracker.record(provider.name, result.tokens_used, result.cost)
                return result
            except (TimeoutError, RateLimitError, ServiceUnavailableError):
                continue
        # All LLMs are unavailable → downgrade to rules engine
        return LLMResult.DEGRADED(reason="All LLM providers unavailable")
    
    async def health_check(self) -> HealthStatus:
        """Check primary LLM provider availability"""
        try:
            await self.primary_provider.complete("test", max_tokens=1)
            return HealthStatus.HEALTHY
        except Exception:
            return HealthStatus.DEGRADED # Not UNHEALTHY, due to downgrade chain

class LLMDegradationChain:
    """LLM degraded link definition"""
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
        "AG-DO": [], # Rule engine, no LLM dependency
        "AG-ST": [
            {"provider": "openai", "model": "gpt-4o-mini", "cost_per_1k_tokens": 0.00015},
            {"provider": "local", "model": "codellama-7b", "cost_per_1k_tokens": 0},
            {"provider": "rule_engine", "model": None, "cost_per_1k_tokens": 0},
        ],
        "AG-MA": [], # Rule engine, no LLM dependency
    }
```### 3.2 LLM Cost Tracker```python
class LLMCostTracker:
    """Real-time tracking of LLM call costs, benchmarking R05 V6.0-S2"""
    
    def record(self, agent_id, provider, model, tokens, cost):
        """Record a single call"""
        # Write to the time series database (Prometheus counter)
        ...
    
    def check_budget(self, agent_id, task_tier) -> BudgetStatus:
        """Check if the cost ceiling is exceeded"""
        PER_TASK_CEILING = {
            "simple": 0.01, "medium": 0.10, "complex": 1.00
        }
        current_task_cost = self.get_current_task_cost(agent_id)
        ceiling = PER_TASK_CEILING[task_tier]
        if current_task_cost >= ceiling:
            return BudgetStatus.EXCEEDED # → Automatically downgrade to small model
        elif current_task_cost >= ceiling * 0.8:
            return BudgetStatus.WARNING
        return BudgetStatus.OK
```---

## 4. Credential management [Based on R13 AC-4]

| Credential type | Management method | Rotation | Applicable Agent |
|---------|---------|------|-----------|
| Git API Token | Vault Dynamic Secrets | Every 24h | AG-CD |
| CI API Token | Vault Dynamic Secrets | Every 24h | AG-CT |
| K8s ServiceAccount | K8s RBAC + bound token | Automatic | AG-DO, AG-ST |
| Prometheus API Key | Vault KV v2 | Every 90 days | AG-MA |
| LLM API Key | Vault KV v2 (encrypted at-rest) | Every 90 days | AG-CD, AG-CT, AG-ST |
| Jira/Linear API Token | Vault KV v2 | Every 90 days | AG-FD |
| SAST Tool License | Vault KV v2 | By license period | AG-AU |
| BI Database Credentials | Vault Dynamic Secrets | Every 1h (short-term lease) | AG-BI |

---

## 5. Summary list of linkage between external faults and Agent LOA degradation

| Agent | Required dependency failure | LOA impact | Functional impact |
|-------|------------|---------|---------|
| AG-CD | Git is not available | LOA → ≤4 | Generate diff files for manual submission |
| AG-CD | LLM full link unavailable | LOA → ≤4 | Rule template generation code |
| AG-CT | CI system unavailable | LOA → ≤4 | Run test subset locally |
| AG-DO | K8s API is not available | LOA → ≤4 | Generate YAML for manual apply |
| AG-MA | Prometheus is not available | LOA → ≤4 | K8s metrics-server basic indicators |
| AG-AU | SAST tool not available | LOA → ≤4 | Mark "Unaudited" and block transfer door |
| AG-BI | Data warehouse is not available | LOA → ≤4 | Aggregate data using cache |

---

## 6. Acceptance criteria mapping

| AC | Verification method |
|----|---------|
| R13 AC-1: All inner loop 5 Agent required adapters are implemented | Integration test: At least 1 operation closed loop for each adapter |
| R13 AC-2: Tool switching demonstration | GitHub→GitLab adapter hot switching, AG-CD functionality remains unchanged |
| R13 AC-3: External fault degradation triggers correctly | Injection Git is not available → AG-CD LOA ≤4 verification |
| R13 AC-4: Credentials managed through Vault | Vault audit log verification + no hardcoded scans |