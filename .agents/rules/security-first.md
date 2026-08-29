# Security Directives

- Configuration: Secrets, keys, and credentials must only come from environment variables.
- Password Security: Passwords must be hashed using `bcrypt`. Compare hashes with `bcrypt.checkpw()`.
- Authentication: Issue short-lived JWT tokens signed with a cryptographically secure key generated at startup. Set tokens in `HttpOnly; SameSite=Strict` cookies.
- Rate Limiting: Apply sliding-window or token-bucket in-memory rate limiting to `/api/auth/*` and `/api/ptz/*`.
- Input Validation: Enforce strict type, length, and range checks on all HTTP endpoints (e.g. clamp pan/tilt velocities to valid ranges).
- HTTP Security Headers: Send `Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`.
- Command Execution: Never use `shell=True` in subprocess calls. Pass arguments as explicit lists.
