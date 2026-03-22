# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| main    | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**DO NOT open a public issue for security vulnerabilities.**

Please report security vulnerabilities by emailing: security@your-org.com

You will receive a response within 48 hours. We will work with you to understand and address the issue before any public disclosure.

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Our Commitment

- We will acknowledge your report within 48 hours
- We will provide an estimated timeline for a fix within 7 days
- We will notify you when the vulnerability is fixed
- We will credit you (unless you prefer to remain anonymous)

## Threat Model

UEWM's threat model (T1-T5) is documented in our [Safety & Governance Design Document](docs/en/design/UEWM_Safety_Governance_V6.md). This covers: Agent injection (T1), LoRA poisoning (T2), cross-tenant leakage (T3), privilege escalation (T4), and Brain Core compromise (T5).
