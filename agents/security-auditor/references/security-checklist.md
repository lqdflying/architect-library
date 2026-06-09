# Security Checklist

Quick reference for web application security. Use alongside the security-auditor agent.

## Threat Modeling (Start Here)

- [ ] Trust boundaries mapped (requests, uploads, webhooks, third-party APIs, LLM output)
- [ ] Assets named (credentials, PII, payment data, admin actions, money movement)
- [ ] STRIDE run per boundary (Spoofing, Tampering, Repudiation, Info disclosure, DoS, Elevation)
- [ ] Abuse cases written next to use cases ("how would I misuse this?")

## Pre-Commit Checks

- [ ] No secrets in code (`git diff --cached | grep -i "password\|secret\|api_key\|token"`)
- [ ] `.gitignore` covers: `.env`, `.env.local`, `*.pem`, `*.key`
- [ ] `.env.example` uses placeholder values (not real secrets)

## Authentication

- [ ] Passwords hashed with bcrypt (≥12 rounds), scrypt, or argon2
- [ ] Session cookies: `httpOnly`, `secure`, `sameSite: 'lax'`
- [ ] Session expiration configured (reasonable max-age)
- [ ] Rate limiting on login endpoint (≤10 attempts per 15 minutes)
- [ ] Password reset tokens: time-limited (≤1 hour), single-use

## Authorization

- [ ] Every protected endpoint checks authentication
- [ ] Every resource access checks ownership/role (prevents IDOR)
- [ ] Admin endpoints require admin role verification
- [ ] API keys scoped to minimum necessary permissions

## Input Validation

- [ ] All user input validated at system boundaries
- [ ] Validation uses allowlists (not denylists)
- [ ] SQL queries parameterized (no string concatenation)
- [ ] HTML output encoded (use framework auto-escaping)
- [ ] Server-side URL fetches allowlisted; private/reserved IPs blocked (SSRF)

## Security Headers

- Content-Security-Policy, Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options, Referrer-Policy

## Dependency Security

- [ ] `npm audit` (or equivalent) run; critical/high addressed
- [ ] Lockfile committed; CI uses `npm ci`
- [ ] New dependencies reviewed (maintenance, `postinstall` scripts)

## AI / LLM Security

- [ ] Model output treated as untrusted
- [ ] Prompt injection assumed; permissions enforced in code
- [ ] Secrets and cross-tenant data kept out of context
- [ ] Tool permissions scoped; destructive actions require confirmation
- [ ] Token, rate, and recursion limits set

## OWASP Top 10 Quick Reference

| # | Vulnerability | Prevention |
|---|---------------|------------|
| 1 | Broken Access Control | Auth checks on every endpoint, ownership verification |
| 2 | Cryptographic Failures | HTTPS, strong hashing, no secrets in code |
| 3 | Injection | Parameterized queries, input validation |
| 4 | Insecure Design | Threat modeling at design time |
| 5 | Security Misconfiguration | Security headers, minimal permissions, audit deps |
| 6 | Vulnerable Components | `npm audit`, keep deps updated |
| 7 | Auth Failures | Strong passwords, rate limiting, session management |
| 8 | Data Integrity Failures | Verify updates/dependencies, signed artifacts |
| 9 | Logging Failures | Log security events, don't log secrets |
| 10 | SSRF | Validate/allowlist URLs, restrict outbound requests |

## OWASP Top 10 for LLMs Quick Reference

| ID | Risk | Prevention |
|----|------|------------|
| LLM01 | Prompt Injection | Enforce permissions in code, not only system prompt |
| LLM02 | Sensitive Information Disclosure | Keep secrets/PII out of prompts; filter outputs |
| LLM05 | Improper Output Handling | Treat model output as untrusted; validate and encode |
| LLM06 | Excessive Agency | Scope tool permissions; confirm destructive actions |
| LLM10 | Unbounded Consumption | Cap tokens, rate, and recursion depth |
