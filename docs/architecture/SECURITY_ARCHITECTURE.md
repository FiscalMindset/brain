# Security Architecture
PBKDF2-HMAC-SHA256 password hashing, HMAC-signed bearer tokens (stdlib only), per-IP rate limiting on auth, dummy-verify on unknown email (timing-attack resistance), `require_user` dependency on every user route, startup `SECRET_KEY` warning when the dev default is used. Threat model: `../security/THREAT_MODEL.md`.
