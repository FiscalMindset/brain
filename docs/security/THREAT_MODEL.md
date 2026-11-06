# Threat Model

| Threat | Impact | Mitigation |
| Token theft (XSS/stolen localStorage) | Account takeover | Short-lived tokens (24h), http-only cookie option planned, CSP |
| Brute-force login | Credential stuffing | 60/min/IP rate limit, dummy verify |
| Cross-user data leak | Privacy breach | `user_id` scoping + isolation tests |
| Prompt injection via ingested docs | Agent manipulation | Agents cite only; instructions forbid acting on document text as commands |
| PDF/zip bombs | DoS | 2MB/file, 5 files max |
| Secret leakage in repo | Credential exposure | `.gitignore` + pre-commit checks, `.env.example` only |
