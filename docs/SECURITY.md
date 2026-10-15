# Security Policy

## Security Model
When deployed locally or exposed to external networks (e.g. via Cloudflare Tunnels), `camera-ptz` protects the camera feed and control endpoints through:
1. **Authentication**: Mandatory password verification using `bcrypt` and signed JWT session tokens.
2. **Cookie Security**: `HttpOnly`, `SameSite=Strict`, and `Secure` (when HTTPS) attributes on session cookies.
3. **Rate Limiting**: Sliding-window rate limiting on login attempts to mitigate brute-force attacks.
4. **Input Sanitization**: Range and type validation on all REST API inputs.
5. **Hardened Containerization**: Non-root execution, read-only root filesystems, dropped Linux capabilities, and `no-new-privileges`.
