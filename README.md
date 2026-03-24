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

For detailed information on UEWM's core capabilities, please refer to the specific design documents:
- **[H-JEPA Brain Core & Architecture](docs/en/design/UEWM_Architecture_deliver_v1.1.md)**
- **[12 Specialized AI Agents](docs/en/design/UEWM_Agents_Design_deliver_v1.1.md)**
- **[Self-Evolution Mechanisms](docs/en/design/UEWM_Self_Evolution_deliver_v1.1.md)**
- **[Enterprise Security & Governance](docs/en/design/UEWM_Safety_Governance_deliver_v1.1.md)**
- **[EIP Protocol Specifications](docs/en/design/UEWM_EIP_Protocol_deliver_v1.1.md)**
- **[Data & Privacy Strategy](docs/en/design/UEWM_Data_Strategy_deliver_v1.1.md)**

### Architecture

Please refer to the comprehensive **[System Architecture Design](docs/en/design/UEWM_Architecture_deliver_v1.1.md)** document for detailed architectural diagrams, Brain Core component breakdowns, and sequence interactions.

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

📖 **[Full English documentation →](docs/en/)** | 📖 **[完整中文文档 →](docs/zh/)**

| Core Document | Path | Description |
|---------------|------|-------------|
| **Requirements V6.1** | [`requirements/UEWM_Requirements_V6.1.md`](docs/en/requirements/UEWM_Requirements_V6.1.md) | The unified source of truth for all requirements and ACs |
| **System Architecture 1.1** | [`design/UEWM_Architecture_deliver_v1.1.md`](docs/en/design/UEWM_Architecture_deliver_v1.1.md) | Core system architecture, Brain Core components, H-JEPA |
| **Agents Design 1.1** | [`design/UEWM_Agents_Design_deliver_v1.1.md`](docs/en/design/UEWM_Agents_Design_deliver_v1.1.md) | 12 AI Agents, three-ring architecture, ALFA framework |
| **Self-Evolution 1.1** | [`design/UEWM_Self_Evolution_deliver_v1.1.md`](docs/en/design/UEWM_Self_Evolution_deliver_v1.1.md) | Continuous learning, circuit breakers, Pareto optimization |
| **EIP Protocol 1.1** | [`design/UEWM_EIP_Protocol_deliver_v1.1.md`](docs/en/design/UEWM_EIP_Protocol_deliver_v1.1.md) | Engineering Intelligence Protocol, RPC/Messaging schemas |
| **Safety Governance 1.1** | [`design/UEWM_Safety_Governance_deliver_v1.1.md`](docs/en/design/UEWM_Safety_Governance_deliver_v1.1.md) | Security framework, RBAC compliance, SOC 2 roadmap |
| **Data Strategy 1.1** | [`design/UEWM_Data_Strategy_deliver_v1.1.md`](docs/en/design/UEWM_Data_Strategy_deliver_v1.1.md) | Training pipelines, knowledge transfer, federated learning |
| **Deployment Ops 1.1** | [`design/UEWM_Deployment_Operations_deliver_v1.1.md`](docs/en/design/UEWM_Deployment_Operations_deliver_v1.1.md) | Cluster topology, observability, error budget policies |
| **Integration Map 1.1** | [`design/UEWM_Integration_Map_deliver_v1.1.md`](docs/en/design/UEWM_Integration_Map_deliver_v1.1.md) | External tool adapters, system boundaries layer |
| **Engineering Spec 1.1** | [`design/UEWM_Engineering_Spec_deliver_v1.1.md`](docs/en/design/UEWM_Engineering_Spec_deliver_v1.1.md) | API dependencies, sequence architectures |
| **Traceability Matrix 1.1** | [`design/UEWM_Traceability_Matrix_deliver_v1.1.md`](docs/en/design/UEWM_Traceability_Matrix_deliver_v1.1.md) | End-to-end design requirement coverage assessment |

> *Note: Historic architecture iterations, coverage reports, and GAP analyses are maintained in the [`docs/en/design/arch_20260324`](docs/en/design/arch_20260324) and [`docs/en/design/arch_20260322`](docs/en/design/arch_20260322) archives.*

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

### 核心特性与系统架构

