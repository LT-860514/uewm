# Contributing to UEWM

Thank you for your interest in contributing to UEWM! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Contributor License Agreement](#contributor-license-agreement)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Convention](#commit-convention)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## Contributor License Agreement (CLA)

Before we can accept your contributions, you must sign our [Contributor License Agreement](CLA.md). This is required because UEWM is dual-licensed (AGPL v3 + Commercial), and we need the legal right to include your contributions under both licenses.

**Why is this needed?** The CLA grants the UEWM project the right to distribute your contributions under the AGPL v3.0 open-source license AND under our commercial license. Without this, we cannot offer the commercial license that funds ongoing development.

The CLA bot will automatically prompt you when you open your first PR.

## Getting Started

### Prerequisites

- Python 3.12+
- Go 1.22+ (for EIP Gateway)
- Docker & Docker Compose
- Kubernetes (minikube or kind for local dev)
- protoc (Protocol Buffers compiler)
- buf (Protobuf linting)

### Setup Development Environment

```bash
# Clone the repo
git clone https://github.com/YOUR_ORG/uewm.git
cd uewm

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Verify setup
make test
```

### Project Structure

```
uewm/
├── src/                 # Source code
│   ├── brain/           # Brain Core (Z-Buffer, JEPA, EBM, Orchestration)
│   ├── agents/          # Agent framework + 12 agent implementations
│   ├── evolution/       # Self-evolution engine (safety envelope, circuit breaker)
│   ├── perception/      # Encoders + alignment training
│   ├── eip/             # EIP protocol implementation
│   ├── knowledge/       # Knowledge transfer + federated learning
│   ├── security/        # RBAC, audit, cert management
│   ├── data/            # Data pipeline + quality validation
│   └── testing/         # Load test + chaos test frameworks
├── proto/               # Protobuf IDL definitions
├── docs/                # Design documents (en + zh)
├── helm/                # Kubernetes Helm charts
├── tests/               # Test suites
└── examples/            # Example configurations
```

## Development Workflow

### Branching Strategy

- `main` — stable, release-ready code
- `develop` — integration branch for next release
- `feature/{name}` — feature branches (from `develop`)
- `fix/{name}` — bug fix branches
- `docs/{name}` — documentation updates

### Making Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature develop`
3. Make your changes
4. Write/update tests
5. Run tests: `make test`
6. Run linting: `make lint`
7. Commit with conventional commits
8. Push and open a PR against `develop`

## Coding Standards

### Python

- Style: [Black](https://black.readthedocs.io/) formatter (line length 100)
- Linting: [Ruff](https://docs.astral.sh/ruff/)
- Type hints: Required for all public APIs
- Docstrings: Google style
- Minimum test coverage: 80%

### Go (EIP Gateway)

- Style: `gofmt` + `golangci-lint`
- Tests: `go test ./...`

### Protobuf

- Linting: `buf lint`
- Breaking change detection: `buf breaking`
- All enums must start with `XXX_UNKNOWN = 0`

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `ci`, `chore`

Scopes: `brain`, `agent`, `eip`, `evolution`, `security`, `data`, `deploy`, `docs`

Examples:
```
feat(brain): implement Z-Buffer Manager read/write operations
fix(eip): correct PERMISSION_DENIED response code handling
docs(architecture): update EBM calibration plan section
test(agent): add DEGRADED state transition tests
```

## Pull Request Process

1. Ensure your PR description explains **what** and **why**
2. Link related issues: `Closes #123`
3. All CI checks must pass (tests, lint, protobuf compilation)
4. At least 1 maintainer approval required
5. Squash merge into `develop`

### PR Template

When you open a PR, you'll see a template. Please fill in all sections.

## Areas Where We Need Help

### High Priority (Phase 0)

- [ ] EIP Protobuf IDL implementation + gRPC service
- [ ] Z-Buffer Manager (read/write/snapshot)
- [ ] JEPA Predictor basic implementation
- [ ] EBM Arbiter with energy function
- [ ] Agent framework + state machine
- [ ] Inner ring Agent implementations (AG-CD, AG-CT, AG-DO, AG-ST, AG-MA)
- [ ] ALFA framework (LOA calculation)
- [ ] TRL Evaluator

### Medium Priority

- [ ] Safety envelope implementation
- [ ] Circuit breaker state machine
- [ ] Error budget engine
- [ ] Helm chart development
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Documentation improvements

### Good First Issues

Look for issues labeled [`good-first-issue`](https://github.com/YOUR_ORG/uewm/labels/good-first-issue).

## Questions?

- Open a [Discussion](https://github.com/YOUR_ORG/uewm/discussions) for general questions
- Open an [Issue](https://github.com/YOUR_ORG/uewm/issues) for bugs or feature requests
- Read the [design docs](docs/en/) for architecture understanding

Thank you for contributing to UEWM! 🚀
