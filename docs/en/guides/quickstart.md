# Quickstart Guide

> ⚠️ UEWM is in Design Complete phase. This guide will be updated when Phase 0 implementation begins.

## Prerequisites

- Python 3.12+
- Docker Desktop
- 16GB RAM minimum (Profile-S)
- NVIDIA GPU recommended (A100 for full Profile-M)

## Quick Start (Coming Soon)

```bash
# 1. Clone
git clone https://github.com/YOUR_ORG/uewm.git && cd uewm

# 2. Install
pip install -e .

# 3. Initialize (Profile-S for local development)
uewm init --profile s

# 4. Start Brain Core
uewm start brain

# 5. Start inner ring Agents
uewm start agents --ring inner

# 6. Open Dashboard
open http://localhost:8080
```
