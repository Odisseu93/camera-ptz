# Camera PTZ — Project Rules

## Project Identity & Target Environment
- Real-time IP camera PTZ controller and streaming server via ONVIF/RTSP.
- Target host hardware: Intel Core i5 (1st Gen), 4 GB RAM, Linux.
- Core design priority: Security > Performance/Low Resource Usage > Code Clarity > Features.

## Language Standards
- Code (variables, functions, classes, docstrings, internal comments): **English**
- Terminal user-facing messages & prompts (print, CLI logs, speech feedback): **Portuguese (Brazil)**
- Technical documentation (README, ARCHITECTURE, ADRs, API docs): **English**
- Git commit messages: **English**, following Conventional Commits.

## Python Coding Standards
- Target runtime: Python 3.11+.
- Always include `from __future__ import annotations` at the top of Python modules.
- Strict type hints on all public functions, methods, and module interfaces.
- Google-style docstrings for public classes and functions (focusing on "why", never duplicating type signatures).
- Clean import ordering: standard library -> third-party -> local modules (isort standard).
- Maximum line length: 88 characters (Black standard).
- No unhandled generic exceptions (`except:` or `except Exception:` without logging/re-raising).
- Use `logging` for server/system events, avoid debug `print()` in production libraries.

## Anti-AI-Slop Rules (Strictly Enforced)
- NEVER generate trivial or tautological comments (e.g. `# increment index` before `i += 1`).
- NEVER use hyperbolic adjectives in docstrings ("cutting-edge", "blazing fast", "elegant", "robust").
- NEVER add orphan `TODO`/`FIXME` comments without concrete context or issue tracking.
- NEVER invent unnecessary abstractions, factories, or deep inheritance for single-use components.
- Preserve existing comments and docstrings unless explicitly changing that subsystem.
- Code must be self-documenting with precise, domain-accurate naming.
- Maximum 1 level of indirection; keep modules cohesive and under 300 lines where practical.

## Hardware & Resource Constraints (4GB RAM Budget)
- Web mode target memory footprint: <= 300 MB RSS total.
- Desktop mode target memory footprint: <= 150 MB RSS total.
- No heavy async/reactive frameworks or bloated ORMs.
- MJPEG stream encoding must use bounded frame rates (default 15 FPS) and adaptive JPEG quality (default 70).
- Share video capture resources; avoid duplicate RTSP decode pipelines.

## Security Directives
- Never commit or hardcode credentials, secrets, or dynamic session keys.
- Store sensitive configuration in `.env` (ignored by git).
- Hash passwords with bcrypt (never plaintext).
- Use JWT tokens stored in `HttpOnly`, `SameSite=Strict` cookies.
- Validate and bound all input parameters (e.g. PTZ coordinates, resolution dimensions, auth payloads).
- Enforce in-memory rate limiting on authentication and camera control endpoints.
- Apply security headers: Content-Security-Policy, X-Frame-Options DENY, X-Content-Type-Options nosniff.
