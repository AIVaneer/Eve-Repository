# 🔒 Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| V10.x   | ✅ Active |
| V9.x    | ⚠️ Critical fixes only |
| < V9    | ❌ No longer supported |

## Reporting a Vulnerability

If you discover a security vulnerability in the PCVR toolkit, please report it responsibly:

1. **Do NOT open a public issue**
2. Email: [security contact — or use GitHub's private vulnerability reporting]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Affected module(s)
   - Potential impact

### What counts as a security issue?

- API key exposure in code or logs
- Vulnerabilities in the dashboard HTTP server (`dashboard.py`)
- Injection risks in automation rule evaluation (`automation.py`)
- Insecure handling of `github_token.txt` or `integration_keys.json`
- Cross-chain data manipulation vectors (`multichain.py`)

### What is NOT a security issue?

- Feature requests
- Bugs that don't have security implications
- Questions about how the toolkit works

## Response Timeline

- **Acknowledgment:** Within 48 hours
- **Assessment:** Within 1 week
- **Fix (if confirmed):** Within 2 weeks for critical, 4 weeks for moderate

## Security Best Practices

When using the toolkit:

- Never commit `integration_keys.json`, `github_token.txt`, or any API keys
- All sensitive files are listed in `.gitignore` — verify before pushing
- Run `python validate.py` regularly to check system integrity
- The dashboard server binds to `localhost` by default — do not expose to public networks without proper security
- Review automation rules before enabling — especially custom rules in `automation_rules_custom.json`

---

*© PCVR STUDIOS · 2026 — Contract: `0x05c870C5C6E7AF4298976886471c69Fc722107e4`*