关于 UEWM 的详细核心能力与系统架构图纸，请参见对应的独立设计文档：
- **[H-JEPA 底座与系统核心架构](docs/zh/design/UEWM_Architecture_deliver_v1.1.md)**
- **[12 大工程 AI 智能体设计](docs/zh/design/UEWM_Agents_Design_deliver_v1.1.md)**
- **[自进化引擎与安全控制](docs/zh/design/UEWM_Self_Evolution_deliver_v1.1.md)**
- **[EIP 通信协议与规范](docs/zh/design/UEWM_EIP_Protocol_deliver_v1.1.md)**
- **[企业级安全治理与合规](docs/zh/design/UEWM_Safety_Governance_deliver_v1.1.md)**
- **[训练数据策略与联邦分级](docs/zh/design/UEWM_Data_Strategy_deliver_v1.1.md)**

### 文档

📖 **[完整中文文档目录 →](docs/zh/)** | 📖 **[Full English documentation →](docs/en/)**

| 核心交付文档 | 相对路径 | 文档说明 |
|--------------|----------|----------|
| **需求规格 V6.1** | [`requirements/UEWM_Requirements_V6.1.md`](docs/zh/requirements/UEWM_Requirements_V6.1.md) | 全项目需求与验收指标 (AC) 的唯一基线引用源 |
| **系统架构 1.1** | [`design/UEWM_Architecture_deliver_v1.1.md`](docs/zh/design/UEWM_Architecture_deliver_v1.1.md) | 系统整体架构、Brain Core 组件、H-JEPA 底座 |
| **智能体设计 1.1** | [`design/UEWM_Agents_Design_deliver_v1.1.md`](docs/zh/design/UEWM_Agents_Design_deliver_v1.1.md) | 12 个工程 AI Agent、三环架构、ALFA 控制框架 |
| **自进化机制 1.1** | [`design/UEWM_Self_Evolution_deliver_v1.1.md`](docs/zh/design/UEWM_Self_Evolution_deliver_v1.1.md) | 持续学习、安全断路器、帕累托进化优化验证 |
| **EIP 协议 1.1** | [`design/UEWM_EIP_Protocol_deliver_v1.1.md`](docs/zh/design/UEWM_EIP_Protocol_deliver_v1.1.md) | 各组件通信 RPC 与消息强类型载荷规范 |
| **安全治理 1.1** | [`design/UEWM_Safety_Governance_deliver_v1.1.md`](docs/zh/design/UEWM_Safety_Governance_deliver_v1.1.md) | 访问控制框架、RBAC 矩阵、SOC 2 安全演练路线 |
| **数据策略 1.1** | [`design/UEWM_Data_Strategy_deliver_v1.1.md`](docs/zh/design/UEWM_Data_Strategy_deliver_v1.1.md) | 训练流水线、基础模型选型与知识联邦学习策略 |
| **部署运维 1.1** | [`design/UEWM_Deployment_Operations_deliver_v1.1.md`](docs/zh/design/UEWM_Deployment_Operations_deliver_v1.1.md) | 拓扑图、可观测性规划、SLO 与错误预算响应 |
| **集成边界 1.1** | [`design/UEWM_Integration_Map_deliver_v1.1.md`](docs/zh/design/UEWM_Integration_Map_deliver_v1.1.md) | 外部工具适配器层、内外置模型调用系统边界 |
| **工程规格 1.1** | [`design/UEWM_Engineering_Spec_deliver_v1.1.md`](docs/zh/design/UEWM_Engineering_Spec_deliver_v1.1.md) | 组件接口调用序列结构细节与配置依赖表 |
| **追溯矩阵 1.1** | [`design/UEWM_Traceability_Matrix_deliver_v1.1.md`](docs/zh/design/UEWM_Traceability_Matrix_deliver_v1.1.md) | 需求到具体系统架构环节的 100% 测试覆盖映射 |

> *注：其余各版本的迭代架构合并记录、差异补丁包和覆盖率分析文档，请分别查阅 [`docs/zh/design/arch_20260324`](docs/zh/design/arch_20260324) 及 [`docs/zh/design/arch_20260322`](docs/zh/design/arch_20260322) 存档目录。*

### 许可证

UEWM 采用双许可：

- **开源：** [AGPL v3.0](LICENSE) — 可自由使用、修改和部署。若将 UEWM 作为网络服务提供，修改部分须以 AGPL 开源。
- **商业许可：** [联系我们](mailto:license@your-org.com)获取商业许可。

> **注意：** 预训练模型权重和客户专属 LoRA 适配器不在 AGPL 许可范围内，属于专有资产。

---

<p align="center">
  <sub>Built with ❤️ by the UEWM Team</sub>
</p>
