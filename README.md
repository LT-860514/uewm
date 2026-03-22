<p align="center">
  <h1 align="center">🧠 UEWM — Universal Engineering World Model</h1>
  <p align="center">
    <em>An AI-native engineering intelligence platform powered by H-JEPA and Energy-Based Models</em>
  </p>
  <p align="center">
    <a href="#features">Features</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#quickstart">Quickstart</a> •
    <a href="#documentation">Docs</a> •
    <a href="#contributing">Contributing</a> •
    <a href="#license">License</a>
  </p>
  <p align="center">
    <a href="https://github.com/YOUR_ORG/uewm/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL%20v3-blue.svg" alt="License: AGPL v3"></a>
    <a href="https://github.com/YOUR_ORG/uewm/actions"><img src="https://img.shields.io/github/actions/workflow/status/YOUR_ORG/uewm/ci.yml?branch=main" alt="CI"></a>
    <img src="https://img.shields.io/badge/python-3.12+-green.svg" alt="Python 3.12+">
    <img src="https://img.shields.io/badge/status-Design%20Complete-orange.svg" alt="Status">
  </p>
</p>

---

[English](#english) | [中文](#中文)

## English

### What is UEWM?

UEWM (Universal Engineering World Model) is an AI system that builds a **predictive world model** of the entire software engineering lifecycle — from market analysis to production monitoring. Unlike traditional AI coding assistants that generate code token-by-token, UEWM reasons in a **latent embedding space** using Joint Embedding Predictive Architecture (H-JEPA) and makes decisions through **Energy-Based Model (EBM)** optimization.

Think of it as an AI that doesn't just write code — it *understands* your entire engineering organization and can predict the downstream consequences of every decision.

### Features

- **🧠 H-JEPA Brain Core** — 8-layer latent space (Z_market → Z_impl → Z_phys) with hierarchical prediction across multiple timescales
- **⚡ EBM Decision Engine** — Energy-based arbitration that evaluates proposals by predicting their full-system impact, not just local correctness
- **🤖 12 Specialized AI Agents** — Three-ring architecture (Inner/Middle/Outer) with dynamic Level of Automation (LOA 1-10) controlled by the ALFA framework
- **🔄 Self-Evolution** — LoRA-based continuous learning with safety envelope, circuit breaker, and Pareto improvement constraints
- **🛡️ Enterprise Security** — Threat model T1-T5, RBAC with 8 roles × 7 permissions, SOC 2 compliance roadmap, penetration test plan
- **📡 EIP Protocol** — Strong-typed gRPC + Kafka communication protocol with 15+ message types
- **🔐 Privacy-Preserving Knowledge Transfer** — KSL-tiered (0-4) federated learning with differential privacy (ε-budget)
- **📊 TRL Maturity Model** — Technology Readiness Levels (0-5) drive system behavior automatically

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              External World (Code / CI / Monitoring)         │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│         Multi-Modal Perception Layer (8 Encoders)            │
│         CodeBERT │ TFT │ TimesFM │ GraphSAGE+BERT           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    H-JEPA Brain Core                          │
│  Z-Buffer │ JEPA Predictor │ EBM Arbiter │ Causal Graph     │
│  Orchestration │ TRL Evaluator │ Error Budget │ Evolution    │
└──────────────────────────┬──────────────────────────────────┘
                           │ EIP Protocol (gRPC + Kafka)
┌──────────────────────────▼──────────────────────────────────┐
│              12 AI Agents (Three-Ring)                        │
│  Outer: PA│PD│BI│PR   Middle: SA│FD│AU   Inner: CD│CT│DO│ST│MA│
└─────────────────────────────────────────────────────────────┘
```

### Quickstart

> ⚠️ UEWM is currently in the **Design Complete** phase. Source code implementation begins in Phase 0. Star this repo to follow progress!

```bash
# Clone the repository
git clone https://github.com/YOUR_ORG/uewm.git
cd uewm

# (Coming in Phase 0) Setup development environment
# pip install -e ".[dev]"
# uewm init --profile s
```

### Project Status

| Phase | Status | Description |
|-------|--------|-------------|
| Design | ✅ Complete | 10 design docs, 112 acceptance criteria, 100% coverage |
| Phase 0 | 🔄 Starting | MVLS (3 Z-Layers), inner ring 5 Agents, EIP protocol |
| Phase 1 | ⏳ Planned | +2 Z-Layers, middle ring Agents, multi-tenant, federated learning |
| Phase 2 | ⏳ Planned | Full 8 Z-Layers, outer ring Agents, SOC 2 Type II |
| Phase 3 | ⏳ Planned | Full self-optimization, all TRL-5 |

### Documentation

📖 **[Full documentation →](docs/en/)**

| Document | Description |
|----------|-------------|
| [Architecture V7.0](docs/en/architecture/UEWM_Architecture_V7.md) | Core system architecture, Brain Core components, H-JEPA, EBM |
| [EIP Protocol V3.0](docs/en/architecture/UEWM_EIP_Protocol_V3.md) | Communication protocol, Protobuf IDL, JSON examples |
| [Agents Design V6.0](docs/en/design/UEWM_Agents_Design_V6.md) | 12 Agents, three-ring, ALFA, adapters |
| [Self Evolution V8.0](docs/en/design/UEWM_Self_Evolution_V8.md) | Safety envelope, circuit breaker, Pareto, federated learning |
| [Safety & Governance V6.0](docs/en/design/UEWM_Safety_Governance_V6.md) | Threat model, RBAC, SOC 2, penetration testing |
| [Engineering Spec V5.0](docs/en/design/UEWM_Engineering_Spec_V5.md) | Sequence diagrams, component dependencies, deployment artifacts |
| [Data Strategy V4.0](docs/en/design/UEWM_Data_Strategy_V4.md) | Training data pipeline, quality validation, compliance |
| [Deployment & Ops V4.0](docs/en/design/UEWM_Deployment_Operations_V4.md) | K8s topology, SLO system, error budget, load testing |
| [Integration Map V1.0](docs/en/design/UEWM_Integration_Map_V1.md) | External system adapters, LLM management, credentials |
| [Traceability Matrix V2.0](docs/en/traceability/UEWM_Traceability_Matrix_V2.md) | 112 ACs → design sections → verification methods |

### Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) and sign our [CLA](CLA.md) before submitting PRs.

**Good first issues:**
- [ ] Implement EIP Protobuf IDL compilation pipeline
- [ ] Create Z-Buffer Manager basic read/write operations
- [ ] Build Agent state machine framework
- [ ] Set up CI/CD pipeline with GitHub Actions

### License

UEWM is dual-licensed:

- **Open Source:** [GNU Affero General Public License v3.0](LICENSE) — free to use, modify, and deploy. If you offer UEWM as a network service, your modifications must be open-sourced under AGPL.
- **Commercial:** [Contact us](mailto:license@your-org.com) for a commercial license if AGPL doesn't fit your use case.

> **Note:** Pre-trained model weights and customer-specific LoRA adapters are NOT covered by the AGPL license and are proprietary.

---

## 中文

### UEWM 是什么？

UEWM（通用工程世界模型）是一个 AI 系统，它为整个软件工程生命周期（从市场分析到生产监控）构建**预测性世界模型**。与传统逐 token 生成代码的 AI 编程助手不同，UEWM 在**隐空间嵌入**中使用联合嵌入预测架构（H-JEPA）进行推理，并通过**能量基模型（EBM）**优化做出决策。

它不只是写代码——它*理解*你的整个工程组织，并能预测每个决策的下游影响。

### 核心特性

- **🧠 H-JEPA Brain Core** — 8 层隐空间，多时间尺度层级预测
- **⚡ EBM 决策引擎** — 基于能量的全系统影响评估
- **🤖 12 个专业 AI Agent** — 三环架构 + ALFA 自动化等级框架 (LOA 1-10)
- **🔄 自进化** — LoRA 持续学习 + 安全包络 + 断路器 + 帕累托约束
- **🛡️ 企业级安全** — T1-T5 威胁模型 + RBAC + SOC 2 合规
- **📡 EIP 协议** — 强类型 gRPC + Kafka 通信协议
- **🔐 隐私保护知识迁移** — KSL 分级联邦学习 + 差分隐私
- **📊 TRL 成熟度模型** — 技术就绪度等级 (0-5) 自动驱动系统行为

### 文档

📖 **[完整中文文档 →](docs/zh/)**

### 许可证

UEWM 采用双许可：

- **开源：** [AGPL v3.0](LICENSE) — 可自由使用、修改和部署。若将 UEWM 作为网络服务提供，修改部分须以 AGPL 开源。
- **商业许可：** [联系我们](mailto:license@your-org.com)获取商业许可。

> **注意：** 预训练模型权重和客户专属 LoRA 适配器不在 AGPL 许可范围内，属于专有资产。

---

<p align="center">
  <sub>Built with ❤️ by the UEWM Team</sub>
</p>
