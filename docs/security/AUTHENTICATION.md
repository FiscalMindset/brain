# Authentication
PBKDF2 (120k rounds) + HMAC bearer tokens. Register/login at `/api/auth/*`. Tokens expire in 24h. Unknown-email logins run dummy verify and return identical 401.
